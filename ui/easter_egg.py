"""
Easter egg window — plays assets/easter_egg.mp4 when Jack-J97 is searched.
"""
from __future__ import annotations
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Adw, Gio, GLib

# Path to the bundled video, relative to this file's package root
_ASSET = Path(__file__).parent.parent / "assets" / "easter_egg.mp4"

_shown_this_session = False   # only surprise them once per run


def maybe_trigger(query: str, parent: Gtk.Window):
    """Call this after every search. Shows the egg if the query matches."""
    global _shown_this_session
    if _shown_this_session:
        return
    if "jack-j97" not in query.lower() and "jackj97" not in query.lower():
        return
    if not _ASSET.exists():
        return   # no video file → silently skip
    _shown_this_session = True
    # Small delay so search results appear first
    GLib.timeout_add(400, lambda: (_open(parent), False))


def _open(parent: Gtk.Window):
    win = _EasterEggWindow(parent)
    win.present()


class _EasterEggWindow(Adw.Window):
    def __init__(self, parent: Gtk.Window):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(False)
        self.set_title("🎵 !!!")
        self.set_default_size(480, 320)
        self.set_resizable(False)

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        toolbar.add_top_bar(header)

        # GTK4 native video widget
        video = Gtk.Video()
        video.set_file(Gio.File.new_for_path(str(_ASSET)))
        video.set_autoplay(True)
        video.set_loop(False)
        video.set_vexpand(True)
        video.set_hexpand(True)

        toolbar.set_content(video)
        self.set_content(toolbar)
