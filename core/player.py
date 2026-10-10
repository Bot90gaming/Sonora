"""
Audio player backed by PyQt6.QtMultimedia.QMediaPlayer.

"""
from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, pyqtSlot
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class Player(QObject):
    # Declare position/duration as 'qint64' to match QMediaPlayer's signal type exactly
    position_changed = pyqtSignal('qint64')
    duration_changed = pyqtSignal('qint64')
    state_changed    = pyqtSignal(str)
    volume_changed   = pyqtSignal(int)
    error_occurred   = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._media = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._media.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)

        self._media.positionChanged.connect(self.position_changed)
        self._media.durationChanged.connect(self.duration_changed)
        self._media.playbackStateChanged.connect(self._on_state)
        self._media.errorOccurred.connect(self._on_error)

    # ── Controls ──────────────────────────────────────────────────────────────

    def play_url(self, url: str):
        self._media.setSource(QUrl(url))
        self._media.play()

    def play(self):
        self._media.play()

    def pause(self):
        self._media.pause()

    def stop(self):
        self._media.stop()

    def seek(self, ms: int):
        self._media.setPosition(ms)

    def seek_percent(self, pct: float):
        dur = self._media.duration()
        if dur > 0:
            self._media.setPosition(int(pct * dur))

    # ── Volume ────────────────────────────────────────────────────────────────

    def set_volume(self, vol: int):
        clamped = max(0, min(vol, 100))
        self._audio.setVolume(clamped / 100.0)
        self.volume_changed.emit(clamped)

    def get_volume(self) -> int:
        return int(self._audio.volume() * 100)

    def toggle_mute(self):
        self._audio.setMuted(not self._audio.isMuted())

    # ── State ─────────────────────────────────────────────────────────────────

    def is_playing(self) -> bool:
        return self._media.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def get_position(self) -> int:
        return self._media.position()

    def get_duration(self) -> int:
        return self._media.duration()

    # ── Internal ──────────────────────────────────────────────────────────────

    @pyqtSlot(QMediaPlayer.PlaybackState)
    def _on_state(self, state):
        S = QMediaPlayer.PlaybackState
        if state == S.PlayingState:
            self.state_changed.emit("playing")
        elif state == S.PausedState:
            self.state_changed.emit("paused")
        elif state == S.StoppedState:
            pos, dur = self._media.position(), self._media.duration()
            if dur > 0 and pos >= dur - 500:
                self.state_changed.emit("ended")
            else:
                self.state_changed.emit("stopped")

    @pyqtSlot(QMediaPlayer.Error, str)
    def _on_error(self, error, msg: str):
        if error != QMediaPlayer.Error.NoError:
            self.error_occurred.emit(msg)
            self.state_changed.emit("stopped")