"""
Shared GTK4 helper widgets and utilities.
"""
from __future__ import annotations
import threading
import requests

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio


def fmt_ms(ms: int) -> str:
    s = max(0, ms // 1000)
    return f"{s // 60}:{s % 60:02d}"


def fmt_dur(s) -> str:
    if not s:
        return "--"
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


def load_thumbnail_async(url: str, callback):
    """
    Fetch `url` in a daemon thread; call callback(pixbuf | None) on the
    GLib main loop when done.
    """
    def _fetch():
        try:
            data = requests.get(url, timeout=6).content
            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pix = loader.get_pixbuf()
            pix = pix.scale_simple(56, 56, GdkPixbuf.InterpType.BILINEAR)
            GLib.idle_add(callback, pix)
        except Exception:
            GLib.idle_add(callback, None)

    threading.Thread(target=_fetch, daemon=True).start()


def track_row(song: dict) -> Gtk.Box:
    """
    Build a compact horizontal row for one track — used in both Search and Library.
    The returned box has a `.song` attribute set to the song dict.
    """
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.set_margin_top(6)
    box.set_margin_bottom(6)
    box.set_margin_start(12)
    box.set_margin_end(12)
    box.song = song   # Lưu bài hát để truy xuất khi kích hoạt.

    # Ảnh bìa giữ chỗ
    thumb = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
    thumb.set_pixel_size(40)
    thumb.add_css_class("track-thumb")
    box.append(thumb)

    # Tên bài hát và nghệ sĩ
    info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    info.set_hexpand(True)

    lbl_title = Gtk.Label(label=song.get("title", ""))
    lbl_title.set_halign(Gtk.Align.START)
    lbl_title.set_ellipsize(3)   # Cắt bớt văn bản ở cuối theo quy tắc của Pango.
    lbl_title.add_css_class("title-4")

    lbl_artist = Gtk.Label(label=song.get("artist", ""))
    lbl_artist.set_halign(Gtk.Align.START)
    lbl_artist.set_ellipsize(3)
    lbl_artist.add_css_class("caption")
    lbl_artist.add_css_class("dim-label")

    info.append(lbl_title)
    info.append(lbl_artist)
    box.append(info)

    # Thời lượng
    lbl_dur = Gtk.Label(label=fmt_dur(song.get("duration")))
    lbl_dur.add_css_class("caption")
    lbl_dur.add_css_class("dim-label")
    lbl_dur.set_width_chars(5)
    lbl_dur.set_xalign(1.0)
    box.append(lbl_dur)

    # Tải ảnh bìa nếu có
    url = song.get("thumbnail", "")
    if url:
        def _set_thumb(pix):
            if pix:
                thumb.set_from_pixbuf(pix)
        load_thumbnail_async(url, _set_thumb)

    return box


def make_track_list(songs: list[dict],
                    on_activate,
                    on_menu=None) -> Gtk.ScrolledWindow:
    """
    Build a scrollable Gtk.ListBox of track rows.
    on_activate(song) is called on double-click / Enter.
    on_menu(song, x, y) is called on right-click (optional).
    Returns the ScrolledWindow containing the list.
    """
    lb = Gtk.ListBox()
    lb.set_selection_mode(Gtk.SelectionMode.SINGLE)
    lb.add_css_class("boxed-list")

    for song in songs:
        row = Gtk.ListBoxRow()
        row.song = song
        row.set_child(track_row(song))
        lb.append(row)

    def _activated(listbox, row):
        on_activate(row.song)

    lb.connect("row-activated", _activated)

    if on_menu:
        gesture = Gtk.GestureClick()
        gesture.set_button(3)   # Nhấn chuột phải.

        def _right_click(g, n, x, y):
            row = lb.get_row_at_y(int(y))
            if row:
                on_menu(row.song, x, y)

        gesture.connect("pressed", _right_click)
        lb.add_controller(gesture)

    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    sw.set_vexpand(True)
    sw.set_child(lb)
    return sw
