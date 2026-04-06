"""
styles.py
=========
Centralised stylesheet and colour constants for the application.

All visual tokens live here so the rest of the codebase never contains
hard-coded hex values — making theme changes a one-file job.
"""

# ── Colour palette ────────────────────────────────────────────────────────────
ACCENT: str = "#5c7cfa"          # primary blue-purple accent
ACCENT_HOVER: str = "#748ffc"
ACCENT_PRESS: str = "#4263eb"

BACKGROUND: str = "#12121e"      # near-black app background
SURFACE: str = "#1a1a2e"         # card / panel surface
SURFACE_ALT: str = "#22223a"     # slightly lighter surface
BORDER: str = "#2e2e4a"          # subtle border
BORDER_FOCUS: str = "#5c7cfa"    # focused input border

TEXT_PRIMARY: str = "#e8e8ff"    # main readable text
TEXT_SECONDARY: str = "#7c7caa"  # labels, hints
TEXT_DISABLED: str = "#44445a"

LOG_BACKGROUND: str = "#0d0d18"
LOG_TEXT_COLOR: str = "#c8c8e8"
LOG_SUCCESS_COLOR: str = "#69f0ae"
LOG_ERROR_COLOR: str = "#ff5252"
LOG_INFO_COLOR: str = "#4fc3f7"

# ── Reusable widget styles ────────────────────────────────────────────────────

PANEL_STYLE: str = f"""
    QWidget {{
        background-color: {SURFACE};
        border-radius: 6px;
    }}
"""

INPUT_STYLE: str = f"""
    QLineEdit {{
        background-color: {SURFACE_ALT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 13px;
        font-family: 'Courier New', monospace;
    }}
    QLineEdit:focus {{
        border: 1px solid {BORDER_FOCUS};
    }}
    QLineEdit:disabled {{
        color: {TEXT_DISABLED};
        background-color: {SURFACE};
    }}
"""

LABEL_STYLE: str = f"""
    QLabel {{
        color: {TEXT_SECONDARY};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
"""

PRIMARY_BUTTON_STYLE: str = f"""
    QPushButton {{
        background-color: {ACCENT};
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 10px 28px;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_PRESS};
    }}
    QPushButton:disabled {{
        background-color: {BORDER};
        color: {TEXT_DISABLED};
    }}
"""

SECONDARY_BUTTON_STYLE: str = f"""
    QPushButton {{
        background-color: {SURFACE_ALT};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {BORDER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton:disabled {{
        color: {TEXT_DISABLED};
    }}
"""

APP_STYLESHEET: str = f"""
    QMainWindow, QWidget {{
        background-color: {BACKGROUND};
        color: {TEXT_PRIMARY};
        font-family: 'Courier New', monospace;
    }}
    QScrollBar:vertical {{
        background: {SURFACE};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QToolTip {{
        background-color: {SURFACE_ALT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        padding: 4px 8px;
        border-radius: 3px;
    }}
"""
