"""Application stylesheet.

Token-based QSS — every colour, spacing, radius, and font size is a
named value here, not magic numbers in widget code. To retheme the
app, change a token in this file only.

Object names referenced (set via setObjectName):
- QWidget#navRail           — left navigation rail
- QPushButton#navButton     — nav button (default + checked states)
- QLabel#navBrand / #navBrandFallback / #navFooter
- QWidget#mainContainer     — page content card with shadow
- QLabel#titleLabel         — page titles
- QLabel#sectionLabel       — page subtitles / console header
- QLabel#statusLabel        — page status / footer text
- QLabel#metaLabel / #metaValue
- QLabel#aboutBody
- QLabel#fileLabel
- QTextEdit#liveConsole
- QPushButton#primaryBtn    — main action button (Start / Save)
"""


# ----- Colour tokens (Catppuccin Mocha-ish, dark) -----
COLOR_BG = "#0d0e15"               # main window background
COLOR_BG_RAIL = "#0a0b12"          # nav rail background
COLOR_BG_CARD = "rgba(20, 21, 33, 0.7)"  # main content card
COLOR_BG_INPUT = "rgba(255, 255, 255, 0.05)"
COLOR_BG_INPUT_FOCUS = "rgba(255, 255, 255, 0.08)"

COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_BORDER_INPUT = "rgba(255, 255, 255, 0.10)"
COLOR_BORDER_INPUT_FOCUS = "#89b4fa"

COLOR_TEXT = "#e2e4f3"
COLOR_TEXT_DIM = "#a6adc8"
COLOR_TEXT_MUTED = "#7f849c"
COLOR_TEXT_PRIMARY = "#0d0e15"     # text on top of primary buttons

COLOR_ACCENT = "#89b4fa"           # primary blue
COLOR_ACCENT_HOVER = "#b4befe"
COLOR_ACCENT_TRANS = "rgba(137, 180, 250, 0.08)"
COLOR_ACCENT_TRANS_HOVER = "rgba(137, 180, 250, 0.18)"
COLOR_ACCENT_TRANS_BORDER = "rgba(137, 180, 250, 0.3)"
COLOR_ACCENT_TRANS_BORDER_HOVER = "rgba(137, 180, 250, 0.5)"

# Spacing
RADIUS_SM = 6
RADIUS_MD = 8
RADIUS_LG = 10
RADIUS_XL = 16

# Type
TYPE_MONO = "'Consolas', 'Courier New', monospace"
TYPE_SANS = "'Segoe UI', 'Inter', system-ui, sans-serif"


