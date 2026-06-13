"""About page — author credits, version, repo, and license.

Senior design choices:
- Card-based layout. Each logical block (Author, Project, Stack,
  License, Repository) is its own Card.
- Author block centres the brand mark + name + URL — a tiny
  visual signature rather than a wall of text.
- Version is pulled from tawreed_app.__init__ at runtime so a version
  bump only needs to be done in one place.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtCore import QUrl

from tawreed_app import __version__, __appname__, __author__, __author_url__, __license__, __repo_url__
from gui.assets import LOGO_PNG_PATH
from gui.widgets import Card, PageHeader, Section, StatusPill


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            __appname__,
            "AI-driven BOQ work-package extraction for construction quantity surveyors.",
        ))

        # ----- Author card -----
        author_card = Card("Author & Credits")
        body = QHBoxLayout()
        body.setSpacing(16)
        body.setContentsMargins(0, 0, 0, 0)

        mark = QLabel()
        if LOGO_PNG_PATH.exists():
            pix = QPixmap(str(LOGO_PNG_PATH)).scaled(
                72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            mark.setPixmap(pix)
        else:
            mark.setText("T")
            mark.setObjectName("navBrandFallback")
        mark.setAlignment(Qt.AlignCenter)
        body.addWidget(mark)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name = QLabel(f"Built by {__author__}")
        name.setObjectName("authorName")
        text_col.addWidget(name)
        url = QLabel(f'<a href="{__author_url__}" style="color:#89b4fa;">{__author_url__}</a>')
        url.setObjectName("authorUrl")
        url.setTextFormat(Qt.RichText)
        url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        url.setOpenExternalLinks(True)
        text_col.addWidget(url)
        bio = QLabel(
            "Tawreed was built to help construction quantity surveyors "
            "categorize Bill of Quantities items into high-level work packages "
            "using LLMs. The current build is a single-user desktop app; all "
            "settings, history, and outputs live locally on your machine."
        )
        bio.setObjectName("hint")
        bio.setWordWrap(True)
        text_col.addWidget(bio)
        body.addLayout(text_col, stretch=1)
        author_card.addLayout(body)
        layout.addWidget(author_card)

        # ----- Project card -----
        project_card = Card("Project")

        def _row(label: str, value: str) -> QHBoxLayout:
            r = QHBoxLayout()
            r.setSpacing(8)
            l = QLabel(label)
            l.setObjectName("metaLabel")
            l.setFixedWidth(110)
            v = QLabel(value)
            v.setObjectName("metaValue")
            v.setTextInteractionFlags(Qt.TextBrowserInteraction)
            v.setWordWrap(True)
            r.addWidget(l)
            r.addWidget(v, stretch=1)
            return r

        project_card.addLayout(_row("App name", __appname__))
        project_card.addLayout(_row("Version", f"v{__version__}"))
        project_card.addLayout(_row("License", __license__))
        project_card.addLayout(_row("Repository",
            f'<a href="{__repo_url__}" style="color:#89b4fa;">{__repo_url__}</a>'))
        project_card.addLayout(_row("Status", "Released"))
        layout.addWidget(project_card)

        # ----- Stack card -----
        stack_card = Card("Built With")
        stack_card.addLayout(_row("Language", "Python 3.10+"))
        stack_card.addLayout(_row("UI framework", "PySide6 (Qt for Python)"))
        stack_card.addLayout(_row("LLM providers", "OpenAI · Anthropic · Google Gemini · OpenAI-compatible"))
        stack_card.addLayout(_row("Data", "openpyxl · pandas · SQLite"))
        stack_card.addLayout(_row("Packaging", "PyInstaller (onedir)"))
        layout.addWidget(stack_card)

        # ----- Action row -----
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        repo_btn = QPushButton("Open Repository")
        repo_btn.setObjectName("primaryBtn")
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(__repo_url__)))
        author_btn = QPushButton("Author Website")
        author_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(__author_url__)))
        action_row.addWidget(repo_btn)
        action_row.addWidget(author_btn)
        action_row.addStretch()
        layout.addLayout(action_row)

        # ----- Footer -----
        footer = QLabel(
            f"© {__author__}. Released under the {__license__} License."
        )
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        layout.addStretch(1)
