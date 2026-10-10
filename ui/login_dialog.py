"""
Login dialog — browser-headers auth — modern M3 redesign.
"""
from __future__ import annotations
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame
)
from auth.auth_manager import setup_from_headers
import ui.theme as T


class SetupWorker(QObject):
    success = pyqtSignal()
    error   = pyqtSignal(str)

    def __init__(self, headers_raw: str):
        super().__init__()
        self.headers_raw = headers_raw

    def run(self):
        try:
            setup_from_headers(self.headers_raw)
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))


class _Step(QFrame):
    """Numbered step chip."""
    def __init__(self, num: int, text: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {T.SURFACE_VAR};
                border-radius: {T.RADIUS_SM}px;
                border: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(T.SP_3, T.SP_2, T.SP_3, T.SP_2)
        row.setSpacing(T.SP_3)

        badge = QLabel(str(num))
        badge.setFixedSize(24, 24)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: {T.PRIMARY_CONTAINER};
            color: {T.ON_PRIMARY_CONT};
            border-radius: 12px;
            font-size: {T.TS_LABEL}px;
            font-weight: 700;
        """)
        row.addWidget(badge)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {T.ON_SURFACE}; font-size: {T.TS_BODY}px;")
        row.addWidget(lbl, stretch=1)


class LoginDialog(QDialog):
    logged_in = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in to YouTube Music")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setStyleSheet(T.GLOBAL_QSS + f"""
            QDialog {{
                background: {T.BG};
            }}
        """)
        self._thread: QThread | None = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(T.SP_4)
        layout.setContentsMargins(T.SP_5, T.SP_5, T.SP_5, T.SP_5)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        icon = QLabel("🎵")
        icon.setStyleSheet(f"font-size: {T.TS_DISPLAY}px;")
        header.addWidget(icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(T.SP_1)
        lbl_title = QLabel("Sign in to YouTube Music")
        lbl_title.setStyleSheet(f"""
            color: {T.ON_SURFACE};
            font-size: {T.TS_HEADLINE}px;
            font-weight: 700;
        """)
        lbl_sub = QLabel("Paste your browser request headers below to authenticate.")
        lbl_sub.setStyleSheet(f"color: {T.ON_SURFACE_VARIANT}; font-size: {T.TS_BODY}px;")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header.addLayout(title_col, stretch=1)
        layout.addLayout(header)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {T.OUTLINE_VARIANT};")
        layout.addWidget(div)

        # ── Steps card ────────────────────────────────────────────────────────
        steps_card = QFrame()
        steps_card.setStyleSheet(f"""
            QFrame {{
                background: {T.SURFACE};
                border-radius: {T.RADIUS_LG}px;
                border: 1px solid {T.OUTLINE_VARIANT};
            }}
        """)
        steps_layout = QVBoxLayout(steps_card)
        steps_layout.setContentsMargins(T.SP_4, T.SP_4, T.SP_4, T.SP_4)
        steps_layout.setSpacing(T.SP_2)

        steps_lbl = QLabel("How to get your headers:")
        steps_lbl.setStyleSheet(f"""
            color: {T.ON_SURFACE_VARIANT};
            font-size: {T.TS_LABEL}px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        steps_layout.addWidget(steps_lbl)

        for num, text in [
            (1, "Open music.youtube.com in your browser and sign in."),
            (2, "Press F12 → go to the Network tab → refresh the page (F5)."),
            (3, "Click any request to music.youtube.com."),
            (4, 'Go to the Headers tab → scroll to "Request Headers" and copy everything there.'),
            (5, "Paste the copied headers into the text field below."),
        ]:
            steps_layout.addWidget(_Step(num, text))

        layout.addWidget(steps_card)

        # ── Headers input ─────────────────────────────────────────────────────
        lbl_input = QLabel("Request headers:")
        lbl_input.setStyleSheet(f"color: {T.ON_SURFACE_VARIANT}; font-size: {T.TS_LABEL}px;")
        layout.addWidget(lbl_input)

        self.headers_edit = QTextEdit()
        self.headers_edit.setPlaceholderText(
            "Paste your request headers here…\n\n"
            "Example:\n"
            "cookie: VISITOR_INFO1_LIVE=…; __Secure-3PSID=…\n"
            "authorization: SAPISIDHASH …"
        )
        self.headers_edit.setMinimumHeight(120)
        self.headers_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {T.SURFACE_VAR};
                color: {T.ON_SURFACE};
                border: 1px solid {T.OUTLINE_VARIANT};
                border-radius: {T.RADIUS_MD}px;
                font-family: "Cascadia Code", "Fira Code", monospace;
                font-size: {T.TS_LABEL}px;
                padding: {T.SP_3}px;
                selection-background-color: {T.PRIMARY_CONTAINER};
            }}
            QTextEdit:focus {{
                border: 2px solid {T.PRIMARY};
            }}
        """)
        layout.addWidget(self.headers_edit)

        # ── Status ────────────────────────────────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color: {T.ON_SURFACE_VARIANT}; font-size: {T.TS_LABEL}px;")
        layout.addWidget(self.status_lbl)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_skip = QPushButton("Skip for now")
        self.btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_skip.setStyleSheet(T.outline_btn(100))
        self.btn_skip.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_skip)

        self.btn_signin = QPushButton("Sign in")
        self.btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signin.setStyleSheet(T.filled_btn(100))
        self.btn_signin.clicked.connect(self._do_sign_in)
        btn_row.addWidget(self.btn_signin)

        layout.addLayout(btn_row)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _do_sign_in(self):
        raw = self.headers_edit.toPlainText().strip()
        if not raw:
            self.status_lbl.setText("Please paste your request headers first.")
            return

        self.btn_signin.setEnabled(False)
        self.btn_signin.setText("Signing in…")
        self.status_lbl.setText("")

        self._thread = QThread()
        self._worker = SetupWorker(raw)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._thread.start()

    def _on_success(self):
        if self._thread:
            self._thread.quit()
        self.logged_in.emit()
        self.accept()

    def _on_error(self, msg: str):
        if self._thread:
            self._thread.quit()
        self.btn_signin.setEnabled(True)
        self.btn_signin.setText("Sign in")
        self.status_lbl.setText(f"Error: {msg}")
        self.status_lbl.setStyleSheet(f"color: {T.ERROR}; font-size: {T.TS_LABEL}px;")