"""
Bottom player bar — GTK4 / Adwaita.
"""
from __future__ import annotations
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from core.player import Player
from ui.widgets import fmt_ms, load_thumbnail_async, thumbnail_url


class PlayerBar(Gtk.Box):
    """
    Fixed-height bar at the bottom of the window.
    Signals emitted (via plain Python callbacks to avoid GObject boilerplate):
        request_next()
        request_prev()
    """

    def __init__(self, player: Player):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.player = player
        self._dragging   = False
        self._liked       = False
        self._current_vid = ""
        self.on_next: callable | None = None
        self.on_prev: callable | None = None
        self.on_like: callable | None = None   # on_like(video_id, liked: bool)

        self.add_css_class("player-bar")

        # Wire player callbacks
        self.player.on_position     = self._on_position
        self.player.on_state_change = self._on_state
        self.player.on_error        = self._on_error

        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        self.set_spacing(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(8)
        self.set_margin_bottom(8)

        # ── Left: art + info ─────────────────────────────────────────────────
        left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        left.set_size_request(260, -1)

        self._thumb = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
        self._thumb.set_pixel_size(24)
        self._thumb.set_size_request(72, 40)
        self._thumb.add_css_class("icon-dropshadow")
        self._thumb.add_css_class("player-art")
        left.append(self._thumb)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        info.set_valign(Gtk.Align.CENTER)

        self._lbl_title = Gtk.Label(label="Nothing playing")
        self._lbl_title.set_halign(Gtk.Align.START)
        self._lbl_title.set_ellipsize(3)
        self._lbl_title.set_max_width_chars(28)
        self._lbl_title.add_css_class("heading")

        self._lbl_artist = Gtk.Label(label="")
        self._lbl_artist.set_halign(Gtk.Align.START)
        self._lbl_artist.set_ellipsize(3)
        self._lbl_artist.set_max_width_chars(28)
        self._lbl_artist.add_css_class("caption")
        self._lbl_artist.add_css_class("dim-label")

        info.append(self._lbl_title)
        info.append(self._lbl_artist)
        left.append(info)
        self.append(left)

        # ── Centre: controls + seek ───────────────────────────────────────────
        centre = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        centre.set_hexpand(True)
        centre.set_valign(Gtk.Align.CENTER)

        # Transport buttons
        btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btns.set_halign(Gtk.Align.CENTER)
        btns.add_css_class("player-controls")

        self._btn_prev = _icon_btn("media-skip-backward-symbolic",  "Previous")
        self._btn_play = _icon_btn("media-playback-start-symbolic", "Play / Pause")
        self._btn_next = _icon_btn("media-skip-forward-symbolic",   "Next")

        self._btn_prev.add_css_class("player-transport")
        self._btn_next.add_css_class("player-transport")
        self._btn_play.add_css_class("player-play")
        self._btn_play.add_css_class("suggested-action")
        self._btn_play.add_css_class("circular")

        self._btn_prev.connect("clicked", lambda *_: self.on_prev and self.on_prev())
        self._btn_next.connect("clicked", lambda *_: self.on_next and self.on_next())
        self._btn_play.connect("clicked", self._toggle_play)

        btns.append(self._btn_prev)
        btns.append(self._btn_play)
        btns.append(self._btn_next)
        centre.append(btns)

        # Seek row
        seek_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        seek_row.set_halign(Gtk.Align.CENTER)
        seek_row.add_css_class("player-seek")

        self._lbl_pos = Gtk.Label(label="0:00")
        self._lbl_pos.add_css_class("caption")
        self._lbl_pos.add_css_class("dim-label")
        self._lbl_pos.set_width_chars(5)

        self._seek = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._seek.set_range(0, 1000)
        self._seek.set_size_request(320, -1)
        self._seek.set_draw_value(False)
        self._seek.set_hexpand(False)
        # GTK4: use GestureDrag instead of button-press/release events
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin",  lambda *_: setattr(self, "_dragging", True))
        drag.connect("drag-end",    self._on_seek_drag_end)
        self._seek.add_controller(drag)

        self._lbl_dur = Gtk.Label(label="0:00")
        self._lbl_dur.add_css_class("caption")
        self._lbl_dur.add_css_class("dim-label")
        self._lbl_dur.set_width_chars(5)

        seek_row.append(self._lbl_pos)
        seek_row.append(self._seek)
        seek_row.append(self._lbl_dur)
        self._loop_btn = Gtk.ToggleButton()
        self._loop_btn.set_icon_name("media-playlist-repeat-song-symbolic")
        self._loop_btn.set_tooltip_text("Repeat current track")
        self._loop_btn.add_css_class("flat")
        self._loop_btn.add_css_class("circular")
        self._loop_btn.connect("toggled", self._on_loop_toggled)
        seek_row.append(self._loop_btn)
        centre.append(seek_row)
        self.append(centre)

        # ── Right: like + volume ──────────────────────────────────────────────
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        right.set_size_request(220, -1)
        right.set_halign(Gtk.Align.END)
        right.set_valign(Gtk.Align.CENTER)
        right.add_css_class("player-side-controls")

        # Like / heart button
        self._like_btn = Gtk.ToggleButton()
        self._like_btn.set_icon_name("emblem-favorite-symbolic")
        self._like_btn.set_tooltip_text("Like this song")
        self._like_btn.set_valign(Gtk.Align.CENTER)
        self._like_btn.add_css_class("flat")
        self._like_btn.add_css_class("circular")
        self._like_btn.set_sensitive(False)   # disabled until a song loads
        self._like_btn.connect("toggled", self._on_like_toggled)
        right.append(self._like_btn)

        vol_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic")
        right.append(vol_icon)

        self._vol = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._vol.set_range(0, 1)
        self._vol.set_value(0.8)
        self._vol.set_size_request(100, -1)
        self._vol.set_draw_value(False)
        self._vol.connect("value-changed", self._on_volume)
        right.append(self._vol)
        self.append(right)

    # ── Public ────────────────────────────────────────────────────────────────

    def set_loading(self, loading: bool):
        """Show/hide a spinner on the play button while audio is downloading."""
        if loading:
            self._btn_play.set_icon_name("content-loading-symbolic")
            self._btn_play.set_sensitive(False)
        else:
            self._btn_play.set_icon_name("media-playback-start-symbolic")
            self._btn_play.set_sensitive(True)

    def load_song(self, song: dict):
        self._lbl_title.set_label(song.get("title", "Unknown"))
        self._lbl_artist.set_label(song.get("artist", ""))
        self._thumb.set_from_icon_name("audio-x-generic-symbolic")
        url = thumbnail_url(song)
        if url:
            load_thumbnail_async(url, self._set_thumb)

        # Reset like state for new song
        self._current_vid = song.get("videoId", "")
        self._liked = False
        # Block signal to avoid triggering the callback while resetting
        self._like_btn.handler_block_by_func(self._on_like_toggled)
        self._like_btn.set_active(False)
        self._like_btn.set_sensitive(bool(self._current_vid))
        self._like_btn.handler_unblock_by_func(self._on_like_toggled)
        self._update_like_style()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _toggle_play(self, *_):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def _on_seek_drag_end(self, gesture, offset_x, offset_y):
        self._dragging = False
        self.player.seek_percent(self._seek.get_value() / 1000.0)

    def _on_volume(self, scale):
        self.player.set_volume(scale.get_value())

    def _on_loop_toggled(self, button):
        loop_enabled = button.get_active()
        button.set_tooltip_text(
            "Stop repeating current track" if loop_enabled
            else "Repeat current track")
        if loop_enabled:
            button.add_css_class("accent")
        else:
            button.remove_css_class("accent")
        self.player.set_loop_enabled(loop_enabled)

    def _on_position(self, pos_ms: int, dur_ms: int):
        self._lbl_pos.set_label(fmt_ms(pos_ms))
        self._lbl_dur.set_label(fmt_ms(dur_ms))
        if not self._dragging and dur_ms > 0:
            self._seek.set_value(pos_ms / dur_ms * 1000)

    def _on_state(self, state: str):
        icon = ("media-playback-pause-symbolic"
                if state == "playing"
                else "media-playback-start-symbolic")
        self._btn_play.set_icon_name(icon)
        if state == "ended" and self.on_next:
            self.on_next()

    def _on_like_toggled(self, btn):
        self._liked = btn.get_active()
        self._update_like_style()
        if self.on_like and self._current_vid:
            self.on_like(self._current_vid, self._liked)

    def _update_like_style(self):
        if self._liked:
            self._like_btn.add_css_class("accent")
        else:
            self._like_btn.remove_css_class("accent")

    def _on_error(self, msg: str):
        self._lbl_title.set_label(f"Error: {msg}")

    def _set_thumb(self, pix):
        if pix:
            self._thumb.set_from_pixbuf(pix)


# ── Helper ────────────────────────────────────────────────────────────────────

def _icon_btn(icon: str, tooltip: str) -> Gtk.Button:
    btn = Gtk.Button()
    btn.set_icon_name(icon)
    btn.set_tooltip_text(tooltip)
    btn.set_valign(Gtk.Align.CENTER)
    btn.add_css_class("circular")
    btn.add_css_class("flat")
    return btn
