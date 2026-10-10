"""
Wrapper around ytmusicapi for search, library, and playlist operations.
"""
from __future__ import annotations
from builtins import ValueError
from typing import Any
from ytmusicapi import YTMusic


class MusicAPI:
    def __init__(self, ytmusic: YTMusic):
        self.yt = ytmusic

    # ─── Search ───────────────────────────────────────────────────────────────

    def search_songs(self, query: str, limit: int = 20) -> list[dict]:
        results = self.yt.search(query, filter="songs", limit=limit)
        return [self._parse_song(r) for r in results]

    def search_albums(self, query: str, limit: int = 20) -> list[dict]:
        return self.yt.search(query, filter="albums", limit=limit)

    def search_artists(self, query: str, limit: int = 20) -> list[dict]:
        return self.yt.search(query, filter="artists", limit=limit)

    def search_playlists(self, query: str, limit: int = 20) -> list[dict]:
        return self.yt.search(query, filter="playlists", limit=limit)

    # ─── Library ──────────────────────────────────────────────────────────────

    def get_liked_songs(self, limit: int = 100) -> list[dict]:
        playlist = self.yt.get_liked_songs(limit=limit)
        tracks = playlist.get("tracks", [])
        return [self._parse_song(t) for t in tracks]

    def get_library_playlists(self) -> list[dict]:
        return self.yt.get_library_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        playlist = self.yt.get_playlist(playlist_id, limit=None)
        tracks = playlist.get("tracks", [])
        return [self._parse_song(t) for t in tracks]

    def get_library_albums(self) -> list[dict]:
        return self.yt.get_library_albums()

    def get_album_tracks(self, browse_id: str) -> list[dict]:
        album = self.yt.get_album(browse_id)
        tracks = album.get("tracks", [])
        return [self._parse_song(t) for t in tracks]

    # ─── Recommendations ─────────────────────────────────────────────────────

    def get_home(self) -> list[dict]:
        return self.yt.get_home()

    def get_song_related(self, video_id: str) -> list[dict]:
        related = self.yt.get_song_related(video_id)
        songs = []
        for section in related:
            if section.get("contents"):
                for item in section["contents"]:
                    if item.get("videoId"):
                        songs.append(self._parse_song(item))
        return songs

    # ─── Stream URL ───────────────────────────────────────────────────────────

    def get_stream_url(self, video_id: str) -> str | None:
        """
        Use yt-dlp to extract the best audio stream URL.
        This avoids needing the YouTube Data API quota.
        """
        import yt_dlp
        url = f"https://music.youtube.com/watch?v={video_id}"
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url")

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _parse_song(self, item: dict) -> dict:
        """Normalise varying API response shapes into a flat song dict."""
        artists = item.get("artists") or []
        if isinstance(artists, list):
            artist_name = ", ".join(a.get("name", "") for a in artists)
        else:
            artist_name = str(artists)

        thumbnail = ""
        thumbs = item.get("thumbnails") or []
        if thumbs:
            thumbnail = thumbs[-1].get("url", "")

        album = item.get("album") or {}
        album_name = album.get("name", "") if isinstance(album, dict) else ""

        duration = item.get("duration") or item.get("duration_seconds") or 0
        if isinstance(duration, str):
            parts = duration.split(":")
            try:
                if len(parts) == 2:
                    duration = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except ValueError:
                duration = 0

        return {
            "videoId": item.get("videoId", ""),
            "title": item.get("title", "Unknown Title"),
            "artist": artist_name,
            "album": album_name,
            "duration": duration,
            "thumbnail": thumbnail,
        }
