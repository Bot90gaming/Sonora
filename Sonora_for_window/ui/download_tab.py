"""
Download tab: shows active and completed downloads.
"""
from __future__ import annotations
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog,
    QComboBox, QAbstractItemView
)
from core.downloader import Downloader, DEFAULT_DOWNLOAD_DIR


class DownloadTab(QWidget):
    def __init__(self, downloader: Downloader, parent=None):
        super().__init__(parent)
        self.downloader   = downloader
        self._out_dir     = DEFAULT_DOWNLOAD_DIR
        self._format      = "mp3"
        self._active: dict[str, int] = {}   # Ánh xạ video_id sang số hàng.
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── Hàng cài đặt ──
        settings = QHBoxLayout()
        lbl = QLabel("Save to:")
        lbl.setStyleSheet("color:#888aaa; font-size:12px;")
        self.dir_lbl = QLabel(str(self._out_dir))
        self.dir_lbl.setStyleSheet("color:#c3b5ff; font-size:12px;")
        btn_dir = QPushButton("Browse…")
        btn_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_dir.setStyleSheet("""
            QPushButton {
                background:#2a2a4a; color:#e0e0ff; border:1px solid #3a3a6a;
                border-radius:6px; padding:4px 10px; font-size:11px;
            }
            QPushButton:hover { background:#3a3a6a; }
        """)
        btn_dir.clicked.connect(self._pick_dir)

        fmt_lbl = QLabel("Format:")
        fmt_lbl.setStyleSheet("color:#888aaa; font-size:12px;")
        self.fmt_box = QComboBox()
        self.fmt_box.addItems(["mp3", "m4a", "flac", "opus", "wav"])
        self.fmt_box.setStyleSheet("""
            QComboBox {
                background:#1e1e3a; color:#e0e0ff; border:1px solid #3a3a6a;
                border-radius:6px; padding:4px 8px; font-size:11px;
            }
            QComboBox::drop-down { border:none; }
            QComboBox QAbstractItemView {
                background:#1e1e3a; color:#e0e0ff;
                selection-background-color:#3a3a6a;
            }
        """)
        self.fmt_box.currentTextChanged.connect(lambda t: setattr(self, "_format", t))

        settings.addWidget(lbl)
        settings.addWidget(self.dir_lbl)
        settings.addWidget(btn_dir)
        settings.addSpacing(20)
        settings.addWidget(fmt_lbl)
        settings.addWidget(self.fmt_box)
        settings.addStretch()
        layout.addLayout(settings)

        # ── Bảng tải xuống ──
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Title", "Artist", "Progress", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 180)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background:#12122a; color:#e0e0ff;
                gridline-color:#2a2a4a; border:none; font-size:12px;
            }
            QHeaderView::section {
                background:#1a1a3a; color:#888aaa;
                padding:6px; border:none; font-size:11px;
            }
            QTableWidget::item:selected { background:#2a2a5a; }
        """)
        layout.addWidget(self.table)

        self.status_lbl = QLabel("No downloads yet.")
        self.status_lbl.setStyleSheet("color:#888aaa; font-size:11px;")
        layout.addWidget(self.status_lbl)

    def _connect_signals(self):
        self.downloader.progress.connect(self._on_progress)
        self.downloader.finished.connect(self._on_finished)
        self.downloader.error.connect(self._on_error)

    # ── API công khai ────────────────────────────────────────────────────────

    def start_download(self, song: dict):
        vid   = song.get("videoId", "")
        title = song.get("title", "Unknown")
        artist = song.get("artist", "")
        if not vid:
            return
        if vid in self._active:
            return  # Bài hát đã có trong bảng.

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(title))
        self.table.setItem(row, 1, QTableWidgetItem(artist))

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setStyleSheet("""
            QProgressBar {
                background:#1e1e3a; border:1px solid #3a3a6a;
                border-radius:4px; text-align:center; color:#e0e0ff; font-size:10px;
            }
            QProgressBar::chunk { background:#7c6af7; border-radius:4px; }
        """)
        self.table.setCellWidget(row, 2, bar)
        self.table.setItem(row, 3, QTableWidgetItem("Downloading…"))

        self._active[vid] = row
        self.downloader.download(vid, title, artist, self._out_dir, self._format)
        self.status_lbl.setText(f"Downloading: {title}")

    # ── Hàm xử lý tín hiệu ───────────────────────────────────────────────────

    def _on_progress(self, vid: str, pct: float):
        row = self._active.get(vid)
        if row is None:
            return
        bar: QProgressBar = self.table.cellWidget(row, 2)
        if bar:
            bar.setValue(int(pct))

    def _on_finished(self, vid: str, path: str):
        row = self._active.pop(vid, None)
        if row is None:
            return
        bar: QProgressBar = self.table.cellWidget(row, 2)
        if bar:
            bar.setValue(100)
        self.table.setItem(row, 3, QTableWidgetItem("✓ Done"))
        self.status_lbl.setText(f"Saved: {Path(path).name}")

    def _on_error(self, vid: str, msg: str):
        row = self._active.pop(vid, None)
        if row is None:
            return
        self.table.setItem(row, 3, QTableWidgetItem(f"✗ {msg[:40]}"))

    def _pick_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select download folder", str(self._out_dir))
        if d:
            self._out_dir = Path(d)
            self.dir_lbl.setText(d)
