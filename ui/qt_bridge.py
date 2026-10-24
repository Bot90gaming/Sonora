"""Qt/QML bridge for Sonora's music, playback, and account services."""
from __future__ import annotations

import logging
import tempfile
import threading
import time
from pathlib import Path

import yt_dlp
from qtpy.QtCore import QObject, Property, QRunnable, QThreadPool, Signal, Slot
from qtpy.QtGui import QGuiApplication, QPalette

from auth.auth_manager import (
    get_ytmusic_client,
    is_authenticated,
    logout,
    setup_from_headers,
)
from core.api import AuthenticationRequiredError, MusicAPI
from core.downloader import Downloader
from core.player import Player
from core import settings as cfg

logger = logging.getLogger(__name__)


class _WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(object)
    finished = Signal(int)


class _Worker(QRunnable):
    def __init__(self, token, function):
        super().__init__()
        self.token = token
        self.function = function
        self.signals = _WorkerSignals()

    def run(self):
        try:
            self.signals.result.emit(self.function())
        except AuthenticationRequiredError as exc:
            logger.info("YouTube Music requires a fresh sign-in")
            self.signals.error.emit(exc)
        except Exception as exc:
            logger.exception("Background UI task failed")
            self.signals.error.emit(exc)
        finally:
            self.signals.finished.emit(self.token)


class _Completion(QObject):
    result = Signal(object)
    error = Signal(object)

    def __init__(self, callback, error_callback, parent):
        super().__init__(parent)
        self.callback = callback
        self.result.connect(self._deliver_result)
        self.error.connect(error_callback)

    @Slot(object)
    def _deliver_result(self, result):
        self.callback(result)


