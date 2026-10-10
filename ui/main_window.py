"""
Main application window — no auth, boots straight into the player.
"""
from __future__ import annotations
from collections import deque

from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar
)

from auth.auth_manager import get_ytmusic_client
from core.api import MusicAPI
from core.player import Player
from core.downloader import Downloader
from ui.player_bar import PlayerBar
from ui.search_tab import SearchTab
from ui.library_tab import LibraryTab
from ui.download_tab import DownloadTab


# ── Stream URL fetcher (background thread) ────────────────────────────────────

class StreamFetcher(QObject):
    ready = pyqtSignal(str, dict)
    error = pyqtSignal(str)

    def __init__(self, api: MusicAPI, song: dict):
        super().__init__()
        self.api  = api
        self.song = song

    def run(self):
        try:
            url = self.api.get_stream_url(self.song["videoId"])
            if url:
                self.ready.emit(url, self.song)
            else:
                self.error.emit("Could not get stream URL.")
        except Exception as e:
            self.error.emit(str(e))


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 YTMusic Player")
        self.setMinimumSize(1000, 680)
        self._queue: deque[dict] = deque()
        self._current_song: dict | None = None
        self._fetch_thread: QThread | None = None

        self._apply_global_style()
        self.setStatusBar(QStatusBar())

        ytm = get_ytmusic_client()
        self.api        = MusicAPI(ytm)
        self.player     = Player(self)
        self.downloader = Downloader(self)

        self._build_ui()

    def _apply_global_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#0d0d1f; color:#e0e0ff; }
            QTabWidget::pane { border:none; background:#0d0d1f; }
            QTabBar::tab {
                background:#1a1a3a; color:#888aaa;
                padding:8px 20px; border:none; font-size:12px;
            }
            QTabBar::tab:selected { background:#2a2a5a; color:#e0e0ff; border-bottom:2px solid #7c6af7; }
            QTabBar::tab:hover    { background:#2a2a4a; }
            QStatusBar { color:#555577; font-size:11px; }
            QScrollBar:vertical { background:#12122a; width:8px; border:none; }
            QScrollBar::handle:vertical { background:#3a3a6a; border-radius:4px; min-height:20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
        """)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top bar ──
        top_bar = QWidget()
        top_bar.setFixedHeight(40)
        top_bar.setStyleSheet("background:#0d0d1f; border-bottom:1px solid #1a1a3a;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 16, 0)
        app_title = QLabel("🎵 YTMusic Player")
        app_title.setStyleSheet("color:#7c6af7; font-weight:700; font-size:14px;")
        top_layout.addWidget(app_title)
        top_layout.addStretch()
        layout.addWidget(top_bar)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.search_tab   = SearchTab(self.api)
        self.library_tab  = LibraryTab(self.api)
        self.download_tab = DownloadTab(self.downloader)
        self.tabs.addTab(self.search_tab,   "🔍  Search")
        self.tabs.addTab(self.library_tab,  "📚  Library")
        self.tabs.addTab(self.download_tab, "⬇  Downloads")
        layout.addWidget(self.tabs)

        # ── Player bar ──
        self.player_bar = PlayerBar(self.player)
        layout.addWidget(self.player_bar)

        # ── Signals ──
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
        if self._fetch_thread and self._fetch_thread.isRunning():
            self._fetch_thread.quit()
            self._fetch_thread.wait()

        self._fetch_thread = QThread()
        self._fetcher = StreamFetcher(self.api, song)
        self._fetcher.moveToThread(self._fetch_thread)
        self._fetch_thread.started.connect(self._fetcher.run)
        self._fetcher.ready.connect(self._on_stream_ready)
        self._fetcher.error.connect(self._on_stream_error)
        self._fetch_thread.start()

    @pyqtSlot(str, dict)
    def _on_stream_ready(self, url: str, song: dict):
        self.player.play_url(url)
        self.statusBar().showMessage(
            f"Now playing: {song.get('title', '')} — {song.get('artist', '')}")
        if self._fetch_thread:
            self._fetch_thread.quit()

    @pyqtSlot(str)
    def _on_stream_error(self, msg: str):
        self.statusBar().showMessage(f"Stream error: {msg}", 6000)
        if self._fetch_thread:
            self._fetch_thread.quit()
