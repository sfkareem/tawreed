"""Main Workspace page: the BOQ processor UI.

This is the page the user lands on when they open the app. It hosts
the file-picker, the primary action button, and the live console that
streams AI progress.

Behaviour is identical to the previous monolithic MainWindow content;
this file just relocates the layout into a QWidget subclass so the
shell can swap it in and out of a QStackedWidget.
"""
import os
import asyncio

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt

from core import db
from gui.worker import BOQProcessor, WorkerSignals


class WorkspacePage(QWidget):
    """The main BOQ processing workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.signals = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("BOQ Processor")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")

        select_btn = QPushButton("Browse BOQ...")
        select_btn.clicked.connect(self.browse_file)

        self.process_btn = QPushButton("Start Processing")
        self.process_btn.setObjectName("primaryBtn")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)

        controls_layout.addWidget(select_btn)
        controls_layout.addWidget(self.file_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.process_btn)
        layout.addLayout(controls_layout)

        console_label = QLabel("Live Console")
        console_label.setObjectName("sectionLabel")
        layout.addWidget(console_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setObjectName("liveConsole")
        layout.addWidget(self.console, stretch=1)

    def browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select BOQ Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.process_btn.setEnabled(True)

    def log(self, text: str) -> None:
        self.console.insertPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_processing(self) -> None:
        if not self.selected_file:
            return

        settings = db.get_settings()
        if not settings or not settings.get("api_key"):
            QMessageBox.warning(
                self,
                "Settings Required",
                "Please configure an API key in Settings first.",
            )
            return

        self.process_btn.setEnabled(False)
        self.console.clear()
        self.log("Initializing processor...\n")

        # Disconnect any previous signal handlers so the page can be reused.
        self.signals = WorkerSignals()
        self.signals.log.connect(self.log)
        self.signals.finished.connect(self.on_processing_finished)
        self.signals.error.connect(self.on_processing_error)

        processor = BOQProcessor(self.selected_file, self.signals)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in this thread (shouldn't happen in normal flow
            # because main.py installs qasync, but fall back gracefully).
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(processor.process())

    def on_processing_finished(self, output_path: str) -> None:
        self.log(f"\n\n🎉 Processing complete!\nOutput saved to: {output_path}\n")
        self.process_btn.setEnabled(True)
        QMessageBox.information(
            self, "Complete", f"Successfully generated Work Packages!\nSaved to:\n{output_path}"
        )

    def on_processing_error(self, error_msg: str) -> None:
        self.log(f"\n\n❌ Error during processing:\n{error_msg}\n")
        self.process_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to process BOQ:\n{error_msg}")
