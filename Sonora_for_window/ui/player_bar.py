"""
Bottom player bar — modern M3 redesign.
Album art  |  song info  |  transport + seek  |  volume
"""
from __future__ import annotations
import requests
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QObject, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QSizePolicy, QFrame
)
from core.player import Player
import ui.theme as T


def _fmt_ms(ms: int) -> str:
    s = max(0, ms // 1000)
    return f"{s // 60}:{s % 60:02d}"


def _rounded_pixmap(pix: QPixmap, radius: int) -> QPixmap:
    """Clip pixmap to rounded rectangle."""
    size = pix.size()
    result = QPixmap(size)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pix)
    painter.end()
    return result


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
            scaled = pix.scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Cắt chính giữa ảnh thành kích thước 64×64.
            x = (scaled.width()  - 64) // 2
            y = (scaled.height() - 64) // 2
            cropped = scaled.copy(x, y, 64, 64)
            self.loaded.emit(_rounded_pixmap(cropped, T.RADIUS_MD))
        except Exception:
            self.loaded.emit(QPixmap())


class PlayerBar(QWidget):
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

    # ── Khởi tạo giao diện ───────────────────────────────────────────────────

    def _build_ui(self):
        self.setFixedHeight(96)
        self.setStyleSheet(f"""
            PlayerBar {{
                background: {T.SURFACE};
                border-top: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(T.SP_4, T.SP_3, T.SP_4, T.SP_3)
        root.setSpacing(T.SP_4)

        # ── Bên trái: ảnh bìa và thông tin ───────────────────────────────────
        self.thumb = QLabel()
        self.thumb.setFixedSize(64, 64)
        self.thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb.setStyleSheet(f"""
            QLabel {{
                background: {T.SURFACE_HIGH};
                border-radius: {T.RADIUS_MD}px;
                color: {T.PRIMARY};
                font-size: 24px;
            }}
        """)
        self.thumb.setText("♫")
        root.addWidget(self.thumb)

        info_col = QVBoxLayout()
        info_col.setSpacing(T.SP_1)
        info_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_title = QLabel("Nothing playing")
        self.lbl_title.setStyleSheet(f"""
            color: {T.ON_SURFACE};
            font-size: {T.TS_TITLE}px;
            font-weight: 600;
        """)
        self.lbl_title.setMaximumWidth(220)
        self.lbl_title.setWordWrap(False)

        self.lbl_artist = QLabel("")
        self.lbl_artist.setStyleSheet(f"""
            color: {T.ON_SURFACE_VARIANT};
            font-size: {T.TS_LABEL}px;
        """)
        self.lbl_artist.setMaximumWidth(220)

        info_col.addWidget(self.lbl_title)
        info_col.addWidget(self.lbl_artist)
        root.addLayout(info_col)

        root.addStretch()

        # ── Ở giữa: điều khiển phát và tua bài ───────────────────────────────
        centre_col = QVBoxLayout()
        centre_col.setSpacing(T.SP_2)
        centre_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Hàng nút điều khiển phát
        btn_row = QHBoxLayout()
        btn_row.setSpacing(T.SP_2)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")

        self.btn_prev.setStyleSheet(T.icon_btn(36))
        self.btn_next.setStyleSheet(T.icon_btn(36))
        self.btn_play.setStyleSheet(T.primary_icon_btn(48))

        for btn in (self.btn_prev, self.btn_play, self.btn_next):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_row.addWidget(self.btn_prev)
        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_next)

        # Hàng điều khiển tua bài
        seek_row = QHBoxLayout()
        seek_row.setSpacing(T.SP_2)
        seek_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_pos = QLabel("0:00")
        self.lbl_dur = QLabel("0:00")
        for lbl in (self.lbl_pos, self.lbl_dur):
            lbl.setStyleSheet(f"""
                color: {T.ON_SURFACE_VARIANT};
                font-size: {T.TS_CAPTION}px;
                font-variant-numeric: tabular-nums;
            """)
            lbl.setFixedWidth(34)

        self.seek_bar = QSlider(Qt.Orientation.Horizontal)
        self.seek_bar.setRange(0, 1000)
        self.seek_bar.setMinimumWidth(320)
        self.seek_bar.setMaximumWidth(480)
        self.seek_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.seek_bar.setStyleSheet(T.SLIDER_QSS)

        seek_row.addWidget(self.lbl_pos)
        seek_row.addWidget(self.seek_bar)
        seek_row.addWidget(self.lbl_dur)

        centre_col.addLayout(btn_row)
        centre_col.addLayout(seek_row)
        root.addLayout(centre_col)

        root.addStretch()

        # ── Bên phải: âm lượng ───────────────────────────────────────────────
        vol_col = QVBoxLayout()
        vol_col.setSpacing(T.SP_1)
        vol_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_vol = QLabel("🔊")
        lbl_vol.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        lbl_vol.setStyleSheet(f"color: {T.ON_SURFACE_VARIANT}; font-size: {T.TS_BODY}px;")

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.setStyleSheet(T.SLIDER_QSS)
        self.vol_slider.setCursor(Qt.CursorShape.PointingHandCursor)

        vol_col.addWidget(lbl_vol, alignment=Qt.AlignmentFlag.AlignHCenter)
        vol_col.addWidget(self.vol_slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(vol_col)

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

    # ── Phần công khai ───────────────────────────────────────────────────────

    def load_song(self, song: dict):
        self._current_song = song
        title  = song.get("title", "Unknown")
        artist = song.get("artist", "")
        self.lbl_title.setText(title)
        self.lbl_artist.setText(artist)
        self.thumb.clear()
        self.thumb.setText("♫")
        url = song.get("thumbnail", "")
        if url:
            self._load_thumbnail(url)

    # ── Hàm xử lý tín hiệu ───────────────────────────────────────────────────

    def _toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def _on_seek_released(self):
        self._dragging_seek = False
        self.player.seek_percent(self.seek_bar.value() / 1000.0)

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
        if state == "playing":
            self.btn_play.setText("⏸")
        else:
            self.btn_play.setText("▶")
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
            self.thumb.clear()
            self.thumb.setPixmap(pix)
        if self._thumb_thread:
            self._thumb_thread.quit()