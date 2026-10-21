"""
Main application window — GTK4 / Adwaita.
"""
from __future__ import annotations
import logging
import os
import tempfile
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

import yt_dlp

from auth.auth_manager import is_authenticated, get_ytmusic_client, logout
from core.api      import MusicAPI
from core.player   import Player
from core          import settings as cfg
from ui.player_bar    import PlayerBar
from ui.for_you_page  import ForYouPage
from ui.search_page   import SearchPage
from ui.library_page  import LibraryPage
from ui.download_page import DownloadPage
from ui.login_dialog  import LoginDialog
from ui.settings_page import SettingsPage
from ui.queue_dialog import QueueDialog
from ui.glass_theme   import apply as apply_glass

logger = logging.getLogger(__name__)


class MainWindow(Adw.ApplicationWindow):
    """
    Top-level window:
        ┌─ HeaderBar (ViewSwitcher) ─────────────────────────────┐
        │                                                         │
        │  ViewStack (For You | Search | Library | Downloads)      │
        │                                                         │
        ├─ PlayerBar ─────────────────────────────────────────────┤
        └─────────────────────────────────────────────────────────┘
    Playback queue is a list of song dictionaries; yt-dlp downloads current
    and station tracks on daemon threads.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("YT Music")
        self.set_default_size(1100, 680)

        self._player = Player()
        self._queue:  list[dict] = []
        self._q_idx:  int        = 0
        self._api:    MusicAPI | None = None
        self._station_request_id = 0
        self._station_cache_dir = os.path.join(
            tempfile.gettempdir(), "sonora_station_cache")
        self._audio_download_locks = {}
        self._audio_download_locks_guard = threading.Lock()
        self._queue_dialog: QueueDialog | None = None

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

        self._for_you_page = ForYouPage(
            api=_stub_api(),
            on_play=self._play_song,
            on_queue=self._enqueue,
            on_download=self.download_song,
            on_play_all=self._play_all,
        )
        self._search_page = SearchPage(
            api=_stub_api(),
            on_play=self._play_song,
            on_queue=self._enqueue,
            on_download=self.download_song,
            on_play_all=self._play_all,
        )
        self._lib_page = LibraryPage(
            api=_stub_api(),
            on_play=self._play_song,
            on_queue=self._enqueue,
            on_download=self.download_song,
            on_play_all=self._play_all,
        )

        self._stack.add_titled_with_icon(
            self._for_you_page, "for-you", "For You",
            "starred-symbolic")
        self._stack.add_titled_with_icon(
            self._search_page, "search", "Search",
            "system-search-symbolic")
        self._stack.add_titled_with_icon(
            self._lib_page, "library", "Library",
            "emblem-music-symbolic")
        self._stack.add_titled_with_icon(
            self._dl_page, "downloads", "Downloads",
            "folder-download-symbolic")

        self._settings_page = SettingsPage(
            on_theme_change=self._apply_theme,
            on_logout=self._on_settings_logout,
            on_login=self._show_login,
        )
        self._stack.add_titled_with_icon(
            self._settings_page, "settings", "Settings",
            "preferences-system-symbolic")

        # ViewSwitcher in the header
        switcher = Adw.ViewSwitcher()
        switcher.set_stack(self._stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Player bar (bottom)
        self._player_bar = PlayerBar(self._player)
        self._player_bar.on_next = self._next_track
        self._player_bar.on_prev = self._prev_track
        self._player_bar.on_like = self._on_like_song
        self._player_bar.on_station = self._start_station
        self._player_bar.on_queue = self._show_queue

        # Assemble
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.append(self._stack)
        content_box.append(self._player_bar)

        if hasattr(Adw, "BreakpointBin"):
            responsive = Adw.BreakpointBin()
            responsive.set_child(toolbar_view)
            responsive.set_size_request(320, 360)

            def add_breakpoint(
                max_width: int,
                compact: bool = False,
                library: bool = False,
                narrow: bool = False,
            ):
                breakpoint = Adw.Breakpoint.new(
                    Adw.BreakpointCondition.parse(
                        f"max-width: {max_width}sp"))
                breakpoint.add_setter(
                    switcher, "policy", Adw.ViewSwitcherPolicy.NARROW)

                if compact:
                    breakpoint.add_setter(
                        self._player_bar, "orientation",
                        Gtk.Orientation.VERTICAL)
                    breakpoint.add_setter(
                        self._player_bar._left, "width-request", -1)
                    breakpoint.add_setter(
                        self._player_bar._right, "width-request", -1)
                    breakpoint.add_setter(
                        self._player_bar._seek, "width-request", 180)

                if library:
                    breakpoint.add_setter(
                        self._lib_page, "orientation",
                        Gtk.Orientation.VERTICAL)
                    breakpoint.add_setter(
                        self._lib_page._sidebar_box, "width-request", -1)
                    breakpoint.add_setter(
                        self._lib_page._sidebar_box, "height-request", 160)
                    breakpoint.add_setter(
                        self._lib_page, "resize-start-child", True)

                if narrow:
                    breakpoint.add_setter(
                        self._search_page._bar, "orientation",
                        Gtk.Orientation.VERTICAL)
                    breakpoint.add_setter(
                        self._dl_page._bar, "orientation",
                        Gtk.Orientation.VERTICAL)
                    breakpoint.add_setter(
                        self._dl_page._dir_btn, "hexpand", True)
                    breakpoint.add_setter(
                        self._dl_page._toolbar_spacer, "visible", False)
                    breakpoint.add_setter(
                        self._player_bar._seek, "width-request", 120)
                    breakpoint.add_setter(
                        self._player_bar._vol, "width-request", 64)
                    breakpoint.add_setter(
                        self._settings_page._quality_dropdown,
                        "width-request", 150)

                responsive.add_breakpoint(breakpoint)

            add_breakpoint(850)
            add_breakpoint(700, compact=True)
            add_breakpoint(620, compact=True, library=True)
            add_breakpoint(
                560, compact=True, library=True, narrow=True)
            self._responsive = responsive
        else:
            responsive = None

        self._toast_overlay.set_child(content_box)
        toolbar_view.set_content(self._toast_overlay)
        self.set_content(
            responsive if responsive is not None else toolbar_view)

    def _build_acct_menu(self) -> Gtk.Popover:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.add_css_class("account-menu-content")

        self._acct_lbl = Gtk.Label(label="Not signed in")
        self._acct_lbl.add_css_class("caption")
        self._acct_lbl.add_css_class("dim-label")
        self._acct_lbl.add_css_class("account-menu-status")
        box.append(self._acct_lbl)

        sep = Gtk.Separator()
        box.append(sep)

        self._login_btn = Gtk.Button(label="Sign in…")
        self._login_btn.add_css_class("flat")
        self._login_btn.add_css_class("account-menu-action")
        self._login_btn.connect("clicked", self._show_login)
        box.append(self._login_btn)

        self._logout_btn = Gtk.Button(label="Sign out")
        self._logout_btn.add_css_class("flat")
        self._logout_btn.add_css_class("account-menu-action")
        self._logout_btn.connect("clicked", self._do_logout)
        box.append(self._logout_btn)

        popover = Gtk.Popover()
        popover.add_css_class("account-popover")
        popover.set_child(box)
        return popover

    # ── API init ──────────────────────────────────────────────────────────────

    def _init_api(self):
        def _build():
            try:
                client = get_ytmusic_client()
                api    = MusicAPI(client)
                GLib.idle_add(self._apply_api, api)
            except Exception:
                logger.exception("Could not initialize YouTube Music API")

        threading.Thread(target=_build, daemon=True).start()

    def _apply_api(self, api: MusicAPI):
        logger.info(
            "YouTube Music API initialized (saved_auth=%s)",
            is_authenticated(),
        )
        self._api = api
        self._for_you_page.set_api(api, authenticated=is_authenticated())
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
        self._update_queue_ui()
        self._start_playing(song)

    def _enqueue(self, song: dict):
        if not self._queue:
            self._q_idx = -1
        self._queue.append(song)
        self._update_queue_ui()
        self._toast("Added to queue")

    def _play_all(self, songs: list[dict]):
        """Load a full list into the queue and start from the first playable track."""
        playable = [s for s in songs if s.get("videoId")]
        if not playable:
            self._toast("No playable tracks in this playlist")
            return
        self._queue = playable
        self._q_idx = 0
        self._update_queue_ui()
        self._start_playing(playable[0])
        self._toast(f"Playing {len(playable)} tracks")

    def _start_playing(self, song: dict):
        self._station_request_id += 1
        self._player_bar.set_station_loading(False)
        self._player_bar.load_song(song)
        self._update_queue_ui()
        vid = song.get("videoId", "")
        if not vid:
            self._toast("No video ID — cannot play")
            return
        logger.info("Starting track playback (video_id=%s)", vid)
        # Show loading state in player bar
        GLib.idle_add(self._player_bar.set_loading, True)
        threading.Thread(target=self._download_and_play,
                         args=(vid,), daemon=True).start()

    def _download_and_play(self, video_id: str, attempt: int = 1):
        """
        Download the audio to a temp file then play from disk.
        This avoids mid-stream TLS drops that happen when GStreamer
        tries to play YouTube CDN URLs directly.
        """
        import time
        try:
            out_file = self._download_audio_file(
                video_id, self._station_cache_dir)

            logger.debug("Audio prepared for playback (video_id=%s)", video_id)
            from pathlib import Path
            file_uri = Path(out_file).resolve().as_uri()
            GLib.idle_add(self._player_bar.set_loading, False)
            GLib.idle_add(self._player.play_uri, file_uri)
            GLib.idle_add(self._cleanup_station_cache)

        except Exception as exc:
            msg = str(exc)
            if attempt < 3 and ("403" in msg or "429" in msg or "Forbidden" in msg
                                 or "connection" in msg.lower()):
                logger.warning("Playback attempt %d failed; retrying (video_id=%s): %s",
                               attempt, video_id, msg)
                time.sleep(1.5 * attempt)
                self._download_and_play(video_id, attempt + 1)
            else:
                logger.exception("Playback failed (video_id=%s)", video_id)
                GLib.idle_add(self._player_bar.set_loading, False)
                GLib.idle_add(self._toast, f"Playback error: {exc}")

    def _download_audio_file(self, video_id: str, directory: str) -> str:
        import os

        lock_key = (directory, video_id)
        with self._audio_download_locks_guard:
            download_lock = self._audio_download_locks.setdefault(
                lock_key, threading.Lock())
        with download_lock:
            out_file = self._find_audio_file(directory, video_id)
            if out_file:
                return out_file

            os.makedirs(directory, exist_ok=True)
            url = f"https://music.youtube.com/watch?v={video_id}"
            ydl_opts = {
                "format": (
                    "bestaudio[ext=webm]/bestaudio[ext=opus]/"
                    "bestaudio[ext=m4a]/bestaudio/best"),
                "quiet": True,
                "no_warnings": True,
                "nocache": True,
                "outtmpl": os.path.join(directory, f"sonora_{video_id}.%(ext)s"),
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    ),
                },
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
            out_file = self._find_audio_file(directory, video_id)
            if not out_file:
                raise RuntimeError(
                    "yt-dlp completed without producing an audio file")
            return out_file

    @staticmethod
    def _find_audio_file(directory: str, video_id: str) -> str | None:
        import glob
        import os

        candidates = glob.glob(os.path.join(directory, f"sonora_{video_id}.*"))
        return next((path for path in candidates
                     if os.path.isfile(path)
                     and not path.endswith((".part", ".ytdl"))), None)

    def _start_station(self):
        api = self._api
        if not api:
            self._toast("YouTube Music is still connecting")
            return
        if (not self._queue or self._q_idx < 0
                or self._q_idx >= len(self._queue)):
            self._toast("Play a song before starting a station")
            return

        source = self._queue[self._q_idx]
        video_id = source.get("videoId", "")
        if not video_id:
            self._toast("This track cannot start a station")
            return

        self._station_request_id += 1
        request_id = self._station_request_id
        self._player_bar.set_station_loading(True)

        def fetch_station():
            try:
                songs = api.get_station(video_id, limit=5)
                GLib.idle_add(
                    self._apply_station, request_id, video_id, source, songs)
            except Exception as exc:
                logger.exception("Could not create station (video_id=%s)", video_id)
                GLib.idle_add(
                    self._station_failed, request_id, str(exc))

        threading.Thread(target=fetch_station, daemon=True).start()

    def _apply_station(self, request_id, video_id, source, songs):
        if request_id != self._station_request_id:
            return
        if (not self._queue or self._q_idx < 0
                or self._q_idx >= len(self._queue)
                or self._queue[self._q_idx].get("videoId") != video_id):
            self._player_bar.set_station_loading(False)
            return
        self._player_bar.set_station_loading(False)
        if not songs:
            self._toast("No station tracks were found for this song")
            return

        self._queue = [source, *songs]
        self._q_idx = 0
        self._update_queue_ui()
        self._toast(f"Station added: {len(songs)} tracks downloading in background")
        threading.Thread(
            target=self._prefetch_station_tracks,
            args=(request_id, songs), daemon=True).start()

    def _station_failed(self, request_id, message):
        if request_id == self._station_request_id:
            self._player_bar.set_station_loading(False)
            self._toast(f"Could not start station: {message}")

    def _prefetch_station_tracks(self, request_id, songs):
        failures = 0
        for song in songs:
            if request_id != self._station_request_id:
                break
            video_id = song.get("videoId", "")
            if not video_id:
                continue
            try:
                self._download_audio_file(video_id, self._station_cache_dir)
            except Exception:
                failures += 1
                logger.exception(
                    "Could not pre-download station track (video_id=%s)",
                    video_id)
        if failures:
            GLib.idle_add(
                self._toast, f"Could not pre-download {failures} station tracks")
        GLib.idle_add(self._cleanup_station_cache)

    def _cleanup_station_cache(self):
        if not self._station_cache_dir:
            return
        import os

        pending_songs = (
            self._queue[self._q_idx:] if self._q_idx >= 0 else self._queue)
        queued_ids = {
            song.get("videoId")
            for song in pending_songs if song.get("videoId")
        }
        try:
            for name in os.listdir(self._station_cache_dir):
                if (name.startswith("sonora_")
                        and not any(name.startswith(f"sonora_{video_id}.")
                                    for video_id in queued_ids)):
                    os.remove(os.path.join(self._station_cache_dir, name))
        except OSError:
            logger.exception("Could not clean the station audio cache")

    def _show_queue(self):
        dialog = QueueDialog(
            self, self._queue, self._q_idx, self._move_queue_item,
            self._remove_queue_item, self._clear_upcoming)
        dialog.connect("close-request", self._on_queue_dialog_close)
        self._queue_dialog = dialog
        dialog.present()

    def _on_queue_dialog_close(self, *_):
        self._queue_dialog = None
        return False

    def _move_queue_item(self, index: int, offset: int):
        target = index + offset
        if (self._q_idx < index < len(self._queue)
                and self._q_idx < target < len(self._queue)):
            self._queue[index], self._queue[target] = (
                self._queue[target], self._queue[index])
            self._update_queue_ui()

    def _remove_queue_item(self, index: int):
        if self._q_idx < index < len(self._queue):
            self._queue.pop(index)
            self._update_queue_ui()

    def _clear_upcoming(self):
        self._queue = self._queue[:self._q_idx + 1]
        self._update_queue_ui()

    def _update_queue_ui(self):
        self._player_bar.set_queue_count(len(self._queue))
        if self._queue_dialog:
            self._queue_dialog.refresh(self._queue, self._q_idx)

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

    # ── Like ──────────────────────────────────────────────────────────────────

    def _on_like_song(self, video_id: str, liked: bool):
        if not self._api:
            self._toast("Sign in to like songs")
            return

        def _do():
            try:
                if liked:
                    self._api.like_song(video_id)
                    GLib.idle_add(self._toast, "Added to Liked Songs ♥")
                else:
                    self._api.unlike_song(video_id)
                    GLib.idle_add(self._toast, "Removed from Liked Songs")
            except Exception as exc:
                logger.exception("Could not update liked-song status")
                GLib.idle_add(self._toast, f"Could not update like: {exc}")

        threading.Thread(target=_do, daemon=True).start()

    # ── Download helper ───────────────────────────────────────────────────────

    def download_song(self, song: dict):
        self._stack.set_visible_child_name("downloads")
        self._dl_page.download_song(song)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _apply_theme(self):
        apply_glass(
            theme=cfg.get("theme"),
            glass=cfg.get("glass_effect"),
            accent=cfg.get("accent"),
        )

    def _on_settings_logout(self):
        self._init_api()
        self._toast("Signed out")

    def _toast(self, msg: str):
        toast = Adw.Toast.new(msg)
        toast.set_timeout(3)
        self._toast_overlay.add_toast(toast)


# ── Stub API (before real client is ready) ────────────────────────────────────

class _stub_api:
    def get_home(self, **kw): return []
    def search(self, *a, **kw): return []
    def get_liked_songs(self, **kw): return []
    def get_library_playlists(self): return []
    def get_playlist_tracks(self, *a): return []
    def get_library_albums(self): return []
    def get_album_tracks(self, *a): return []
