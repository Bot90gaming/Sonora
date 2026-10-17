"""
Downloader — Python threading + GLib.idle_add (no PyQt6).
"""
from __future__ import annotations
import logging
import threading
from pathlib import Path
import yt_dlp
from gi.repository import GLib

logger = logging.getLogger(__name__)


class Downloader:
    """
    Spawn one daemon thread per download.
    All callbacks are scheduled on the GLib main loop so they are safe
    to call directly from GTK widget handlers.
    """

    def download(
        self,
        video_id: str,
        title: str,
        artist: str,
        out_dir: Path | str,
        audio_format: str = "mp3",
        on_progress: callable | None = None,   # (pct: int) -> None
        on_done:     callable | None = None,   # (path: str) -> None
        on_error:    callable | None = None,   # (msg: str)  -> None
    ):
        t = threading.Thread(
            target=self._run,
            args=(video_id, title, artist, Path(out_dir),
                  audio_format, on_progress, on_done, on_error),
            daemon=True,
        )
        t.start()

    # ── Worker ────────────────────────────────────────────────────────────────

    def _run(self, video_id, title, artist, out_dir: Path,
             audio_format, on_progress, on_done, on_error):
        logger.info("Starting download (video_id=%s, format=%s)", video_id, audio_format)
        url = f"https://music.youtube.com/watch?v={video_id}"

        safe = lambda s: "".join(c for c in s if c.isalnum() or c in " _-").strip()
        name = f"{safe(artist)} - {safe(title)}" if artist else safe(title)
        template = str(out_dir / f"{name}.%(ext)s")

        def hook(d):
            if d["status"] == "downloading" and on_progress:
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                pct   = int(d.get("downloaded_bytes", 0) / total * 100)
                GLib.idle_add(on_progress, pct)

        ydl_opts = {
            "format":          "bestaudio/best",
            "outtmpl":         template,
            "progress_hooks":  [hook],
            "quiet":           True,
            "no_warnings":     True,
            "postprocessors": [{
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   audio_format,
                "preferredquality": "192",
            }],
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            },
        }

        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            path = str(out_dir / f"{name}.{audio_format}")
            logger.info("Download completed (video_id=%s, path=%s)", video_id, path)
            if on_done:
                GLib.idle_add(on_done, path)
        except Exception as e:
            logger.exception("Download failed (video_id=%s)", video_id)
            if on_error:
                GLib.idle_add(on_error, str(e))
