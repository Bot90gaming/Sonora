"""
Main application window — GTK4 / Adwaita.
"""
from __future__ import annotations
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

import yt_dlp

from auth.auth_manager import is_authenticated, get_ytmusic_client, logout
from core.api    import MusicAPI
from core.player import Player
from ui.player_bar    import PlayerBar
from ui.search_page   import SearchPage
from ui.library_page  import LibraryPage
from ui.download_page import DownloadPage
from ui.login_dialog  import LoginDialog


class MainWindow(Adw.ApplicationWindow):
    """
    Top-level window:
        ┌─ HeaderBar (ViewSwitcher) ─────────────────────────────┐
        │                                                         │
        │  ViewStack (Search | Library | Downloads)               │
        │                                                         │
        ├─ PlayerBar ─────────────────────────────────────────────┤
        └─────────────────────────────────────────────────────────┘
    Playback queue is a simple list[dict]; StreamFetcher resolves
    YouTube audio URLs in a daemon thread.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("YT Music")
        self.set_default_size(1100, 680)

        self._player = Player()
        self._queue:  list[dict] = []
        self._q_idx:  int        = 0
        self._api:    MusicAPI | None = None

        self._toast_overlay = Adw.ToastOverlay()
        self._build()
        self._init_api()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # Root toolbar-view holds header + content
        toolbar_view = Adw.ToolbarView()

        # Header bar
        header = Adw.HeaderBar()
        header.set_centering_policy(Adw.CenteringPolicy.STRICT)

        # Account menu button (right side)
        self._acct_btn = Gtk.MenuButton()
        self._acct_btn.set_icon_name("avatar-default-symbolic")
        self._acct_btn.set_tooltip_text("Account")
        self._acct_menu = self._build_acct_menu()
        self._acct_btn.set_popover(self._acct_menu)
        header.pack_end(self._acct_btn)

        toolbar_view.add_top_bar(header)

        # ViewStack
        self._stack = Adw.ViewStack()
        self._stack.set_vexpand(True)

        # ── Pages ─────────────────────────────────────────────────────────────
        self._dl_page = DownloadPage()

        # search + library get real api later via _init_api
        self._search_page = SearchPage(
            api=_stub_api(),
            on_play=self._play_song,
            on_queue=self._enqueue,
        )
        self._lib_page = LibraryPage(
            api=_stub_api(),
            on_play=self._play_song,
            on_queue=self._enqueue,
        )

        self._stack.add_titled_with_icon(
            self._search_page, "search", "Search",
            "system-search-symbolic")
        self._stack.add_titled_with_icon(
            self._lib_page, "library", "Library",
            "emblem-music-symbolic")
        self._stack.add_titled_with_icon(
            self._dl_page, "downloads", "Downloads",
            "folder-download-symbolic")

        # ViewSwitcher in the header
        switcher = Adw.ViewSwitcher()
        switcher.set_stack(self._stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Player bar (bottom)
        self._player_bar = PlayerBar(self._player)
        self._player_bar.on_next = self._next_track
        self._player_bar.on_prev = self._prev_track

        # Assemble
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.append(self._stack)
        content_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        content_box.append(self._player_bar)

        self._toast_overlay.set_child(content_box)
        toolbar_view.set_content(self._toast_overlay)
        self.set_content(toolbar_view)

    def _build_acct_menu(self) -> Gtk.Popover:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)

        self._acct_lbl = Gtk.Label(label="Not signed in")
        self._acct_lbl.add_css_class("caption")
        self._acct_lbl.add_css_class("dim-label")
        box.append(self._acct_lbl)

        sep = Gtk.Separator()
        box.append(sep)

        self._login_btn = Gtk.Button(label="Sign in…")
        self._login_btn.add_css_class("flat")
        self._login_btn.connect("clicked", self._show_login)
        box.append(self._login_btn)

        self._logout_btn = Gtk.Button(label="Sign out")
        self._logout_btn.add_css_class("flat")
        self._logout_btn.connect("clicked", self._do_logout)
        box.append(self._logout_btn)

        popover = Gtk.Popover()
        popover.set_child(box)
        return popover

    # ── API init ──────────────────────────────────────────────────────────────

    def _init_api(self):
        def _build():
            client = get_ytmusic_client()
            api    = MusicAPI(client)
            GLib.idle_add(self._apply_api, api)

        threading.Thread(target=_build, daemon=True).start()

    def _apply_api(self, api: MusicAPI):
        self._api = api
        self._search_page.api = api
        self._lib_page.api    = api
        if is_authenticated():
            self._acct_lbl.set_text("Signed in")
            self._login_btn.set_visible(False)
            self._logout_btn.set_visible(True)
        else:
            self._acct_lbl.set_text("Not signed in")
            self._login_btn.set_visible(True)
            self._logout_btn.set_visible(False)

    # ── Playback ──────────────────────────────────────────────────────────────

    def _play_song(self, song: dict):
        """Play a single song immediately (replaces queue)."""
        self._queue = [song]
        self._q_idx = 0
        self._start_playing(song)

    def _enqueue(self, song: dict):
        self._queue.append(song)
        self._toast("Added to queue")

    def _start_playing(self, song: dict):
        self._player_bar.load_song(song)
        vid = song.get("videoId", "")
        if not vid:
            self._toast("No video ID — cannot play")
            return
        threading.Thread(target=self._resolve_and_play,
                         args=(vid,), daemon=True).start()

    def _resolve_and_play(self, video_id: str):
        url = f"https://music.youtube.com/watch?v={video_id}"
        ydl_opts = {
            "format":       "bestaudio/best",
            "quiet":        True,
            "no_warnings":  True,
            "skip_download": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            },
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info["url"]
            GLib.idle_add(self._player.play_uri, stream_url)
        except Exception as exc:
            GLib.idle_add(self._toast, f"Stream error: {exc}")

    def _next_track(self):
        if self._q_idx + 1 < len(self._queue):
            self._q_idx += 1
            self._start_playing(self._queue[self._q_idx])

    def _prev_track(self):
        if self._q_idx > 0:
            self._q_idx -= 1
            self._start_playing(self._queue[self._q_idx])

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _show_login(self, *_):
        self._acct_menu.popdown()
        dlg = LoginDialog(parent=self, on_success=self._on_login_success)
        dlg.present()

    def _on_login_success(self):
        self._init_api()
        self._toast("Signed in successfully")

    def _do_logout(self, *_):
        logout()
        self._acct_menu.popdown()
        self._init_api()
        self._toast("Signed out")

    # ── Download helper ───────────────────────────────────────────────────────

    def download_song(self, song: dict):
        self._stack.set_visible_child_name("downloads")
        self._dl_page.download_song(song)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _toast(self, msg: str):
        toast = Adw.Toast.new(msg)
        toast.set_timeout(3)
        self._toast_overlay.add_toast(toast)


# ── Stub API (before real client is ready) ────────────────────────────────────

class _stub_api:
    def search(self, *a, **kw): return []
    def get_liked_songs(self, **kw): return []
    def get_library_playlists(self): return []
    def get_playlist_tracks(self, *a): return []
    def get_library_albums(self): return []
    def get_album_tracks(self, *a): return []
