"""
Search page — GTK4 / Adwaita.
"""
from __future__ import annotations
import logging
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from core.api import MusicAPI
from ui.choice_dropdown import ChoiceDropDown
from ui.widgets import make_track_list
from ui.easter_egg import maybe_trigger


FILTERS = ["songs", "albums", "artists", "playlists", "videos"]

logger = logging.getLogger(__name__)


class SearchPage(Gtk.Box):
    """
    Full-page search view with a text entry, filter dropdown, and results list.
    on_play(song)  — called when the user activates a result.
    on_queue(song) — called by the inline Add to queue button.
    """

    def __init__(self, api: MusicAPI,
                 on_play: callable,
                 on_queue: callable,
                 on_download: callable | None = None,
                 on_play_all: callable | None = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.api         = api
        self.on_play     = on_play
        self.on_queue    = on_queue
        self.on_download = on_download
        self.on_play_all = on_play_all
        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # ── Top bar (static — never removed) ──────────────────────────────────
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._bar = bar
        bar.set_margin_top(12)
        bar.set_margin_bottom(12)
        bar.set_margin_start(16)
        bar.set_margin_end(16)

        self._entry = Gtk.SearchEntry()
        self._entry.set_placeholder_text("Search YouTube Music…")
        self._entry.set_hexpand(True)
        self._entry.connect("activate",       self._do_search)
        self._entry.connect("search-changed", self._on_search_changed)

        self._filter = ChoiceDropDown([filter_.capitalize() for filter_ in FILTERS])

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

    def _show_results(self, results: list[dict]):
        self._clear_content()
        if not results:
            page = Adw.StatusPage()
            page.set_icon_name("edit-find-symbolic")
            page.set_title("No results")
            page.set_vexpand(True)
            self._content.append(page)
            return

        # Detect playlist / album results (have playlistId but no videoId)
        first = results[0]
        is_playlist_results = (not first.get("videoId")
                               and bool(first.get("playlistId") or first.get("browseId")))

        if is_playlist_results:
            self._show_playlist_results(results)
        else:
            sw = make_track_list(results,
                                 on_activate=self.on_play,
                                 on_queue=self.on_queue,
                                 on_download=self.on_download)
            self._content.append(sw)

    def _show_playlist_results(self, playlists: list[dict]):
        """Render a list of playlist/album cards. Clicking one fetches + plays its tracks."""
        lb = Gtk.ListBox()
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        lb.add_css_class("boxed-list")

        for pl in playlists:
            row = Adw.ActionRow()
            row.set_title(pl.get("title", "Unknown"))
            subtitle = pl.get("artist", "") or pl.get("count", "")
            if subtitle:
                row.set_subtitle(subtitle)
            row.set_icon_name("music-queue-symbolic")
            row.set_activatable(True)
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))

            pl_id = pl.get("playlistId") or pl.get("browseId", "")
            pl_name = pl.get("title", "Playlist")
            row.connect("activated", self._on_playlist_activated, pl_id, pl_name)
            lb.append(row)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        sw.set_child(lb)
        self._content.append(sw)

    def _on_playlist_activated(self, row, playlist_id: str, name: str):
        if not playlist_id:
            return
        self._show_loading_playlist(name)

        def _fetch():
            try:
                tracks = self.api.get_playlist_tracks(playlist_id)
                GLib.idle_add(self._on_playlist_loaded, tracks, name)
            except Exception as exc:
                logger.exception("Could not load playlist tracks")
                GLib.idle_add(self._show_error, str(exc))

        threading.Thread(target=_fetch, daemon=True).start()

    def _show_loading_playlist(self, name: str):
        self._clear_content()
        page = Adw.StatusPage()
        page.set_icon_name("emblem-music-symbolic")
        page.set_title(f'Loading “{name}”…')
        page.set_vexpand(True)
        self._content.append(page)

    def _on_playlist_loaded(self, tracks: list[dict], name: str):
        self._clear_content()
        if not tracks:
            page = Adw.StatusPage()
            page.set_icon_name("emblem-music-symbolic")
            page.set_title("No tracks in this playlist")
            page.set_vexpand(True)
            self._content.append(page)
            return

        # Header with back button + Play All
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_top(10)
        header.set_margin_bottom(8)
        header.set_margin_start(12)
        header.set_margin_end(16)

        back_btn = Gtk.Button()
        back_btn.set_icon_name("go-previous-symbolic")
        back_btn.add_css_class("flat")
        back_btn.add_css_class("circular")
        back_btn.set_valign(Gtk.Align.CENTER)
        back_btn.set_tooltip_text("Back to search results")
        back_btn.connect("clicked", lambda *_: self._do_search())
        header.append(back_btn)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_hexpand(True)
        lbl = Gtk.Label(label=name)
        lbl.add_css_class("title-2")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_ellipsize(3)
        title_box.append(lbl)
        count_lbl = Gtk.Label(label=f"{len(tracks)} track{'s' if len(tracks) != 1 else ''}")
        count_lbl.add_css_class("caption")
        count_lbl.add_css_class("dim-label")
        count_lbl.set_halign(Gtk.Align.START)
        title_box.append(count_lbl)
        header.append(title_box)

        if self.on_play_all:
            play_btn = Gtk.Button(label="▶  Play All")
            play_btn.add_css_class("suggested-action")
            play_btn.add_css_class("pill")
            play_btn.set_valign(Gtk.Align.CENTER)
            playable = [t for t in tracks if t.get("videoId")]
            play_btn.connect("clicked", lambda *_: self.on_play_all(playable))
            header.append(play_btn)

        self._content.append(header)
        self._content.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        sw = make_track_list(tracks,
                             on_activate=self.on_play,
                             on_queue=self.on_queue,
                             on_download=self.on_download)
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
                GLib.idle_add(maybe_trigger, query, self.get_root())
            except Exception as exc:
                logger.exception("Search failed (filter=%s)", filter_)
                GLib.idle_add(self._show_error, str(exc))

        threading.Thread(target=_fetch, daemon=True).start()
