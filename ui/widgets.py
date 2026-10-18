"""
Shared GTK4 helper widgets and utilities.
"""
from __future__ import annotations
import threading
import requests
from urllib.parse import quote

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib


def fmt_ms(ms: int) -> str:
    s = max(0, ms // 1000)
    return f"{s // 60}:{s % 60:02d}"


def fmt_dur(s) -> str:
    if not s:
        return "--"
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


def thumbnail_url(song: dict) -> str:
    video_id = song.get("videoId")
    if video_id:
        return f"https://i.ytimg.com/vi/{quote(str(video_id), safe='')}/mqdefault.jpg"
    return song.get("thumbnail", "")


def load_picture_async(url: str, callback):
    """Fetch an image as a GDK texture and call back on the GTK main loop."""
    def _fetch():
        try:
            response = requests.get(url, timeout=6)
            response.raise_for_status()
            data = response.content
            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            GLib.idle_add(callback, texture)
        except Exception:
            GLib.idle_add(callback, None)

    threading.Thread(target=_fetch, daemon=True).start()


def track_row(song: dict,
              on_queue: callable | None = None,
              on_download: callable | None = None) -> Gtk.Box:
    """
    Build a compact horizontal row for one track.
    Optionally shows inline Queue and Download icon buttons.
    """
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.set_margin_top(6)
    box.set_margin_bottom(6)
    box.set_margin_start(12)
    box.set_margin_end(12)
    box.song = song

    # Thumbnail
    thumb = Gtk.Overlay()
    thumb.set_size_request(72, 40)
    picture = Gtk.Picture()
    picture.set_content_fit(Gtk.ContentFit.COVER)
    picture.set_can_shrink(True)
    picture.set_size_request(72, 40)
    picture.add_css_class("track-thumb")
    thumb.set_child(picture)

    placeholder = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
    placeholder.set_pixel_size(24)
    placeholder.set_halign(Gtk.Align.CENTER)
    placeholder.set_valign(Gtk.Align.CENTER)
    placeholder.add_css_class("track-thumb-placeholder")
    thumb.add_overlay(placeholder)
    box.append(thumb)

    # Title + artist
    info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    info.set_hexpand(True)

    lbl_title = Gtk.Label(label=song.get("title", ""))
    lbl_title.set_halign(Gtk.Align.START)
    lbl_title.set_ellipsize(3)
    lbl_title.add_css_class("title-4")

    lbl_artist = Gtk.Label(label=song.get("artist", ""))
    lbl_artist.set_halign(Gtk.Align.START)
    lbl_artist.set_ellipsize(3)
    lbl_artist.add_css_class("caption")
    lbl_artist.add_css_class("dim-label")

    info.append(lbl_title)
    info.append(lbl_artist)
    box.append(info)

    # Duration
    lbl_dur = Gtk.Label(label=fmt_dur(song.get("duration")))
    lbl_dur.add_css_class("caption")
    lbl_dur.add_css_class("dim-label")
    lbl_dur.set_width_chars(5)
    lbl_dur.set_xalign(1.0)
    box.append(lbl_dur)

    # ── Inline action buttons ────────────────────────────────────────────────
    if on_queue is not None:
        btn_q = Gtk.Button()
        btn_q.set_icon_name("list-add-symbolic")
        btn_q.set_tooltip_text("Add to queue")
        btn_q.set_valign(Gtk.Align.CENTER)
        btn_q.add_css_class("flat")
        btn_q.add_css_class("circular")
        btn_q.connect("clicked", lambda *_: on_queue(song))
        box.append(btn_q)

    if on_download is not None:
        btn_dl = Gtk.Button()
        btn_dl.set_icon_name("folder-download-symbolic")
        btn_dl.set_tooltip_text("Download")
        btn_dl.set_valign(Gtk.Align.CENTER)
        btn_dl.add_css_class("flat")
        btn_dl.add_css_class("circular")
        btn_dl.connect("clicked", lambda *_: on_download(song))
        box.append(btn_dl)

    # Load thumbnail if available
    url = thumbnail_url(song)
    if url:
        def _set_thumb(texture):
            if texture:
                picture.set_paintable(texture)
                placeholder.set_visible(False)
        load_picture_async(url, _set_thumb)

    return box


def make_track_list(songs: list[dict],
                    on_activate,
                    on_queue: callable | None = None,
                    on_download: callable | None = None,
                    on_menu=None) -> Gtk.ScrolledWindow:
    """
    Build a scrollable Gtk.ListBox of track rows.
    on_activate(song)  — double-click / Enter
    on_queue(song)     — inline queue button (optional)
    on_download(song)  — inline download button (optional)
    on_menu(song,x,y)  — right-click (optional)
    """
    lb = Gtk.ListBox()
    lb.set_selection_mode(Gtk.SelectionMode.SINGLE)
    lb.add_css_class("boxed-list")

    for song in songs:
        row = Gtk.ListBoxRow()
        row.song = song
        row.set_child(track_row(song,
                                on_queue=on_queue,
                                on_download=on_download))
        lb.append(row)

    def _activated(listbox, row):
        on_activate(row.song)

    lb.connect("row-activated", _activated)

    if on_menu:
        gesture = Gtk.GestureClick()
        gesture.set_button(3)

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
