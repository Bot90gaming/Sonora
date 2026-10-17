"""
Audio player — GStreamer backend (replaces QMediaPlayer).

Callbacks (set externally, called on the GLib main loop):
    on_position(pos_ms, dur_ms)
    on_state_change('playing' | 'paused' | 'stopped' | 'ended')
    on_error(message)
"""
from __future__ import annotations
import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

logger = logging.getLogger(__name__)


class Player:
    def __init__(self):
        self._pipeline = Gst.ElementFactory.make("playbin", "player")
        if not self._pipeline:
            raise RuntimeError(
                "Could not create GStreamer playbin. "
                "Install: sudo apt install gstreamer1.0-plugins-base"
            )
        self._pipeline.set_property("volume", 0.8)
        self._uri: str | None = None
        self._loop_enabled = False

        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        self._timer_id: int | None = None

        # Assign these from outside
        self.on_position:     None | callable = None
        self.on_state_change: None | callable = None
        self.on_error:        None | callable = None

    # ── Public API ────────────────────────────────────────────────────────────

    def play_uri(self, uri: str):
        logger.debug("Starting playback")
        self._uri = uri
        self._pipeline.set_state(Gst.State.NULL)
        self._pipeline.set_property("uri", uri)
        self._pipeline.set_state(Gst.State.PLAYING)
        self._start_timer()
        self._emit_state("playing")

    def play(self):
        logger.debug("Resuming playback")
        self._pipeline.set_state(Gst.State.PLAYING)
        self._start_timer()
        self._emit_state("playing")

    def pause(self):
        logger.debug("Pausing playback")
        self._pipeline.set_state(Gst.State.PAUSED)
        self._stop_timer()
        self._emit_state("paused")

    def stop(self):
        logger.debug("Stopping playback")
        self._pipeline.set_state(Gst.State.NULL)
        self._stop_timer()
        self._emit_state("stopped")

    def set_loop_enabled(self, enabled: bool):
        self._loop_enabled = enabled
        logger.info("Track repeat %s", "enabled" if enabled else "disabled")

    def is_playing(self) -> bool:
        ok, state, _ = self._pipeline.get_state(Gst.CLOCK_TIME_NONE)
        return ok == Gst.StateChangeReturn.SUCCESS and state == Gst.State.PLAYING

    def seek_percent(self, pct: float):
        ok, dur = self._pipeline.query_duration(Gst.Format.TIME)
        if ok and dur > 0:
            self._pipeline.seek_simple(
                Gst.Format.TIME,
                Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                int(pct * dur),
            )

    def set_volume(self, vol: float):
        """vol: 0.0 – 1.0"""
        self._pipeline.set_property("volume", max(0.0, min(1.0, vol)))

    def get_position_ms(self) -> int:
        ok, pos = self._pipeline.query_position(Gst.Format.TIME)
        return pos // 1_000_000 if ok else 0

    def get_duration_ms(self) -> int:
        ok, dur = self._pipeline.query_duration(Gst.Format.TIME)
        return dur // 1_000_000 if ok else 0

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_bus_message(self, bus, msg):
        if msg.type == Gst.MessageType.EOS:
            self._stop_timer()
            if self._loop_enabled and self._uri:
                logger.debug("Track ended; restarting because repeat is enabled")
                self.play_uri(self._uri)
            else:
                self._emit_state("ended")
        elif msg.type == Gst.MessageType.ERROR:
            err, _ = msg.parse_error()
            logger.error("GStreamer playback error: %s", err)
            self._stop_timer()
            if self.on_error:
                GLib.idle_add(self.on_error, str(err))

    def _emit_state(self, state: str):
        if self.on_state_change:
            GLib.idle_add(self.on_state_change, state)

    def _start_timer(self):
        self._stop_timer()
        self._timer_id = GLib.timeout_add(500, self._poll_position)

    def _stop_timer(self):
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

    def _poll_position(self) -> bool:
        if self.on_position:
            self.on_position(self.get_position_ms(), self.get_duration_ms())
        return True   # keep the timeout alive