def _build() -> str:
    return f"""
    /* ---- Base ---- */
    QMainWindow {{
        background-color: {COLOR_BG};
    }}
    QWidget {{
        color: {COLOR_TEXT};
        font-size: 13px;
    }}

    /* ---- Navigation rail ---- */
    QWidget#navRail {{
        background-color: {COLOR_BG_RAIL};
        border-right: 1px solid {COLOR_BORDER};
    }}
    QLabel#navBrand {{
        color: {COLOR_TEXT};
        font-size: 18px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}
    QLabel#navBrandFallback {{
        color: {COLOR_ACCENT};
        font-size: 22px;
        font-weight: bold;
        padding: 20px;
    }}
    QLabel#navFooter {{
        color: {COLOR_TEXT_MUTED};
        font-size: 11px;
        padding-top: 8px;
    }}
    QPushButton#navButton {{
        background-color: transparent;
        color: {COLOR_TEXT_DIM};
        border: 1px solid transparent;
        border-radius: {RADIUS_MD};
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton#navButton:hover {{
        background-color: {COLOR_ACCENT_TRANS};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_ACCENT_TRANS_BORDER};
    }}
    QPushButton#navButton:checked {{
        background-color: {COLOR_ACCENT_TRANS_HOVER};
        color: {COLOR_ACCENT};
        border: 1px solid {COLOR_ACCENT};
        font-weight: 600;
    }}

    /* ---- Page content card ---- */
    QWidget#mainContainer {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: {RADIUS_XL};
    }}

    /* ---- Type roles ---- */
    QLabel#titleLabel {{
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 0.3px;
    }}
    QLabel#sectionLabel {{
        color: {COLOR_TEXT_DIM};
        font-weight: 500;
        font-size: 13px;
    }}
    QLabel#statusLabel {{
        color: {COLOR_TEXT_MUTED};
        font-size: 12px;
    }}
    QLabel#metaLabel {{
        color: {COLOR_TEXT_MUTED};
        font-size: 12px;
        font-weight: bold;
    }}
    QLabel#metaValue {{
        color: {COLOR_TEXT};
        font-size: 13px;
    }}
    QLabel#aboutBody {{
        color: {COLOR_TEXT_DIM};
        font-size: 13px;
        line-height: 1.5;
    }}
    QLabel#fileLabel {{
        color: {COLOR_TEXT_DIM};
        font-size: 13px;
    }}

    /* ---- Inputs ---- */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{
        background-color: {COLOR_BG_INPUT};
        color: #ffffff;
        border: 1px solid {COLOR_BORDER_INPUT};
        border-radius: {RADIUS_SM};
        padding: 8px;
        font-size: 13px;
        selection-background-color: {COLOR_ACCENT};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus {{
        border: 1px solid {COLOR_BORDER_INPUT_FOCUS};
        background-color: {COLOR_BG_INPUT_FOCUS};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}
    QComboBox QAbstractItemView {{
        background-color: #131420;
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_ACCENT_TRANS_HOVER};
        selection-color: {COLOR_ACCENT};
        outline: 0;
    }}

    /* ---- Live console ---- */
    QTextEdit#liveConsole {{
        background-color: rgba(10, 11, 18, 0.6);
        color: {COLOR_TEXT};
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: {RADIUS_LG};
        padding: 12px;
        font-family: {TYPE_MONO};
        font-size: 13px;
    }}

    /* ---- Tables ---- */
    QTableWidget {{
        background-color: rgba(10, 11, 18, 0.45);
        alternate-background-color: rgba(255, 255, 255, 0.02);
        gridline-color: {COLOR_BORDER};
        border: 1px solid {COLOR_BORDER};
        border-radius: {RADIUS_MD};
    }}
    QTableWidget::item {{
        padding: 6px 8px;
    }}
    QHeaderView::section {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_DIM};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {COLOR_BORDER};
        font-weight: 600;
    }}

    /* ---- Buttons ---- */
    QPushButton {{
        background-color: {COLOR_ACCENT_TRANS};
        color: {COLOR_ACCENT};
        border: 1px solid {COLOR_ACCENT_TRANS_BORDER};
        border-radius: {RADIUS_MD};
        padding: 9px 18px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {COLOR_ACCENT_TRANS_HOVER};
        border: 1px solid {COLOR_ACCENT_TRANS_BORDER_HOVER};
    }}
    QPushButton:disabled {{
        background-color: {COLOR_ACCENT_TRANS};
        color: {COLOR_TEXT_MUTED};
        border: 1px solid {COLOR_BORDER};
    }}
    QPushButton#primaryBtn {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_TEXT_PRIMARY};
        border: none;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: {COLOR_ACCENT_HOVER};
    }}
    QPushButton#primaryBtn:disabled {{
        background-color: {COLOR_ACCENT_TRANS_HOVER};
        color: rgba(13, 14, 21, 0.6);
    }}

    /* ---- Scrollbar ---- */
    QScrollBar:vertical {{
        border: none;
        background: rgba(255, 255, 255, 0.02);
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(137, 180, 250, 0.4);
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(137, 180, 250, 0.7);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: rgba(255, 255, 255, 0.02);
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(137, 180, 250, 0.4);
        min-width: 20px;
        border-radius: 4px;
    }}
    """


# Backwards-compat alias so the dialog (now removed) keeps its old import
# working during the deprecation window.
MAIN_WINDOW_STYLE = _build()
SETTINGS_DIALOG_STYLE = _build()  # legacy name
