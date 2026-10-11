"""
Library tab — modern M3 redesign.
"""
from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QListWidget, QListWidgetItem, QSplitter, QLabel,
    QAbstractItemView, QFrame
)
from core.api import MusicAPI
from ui.thread_util import start_thread, retire_thread
import ui.theme as T


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


TRACK_COLUMNS = ["#", "Title", "Artist", "Album", "Duration"]


class LibraryTab(QWidget):
    play_requested     = pyqtSignal(dict)
    add_to_queue       = pyqtSignal(dict)
    download_requested = pyqtSignal(dict)
    play_all_requested = pyqtSignal(list)

    def __init__(self, api: MusicAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._tracks:    list[dict] = []
        self._thread:    QThread | None = None
        self._playlists: list[dict] = []
        self._albums:    list[dict] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SP_5, T.SP_5, T.SP_5, T.SP_4)
        layout.setSpacing(T.SP_4)

        # ── Các nút chọn mục ─────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(T.SP_2)

        self.btn_liked     = QPushButton("❤  Liked Songs")
        self.btn_playlists = QPushButton("📋  Playlists")
        self.btn_albums    = QPushButton("💿  New Releases")

        for btn in (self.btn_liked, self.btn_playlists, self.btn_albums):
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet(T.tonal_btn(0))
            btn_row.addWidget(btn)

        btn_row.addStretch()

        # Nút phát tất cả
        self.btn_play_all = QPushButton("▶  Play All")
        self.btn_play_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_all.setFixedHeight(36)
        self.btn_play_all.setStyleSheet(T.outline_btn(90))
        self.btn_play_all.clicked.connect(
            lambda: self.play_all_requested.emit(self._tracks) if self._tracks else None)
        btn_row.addWidget(self.btn_play_all)

        self.btn_liked.setVisible(False)
        self.btn_playlists.setChecked(True)
        layout.addLayout(btn_row)

        # ── Trạng thái ───────────────────────────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"""
            color: {T.ON_SURFACE_VARIANT};
            font-size: {T.TS_LABEL}px;
        """)
        layout.addWidget(self.status_lbl)

        # ── Nội dung chính: danh sách bên | bảng bài hát ─────────────────────
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle { background: transparent; width: 8px; }
        """)

        # Thanh bên
        sidebar = QFrame()
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {T.SURFACE};
                border-radius: {T.RADIUS_LG}px;
                border: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(T.SP_1, T.SP_2, T.SP_1, T.SP_2)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(T.LIST_QSS)
        self.list_widget.itemClicked.connect(self._on_list_item_clicked)
        sidebar_layout.addWidget(self.list_widget)
        self.splitter.addWidget(sidebar)

        # Thẻ bảng bài hát
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {T.SURFACE};
                border-radius: {T.RADIUS_LG}px;
                border: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        self.track_table = QTableWidget(0, len(TRACK_COLUMNS))
        self.track_table.setHorizontalHeaderLabels(TRACK_COLUMNS)
        # Cột số thứ tự — hẹp
        self.track_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed)
        self.track_table.setColumnWidth(0, 36)
        # Tiêu đề — tự giãn
        self.track_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3, 4):
            self.track_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents)
        self.track_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.track_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.track_table.setShowGrid(False)
        self.track_table.verticalHeader().setVisible(False)
        self.track_table.setAlternatingRowColors(True)
        self.track_table.setStyleSheet(T.TABLE_QSS + f"""
            QTableWidget {{
                alternate-background-color: {T.SURFACE_VAR};
                border-radius: {T.RADIUS_LG}px;
            }}
        """)
        self.track_table.doubleClicked.connect(self._on_double_click)
        self.track_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.track_table.customContextMenuRequested.connect(self._show_context_menu)

        card_layout.addWidget(self.track_table)
        self.splitter.addWidget(card)
        self.splitter.setSizes([220, 900])
        layout.addWidget(self.splitter, stretch=1)

        # Kết nối các nút chọn mục
        self.btn_liked.clicked.connect(lambda: self._load("liked"))
        self.btn_playlists.clicked.connect(lambda: self._load("playlists"))
        self.btn_albums.clicked.connect(lambda: self._load("albums"))

        # Tải danh sách phát khi khởi động
        self._load("playlists")

    # ── Phần công khai ───────────────────────────────────────────────────────

    def set_liked_visible(self, visible: bool):
        self.btn_liked.setVisible(visible)

    # ── Phần nội bộ ──────────────────────────────────────────────────────────

    def _uncheck_all(self):
        for b in (self.btn_liked, self.btn_playlists, self.btn_albums):
            b.setChecked(False)

    def _load(self, action: str):
        self._uncheck_all()
        btn_map = {"liked": self.btn_liked,
                   "playlists": self.btn_playlists,
                   "albums": self.btn_albums}
        if action in btn_map:
            btn_map[action].setChecked(True)

        self.status_lbl.setText("Loading…")
        self.list_widget.clear()
        self.track_table.setRowCount(0)
        self._tracks = []

        retire_thread(self._thread)
        self._worker = LibraryLoader(self.api, action)
        self._worker.liked_ready.connect(self._show_tracks)
        self._worker.playlists_ready.connect(self._show_playlists)
        self._worker.albums_ready.connect(self._show_albums)
        self._worker.tracks_ready.connect(self._show_tracks)
        self._worker.error.connect(lambda e: self.status_lbl.setText(f"Error: {e}"))
        self._thread = start_thread(self._worker)

    def _show_playlists(self, playlists: list[dict]):
        self._playlists = playlists
        self.list_widget.clear()
        for p in playlists:
            item = QListWidgetItem(p.get("title", "Playlist"))
            item.setData(Qt.ItemDataRole.UserRole, ("playlist", p.get("playlistId", "")))
            self.list_widget.addItem(item)
        self.status_lbl.setText(f"{len(playlists)} playlist{'s' if len(playlists) != 1 else ''}")
        retire_thread(self._thread)

    def _show_albums(self, albums: list[dict]):
        self._albums = albums
        self.list_widget.clear()
        for a in albums:
            item = QListWidgetItem(a.get("title", "Album"))
            item.setData(Qt.ItemDataRole.UserRole, ("album", a.get("browseId", "")))
            self.list_widget.addItem(item)
        self.status_lbl.setText(f"{len(albums)} album{'s' if len(albums) != 1 else ''}")
        retire_thread(self._thread)

    def _show_tracks(self, tracks: list[dict]):
        self._tracks = tracks
        self.track_table.setRowCount(0)
        for i, song in enumerate(tracks, 1):
            row = self.track_table.rowCount()
            self.track_table.insertRow(row)
            self.track_table.setRowHeight(row, 44)

            num_item = QTableWidgetItem(str(i))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setForeground(QTableWidgetItem().foreground())
            self.track_table.setItem(row, 0, num_item)
            self.track_table.setItem(row, 1, QTableWidgetItem(song.get("title", "")))
            self.track_table.setItem(row, 2, QTableWidgetItem(song.get("artist", "")))
            self.track_table.setItem(row, 3, QTableWidgetItem(song.get("album", "")))
            self.track_table.setItem(row, 4, QTableWidgetItem(_fmt_dur(song.get("duration"))))
        self.status_lbl.setText(f"{len(tracks)} track{'s' if len(tracks) != 1 else ''}")
        retire_thread(self._thread)

    def _on_list_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        kind, id_ = data
        self.status_lbl.setText("Loading tracks…")
        retire_thread(self._thread)
        action = "playlist_tracks" if kind == "playlist" else "album_tracks"
        self._worker = LibraryLoader(self.api, action, id_)
        self._worker.tracks_ready.connect(self._show_tracks)
        self._worker.error.connect(lambda e: self.status_lbl.setText(f"Error: {e}"))
        self._thread = start_thread(self._worker)

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
        menu.setStyleSheet(f"""
            QMenu {{
                background: {T.SURFACE_VAR};
                color: {T.ON_SURFACE};
                border: 1px solid {T.OUTLINE_VARIANT};
                border-radius: {T.RADIUS_MD}px;
                padding: {T.SP_1}px;
            }}
            QMenu::item {{
                padding: {T.SP_2}px {T.SP_4}px;
                border-radius: {T.RADIUS_SM}px;
            }}
            QMenu::item:selected {{
                background: {T.SURFACE_HIGH};
                color: {T.PRIMARY};
            }}
        """)
        menu.addAction("▶  Play now",          lambda: self.play_requested.emit(song))
        menu.addAction("➕  Add to queue",      lambda: self.add_to_queue.emit(song))
        menu.addAction("▶▶ Play all from here", lambda: self.play_all_requested.emit(self._tracks[row:]))
        menu.addAction("⬇  Download",          lambda: self.download_requested.emit(song))
        menu.exec(self.track_table.viewport().mapToGlobal(pos))