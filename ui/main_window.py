"""
Main application window — modern M3 redesign.
"""
from __future__ import annotations
from collections import deque
import os
import tempfile

import yt_dlp
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar, QPushButton, QFrame
)

from auth.auth_manager import get_ytmusic_client, is_authenticated, logout
from core.api import MusicAPI
from core.player import Player
from core.downloader import Downloader
from ui.player_bar import PlayerBar
from ui.search_tab import SearchTab
from ui.library_tab import LibraryTab
from ui.download_tab import DownloadTab
from ui.thread_util import start_thread, retire_thread
import ui.theme as T


# ── Stream fetcher ────────────────────────────────────────────────────────────

class StreamFetcher(QObject):
    ready    = pyqtSignal(str, dict)
    progress = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, video_id: str, song: dict):
        super().__init__()
        self.video_id = video_id
        self.song     = song
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        tmp = tempfile.mktemp(suffix=".opus")
        ydl_opts = {
            "format": "bestaudio[ext=opus]/bestaudio[ext=webm]/bestaudio/best",
            "outtmpl": tmp,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "postprocessors": [],
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            "extractor_retries": 3,
            "retries": 5,
            "fragment_retries": 5,
        }

        def _hook(d):
            if self._cancelled:
                raise yt_dlp.utils.DownloadCancelled()
            if d.get("status") == "downloading":
                pct = d.get("_percent_str", "").strip()
                self.progress.emit(f"Buffering {self.song.get('title', '')}… {pct}")

        ydl_opts["progress_hooks"] = [_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={self.video_id}", download=True)
                ext  = info.get("ext", "opus")
                real = tmp if os.path.exists(tmp) else f"{tmp}.{ext}"
                if not os.path.exists(real):
                    base = os.path.splitext(tmp)[0]
                    for candidate in (f"{base}.opus", f"{base}.webm",
                                      f"{base}.m4a",  f"{base}.mp4"):
                        if os.path.exists(candidate):
                            real = candidate
                            break
            if self._cancelled:
                _safe_remove(real)
                return
            if os.path.exists(real):
                self.ready.emit(real, self.song)
            else:
                self.error.emit("Temp audio file not found after download.")
        except yt_dlp.utils.DownloadCancelled:
            _safe_remove(tmp)
        except Exception as e:
            _safe_remove(tmp)
            self.error.emit(str(e))


def _safe_remove(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sonora")
        self.setMinimumSize(1100, 720)
        self._queue: deque[dict] = deque()
        self._current_song: dict | None = None
        self._fetch_thread: QThread | None = None
        self._fetcher: StreamFetcher | None = None
        self._temp_files: list[str] = []

        self._apply_global_style()
        self.setStatusBar(QStatusBar())

        self.player     = Player(self)
        self.downloader = Downloader(self)

        self._init_client()
        self._build_ui()
        self._maybe_show_login()

    def _init_client(self):
        ytm      = get_ytmusic_client()
        self.api = MusicAPI(ytm)

    def _maybe_show_login(self):
        if not is_authenticated():
            from ui.login_dialog import LoginDialog
            dlg = LoginDialog(self)
            dlg.logged_in.connect(self._on_logged_in)
            dlg.exec()
        self._update_auth_ui()

    def _on_logged_in(self):
        self._init_client()
        self.search_tab.api  = self.api
        self.library_tab.api = self.api
        self._update_auth_ui()
        self.statusBar().showMessage("Signed in to YouTube Music ✓", 4000)

    def _update_auth_ui(self):
        if is_authenticated():
            self.btn_auth.setText("Sign out")
            self.btn_auth.setToolTip("Sign out of YouTube Music")
        else:
            self.btn_auth.setText("Sign in")
            self.btn_auth.setToolTip("Sign in to YouTube Music")
        self.library_tab.set_liked_visible(is_authenticated())

    def _apply_global_style(self):
        self.setStyleSheet(T.GLOBAL_QSS)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(56)
        top_bar.setStyleSheet(f"""
            QWidget {{
                background: {T.SURFACE};
                border-bottom: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(T.SP_4, 0, T.SP_4, 0)
        top_layout.setSpacing(T.SP_3)

        # App logo + title
        logo = QLabel("♫")
        logo.setStyleSheet(f"""
            color: {T.PRIMARY};
            font-size: {T.TS_DISPLAY}px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        top_layout.addWidget(logo)
        
        title = QLabel("Sonora")
        title.setStyleSheet(f"""
            color: {T.ON_SURFACE};
            font-size: {T.TS_TITLE}px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        top_layout.addWidget(title)
        top_layout.addStretch()

        self.btn_auth = QPushButton("Sign in")
        self.btn_auth.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_auth.setStyleSheet(T.tonal_btn(80))
        self.btn_auth.clicked.connect(self._toggle_auth)
        top_layout.addWidget(self.btn_auth)
        layout.addWidget(top_bar)

        # ── Tab widget ────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {T.BG};
            }}
            QTabBar {{
                background: {T.SURFACE};
            }}
            QTabBar::tab {{
                background: transparent;
                color: {T.ON_SURFACE_VARIANT};
                padding: {T.SP_3}px {T.SP_5}px;
                margin-right: {T.SP_1}px;
                border: none;
                font-size: {T.TS_BODY}px;
                font-weight: 500;
                min-width: 90px;
            }}
            QTabBar::tab:selected {{
                color: {T.PRIMARY};
                border-bottom: 3px solid {T.PRIMARY};
                background: transparent;
            }}
            QTabBar::tab:hover:!selected {{
                color: {T.ON_SURFACE};
                background: {T.HOVER_OVERLAY};
            }}
            QTabBar::tab:first {{
                margin-left: {T.SP_3}px;
            }}
        """)

        self.search_tab   = SearchTab(self.api)
        self.library_tab  = LibraryTab(self.api)
        self.download_tab = DownloadTab(self.downloader)

        self.tabs.addTab(self.search_tab,   "🔍  Search")
        self.tabs.addTab(self.library_tab,  "📚  Library")
        self.tabs.addTab(self.download_tab, "⬇  Downloads")
        layout.addWidget(self.tabs, stretch=1)

        # ── Player bar ────────────────────────────────────────────────────────
        self.player_bar = PlayerBar(self.player)
        layout.addWidget(self.player_bar)

        # ── Signal wiring ─────────────────────────────────────────────────────
        self.search_tab.play_requested.connect(self._play_song)
        self.search_tab.add_to_queue.connect(self._enqueue)
        self.search_tab.download_requested.connect(self.download_tab.start_download)

        self.library_tab.play_requested.connect(self._play_song)
        self.library_tab.add_to_queue.connect(self._enqueue)
        self.library_tab.download_requested.connect(self.download_tab.start_download)
        self.library_tab.play_all_requested.connect(self._play_all)

        self.player_bar.request_next.connect(self._play_next)
        self.player_bar.request_prev.connect(self._play_prev)

        self.player.error_occurred.connect(
            lambda msg: self.statusBar().showMessage(f"Player error: {msg}", 5000))

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _toggle_auth(self):
        if is_authenticated():
            logout()
            self._init_client()
            self.search_tab.api  = self.api
            self.library_tab.api = self.api
            self._update_auth_ui()
            self.statusBar().showMessage("Signed out.", 3000)
        else:
            from ui.login_dialog import LoginDialog
            dlg = LoginDialog(self)
            dlg.logged_in.connect(self._on_logged_in)
            dlg.exec()

    # ── Queue / playback ──────────────────────────────────────────────────────

    def _play_song(self, song: dict):
        if not song.get("videoId"):
            self.statusBar().showMessage("No video ID — cannot stream.", 4000)
            return
        self._current_song = song
        self.player_bar.load_song(song)
        self.player.stop()
        self.statusBar().showMessage(f"Loading: {song.get('title', '')}…")
        self._fetch_stream(song)

    def _enqueue(self, song: dict):
        self._queue.append(song)
        self.statusBar().showMessage(
            f"Added to queue: {song.get('title', '')}  [{len(self._queue)} in queue]", 3000)

    def _play_all(self, songs: list[dict]):
        self._queue.clear()
        if not songs:
            return
        self._queue.extend(songs[1:])
        self._play_song(songs[0])

    def _play_next(self):
        if self._queue:
            self._play_song(self._queue.popleft())

    def _play_prev(self):
        self.player.seek(0)

    def _fetch_stream(self, song: dict):
        if self._fetcher is not None:
            self._fetcher.cancel()
            for sig in (self._fetcher.ready, self._fetcher.error, self._fetcher.progress):
                try:
                    sig.disconnect()
                except Exception:
                    pass
            self._fetcher = None

        retire_thread(self._fetch_thread)

        fetcher = StreamFetcher(song.get("videoId", ""), song)
        fetcher.progress.connect(lambda msg: self.statusBar().showMessage(msg))
        fetcher.ready.connect(self._on_stream_ready)
        fetcher.error.connect(self._on_stream_error)

        self._fetcher      = fetcher
        self._fetch_thread = start_thread(fetcher)

    @pyqtSlot(str, dict)
    def _on_stream_ready(self, path: str, song: dict):
        self._cleanup_temp_files()
        self._temp_files.append(path)
        self.player.play_url(f"file://{path}" if not path.startswith("file://") else path)
        self.statusBar().showMessage(
            f"Now playing: {song.get('title', '')} — {song.get('artist', '')}")

    @pyqtSlot(str)
    def _on_stream_error(self, msg: str):
        self.statusBar().showMessage(f"Stream error: {msg}", 6000)

    def _cleanup_temp_files(self):
        remaining = []
        for path in self._temp_files:
            _safe_remove(path)
            if os.path.exists(path):
                remaining.append(path)
        self._temp_files = remaining

    def closeEvent(self, event):
        self.player.stop()
        if self._fetcher is not None:
            self._fetcher.cancel()
        retire_thread(self._fetch_thread)
        self._cleanup_temp_files()
        super().closeEvent(event)