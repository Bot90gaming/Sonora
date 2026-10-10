"""
Library tab: Liked Songs, Playlists, Albums. 
"""
from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QListWidget, QListWidgetItem, QSplitter, QLabel,
    QAbstractItemView
)
from core.api import MusicAPI


def _fmt_dur(s) -> str:
    if not s:
        return "--"
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


class LibraryLoader(QObject):
    liked_ready     = pyqtSignal(list)
    playlists_ready = pyqtSignal(list)
    albums_ready    = pyqtSignal(list)
    tracks_ready    = pyqtSignal(list)
    error           = pyqtSignal(str)

    def __init__(self, api: MusicAPI, action: str, arg: str = ""):
        super().__init__()
        self.api    = api
        self.action = action
        self.arg    = arg

    def run(self):
        try:
            if self.action == "liked":
                self.liked_ready.emit(self.api.get_liked_songs())
            elif self.action == "playlists":
                self.playlists_ready.emit(self.api.get_library_playlists())
            elif self.action == "albums":
                self.albums_ready.emit(self.api.get_library_albums())
            elif self.action == "playlist_tracks":
                self.tracks_ready.emit(self.api.get_playlist_tracks(self.arg))
            elif self.action == "album_tracks":
                self.tracks_ready.emit(self.api.get_album_tracks(self.arg))
        except Exception as e:
            self.error.emit(str(e))


TRACK_COLUMNS = ["Title", "Artist", "Album", "Duration"]

_BTN_STYLE = """
    QPushButton {
        background: #2a2a4a; color: #e0e0ff;
        border: 1px solid #3a3a6a; border-radius: 6px;
        padding: 6px 14px; font-size: 12px;
    }
    QPushButton:hover  { background: #3a3a6a; }
    QPushButton:checked { background: #7c6af7; border-color: #7c6af7; }
"""

_TABLE_STYLE = """
    QTableWidget {
        background: #12122a; color: #e0e0ff;
        gridline-color: #2a2a4a; border: none; font-size: 12px;
    }
    QHeaderView::section {
        background: #1a1a3a; color: #888aaa;
        padding: 6px; border: none; font-size: 11px;
    }
    QTableWidget::item:selected { background: #2a2a5a; }
    QTableWidget::item:hover    { background: #1e1e3e; }
"""

_LIST_STYLE = """
    QListWidget {
        background: #12122a; color: #e0e0ff;
        border: none; font-size: 12px;
    }
    QListWidget::item { padding: 8px 10px; }
    QListWidget::item:selected { background: #2a2a5a; }
    QListWidget::item:hover    { background: #1e1e3e; }
"""


