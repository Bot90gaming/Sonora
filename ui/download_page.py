"""
Download page — GTK4 / Adwaita.
Shows active + completed downloads as cards in a scrollable list.
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from core.downloader import Downloader


_DEFAULT_DIR = Path(
    os.environ.get("XDG_MUSIC_DIR") or Path.home() / "Music"
)

_FORMATS = ["mp3", "m4a", "opus", "flac", "wav"]


class DownloadPage(Gtk.Box):
    """
    Receives download requests via download_song(song).
    Shows per-song progress cards.
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._downloader = Downloader()
        self._out_dir = _DEFAULT_DIR
        self._fmt_idx = 0   # mp3 default
        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # Settings bar
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.set_margin_top(12)
        bar.set_margin_bottom(12)
        bar.set_margin_start(16)
        bar.set_margin_end(16)

        dir_lbl = Gtk.Label(label="Save to:")
        dir_lbl.add_css_class("caption")

        self._dir_btn = Gtk.Button(label=str(self._out_dir))
        self._dir_btn.set_tooltip_text("Choose download folder")
        self._dir_btn.add_css_class("flat")
        self._dir_btn.connect("clicked", self._pick_dir)

        fmt_lbl = Gtk.Label(label="Format:")
        fmt_lbl.add_css_class("caption")

        self._fmt_drop = Gtk.DropDown.new_from_strings(_FORMATS)
        self._fmt_drop.set_selected(0)
        self._fmt_drop.connect("notify::selected", self._on_fmt_change)

        open_btn = Gtk.Button(label="Open folder")
        open_btn.add_css_class("flat")
        open_btn.connect("clicked", lambda *_: subprocess.Popen(
            ["xdg-open", str(self._out_dir)]))

        bar.append(dir_lbl)
        bar.append(self._dir_btn)
        bar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        bar.append(fmt_lbl)
        bar.append(self._fmt_drop)
        bar.append(Gtk.Box())  # spacer
        bar.append(open_btn)

        # Make spacer expand
        bar.get_first_child()  # dir_lbl — walk to spacer
        spacer = open_btn.get_prev_sibling()
        spacer.set_hexpand(True)

        self.append(bar)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Empty state
        self._empty = Adw.StatusPage()
        self._empty.set_icon_name("folder-download-symbolic")
        self._empty.set_title("No downloads yet")
        self._empty.set_description(
            "Right-click a track in Search or Library and choose Download")
        self._empty.set_vexpand(True)
        self.append(self._empty)

        # Card list (hidden until first download)
        self._card_sw = Gtk.ScrolledWindow()
        self._card_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._card_sw.set_vexpand(True)

        self._card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._card_box.set_margin_top(12)
        self._card_box.set_margin_bottom(12)
        self._card_box.set_margin_start(16)
        self._card_box.set_margin_end(16)

        self._card_sw.set_child(self._card_box)

    # ── Public API ────────────────────────────────────────────────────────────

    def download_song(self, song: dict):
        title  = song.get("title",  "Unknown")
        artist = song.get("artist", "")
        vid    = song.get("videoId", "")
        if not vid:
            return

        fmt = _FORMATS[self._fmt_drop.get_selected()]
        card = _DownloadCard(title, artist)

        # Show card list on first download
        if self._empty.get_parent() is self:
            self.remove(self._empty)
            self.append(self._card_sw)

        self._card_box.append(card)

        self._downloader.download(
            video_id   = vid,
            title      = title,
            artist     = artist,
            out_dir    = self._out_dir,
            audio_format = fmt,
            on_progress = card.set_progress,
            on_done     = card.set_done,
            on_error    = card.set_error,
        )

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _pick_dir(self, *_):
        dialog = Gtk.FileDialog()
        dialog.set_title("Choose download folder")
        dialog.select_folder(
            self.get_root(), None, self._on_dir_chosen, None)

    def _on_dir_chosen(self, dialog, result, _data):
        try:
            f = dialog.select_folder_finish(result)
            self._out_dir = Path(f.get_path())
            self._dir_btn.set_label(str(self._out_dir))
        except Exception:
            pass

    def _on_fmt_change(self, drop, _pspec):
        self._fmt_idx = drop.get_selected()


# ── Download card ─────────────────────────────────────────────────────────────

class _DownloadCard(Gtk.Box):
    def __init__(self, title: str, artist: str):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.add_css_class("card")
        self.set_margin_top(2)
        self.set_margin_bottom(2)

        inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        inner.set_margin_top(10)
        inner.set_margin_bottom(10)
        inner.set_margin_start(12)
        inner.set_margin_end(12)

        icon = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
        icon.set_pixel_size(32)
        inner.append(icon)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)

        lbl_title = Gtk.Label(label=title)
        lbl_title.set_halign(Gtk.Align.START)
        lbl_title.set_ellipsize(3)
        lbl_title.add_css_class("heading")

        lbl_artist = Gtk.Label(label=artist)
        lbl_artist.set_halign(Gtk.Align.START)
        lbl_artist.add_css_class("caption")
        lbl_artist.add_css_class("dim-label")

        info.append(lbl_title)
        info.append(lbl_artist)
        inner.append(info)

        self._status_lbl = Gtk.Label(label="Queued…")
        self._status_lbl.add_css_class("caption")
        self._status_lbl.add_css_class("dim-label")
        inner.append(self._status_lbl)

        self.append(inner)

        self._progress = Gtk.ProgressBar()
        self._progress.set_margin_start(12)
        self._progress.set_margin_end(12)
        self._progress.set_margin_bottom(8)
        self._progress.set_fraction(0)
        self.append(self._progress)

    def set_progress(self, pct: int):
        self._progress.set_fraction(pct / 100)
        self._status_lbl.set_label(f"{pct}%")

    def set_done(self, path: str):
        self._progress.set_fraction(1.0)
        self._status_lbl.set_label("Done ✓")
        self._status_lbl.remove_css_class("dim-label")

    def set_error(self, msg: str):
        self._status_lbl.set_label(f"Error: {msg[:60]}")
        self._status_lbl.remove_css_class("dim-label")
