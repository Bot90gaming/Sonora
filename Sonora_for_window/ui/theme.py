"""Shared dark Material-inspired theme tokens and Qt stylesheets."""
from __future__ import annotations


# Mã màu
BG = "#0f0e17"
SURFACE = "#171622"
SURFACE_VAR = "#22212e"
SURFACE_HIGH = "#2c2a3a"
ON_SURFACE = "#e8e5f2"
ON_SURFACE_VARIANT = "#c5c1d2"
PRIMARY = "#c6aaff"
PRIMARY_CONTAINER = "#4f378b"
ON_PRIMARY_CONT = "#eaddff"
OUTLINE_VARIANT = "#494554"
HOVER_OVERLAY = "#2a2735"
ERROR = "#ffb4ab"

# Khoảng cách
SP_1 = 4
SP_2 = 8
SP_3 = 12
SP_4 = 16
SP_5 = 24

# Bán kính bo góc
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16

# Cỡ chữ
TS_CAPTION = 11
TS_LABEL = 12
TS_BODY = 14
TS_TITLE = 18
TS_HEADLINE = 24
TS_DISPLAY = 32


GLOBAL_QSS = f"""
    QWidget {{
        background: {BG};
        color: {ON_SURFACE};
        font-family: "Segoe UI", sans-serif;
    }}
    QToolTip {{
        background: {SURFACE_HIGH};
        color: {ON_SURFACE};
        border: 1px solid {OUTLINE_VARIANT};
        padding: 4px 8px;
    }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
        background: {SURFACE_VAR};
        color: {ON_SURFACE};
        border: 1px solid {OUTLINE_VARIANT};
        border-radius: {RADIUS_SM}px;
        padding: {SP_2}px {SP_3}px;
        selection-background-color: {PRIMARY_CONTAINER};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border: 2px solid {PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {SURFACE_VAR};
        color: {ON_SURFACE};
        selection-background-color: {SURFACE_HIGH};
        border: 1px solid {OUTLINE_VARIANT};
    }}
    QTableWidget {{
        background: {BG};
        alternate-background-color: {SURFACE};
        color: {ON_SURFACE};
        gridline-color: {OUTLINE_VARIANT};
        border: none;
        selection-background-color: {SURFACE_HIGH};
    }}
    QHeaderView::section {{
        background: {SURFACE};
        color: {ON_SURFACE_VARIANT};
        padding: {SP_2}px;
        border: none;
        border-bottom: 1px solid {OUTLINE_VARIANT};
    }}
    QStatusBar {{
        background: {SURFACE};
        color: {ON_SURFACE_VARIANT};
        border-top: 1px solid {OUTLINE_VARIANT};
    }}
"""


TABLE_QSS = f"""
    QTableWidget {{
        background: {SURFACE};
        color: {ON_SURFACE};
        gridline-color: {OUTLINE_VARIANT};
        border: none;
        font-size: {TS_BODY}px;
        selection-background-color: {SURFACE_HIGH};
    }}
    QHeaderView::section {{
        background: {SURFACE_VAR};
        color: {ON_SURFACE_VARIANT};
        padding: {SP_2}px {SP_3}px;
        border: none;
        font-size: {TS_LABEL}px;
        font-weight: 600;
    }}
    QTableWidget::item {{
        padding: {SP_2}px;
    }}
    QTableWidget::item:selected {{
        background: {SURFACE_HIGH};
        color: {ON_SURFACE};
    }}
    QTableWidget::item:hover {{
        background: {HOVER_OVERLAY};
    }}
"""


LIST_QSS = f"""
    QListWidget {{
        background: transparent;
        color: {ON_SURFACE};
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        padding: {SP_2}px {SP_3}px;
        border-radius: {RADIUS_SM}px;
    }}
    QListWidget::item:selected {{
        background: {PRIMARY_CONTAINER};
        color: {ON_PRIMARY_CONT};
    }}
    QListWidget::item:hover:!selected {{
        background: {HOVER_OVERLAY};
    }}
"""


SLIDER_QSS = f"""
    QSlider::groove:horizontal {{
        height: 4px;
        background: {SURFACE_HIGH};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {PRIMARY};
        border-radius: 2px;
    }}
    QSlider::add-page:horizontal {{
        background: {SURFACE_HIGH};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        width: 12px;
        margin: -4px 0;
        border-radius: 6px;
        background: {PRIMARY};
    }}
"""


def _button_style(
    background: str,
    foreground: str,
    hover: str,
    *,
    min_width: int = 0,
    outlined: bool = False,
    radius: int = RADIUS_LG,
) -> str:
    border = f"1px solid {OUTLINE_VARIANT}" if outlined else "none"
    return f"""
        QPushButton {{
            background: {background};
            color: {foreground};
            border: {border};
            border-radius: {radius}px;
            padding: {SP_2}px {SP_4}px;
            min-width: {min_width}px;
            font-size: {TS_LABEL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {hover};
        }}
        QPushButton:pressed {{
            background: {SURFACE_HIGH};
        }}
        QPushButton:disabled {{
            color: {OUTLINE_VARIANT};
            background: {SURFACE};
        }}
    """


def filled_btn(min_width: int = 0) -> str:
    return _button_style(PRIMARY, "#27154f", "#d8c7ff", min_width=min_width)


def tonal_btn(min_width: int = 0) -> str:
    return _button_style(
        PRIMARY_CONTAINER,
        ON_PRIMARY_CONT,
        SURFACE_HIGH,
        min_width=min_width,
    )


def outline_btn(min_width: int = 0) -> str:
    return _button_style(
        "transparent",
        PRIMARY,
        HOVER_OVERLAY,
        min_width=min_width,
        outlined=True,
    )


def icon_btn(size: int = 36) -> str:
    return f"""
        QPushButton {{
            background: transparent;
            color: {ON_SURFACE_VARIANT};
            border: none;
            border-radius: {size // 2}px;
            min-width: {size}px;
            max-width: {size}px;
            min-height: {size}px;
            max-height: {size}px;
            padding: 0;
            font-size: {TS_BODY}px;
        }}
        QPushButton:hover {{
            background: {HOVER_OVERLAY};
            color: {ON_SURFACE};
        }}
        QPushButton:pressed {{
            background: {SURFACE_HIGH};
        }}
    """


def primary_icon_btn(size: int = 48) -> str:
    return f"""
        QPushButton {{
            background: {PRIMARY};
            color: #27154f;
            border: none;
            border-radius: {size // 2}px;
            min-width: {size}px;
            max-width: {size}px;
            min-height: {size}px;
            max-height: {size}px;
            padding: 0;
            font-size: {TS_TITLE}px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background: #d8c7ff;
        }}
        QPushButton:pressed {{
            background: {PRIMARY_CONTAINER};
            color: {ON_PRIMARY_CONT};
        }}
    """
