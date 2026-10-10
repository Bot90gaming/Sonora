"""
Download songs via yt-dlp in a background thread.
"""
from __future__ import annotations
import os
from pathlib import Path
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import yt_dlp


DEFAULT_DOWNLOAD_DIR = Path.home() / "Music" / "YTMusic"


class DownloadWorker(QObject):
    progress   = pyqtSignal(str, float)   # (video_id, percent 0-100)
    finished   = pyqtSignal(str, str)     # (video_id, file_path)
    error      = pyqtSignal(str, str)     # (video_id, error_message)

    def __init__(self, video_id: str, title: str, artist: str,
                 out_dir: Path = DEFAULT_DOWNLOAD_DIR,
                 audio_format: str = "mp3"):
        super().__init__()
        self.video_id    = video_id
        self.title       = title
        self.artist      = artist
        self.out_dir     = out_dir
        self.audio_format = audio_format
        self._cancelled  = False

    def run(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        url = f"https://music.youtube.com/watch?v={self.video_id}"

        def progress_hook(d):
            if self._cancelled:
                raise yt_dlp.utils.DownloadCancelled()
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                downloaded = d.get("downloaded_bytes", 0)
                pct = downloaded / total * 100
                self.progress.emit(self.video_id, pct)

        safe_title  = "".join(c for c in self.title  if c.isalnum() or c in " _-").strip()
        safe_artist = "".join(c for c in self.artist if c.isalnum() or c in " _-").strip()
        filename = f"{safe_artist} - {safe_title}" if safe_artist else safe_title
        out_template = str(self.out_dir / f"{filename}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_template,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": self.audio_format,
                "preferredquality": "192",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            out_path = str(self.out_dir / f"{filename}.{self.audio_format}")
            self.finished.emit(self.video_id, out_path)
        except yt_dlp.utils.DownloadCancelled:
            self.error.emit(self.video_id, "Download cancelled.")
        except Exception as e:
            self.error.emit(self.video_id, str(e))

    def cancel(self):
        self._cancelled = True


class Downloader(QObject):
    """Manages multiple concurrent downloads."""
    progress   = pyqtSignal(str, float)
    finished   = pyqtSignal(str, str)
    error      = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers: dict[str, tuple[QThread, DownloadWorker]] = {}

    def download(self, video_id: str, title: str, artist: str,
                 out_dir: Path = DEFAULT_DOWNLOAD_DIR,
                 audio_format: str = "mp3"):
        if video_id in self._workers:
            return  # already downloading

        thread = QThread()
        worker = DownloadWorker(video_id, title, artist, out_dir, audio_format)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self.progress)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self._workers[video_id] = (thread, worker)
        thread.start()

    def cancel(self, video_id: str):
        if video_id in self._workers:
            _, worker = self._workers[video_id]
            worker.cancel()

    def _on_finished(self, video_id: str, path: str):
        self._cleanup(video_id)
        self.finished.emit(video_id, path)

    def _on_error(self, video_id: str, msg: str):
        self._cleanup(video_id)
        self.error.emit(video_id, msg)

    def _cleanup(self, video_id: str):
        if video_id in self._workers:
            thread, _ = self._workers.pop(video_id)
            thread.quit()
            thread.wait()
