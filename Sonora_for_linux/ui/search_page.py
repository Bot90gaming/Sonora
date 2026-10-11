"""
Search page — GTK4 / Adwaita.
"""
from __future__ import annotations
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from core.api import MusicAPI
from ui.widgets import make_track_list


FILTERS = ["songs", "albums", "artists", "playlists", "videos"]


class SearchPage(Gtk.Box):
    """
    Full-page search view with a text entry, filter dropdown, and results list.
    on_play(song)  — called when the user activates a result.
    on_queue(song) — called on right-click → Add to queue.
    """

    def __init__(self, api: MusicAPI,
                 on_play: callable,
                 on_queue: callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.api = api
        self.on_play  = on_play
        self.on_queue = on_queue
        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # ── Top bar (static — never removed) ──────────────────────────────────
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.set_margin_top(12)
        bar.set_margin_bottom(12)
        bar.set_margin_start(16)
        bar.set_margin_end(16)

        self._entry = Gtk.SearchEntry()
        self._entry.set_placeholder_text("Search YouTube Music…")
        self._entry.set_hexpand(True)
        self._entry.connect("activate",       self._do_search)
        self._entry.connect("search-changed", self._on_search_changed)

        self._filter = Gtk.DropDown.new_from_strings(FILTERS)
        self._filter.set_selected(0)

        btn_search = Gtk.Button(label="Search")
        btn_search.add_css_class("suggested-action")
        btn_search.connect("clicked", self._do_search)

        bar.append(self._entry)
        bar.append(self._filter)
        bar.append(btn_search)
        self.append(bar)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # ── Content area (dynamic — only this box is ever cleared) ────────────
        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._content.set_vexpand(True)
        self.append(self._content)

        self._show_placeholder()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clear_content(self):
        child = self._content.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._content.remove(child)
            child = nxt

    def _show_placeholder(self):
        self._clear_content()
        page = Adw.StatusPage()
        page.set_icon_name("system-search-symbolic")
        page.set_title("Search for music")
        page.set_description("Type something and press Enter")
        page.set_vexpand(True)
        self._content.append(page)

    def _show_spinner(self):
        self._clear_content()
        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.set_vexpand(True)
        spinner.start()
        self._content.append(spinner)

    def _show_results(self, songs: list[dict]):
        self._clear_content()
        if not songs:
            page = Adw.StatusPage()
            page.set_icon_name("edit-find-symbolic")
            page.set_title("No results")
            page.set_vexpand(True)
            self._content.append(page)
            return
        sw = make_track_list(songs,
                             on_activate=self.on_play,
                             on_menu=self._on_menu)
        self._content.append(sw)

    def _show_error(self, msg: str):
        self._clear_content()
        page = Adw.StatusPage()
        page.set_icon_name("dialog-error-symbolic")
        page.set_title("Search failed")
        page.set_description(msg)
        page.set_vexpand(True)
        self._content.append(page)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_search_changed(self, entry):
        if not entry.get_text().strip():
            self._show_placeholder()

    def _do_search(self, *_):
        query = self._entry.get_text().strip()
        if not query:
            return
        filter_ = FILTERS[self._filter.get_selected()]
        self._show_spinner()

        def _fetch():
            try:
                results = self.api.search(query, filter_=filter_, limit=30)
                GLib.idle_add(self._show_results, results)
            except Exception as exc:
                GLib.idle_add(self._show_error, str(exc))

        threading.Thread(target=_fetch, daemon=True).start()

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
