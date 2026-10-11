"""
Search tab: search bar + filter buttons + results table.
"""
from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QComboBox, QAbstractItemView
)
from core.api import MusicAPI


COLUMNS = ["Title", "Artist", "Album", "Duration"]


def _fmt_dur(s) -> str:
    if not s:
        return "--"
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


class SearchWorker(QObject):
    results_ready = pyqtSignal(list)
    error         = pyqtSignal(str)

    def __init__(self, api: MusicAPI, query: str, filter_: str):
        super().__init__()
        self.api     = api
        self.query   = query
        self.filter_ = filter_

    def run(self):
        try:
            if self.filter_ == "songs":
                data = self.api.search_songs(self.query)
            elif self.filter_ == "albums":
                data = self.api.search_albums(self.query)
            elif self.filter_ == "artists":
                data = self.api.search_artists(self.query)
            else:
                data = self.api.search_playlists(self.query)
            self.results_ready.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class SearchTab(QWidget):
    play_requested     = pyqtSignal(dict)
    add_to_queue       = pyqtSignal(dict)
    download_requested = pyqtSignal(dict)

    def __init__(self, api: MusicAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._results: list[dict] = []
        self._thread: QThread | None = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── Thanh tìm kiếm ──
        bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs, artists, albums…")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e3a; color: #e0e0ff;
                border: 1px solid #3a3a6a; border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #7c6af7; }
        """)
        self.search_input.returnPressed.connect(self._do_search)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["songs", "albums", "artists", "playlists"])
        self.filter_box.setStyleSheet("""
            QComboBox {
                background: #1e1e3a; color: #e0e0ff;
                border: 1px solid #3a3a6a; border-radius: 8px;
                padding: 6px 10px; font-size: 12px; min-width: 90px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1e1e3a; color: #e0e0ff;
                selection-background-color: #3a3a6a;
            }
        """)

        self.btn_search = QPushButton("Search")
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background: #7c6af7; color: white; border: none;
                border-radius: 8px; padding: 8px 18px; font-size: 13px;
            }
            QPushButton:hover { background: #9480ff; }
        """)
        self.btn_search.clicked.connect(self._do_search)

        bar.addWidget(self.search_input)
        bar.addWidget(self.filter_box)
        bar.addWidget(self.btn_search)
        layout.addLayout(bar)

        # ── Nhãn trạng thái ──
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color:#888aaa; font-size:11px;")
        layout.addWidget(self.status_lbl)

        # ── Bảng kết quả ──
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
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
        """)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

    def _do_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.status_lbl.setText("Searching…")
        self.btn_search.setEnabled(False)

        if self._thread and self._thread.isRunning():
            self._thread.quit()

        self._thread = QThread()
        self._worker = SearchWorker(self.api, query, self.filter_box.currentText())
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.results_ready.connect(self._populate)
        self._worker.error.connect(self._on_error)
        self._thread.start()

    def _populate(self, results: list[dict]):
        self._results = results
        self.table.setRowCount(0)
        for song in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(song.get("title", "")))
            self.table.setItem(row, 1, QTableWidgetItem(song.get("artist", song.get("name", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(song.get("album", "")))
            self.table.setItem(row, 3, QTableWidgetItem(_fmt_dur(song.get("duration"))))
        self.status_lbl.setText(f"{len(results)} results")
        self.btn_search.setEnabled(True)
        if self._thread:
            self._thread.quit()

    def _on_error(self, msg: str):
        self.status_lbl.setText(f"Error: {msg}")
        self.btn_search.setEnabled(True)
        if self._thread:
            self._thread.quit()

    def _on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self._results):
            self.play_requested.emit(self._results[row])

    def _show_context_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        row = self.table.rowAt(pos.y())
        if row < 0 or row >= len(self._results):
            return
        song = self._results[row]
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1e1e3a; color:#e0e0ff; border:1px solid #3a3a6a; }
            QMenu::item:selected { background:#3a3a6a; }
        """)
        menu.addAction("▶  Play now",          lambda: self.play_requested.emit(song))
        menu.addAction("➕  Add to queue",      lambda: self.add_to_queue.emit(song))
        menu.addAction("⬇  Download",          lambda: self.download_requested.emit(song))
        menu.exec(self.table.viewport().mapToGlobal(pos))