class SonoraBridge(QObject):
    homeChanged = Signal()
    resultsChanged = Signal()
    searchFilterChanged = Signal()
    libraryChanged = Signal()
    queueChanged = Signal()
    downloadsChanged = Signal()
    nowPlayingChanged = Signal()
    playbackChanged = Signal()
    progressChanged = Signal()
    accountChanged = Signal()
    appearanceChanged = Signal()
    busyChanged = Signal()
    pageChanged = Signal()
    toast = Signal(str)
    positionReceived = Signal(int, int)
    stateReceived = Signal(str)
    playerErrorReceived = Signal(str)
    downloadProgressReceived = Signal(int, int)
    downloadDoneReceived = Signal(int, str)
    downloadErrorReceived = Signal(int, str)

    def __init__(self):
        super().__init__()
        self._pool = QThreadPool.globalInstance()
        self._workers = {}
        self._worker_token = 0
        self._api: MusicAPI | None = None
        self._home: list[dict] = []
        self._home_collections: list[dict] = []
        self._results: list[dict] = []
        self._search_filter = "songs"
        self._last_query = ""
        self._library: list[dict] = []
        self._queue: list[dict] = []
        self._downloads: list[dict] = []
        self._queue_index = -1
        self._now_playing: dict = {}
        self._current_page = "home"
        self._busy = False
        self._playing = False
        self._loading = False
        self._loop = False
        self._liked = False
        self._auth_expired = False
        self._position = 0
        self._duration = 0
        self._volume = 0.8
        self._theme = cfg.get("theme") or "dark"
        self._accent = cfg.get("accent") or "violet"
        self._gl_loop = None
        self._station_generation = 0
        self._cache_dir = Path(tempfile.gettempdir()) / "sonora_station_cache"
        self._audio_download_locks = {}
        self._audio_download_locks_guard = threading.Lock()
        self._player = Player()
        self._downloader = Downloader()
        self.positionReceived.connect(self._apply_position)
        self.stateReceived.connect(self._apply_player_state)
        self.playerErrorReceived.connect(self.toast.emit)
        self.downloadProgressReceived.connect(self._download_progress)
        self.downloadDoneReceived.connect(self._download_complete)
        self.downloadErrorReceived.connect(self._download_failed)
        self._player.on_position = self.positionReceived.emit
        self._player.on_state_change = self.stateReceived.emit
        self._player.on_error = self.playerErrorReceived.emit
        app = QGuiApplication.instance()
        if app:
            app.paletteChanged.connect(
                lambda *_: self.appearanceChanged.emit())
        self._start_glib_loop()
        self._set_busy(True)
        self._run(self._create_api, self._api_ready)

    def _start_glib_loop(self):
        from gi.repository import GLib

        self._gl_loop = GLib.MainLoop()
        threading.Thread(
            target=self._gl_loop.run,
            name="sonora-gstreamer-loop",
            daemon=True,
        ).start()

    def _run(self, function, on_result=None, on_error=None):
        self._worker_token += 1
        token = self._worker_token
        worker = _Worker(token, function)
        completion = _Completion(
            on_result or (lambda _result: None),
            on_error or self._on_task_error,
            self,
        )
        worker.signals.result.connect(completion.result.emit)
        worker.signals.error.connect(completion.error.emit)
        worker.signals.finished.connect(self._worker_finished)
        self._workers[token] = (worker, completion)
        self._pool.start(worker)

    @Slot(int)
    def _worker_finished(self, token):
        self._workers.pop(token, None)

    @staticmethod
    def _create_api():
        return MusicAPI(get_ytmusic_client())

    def _api_ready(self, api):
        self._api = api
        self._auth_expired = False
        self.accountChanged.emit()
        self._set_busy(False)
        self.loadHome()

    def _on_task_error(self, message):
        self._set_busy(False)
        self.toast.emit(str(message))

    def _set_busy(self, busy):
        if self._busy != busy:
            self._busy = busy
            self.busyChanged.emit()

    @Property("QVariantList", notify=homeChanged)
    def homeItems(self):
        return self._home

    @Property("QVariantList", notify=homeChanged)
    def homeCollections(self):
        return self._home_collections

    @Property("QVariantList", notify=resultsChanged)
    def searchResults(self):
        return self._results

    @Property(str, notify=searchFilterChanged)
    def searchFilter(self):
        return self._search_filter

    @Property("QVariantList", notify=libraryChanged)
    def libraryItems(self):
        return self._library

    @Property("QVariantList", notify=queueChanged)
    def queueItems(self):
        return self._queue

    @Property("QVariantList", notify=downloadsChanged)
    def downloads(self):
        return self._downloads

    @Property(int, notify=queueChanged)
    def queueIndex(self):
        return self._queue_index

    @Property("QVariantMap", notify=nowPlayingChanged)
    def nowPlaying(self):
        return self._now_playing

    @Property(bool, notify=playbackChanged)
    def playing(self):
        return self._playing

    @Property(bool, notify=playbackChanged)
    def loading(self):
        return self._loading

    @Property(bool, notify=playbackChanged)
    def loopEnabled(self):
        return self._loop

    @Property(bool, notify=playbackChanged)
    def liked(self):
        return self._liked

    @Property(int, notify=progressChanged)
    def positionMs(self):
        return self._position

    @Property(int, notify=progressChanged)
    def durationMs(self):
        return self._duration

    @Property(float, notify=playbackChanged)
    def volume(self):
        return self._volume

    @Property(str, notify=pageChanged)
    def currentPage(self):
        return self._current_page

    @Property(bool, notify=accountChanged)
    def authenticated(self):
        return is_authenticated() and not self._auth_expired

    @Property(bool, notify=busyChanged)
    def busy(self):
        return self._busy

    @Property(str, notify=appearanceChanged)
    def theme(self):
        return self._theme

    @Property(str, notify=appearanceChanged)
    def accent(self):
        return self._accent

    @Property(str, notify=appearanceChanged)
    def accentColor(self):
        return {
            "violet": "#d0bcff",
            "blue": "#b3c5ff",
            "green": "#a8d4ae",
            "rose": "#f2b8b5",
            "orange": "#ffb77d",
        }.get(self._accent, "#d0bcff")

    @Property(bool, notify=appearanceChanged)
    def darkTheme(self):
        return self._theme == "dark" or (
            self._theme == "system" and self._system_is_dark()
        )

    @staticmethod
    def _system_is_dark():
        palette = QGuiApplication.palette()
        return palette.color(QPalette.ColorRole.Window).lightness() < 128

    @Slot(str)
    def setPage(self, page):
        self._current_page = page
        self.pageChanged.emit()
        if page == "home":
            self.loadHome()
        elif page == "library":
            self.loadLibrary()

    @Slot(str)
    def setTheme(self, theme):
        if theme not in ("dark", "light", "system"):
            return
        self._theme = theme
        cfg.set("theme", theme)
        self.appearanceChanged.emit()

    @Slot(str)
    def setAccent(self, accent):
        if accent not in ("violet", "blue", "green", "rose", "orange"):
            return
        self._accent = accent
        cfg.set("accent", accent)
        self.appearanceChanged.emit()

    @Slot()
    def loadHome(self):
        if not self._api:
            return
        self._set_busy(True)

        def fetch():
            sections = self._api.get_home(limit=8)
            items = []
            collections = []
            for section in sections:
                for item in section.get("contents", []):
                    if item.get("videoId"):
                        items.append(item)
                    else:
                        browse_id = item.get("browseId", "")
                        playlist_id = item.get("playlistId", "")
                        item_type = str(
                            item.get("type") or item.get("resultType") or ""
                        ).casefold()
                        if playlist_id or "playlist" in item_type:
                            kind = "playlist"
                        elif browse_id and (
                            "album" in item_type or browse_id.startswith("MPRE")
                        ):
                            kind = "album"
                        else:
                            continue
                        collection_id = playlist_id or browse_id
                        if not collection_id:
                            continue
                        collections.append({
                            "title": item.get("title", "Untitled collection"),
                            "artist": item.get("count", kind.title()),
                            "thumbnail": self._thumbnail(item),
                            "collectionId": collection_id,
                            "collectionKind": kind,
                        })
            return items, collections

        self._run(fetch, self._apply_home)

    def _apply_home(self, result):
        items, collections = result
        self._home = items
        self._home_collections = collections
        self.homeChanged.emit()
        self._set_busy(False)

    @Slot(str)
    def search(self, query):
        query = query.strip()
        if not query or not self._api:
            self._results = []
            self.resultsChanged.emit()
            return
        self._last_query = query
        filter_name = self._search_filter
        self._set_busy(True)
        self._run(
            lambda: self._api.search(
                query, filter_=filter_name, limit=30),
            lambda items: self._apply_search(items, filter_name),
        )

    @Slot(str)
    def setSearchFilter(self, filter_name):
        if filter_name not in ("songs", "albums", "playlists"):
            return
        self._search_filter = filter_name
        self.searchFilterChanged.emit()
        if self._last_query:
            self.search(self._last_query)

    def _apply_search(self, items, filter_name):
        if filter_name != "songs":
            for item in items:
                item["collectionKind"] = (
                    "album" if filter_name == "albums" else "playlist")
                item["collectionId"] = (
                    item.get("browseId", "") if filter_name == "albums"
                    else item.get("playlistId") or item.get("browseId", "")
                )
        self._results = items
        self.resultsChanged.emit()
        self._set_busy(False)

    @Slot()
    def loadLibrary(self):
        if not self._api:
            return
        self._set_busy(True)

        def fetch():
            if not self.authenticated:
                return []
            songs = self._api.get_liked_songs(limit=100)
            playlists = self._api.get_library_playlists()
            albums = self._api.get_library_albums()
            collections = []
            for item in playlists:
                collections.append({
                    "title": item.get("title", "Untitled playlist"),
                    "artist": item.get("count", "Playlist"),
                    "thumbnail": self._thumbnail(item),
                    "collectionId": item.get("playlistId") or item.get("browseId", ""),
                    "collectionKind": "playlist",
                })
            for item in albums:
                artists = item.get("artists") or []
                artist = (
                    ", ".join(
                        entry.get("name", "") for entry in artists
                        if isinstance(entry, dict)
                    )
                    if isinstance(artists, list) else str(artists)
                )
                collections.append({
                    "title": item.get("title", "Untitled album"),
                    "artist": artist or "Album",
                    "thumbnail": self._thumbnail(item),
                    "collectionId": item.get("browseId", ""),
                    "collectionKind": "album",
                })
            return [*songs, *collections]

        self._run(fetch, self._apply_library, self._on_library_error)

    def _on_library_error(self, error):
        self._set_busy(False)
        if isinstance(error, AuthenticationRequiredError):
            self._auth_expired = True
            self._library = []
            self.libraryChanged.emit()
            self.accountChanged.emit()
        self.toast.emit(str(error))

    @staticmethod
    def _thumbnail(item):
        thumbnails = item.get("thumbnails") or []
        if thumbnails and isinstance(thumbnails[-1], dict):
            return thumbnails[-1].get("url", "")
        return item.get("thumbnail", "")

    def _apply_library(self, items):
        self._library = items
        self.libraryChanged.emit()
        self._set_busy(False)

    @Slot("QVariantMap")
    def openCollection(self, collection):
        collection_id = collection.get("collectionId")
        kind = collection.get("collectionKind")
        if not collection_id or not self._api:
            self.toast.emit("This collection is unavailable")
            return
        self._set_busy(True)
        fetch = (
            lambda: self._api.get_playlist_tracks(collection_id)
            if kind == "playlist"
            else self._api.get_album_tracks(collection_id)
        )
        self._run(fetch, self._apply_library)

    @Slot("QVariantMap")
    def playSong(self, song):
        self._queue = [dict(song)]
        self._queue_index = 0
        self.queueChanged.emit()
        self._start_song(self._queue[0])

    @Slot("QVariantMap")
    def enqueue(self, song):
        self._queue.append(dict(song))
        self.queueChanged.emit()
        self.toast.emit("Added to queue")

    @Slot()
    def togglePlayback(self):
        if self._loading:
            return
        if self._playing:
            self._player.pause()
        elif self._now_playing:
            self._player.play()
        elif self._queue:
            self._queue_index = max(0, self._queue_index)
            self.queueChanged.emit()
            self._start_song(self._queue[self._queue_index])

    @Slot()
    def nextTrack(self):
        if self._queue_index + 1 < len(self._queue):
            self._queue_index += 1
            self.queueChanged.emit()
            self._start_song(self._queue[self._queue_index])

    @Slot(int)
    def playQueueItem(self, index):
        if index < 0 or index >= len(self._queue):
            return
        self._queue_index = index
        self.queueChanged.emit()
        self._start_song(self._queue[index])

    @Slot(int)
    def removeQueueItem(self, index):
        if index < 0 or index >= len(self._queue):
            return
        self._queue.pop(index)
        if index < self._queue_index:
            self._queue_index -= 1
        elif index == self._queue_index:
            if self._queue:
                self._queue_index = min(index, len(self._queue) - 1)
                self._start_song(self._queue[self._queue_index])
            else:
                self._queue_index = -1
                self._now_playing = {}
                self._player.stop()
                self.nowPlayingChanged.emit()
        self.queueChanged.emit()

    @Slot(int, int)
    def moveQueueItem(self, index, offset):
        target = index + offset
        if (
            index <= self._queue_index
            or target <= self._queue_index
            or index < 0
            or target >= len(self._queue)
        ):
            return
        song = self._queue.pop(index)
        self._queue.insert(target, song)
        self.queueChanged.emit()

    @Slot()
    def clearUpcoming(self):
        if self._queue_index < 0:
            self._queue.clear()
        else:
            self._queue = self._queue[:self._queue_index + 1]
        self.queueChanged.emit()

    @Slot()
    def clearQueue(self):
        self._queue.clear()
        self._queue_index = -1
        self._now_playing = {}
        self._player.stop()
        self.queueChanged.emit()
        self.nowPlayingChanged.emit()

    @Slot()
    def previousTrack(self):
        if self._position > 3000:
            self.seek(0)
        elif self._queue_index > 0:
            self._queue_index -= 1
            self.queueChanged.emit()
            self._start_song(self._queue[self._queue_index])

    def _start_song(self, song):
        video_id = song.get("videoId")
        if not video_id:
            self.toast.emit("This track cannot be played")
            return
        self._station_generation += 1
        self._now_playing = dict(song)
        self._liked = False
        self._loading = True
        self._playing = False
        self._position = 0
        self._duration = 0
        self.nowPlayingChanged.emit()
        self.playbackChanged.emit()
        self.progressChanged.emit()

        def prepare():
            return self._download_audio_file(video_id)

        generation = self._station_generation
        self._worker_token += 1
        token = self._worker_token
        worker = _Worker(token, prepare)
        completion = _Completion(
            lambda uri: self._audio_ready(generation, uri),
            self._playback_error,
            self,
        )
        worker.signals.result.connect(completion.result.emit)
        worker.signals.error.connect(completion.error.emit)
        worker.signals.finished.connect(self._worker_finished)
        self._workers[token] = (worker, completion)
        self._pool.start(worker)

    def _download_audio_file(self, video_id):
        lock_key = (str(self._cache_dir), video_id)
        with self._audio_download_locks_guard:
            download_lock = self._audio_download_locks.setdefault(
                lock_key, threading.Lock())

        with download_lock:
            candidates = [
                path for path in self._cache_dir.glob(f"sonora_{video_id}.*")
                if path.is_file()
                and not path.name.endswith((".part", ".ytdl"))
            ] if self._cache_dir.exists() else []
            if candidates:
                return str(candidates[0].resolve().as_uri())

            self._cache_dir.mkdir(parents=True, exist_ok=True)
            template = str(self._cache_dir / f"sonora_{video_id}.%(ext)s")
            options = {
                "format": (
                    "bestaudio[ext=webm]/bestaudio[ext=opus]/"
                    "bestaudio[ext=m4a]/bestaudio/best"),
                "quiet": True,
                "no_warnings": True,
                "nocache": True,
                "outtmpl": template,
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    ),
                },
            }
            for attempt in range(1, 4):
                try:
                    with yt_dlp.YoutubeDL(options) as ydl:
                        ydl.extract_info(
                            f"https://music.youtube.com/watch?v={video_id}",
                            download=True,
                        )
                    candidates = [
                        path for path in self._cache_dir.glob(
                            f"sonora_{video_id}.*")
                        if path.is_file()
                        and not path.name.endswith((".part", ".ytdl"))
                    ]
                    if not candidates:
                        raise RuntimeError(
                            "Audio download completed without a playable file")
                    return str(candidates[0].resolve().as_uri())
                except Exception as exc:
                    message = str(exc).lower()
                    retryable = (
                        "403" in message or "429" in message
                        or "forbidden" in message or "connection" in message
                    )
                    if attempt == 3 or not retryable:
                        raise
                    logger.warning(
                        "Playback download attempt %d failed (video_id=%s); retrying: %s",
                        attempt,
                        video_id,
                        exc,
                    )
                    time.sleep(1.5 * attempt)

    @Slot(str)
    def _playback_error(self, message):
        self._loading = False
        self.playbackChanged.emit()
        self.toast.emit(f"Playback error: {message}")

    def _audio_ready(self, generation, uri):
        if generation != self._station_generation:
            return
        from gi.repository import GLib

        self._loading = False
        self.playbackChanged.emit()
        GLib.idle_add(self._player.play_uri, uri)

    @Slot(int, int)
    def _apply_position(self, position, duration):
        self._position = position
        self._duration = duration
        self.progressChanged.emit()

    @Slot(str)
    def _apply_player_state(self, state):
        self._playing = state == "playing"
        if state == "ended":
            if self._loop:
                self._start_song(self._now_playing)
            else:
                self.nextTrack()
        self.playbackChanged.emit()

    @Slot(int, int)
    def _download_progress(self, index, progress):
        if index < len(self._downloads):
            self._downloads[index]["progress"] = progress
            self.downloadsChanged.emit()

    @Slot(int, str)
    def _download_complete(self, index, path):
        if index < len(self._downloads):
            self._downloads[index]["status"] = "Saved"
            self._downloads[index]["progress"] = 100
            self._downloads[index]["path"] = path
            self.downloadsChanged.emit()
        self.toast.emit(f"Downloaded {Path(path).name}")

    @Slot(int, str)
    def _download_failed(self, index, message):
        if index < len(self._downloads):
            self._downloads[index]["status"] = "Failed"
            self.downloadsChanged.emit()
        self.toast.emit(f"Download failed: {message}")

    @Slot(float)
    def seek(self, fraction):
        self._player.seek_percent(max(0.0, min(1.0, fraction)))

    @Slot(float)
    def setVolume(self, volume):
        self._volume = max(0.0, min(1.0, volume))
        self._player.set_volume(self._volume)
        self.playbackChanged.emit()

    @Slot()
    def toggleLoop(self):
        self._loop = not self._loop
        self._player.set_loop_enabled(self._loop)
        self.playbackChanged.emit()

    @Slot(str)
    def showToast(self, message):
        self.toast.emit(message)

    @Slot("QVariantMap")
    def likeSong(self, song):
        if not self._api or not song.get("videoId"):
            self.toast.emit("Sign in to like songs")
            return
        liked = not self._liked
        action = self._api.like_song if liked else self._api.unlike_song

        def update():
            action(song["videoId"])
            return liked

        def updated(value):
            self._liked = value
            self.playbackChanged.emit()
            self.toast.emit(
                "Added to Liked Songs" if value else "Removed from Liked Songs")

        self._run(update, updated)

    @Slot(str)
    def signInWithHeaders(self, headers):
        self._set_busy(True)

        def sign_in():
            setup_from_headers(headers)
            return self._create_api()

        self._run(sign_in, self._api_ready)

    @Slot()
    def signOut(self):
        logout()
        self._library = []
        self.libraryChanged.emit()
        self.accountChanged.emit()
        self.toast.emit("Signed out")

    @Slot("QVariantMap")
    def startStation(self, song):
        if not self._api or not song.get("videoId"):
            self.toast.emit("Select a playable song to start a station")
            return
        video_id = song["videoId"]
        generation = self._station_generation
        self._set_busy(True)

        def fetch():
            return self._api.get_station(video_id, limit=5)

        def apply_station(songs):
            if generation != self._station_generation:
                return
            if not songs:
                self._set_busy(False)
                self.toast.emit("No station tracks were found for this song")
                return
            self._queue = [dict(song), *songs]
            self._queue_index = 0
            self.queueChanged.emit()
            self._set_busy(False)
            self.toast.emit(f"Station added: {len(songs)} tracks")
            self._start_song(self._queue[0])
            prefetch_generation = self._station_generation

            def prefetch():
                failures = 0
                for station_song in songs:
                    if prefetch_generation != self._station_generation:
                        break
                    try:
                        self._download_audio_file(station_song["videoId"])
                    except Exception:
                        failures += 1
                        logger.exception(
                            "Could not pre-download station track (video_id=%s)",
                            station_song.get("videoId"),
                        )
                return failures

            def prefetch_complete(failures):
                if failures:
                    self.toast.emit(
                        f"Could not pre-download {failures} station tracks")

            self._run(prefetch, prefetch_complete)

        self._run(fetch, apply_station)

    @Slot("QVariantMap")
    def downloadSong(self, song):
        video_id = song.get("videoId")
        if not video_id:
            self.toast.emit("This item cannot be downloaded")
            return
        output_dir = Path(cfg.get("download_dir") or Path.home() / "Music")
        audio_format = cfg.get("download_format") or "mp3"
        download_id = len(self._downloads)
        self._downloads.append({
            "title": song.get("title", "Unknown"),
            "artist": song.get("artist", ""),
            "status": "Downloading",
            "progress": 0,
        })
        self.downloadsChanged.emit()
        self._downloader.download(
            video_id,
            song.get("title", "Unknown"),
            song.get("artist", ""),
            output_dir,
            audio_format,
            on_progress=lambda progress: self.downloadProgressReceived.emit(
                download_id, progress),
            on_done=lambda path: self.downloadDoneReceived.emit(
                download_id, path),
            on_error=lambda message: self.downloadErrorReceived.emit(
                download_id, message),
        )
