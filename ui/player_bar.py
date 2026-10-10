"""
Bottom player bar: album art, song info, transport controls, seek, volume.
"""
from __future__ import annotations
import requests
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QObject
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QSizePolicy
)
from core.player import Player


def _fmt_ms(ms: int) -> str:
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"


class ThumbnailLoader(QObject):
    loaded = pyqtSignal(QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            data = requests.get(self.url, timeout=5).content
            pix = QPixmap()
            pix.loadFromData(data)
            self.loaded.emit(pix.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation))
        except Exception:
            self.loaded.emit(QPixmap())


class PlayerBar(QWidget):
    # Emitted when user clicks next/prev (queue managed by main window)
    request_next = pyqtSignal()
    request_prev = pyqtSignal()

    def __init__(self, player: Player, parent=None):
        super().__init__(parent)
        self.player = player
        self._dragging_seek = False
        self._current_song: dict | None = None
        self._thumb_thread: QThread | None = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self.setFixedHeight(88)
        self.setStyleSheet("""
            PlayerBar {
                background: #1a1a2e;
                border-top: 1px solid #2a2a4a;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(16)

        # ── Album art ──
        self.thumb = QLabel()
        self.thumb.setFixedSize(56, 56)
        self.thumb.setStyleSheet("border-radius: 6px; background: #2a2a4a;")
        self.thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.thumb)

        # ── Song info ──
        info = QVBoxLayout()
        info.setSpacing(2)
        self.lbl_title  = QLabel("No song playing")
        self.lbl_artist = QLabel("")
        self.lbl_title.setStyleSheet("color:#e0e0ff; font-weight:600; font-size:13px;")
        self.lbl_artist.setStyleSheet("color:#888aaa; font-size:11px;")
        self.lbl_title.setMaximumWidth(200)
        self.lbl_artist.setMaximumWidth(200)
        info.addWidget(self.lbl_title)
        info.addWidget(self.lbl_artist)
        root.addLayout(info)

        root.addStretch()

        # ── Transport controls ──
        ctrl = QVBoxLayout()
        ctrl.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")
        for btn in (self.btn_prev, self.btn_play, self.btn_next):
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2a2a4a; color: #e0e0ff;
                    border-radius: 18px; font-size: 14px; border: none;
                }
                QPushButton:hover { background: #3a3a6a; }
                QPushButton:pressed { background: #4a4aaa; }
            """)
        btn_row.addWidget(self.btn_prev)
        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_next)

        # Seek + time
        seek_row = QHBoxLayout()
        seek_row.setSpacing(6)
        self.lbl_pos  = QLabel("0:00")
        self.lbl_dur  = QLabel("0:00")
        self.seek_bar = QSlider(Qt.Orientation.Horizontal)
        self.seek_bar.setRange(0, 1000)
        self.seek_bar.setFixedWidth(300)
        self.seek_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px; background: #2a2a4a; border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #7c6af7; border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px; height: 12px; margin: -4px 0;
                background: #c3b5ff; border-radius: 6px;
            }
        """)
        for lbl in (self.lbl_pos, self.lbl_dur):
            lbl.setStyleSheet("color:#888aaa; font-size:11px;")
        seek_row.addWidget(self.lbl_pos)
        seek_row.addWidget(self.seek_bar)
        seek_row.addWidget(self.lbl_dur)

        ctrl.addLayout(btn_row)
        ctrl.addLayout(seek_row)
        root.addLayout(ctrl)

        root.addStretch()

        # ── Volume ──
        vol_layout = QVBoxLayout()
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lbl_vol = QLabel("🔊")
        lbl_vol.setStyleSheet("color:#888aaa; font-size:14px;")
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(90)
        self.vol_slider.setStyleSheet(self.seek_bar.styleSheet())
        vol_layout.addWidget(lbl_vol, alignment=Qt.AlignmentFlag.AlignHCenter)
        vol_layout.addWidget(self.vol_slider)
        root.addLayout(vol_layout)

    def _connect_signals(self):
        self.btn_play.clicked.connect(self._toggle_play)
        self.btn_prev.clicked.connect(self.request_prev)
        self.btn_next.clicked.connect(self.request_next)

        self.seek_bar.sliderPressed.connect(lambda: setattr(self, "_dragging_seek", True))
        self.seek_bar.sliderReleased.connect(self._on_seek_released)

        self.vol_slider.valueChanged.connect(self.player.set_volume)

        self.player.position_changed.connect(self._on_position)
        self.player.duration_changed.connect(self._on_duration)
        self.player.state_changed.connect(self._on_state)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_song(self, song: dict):
        self._current_song = song
        self.lbl_title.setText(song.get("title", "Unknown"))
        self.lbl_artist.setText(song.get("artist", ""))
        self.thumb.setText("♪")
        url = song.get("thumbnail", "")
        if url:
            self._load_thumbnail(url)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def _on_seek_released(self):
        self._dragging_seek = False
        pct = self.seek_bar.value() / 1000.0
        self.player.seek_percent(pct)

    @pyqtSlot('qint64')
    def _on_position(self, ms):
        ms = int(ms)
        if not self._dragging_seek:
            dur = self.player.get_duration()
            if dur > 0:
                self.seek_bar.setValue(int(ms / dur * 1000))
        self.lbl_pos.setText(_fmt_ms(ms))

    @pyqtSlot('qint64')
    def _on_duration(self, ms):
        self.lbl_dur.setText(_fmt_ms(int(ms)))

    @pyqtSlot(str)
    def _on_state(self, state: str):
        self.btn_play.setText("⏸" if state == "playing" else "▶")
        if state == "ended":
            self.request_next.emit()

    def _load_thumbnail(self, url: str):
        if self._thumb_thread and self._thumb_thread.isRunning():
            self._thumb_thread.quit()
        self._thumb_thread = QThread()
        self._loader = ThumbnailLoader(url)
        self._loader.moveToThread(self._thumb_thread)
        self._thumb_thread.started.connect(self._loader.run)
        self._loader.loaded.connect(self._set_thumbnail)
        self._thumb_thread.start()

    @pyqtSlot(QPixmap)
    def _set_thumbnail(self, pix: QPixmap):
        if not pix.isNull():
            self.thumb.setPixmap(pix)
        if self._thumb_thread:
            self._thumb_thread.quit()