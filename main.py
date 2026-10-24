import logging
import os
import sys
from pathlib import Path

os.environ["QT_API"] = "pyside6"
os.environ.setdefault("QSG_RHI_BACKEND", "opengl")

logger = logging.getLogger(__name__)

from qtpy.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from PySide6.QtQml import QQmlApplicationEngine

_bridge = None


def main():
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGL)
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
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Sonora")
    app.setOrganizationName("io.github")
    app.setApplicationVersion("1.0.0")
    engine = QQmlApplicationEngine()
    _load_ui(engine)
    if not engine.rootObjects():
        logger.error("Could not load Sonora QML interface")
        return 1
    exit_code = app.exec()
    logger.info("Sonora exited with status %d", exit_code)
    return exit_code


def _load_ui(engine: QQmlApplicationEngine):
    global _bridge

    import gi
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
    from ui.qt_bridge import SonoraBridge

    Gst.init(None)
    _bridge = SonoraBridge()
    engine.setInitialProperties({"bridge": _bridge})
    qml_path = Path(__file__).parent / "ui" / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))


if __name__ == "__main__":
    sys.exit(main())
