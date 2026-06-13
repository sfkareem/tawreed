"""About page: app name, version, build, credits, and a link to the repo."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


APP_NAME = "Tawreed"
APP_TAGLINE = "AI-driven BOQ work-package extraction"
APP_VERSION = "0.1.0"
APP_REPO_URL = "https://github.com/sfkareem/tawreed"


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        tagline = QLabel(APP_TAGLINE)
        tagline.setObjectName("sectionLabel")
        layout.addWidget(tagline)

        version_row = QHBoxLayout()
        version_label = QLabel("Version:")
        version_label.setObjectName("metaLabel")
        version_value = QLabel(APP_VERSION)
        version_value.setObjectName("metaValue")
        version_row.addWidget(version_label)
        version_row.addWidget(version_value)
        version_row.addStretch()
        layout.addLayout(version_row)

        stack_row = QHBoxLayout()
        stack_label = QLabel("Stack:")
        stack_label.setObjectName("metaLabel")
        stack_value = QLabel("Python 3.11 · PySide6 · openai · openpyxl · SQLite")
        stack_value.setObjectName("metaValue")
        stack_value.setWordWrap(True)
        stack_row.addWidget(stack_label)
        stack_row.addWidget(stack_value, stretch=1)
        layout.addLayout(stack_row)

        layout.addSpacing(20)

        credits = QLabel(
            "Tawreed was built to help construction quantity surveyors "
            "categorize Bill of Quantities items into high-level work packages "
            "using LLMs. The current build is a single-user desktop app; all "
            "settings, history, and outputs live locally."
        )
        credits.setObjectName("aboutBody")
        credits.setWordWrap(True)
        layout.addWidget(credits)

        layout.addSpacing(20)

        link_row = QHBoxLayout()
        repo_btn = QPushButton("Open Repository")
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(APP_REPO_URL)))
        link_row.addWidget(repo_btn)
        link_row.addStretch()
        layout.addLayout(link_row)

        layout.addStretch(1)
