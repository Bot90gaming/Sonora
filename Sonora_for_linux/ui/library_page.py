"""
Library page — GTK4 / Adwaita.
Sidebar: Liked Songs / Playlists / Albums
Main panel: track list for the selected item.
"""
from __future__ import annotations
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from core.api import MusicAPI
from ui.widgets import make_track_list


class LibraryPage(Gtk.Paned):
    """
    Horizontal Paned: left sidebar + right track panel.
    on_play(song)  — called on track activation.
    on_queue(song) — called on right-click → Add to queue.
    """

    def __init__(self, api: MusicAPI,
                 on_play: callable,
                 on_queue: callable,
                 on_download: callable | None = None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.api         = api
        self.on_play     = on_play
        self.on_queue    = on_queue
        self.on_download = on_download
        self._track_panel: Gtk.Widget | None = None
        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # ── Left sidebar ──────────────────────────────────────────────────────
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar_box.set_size_request(220, -1)

        sidebar_header = Gtk.Label(label="Library")
        sidebar_header.add_css_class("heading")
        sidebar_header.set_margin_top(16)
        sidebar_header.set_margin_bottom(8)
        sidebar_header.set_margin_start(16)
        sidebar_header.set_halign(Gtk.Align.START)
        sidebar_box.append(sidebar_header)

        self._sidebar_lb = Gtk.ListBox()
        self._sidebar_lb.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._sidebar_lb.add_css_class("navigation-sidebar")
        self._sidebar_lb.connect("row-selected", self._on_sidebar_select)

        sidebar_sw = Gtk.ScrolledWindow()
        sidebar_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_sw.set_vexpand(True)
        sidebar_sw.set_child(self._sidebar_lb)
        sidebar_box.append(sidebar_sw)

        self.set_start_child(sidebar_box)
        self.set_resize_start_child(False)
        self.set_shrink_start_child(False)

        # ── Right panel ───────────────────────────────────────────────────────
        self._right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._right.set_hexpand(True)

        self._status = Adw.StatusPage()
        self._status.set_icon_name("emblem-music-symbolic")
        self._status.set_title("Your Library")
        self._status.set_description("Select a playlist or album from the sidebar")
        self._status.set_vexpand(True)
        self._right.append(self._status)

        self.set_end_child(self._right)
        self.set_resize_end_child(True)

        # Populate sidebar
        self._populate_sidebar()

    def _populate_sidebar(self):
        # Static items
        for label, key in [
            ("♥  Liked Songs", "liked"),
            ("── Playlists ──", None),
        ]:
            row = Gtk.ListBoxRow()
            row._key = key
            lbl = Gtk.Label(label=label)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_top(8)
            lbl.set_margin_bottom(8)
            lbl.set_margin_start(12)
            if key is None:
                lbl.add_css_class("caption")
                lbl.add_css_class("dim-label")
                row.set_selectable(False)
            row.set_child(lbl)
            self._sidebar_lb.append(row)

        # Load playlists + albums async
        threading.Thread(target=self._fetch_sidebar, daemon=True).start()

    def _fetch_sidebar(self):
        try:
            playlists = self.api.get_library_playlists() or []
        except Exception:
            playlists = []
        try:
            albums = self.api.get_library_albums() or []
        except Exception:
            albums = []
        GLib.idle_add(self._append_sidebar_items, playlists, albums)

    def _append_sidebar_items(self, playlists, albums):
        for pl in playlists:
            row = Gtk.ListBoxRow()
            row._key  = ("playlist", pl.get("playlistId", ""))
            row._name = pl.get("title", "Playlist")
            lbl = Gtk.Label(label=f"  {row._name}")
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_top(6)
            lbl.set_margin_bottom(6)
            lbl.set_margin_start(12)
            lbl.set_ellipsize(3)
            lbl.set_max_width_chars(22)
            row.set_child(lbl)
            self._sidebar_lb.append(row)

        # Albums separator
        sep_row = Gtk.ListBoxRow()
        sep_row._key = None
        sep_row.set_selectable(False)
        sep_lbl = Gtk.Label(label="── Albums ──")
        sep_lbl.set_halign(Gtk.Align.START)
        sep_lbl.set_margin_start(12)
        sep_lbl.add_css_class("caption")
        sep_lbl.add_css_class("dim-label")
        sep_row.set_child(sep_lbl)
        self._sidebar_lb.append(sep_row)

        for al in albums:
            row = Gtk.ListBoxRow()
            row._key  = ("album", al.get("browseId", ""))
            row._name = al.get("title", "Album")
            lbl = Gtk.Label(label=f"  {row._name}")
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_top(6)
            lbl.set_margin_bottom(6)
            lbl.set_margin_start(12)
            lbl.set_ellipsize(3)
            lbl.set_max_width_chars(22)
            row.set_child(lbl)
            self._sidebar_lb.append(row)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_sidebar_select(self, lb, row):
        if row is None or not hasattr(row, "_key"):
            return
        key = row._key
        if key is None:
            return
        if key == "liked":
            self._load_tracks("liked", None)
        elif isinstance(key, tuple):
            kind, bid = key
            self._load_tracks(kind, bid)

    def _load_tracks(self, kind: str, browse_id: str | None):
        self._show_spinner()

        def _fetch():
            try:
                if kind == "liked":
                    songs = self.api.get_liked_songs(limit=200)
                elif kind == "playlist":
                    songs = self.api.get_playlist_tracks(browse_id)
                else:  # album
                    songs = self.api.get_album_tracks(browse_id)
                GLib.idle_add(self._show_tracks, songs)
            except Exception as exc:
                msg = str(exc)
                # ytmusicapi returns this when not signed in
                if "Sign in" in msg or "twoColumn" in msg or "singleColumn" in msg:
                    GLib.idle_add(self._show_not_signed_in)
                else:
                    GLib.idle_add(self._show_error, msg)

        threading.Thread(target=_fetch, daemon=True).start()

    def _show_not_signed_in(self):
        self._clear_right()
        page = Adw.StatusPage()
        page.set_icon_name("avatar-default-symbolic")
        page.set_title("Sign in to see your library")
        page.set_description(
            "Click the avatar icon in the top-right corner, then choose Sign in.")
        page.set_vexpand(True)
        self._right.append(page)

    def _show_spinner(self):
        self._clear_right()
        sp = Gtk.Spinner()
        sp.set_size_request(48, 48)
        sp.set_halign(Gtk.Align.CENTER)
        sp.set_valign(Gtk.Align.CENTER)
        sp.set_vexpand(True)
        sp.start()
        self._right.append(sp)

    def _show_tracks(self, songs: list[dict]):
        self._clear_right()
        if not songs:
            page = Adw.StatusPage()
            page.set_icon_name("emblem-music-symbolic")
            page.set_title("No tracks")
            page.set_vexpand(True)
            self._right.append(page)
            return
        sw = make_track_list(songs,
                             on_activate=self.on_play,
                             on_queue=self.on_queue,
                             on_download=self.on_download,
                             on_menu=self._on_menu)
        self._right.append(sw)

    def _show_error(self, msg: str):
        self._clear_right()
        page = Adw.StatusPage()
        page.set_icon_name("dialog-error-symbolic")
        page.set_title("Failed to load")
        page.set_description(msg)
        page.set_vexpand(True)
        self._right.append(page)

    def _clear_right(self):
        child = self._right.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._right.remove(child)
            child = nxt

    def _on_menu(self, song: dict, x: float, y: float):
        popover = Gtk.Popover()
        menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        btn = Gtk.Button(label="Add to queue")
        btn.add_css_class("flat")
        btn.connect("clicked", lambda *_: (self.on_queue(song), popover.popdown()))
        menu.append(btn)
        popover.set_child(menu)
        popover.set_parent(self)
        popover.popup()
