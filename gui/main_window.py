"""Main application shell.

A QMainWindow with:
- a fixed-width left rail (navigation buttons)
- a QStackedWidget that swaps in the current page
- a status footer in the rail (version + repo link)

Pages live in ``gui/pages/``. To add a new page:
1. Create ``gui/pages/<name>_page.py`` with a ``<Name>Page(QWidget)`` class.
2. Import it below and register it in ``self._pages`` with a label.
3. Add a button in ``_build_nav()``.
"""
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy,
    QFrame,
)
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtGui import QPixmap, QColor

from gui.styles import load_stylesheet
from gui.pages.workspace_page import WorkspacePage
from gui.pages.history_page import HistoryPage
from gui.pages.settings_page import SettingsPage
from gui.pages.about_page import AboutPage
from gui.assets import LOGO_PNG_PATH

from tawreed_app import __version__, __appname__


class MainWindow(QMainWindow):
    """Top-level shell. Holds nav + page stack; no business logic."""

    NAV_ITEMS = [
        ("workspace", "Workspace"),
        ("history", "History"),
        ("settings", "Settings"),
        ("about", "About"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__appname__} — AI BOQ Processing")
        self.setStyleSheet(load_stylesheet("dark"))

        self._nav_buttons: dict[str, QPushButton] = {}
        self._pages: dict[str, QWidget] = {}
        self._build_ui()
        # _restore_window_state also selects the correct page.
        self._restore_window_state()

    # ----- UI construction ------------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_nav())
        root_layout.addWidget(self._build_page_stack(), stretch=1)

    def _build_nav(self) -> QWidget:
        rail = QWidget()
        rail.setObjectName("navRail")
        rail.setFixedWidth(220)
        rail.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(16, 24, 16, 20)
        rail_layout.setSpacing(8)

        # Brand block
        brand = QWidget()
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 16)
        brand_layout.setSpacing(6)

        logo_label = QLabel()
        if LOGO_PNG_PATH.exists():
            pixmap = QPixmap(str(LOGO_PNG_PATH)).scaled(
                72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("TAWREED")
            logo_label.setObjectName("navBrandFallback")
        logo_label.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo_label)

        app_label = QLabel("Tawreed")
        app_label.setObjectName("navBrand")
        app_label.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(app_label)

        tagline = QLabel("AI BOQ work packages")
        tagline.setObjectName("navTagline")
        tagline.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(tagline)

        rail_layout.addWidget(brand)

        # Page stack — registered up here so the nav buttons can target it.
        # (The actual QStackedWidget is built in _build_page_stack; we just
        # create a reference to it via self._stack from the caller.)
        rail_layout.addSpacing(8)
        for key, label in self.NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, k=key: self.select_page(k))
            self._nav_buttons[key] = btn
            rail_layout.addWidget(btn)

        rail_layout.addStretch(1)

        # Accent stripe (visual brand mark, sits above the footer).
        stripe = QFrame()
        stripe.setObjectName("navAccentStripe")
        stripe.setFixedHeight(2)
        rail_layout.addWidget(stripe)

        footer = QLabel(f"v{__version__}  ·  {__appname__}")
        footer.setObjectName("navFooter")
        footer.setAlignment(Qt.AlignCenter)
        rail_layout.addWidget(footer)

        return rail

    def _build_page_stack(self) -> QWidget:
        container = QWidget()
        container.setObjectName("mainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(28, 28, 28, 28)
        container_layout.setSpacing(0)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        self._stack = QStackedWidget(container)
        container_layout.addWidget(self._stack)

        # Register pages
        self._pages["workspace"] = WorkspacePage()
        self._pages["history"] = HistoryPage()
        self._pages["settings"] = SettingsPage()
        self._pages["about"] = AboutPage()
        for key, widget in self._pages.items():
            self._stack.addWidget(widget)

        return container

    # ----- Page switching -------------------------------------------------

    def select_page(self, key: str) -> None:
        if key not in self._pages:
            return
        self._stack.setCurrentWidget(self._pages[key])
        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)
        # If the page exposes a refresh hook (History page does), call it.
        refresh = getattr(self._pages[key], "refresh", None)
        if callable(refresh):
            try:
                refresh()
            except Exception:
                # Don't let a refresh failure prevent navigation; the page
                # itself is responsible for surfacing the error in its UI.
                pass

    # ----- Window state persistence --------------------------------------

    def _restore_window_state(self) -> None:
        settings = QSettings("sfkareem", "Tawreed")
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.resize(1180, 800)
        # Last-visited page (default: workspace). Use select_page so the
        # nav highlight and the page's refresh hook both fire.
        last = settings.value("last_page", "workspace")
        if last in self._pages:
            self.select_page(last)

    # ----- Single-instance integration -----------------------------------

    def bring_to_front(self, _message: str = "") -> None:
        """Slot for the SingleApplication message_received signal.

        Raises and activates the window so the user sees the existing
        instance when they double-click the icon a second time.
        """
        if self.isMinimized():
            self.showNormal()
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()

    # ----- Window state persistence --------------------------------------

    def closeEvent(self, event) -> None:
        settings = QSettings("sfkareem", "Tawreed")
        settings.setValue("geometry", self.saveGeometry())
        current = self._stack.currentWidget()
        for key, widget in self._pages.items():
            if widget is current:
                settings.setValue("last_page", key)
                break
        super().closeEvent(event)
