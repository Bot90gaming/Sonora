"""
Wrapper around ytmusicapi — no framework dependency.
"""
from __future__ import annotations
import json
import logging
from html.parser import HTMLParser
from urllib.parse import urlsplit
from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)


class AuthenticationRequiredError(RuntimeError):
    """Raised when YouTube Music returns its signed-out library placeholder."""


class _HTMLTitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def _log_response_metadata(response, *args, **kwargs):
    content_type = response.headers.get("Content-Type", "unknown")
    invalid_json = False
    title = ""
    if response.content and "json" in content_type.lower():
        try:
            response.json()
        except ValueError:
            invalid_json = True
    elif response.content and "html" in content_type.lower():
        title_parser = _HTMLTitleParser()
        title_parser.feed(response.text)
        title = " ".join(title_parser.title.split())[:120]

    if (response.status_code >= 400 or not response.content or invalid_json
            or "json" not in content_type.lower()):
        path = urlsplit(response.url).path
        logger.warning(
            "YouTube Music returned an unexpected response "
            "(status=%d, path=%s, content_type=%s, bytes=%d, "
            "invalid_json=%s, html_title=%r)",
            response.status_code, path, content_type, len(response.content),
            invalid_json, title,
        )
    return response


class MusicAPI:
    def __init__(self, ytmusic: YTMusic):
        self.yt = ytmusic
        self.yt._session.hooks["response"].append(_log_response_metadata)

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str, filter_: str = "songs", limit: int = 20) -> list[dict]:
        logger.debug("Searching YouTube Music (filter=%s, limit=%d)", filter_, limit)
        try:
            raw = self.yt.search(query, filter=filter_, limit=limit)
        except json.JSONDecodeError as exc:
            logger.warning(
                "YouTube Music returned invalid response for search with authenticated client (%s). "
                "Attempting fallback to unauthenticated search...",
                exc,
            )
            try:
                raw = YTMusic().search(query, filter=filter_, limit=limit)
            except Exception:
                raise RuntimeError(
                    "YouTube Music returned an empty or invalid response. "
                    "Check the terminal log for HTTP status and response metadata. "
                    "HTTP 400 means the request was rejected; HTTP 401 or 403 may "
                    "mean the saved sign-in has expired."
                ) from exc
        if filter_ == "songs":
            results = [self._parse_song(r) for r in raw]
        else:
            results = [
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
        logger.debug("Search returned %d results", len(results))
        return results

    def get_home(self, limit: int = 6) -> list[dict]:
        """Get personalized home sections and normalize playable song entries."""
        try:
            sections = self.yt.get_home(limit=limit) or []
        except json.JSONDecodeError as exc:
            logger.warning(
                "YouTube Music returned an invalid response (JSON decode error) for home feed: %s. "
                "Attempting fallback to unauthenticated client...",
                exc,
            )
            try:
                sections = YTMusic().get_home(limit=limit) or []
            except Exception as fallback_exc:
                raise RuntimeError(
                    "YouTube Music returned an invalid response and fallback failed."
                ) from fallback_exc
        if not isinstance(sections, list):
            raise RuntimeError("YouTube Music returned an invalid home feed.")

        normalized_sections = []
        invalid_sections = 0
        invalid_items = 0
        for section in sections:
            if not isinstance(section, dict):
                invalid_sections += 1
                continue

            contents = []
            section_contents = section.get("contents") or []
            if not isinstance(section_contents, list):
                invalid_items += 1
                section_contents = []
            for item in section_contents:
                if not isinstance(item, dict):
                    invalid_items += 1
                    continue
                result = self._parse_song(item) if item.get("videoId") else item
                raw_thumbnails = item.get("thumbnails") or []
                thumbnails = (
                    [thumb for thumb in raw_thumbnails if isinstance(thumb, dict)]
                    if isinstance(raw_thumbnails, list) else []
                )
                if not result.get("thumbnail") and thumbnails:
                    result["thumbnail"] = thumbnails[-1].get("url", "")
                contents.append(result)
            normalized_sections.append({**section, "contents": contents})

        if invalid_sections or invalid_items:
            logger.warning(
                "Ignored malformed YouTube Music home feed entries "
                "(sections=%d, items=%d)",
                invalid_sections, invalid_items,
            )
        return normalized_sections

    # ── Library ───────────────────────────────────────────────────────────────

    def get_liked_songs(self, limit: int = 100) -> list[dict]:
        try:
            tracks = self.yt.get_liked_songs(limit=limit).get("tracks", [])
        except KeyError as exc:
            response = str(exc).casefold()
            if (
                "singlecolumnbrowseresultsrenderer" in response
                and ("sign in" in response or "signinendpoint" in response)
            ):
                raise AuthenticationRequiredError(
                    "YouTube Music returned a sign-in page instead of your "
                    "Liked Songs. Your saved session may have expired. "
                    "Sign in again in Settings → Account."
                ) from None
            raise
        return [self._parse_song(track) for track in tracks]

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

    def get_station(self, video_id: str, limit: int = 5) -> list[dict]:
        """Return up to ``limit`` playable tracks from a YouTube Music radio mix."""
        if not video_id or limit <= 0:
            return []
        result = self.yt.get_watch_playlist(
            videoId=video_id, radio=True, limit=max(limit * 2, limit + 1))
        tracks = result.get("tracks") if isinstance(result, dict) else None
        if not isinstance(tracks, list):
            logger.warning("YouTube Music returned an invalid station for video_id=%s",
                           video_id)
            return []

        songs = []
        seen = {video_id}
        for track in tracks:
            if not isinstance(track, dict):
                continue
            song = self._parse_song(track)
            track_id = song.get("videoId")
            if not track_id or track_id in seen:
                continue
            seen.add(track_id)
            songs.append(song)
            if len(songs) >= limit:
                break
        return songs

    # ── Like / Rate ───────────────────────────────────────────────────────────

    def like_song(self, video_id: str) -> None:
        """Rate a song as LIKE."""
        self.yt.rate_song(video_id, "LIKE")

    def unlike_song(self, video_id: str) -> None:
        """Remove like (set to INDIFFERENT)."""
        self.yt.rate_song(video_id, "INDIFFERENT")

    def get_song_lyrics(self, video_id: str) -> dict | None:
        """Fetch lyrics (with timestamps if available) for a given video_id."""
        if not video_id:
            return None
        try:
            watch = self.yt.get_watch_playlist(videoId=video_id)
            if not isinstance(watch, dict):
                return None
            browse_id = watch.get("lyrics")
            if not browse_id:
                return None
            data = None
            try:
                data = self.yt.get_lyrics(browse_id, timestamps=True)
            except Exception:
                pass
            if not data:
                data = self.yt.get_lyrics(browse_id, timestamps=False)
            if not data or not isinstance(data, dict):
                return None
            return data
        except Exception as e:
            logger.debug("Failed to retrieve lyrics for %s: %s", video_id, e)
            return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_song(self, item: dict) -> dict:
        artists = item.get("artists") or []
        artist = (
            ", ".join(a.get("name", "") for a in artists if isinstance(a, dict))
            if isinstance(artists, list) else str(artists)
        )

        raw_thumbnails = item.get("thumbnails") or []
        thumbs = (
            [thumb for thumb in raw_thumbnails if isinstance(thumb, dict)]
            if isinstance(raw_thumbnails, list) else []
        )
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
        video = item.get("video")
        video_id = item.get("videoId") or (
            video.get("videoId", "") if isinstance(video, dict) else "")

        return {
            "videoId":   video_id,
            "title":     item.get("title", "Unknown Title"),
            "artist":    artist,
            "album":     album_name,
            "duration":  dur,
            "thumbnail": thumbnail,
        }
