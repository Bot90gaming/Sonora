"""
Bottom player bar — GTK4 / Adwaita.
"""
from __future__ import annotations
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GLib, GdkPixbuf

from core.player import Player
from ui.widgets import fmt_ms, load_thumbnail_async


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
        self._dragging = False
        self.on_next: callable | None = None
        self.on_prev: callable | None = None

        self.add_css_class("toolbar")
        self.set_margin_top(0)

        # Kết nối các hàm xử lý sự kiện của trình phát.
        self.player.on_position     = self._on_position
        self.player.on_state_change = self._on_state
        self.player.on_error        = self._on_error

        self._build()

    # ── Khởi tạo giao diện ───────────────────────────────────────────────────

    def _build(self):
        self.set_spacing(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(8)
        self.set_margin_bottom(8)

        # ── Bên trái: ảnh bìa và thông tin ───────────────────────────────────
        left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        left.set_size_request(260, -1)

        self._thumb = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
        self._thumb.set_pixel_size(56)
        self._thumb.add_css_class("icon-dropshadow")
        left.append(self._thumb)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
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

        # ── Ở giữa: điều khiển và tua bài ────────────────────────────────────
        centre = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        centre.set_hexpand(True)
        centre.set_valign(Gtk.Align.CENTER)

        # Các nút điều khiển phát
        btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btns.set_halign(Gtk.Align.CENTER)

        self._btn_prev = _icon_btn("media-skip-backward-symbolic",  "Previous")
        self._btn_play = _icon_btn("media-playback-start-symbolic", "Play / Pause")
        self._btn_next = _icon_btn("media-skip-forward-symbolic",   "Next")

        self._btn_play.add_css_class("suggested-action")
        self._btn_play.add_css_class("circular")

        self._btn_prev.connect("clicked", lambda *_: self.on_prev and self.on_prev())
        self._btn_next.connect("clicked", lambda *_: self.on_next and self.on_next())
        self._btn_play.connect("clicked", self._toggle_play)

        btns.append(self._btn_prev)
        btns.append(self._btn_play)
        btns.append(self._btn_next)
        centre.append(btns)

        # Hàng điều khiển tua bài
        seek_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        seek_row.set_halign(Gtk.Align.CENTER)

        self._lbl_pos = Gtk.Label(label="0:00")
        self._lbl_pos.add_css_class("caption")
        self._lbl_pos.add_css_class("dim-label")
        self._lbl_pos.set_width_chars(5)

        self._seek = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._seek.set_range(0, 1000)
        self._seek.set_size_request(320, -1)
        self._seek.set_draw_value(False)
        self._seek.set_hexpand(False)
        # GTK4: dùng GestureDrag thay cho sự kiện nhấn/thả chuột.
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
        centre.append(seek_row)
        self.append(centre)

        # ── Bên phải: âm lượng ───────────────────────────────────────────────
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        right.set_size_request(200, -1)
        right.set_halign(Gtk.Align.END)
        right.set_valign(Gtk.Align.CENTER)

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

    # ── Phần công khai ───────────────────────────────────────────────────────

    def load_song(self, song: dict):
        self._lbl_title.set_label(song.get("title", "Unknown"))
        self._lbl_artist.set_label(song.get("artist", ""))
        self._thumb.set_from_icon_name("audio-x-generic-symbolic")
        url = song.get("thumbnail", "")
        if url:
            load_thumbnail_async(url, self._set_thumb)

    # ── Hàm xử lý sự kiện ────────────────────────────────────────────────────

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

    def _on_error(self, msg: str):
        self._lbl_title.set_label(f"Error: {msg}")

    def _set_thumb(self, pix):
        if pix:
            self._thumb.set_from_pixbuf(pix)


# ── Hàm hỗ trợ ───────────────────────────────────────────────────────────────

def _icon_btn(icon: str, tooltip: str) -> Gtk.Button:
    btn = Gtk.Button()
    btn.set_icon_name(icon)
    btn.set_tooltip_text(tooltip)
    btn.add_css_class("circular")
    btn.add_css_class("flat")
    return btn
