"""
YTMusic Player — GTK4 + libadwaita entry point (Linux).
"""
import logging
import sys

logger = logging.getLogger(__name__)

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Adw, Gst

# Initialise GStreamer before anything else
Gst.init(None)


def main():
    debug = "--debug" in sys.argv[1:]
    if debug:
        sys.argv[:] = [arg for arg in sys.argv if arg != "--debug"]
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
    logger.info("Starting Sonora%s", " with debug logging" if debug else "")
    app = Adw.Application(application_id="io.github.ytmusic_player")

    # Force dark colour scheme to match our purple aesthetic
    app.connect("activate", _on_activate)

    exit_code = app.run(sys.argv)
    logger.info("Sonora exited with status %d", exit_code)
    sys.exit(exit_code)


def _on_activate(app: Adw.Application):
    logger.debug("Activating application")
    # Apply saved theme, surface style, and accent colour.
    from core import settings as cfg
    from ui.glass_theme import apply as apply_glass
    apply_glass(
        theme=cfg.get("theme"),
        glass=cfg.get("glass_effect"),
        accent=cfg.get("accent"),
    )

    from ui.main_window import MainWindow
    win = MainWindow(application=app)
    win.present()


if __name__ == "__main__":
    main()