class LibraryTab(QWidget):
    play_requested     = pyqtSignal(dict)
    add_to_queue       = pyqtSignal(dict)
    download_requested = pyqtSignal(dict)
    play_all_requested = pyqtSignal(list)   # whole track list

    def __init__(self, api: MusicAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._tracks: list[dict] = []
        self._thread: QThread | None = None
        self._playlists: list[dict] = []
        self._albums:    list[dict] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── Section buttons ──
        btn_row = QHBoxLayout()
        self.btn_playlists = QPushButton("📋  Featured Playlists")
        self.btn_albums    = QPushButton("💿  New Releases")
        for btn in (self.btn_playlists, self.btn_albums):
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(_BTN_STYLE)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        self.btn_playlists.setChecked(True)
        layout.addLayout(btn_row)

        # ── Status ──
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color:#888aaa; font-size:11px;")
        layout.addWidget(self.status_lbl)

        # ── Splitter: list (playlists/albums) | tracks ──
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(_LIST_STYLE)
        self.list_widget.setMaximumWidth(220)
        self.list_widget.itemClicked.connect(self._on_list_item_clicked)
        self.splitter.addWidget(self.list_widget)

        self.track_table = QTableWidget(0, len(TRACK_COLUMNS))
        self.track_table.setHorizontalHeaderLabels(TRACK_COLUMNS)
        self.track_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3):
            self.track_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents)
        self.track_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.track_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.track_table.setStyleSheet(_TABLE_STYLE)
        self.track_table.doubleClicked.connect(self._on_double_click)
        self.track_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.track_table.customContextMenuRequested.connect(self._show_context_menu)
        self.splitter.addWidget(self.track_table)
        self.splitter.setSizes([200, 800])
        layout.addWidget(self.splitter)

        # Wire section buttons
        self.btn_playlists.clicked.connect(lambda: self._load("playlists"))
        self.btn_albums.clicked.connect(lambda: self._load("albums"))

        # Load playlists by default
        self._load("playlists")

    def _uncheck_all(self):
        for b in (self.btn_playlists, self.btn_albums):
            b.setChecked(False)

    def _load(self, action: str):
        self._uncheck_all()
        if   action == "playlists": self.btn_playlists.setChecked(True)
        elif action == "albums":    self.btn_albums.setChecked(True)

        self.status_lbl.setText("Loading…")
        self.list_widget.clear()
        self.track_table.setRowCount(0)

        if self._thread and self._thread.isRunning():
            self._thread.quit()

        self._thread = QThread()
        self._worker = LibraryLoader(self.api, action)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.liked_ready.connect(self._show_tracks)
        self._worker.playlists_ready.connect(self._show_playlists)
        self._worker.albums_ready.connect(self._show_albums)
        self._worker.tracks_ready.connect(self._show_tracks)
        self._worker.error.connect(lambda e: self.status_lbl.setText(f"Error: {e}"))
        self._thread.start()

    def _show_playlists(self, playlists: list[dict]):
        self._playlists = playlists
        self.list_widget.clear()
        for p in playlists:
            item = QListWidgetItem(p.get("title", "Playlist"))
            item.setData(Qt.ItemDataRole.UserRole, ("playlist", p.get("playlistId", "")))
            self.list_widget.addItem(item)
        self.status_lbl.setText(f"{len(playlists)} playlists")
        if self._thread: self._thread.quit()

    def _show_albums(self, albums: list[dict]):
        self._albums = albums
        self.list_widget.clear()
        for a in albums:
            item = QListWidgetItem(a.get("title", "Album"))
            item.setData(Qt.ItemDataRole.UserRole, ("album", a.get("browseId", "")))
            self.list_widget.addItem(item)
        self.status_lbl.setText(f"{len(albums)} albums")
        if self._thread: self._thread.quit()

    def _show_tracks(self, tracks: list[dict]):
        self._tracks = tracks
        self.track_table.setRowCount(0)
        for song in tracks:
            row = self.track_table.rowCount()
            self.track_table.insertRow(row)
            self.track_table.setItem(row, 0, QTableWidgetItem(song.get("title", "")))
            self.track_table.setItem(row, 1, QTableWidgetItem(song.get("artist", "")))
            self.track_table.setItem(row, 2, QTableWidgetItem(song.get("album", "")))
            self.track_table.setItem(row, 3, QTableWidgetItem(_fmt_dur(song.get("duration"))))
        self.status_lbl.setText(f"{len(tracks)} tracks")
        if self._thread: self._thread.quit()

    def _on_list_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        kind, id_ = data
        self.status_lbl.setText("Loading tracks…")

        if self._thread and self._thread.isRunning():
            self._thread.quit()

        action = "playlist_tracks" if kind == "playlist" else "album_tracks"
        self._thread = QThread()
        self._worker = LibraryLoader(self.api, action, id_)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.tracks_ready.connect(self._show_tracks)
        self._worker.error.connect(lambda e: self.status_lbl.setText(f"Error: {e}"))
        self._thread.start()

    def _on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self._tracks):
            self.play_requested.emit(self._tracks[row])

    def _show_context_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        row = self.track_table.rowAt(pos.y())
        if row < 0 or row >= len(self._tracks):
            return
        song = self._tracks[row]
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1e1e3a; color:#e0e0ff; border:1px solid #3a3a6a; }
            QMenu::item:selected { background:#3a3a6a; }
        """)
        menu.addAction("▶  Play now",          lambda: self.play_requested.emit(song))
        menu.addAction("➕  Add to queue",      lambda: self.add_to_queue.emit(song))
        menu.addAction("▶▶ Play all from here", lambda: self.play_all_requested.emit(self._tracks[row:]))
        menu.addAction("⬇  Download",          lambda: self.download_requested.emit(song))
        menu.exec(self.track_table.viewport().mapToGlobal(pos))
