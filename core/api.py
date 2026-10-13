"""
Wrapper around ytmusicapi — no framework dependency.
"""
from __future__ import annotations
from ytmusicapi import YTMusic


class MusicAPI:
    def __init__(self, ytmusic: YTMusic):
        self.yt = ytmusic

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str, filter_: str = "songs", limit: int = 20) -> list[dict]:
        raw = self.yt.search(query, filter=filter_, limit=limit)
        if filter_ == "songs":
            return [self._parse_song(r) for r in raw]
        return [
            {
                "videoId":    r.get("videoId", ""),
                "playlistId": r.get("playlistId") or r.get("browseId", ""),
                "browseId":   r.get("browseId", ""),
                "title":      r.get("title", r.get("name", "Unknown")),
                "artist":     ", ".join(a.get("name", "") for a in r.get("artists", []))
                              if isinstance(r.get("artists"), list) else r.get("artist", ""),
                "album":      (r.get("album") or {}).get("name", ""),
                "duration":   r.get("duration_seconds") or r.get("duration") or 0,
                "thumbnail":  (r.get("thumbnails") or [{}])[-1].get("url", ""),
                "count":      r.get("count", ""),   # playlist / album track count string
            }
            for r in raw
        ]

    # ── Library ───────────────────────────────────────────────────────────────

    def get_liked_songs(self, limit: int = 100) -> list[dict]:
        return [self._parse_song(t)
                for t in self.yt.get_liked_songs(limit=limit).get("tracks", [])]

    def get_library_playlists(self) -> list[dict]:
        return self.yt.get_library_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        return [self._parse_song(t)
                for t in self.yt.get_playlist(playlist_id, limit=None).get("tracks", [])]

    def get_library_albums(self) -> list[dict]:
        return self.yt.get_library_albums()

    def get_album_tracks(self, browse_id: str) -> list[dict]:
        return [self._parse_song(t)
                for t in self.yt.get_album(browse_id).get("tracks", [])]

    # ── Like / Rate ───────────────────────────────────────────────────────────

    def like_song(self, video_id: str) -> None:
        """Rate a song as LIKE."""
        self.yt.rate_song(video_id, "LIKE")

    def unlike_song(self, video_id: str) -> None:
        """Remove like (set to INDIFFERENT)."""
        self.yt.rate_song(video_id, "INDIFFERENT")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_song(self, item: dict) -> dict:
        artists = item.get("artists") or []
        artist  = (", ".join(a.get("name", "") for a in artists)
                   if isinstance(artists, list) else str(artists))

        thumbs    = item.get("thumbnails") or []
        thumbnail = thumbs[-1].get("url", "") if thumbs else ""

        album = item.get("album") or {}
        album_name = album.get("name", "") if isinstance(album, dict) else ""

        dur = item.get("duration") or item.get("duration_seconds") or 0
        if isinstance(dur, str):
            parts = dur.split(":")
            try:
                dur = (int(parts[0]) * 60 + int(parts[1]) if len(parts) == 2
                       else int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]))
            except (ValueError, IndexError):
                dur = 0

        # videoId can live at top-level or nested (e.g. album tracks use .videoId inside track)
        video_id = (item.get("videoId")
                    or (item.get("video") or {}).get("videoId", "")
                    or "")

        return {
            "videoId":   video_id,
            "title":     item.get("title", "Unknown Title"),
            "artist":    artist,
            "album":     album_name,
            "duration":  dur,
            "thumbnail": thumbnail,
        }
