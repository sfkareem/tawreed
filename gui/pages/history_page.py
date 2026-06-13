"""History page: lists past BOQ processing runs from the local SQLite DB.

Read-only. Double-clicking a row is reserved for a future PR that wires
up "open the output Excel in the system viewer".
"""
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView,
)
from PySide6.QtCore import Qt

from core import db


class HistoryPage(QWidget):
    """A read-only list of past processing runs."""

    HEADERS = ["#", "Timestamp", "Project", "Packages", "Output Path"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("Processing History")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        self.open_btn = QPushButton("Open Selected")
        self.open_btn.clicked.connect(self.open_selected)
        actions.addWidget(self.refresh_btn)
        actions.addWidget(self.open_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

    def refresh(self) -> None:
        try:
            history = db.get_history()
        except Exception as e:
            self.table.setRowCount(0)
            self.status_label.setText(f"Failed to load history: {e}")
            return

        self.table.setRowCount(len(history))
        for row_idx, entry in enumerate(history):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(entry.get("id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(entry.get("timestamp", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(entry.get("project_name", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(entry.get("packages_count", ""))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(entry.get("output_path", ""))))

        if history:
            self.status_label.setText(f"{len(history)} run(s) recorded.")
        else:
            self.status_label.setText("No processing history yet. Run a BOQ from the Workspace.")

    def _selected_output_path(self) -> str | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 4).text()

    def open_selected(self) -> None:
        path = self._selected_output_path()
        if not path:
            QMessageBox.information(self, "Nothing selected", "Pick a row first.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "File missing", f"Output file no longer exists:\n{path}")
            return
        # Use the OS-native opener. On Windows, os.startfile; on macOS, open; on Linux, xdg-open.
        try:
            if sys.platform == "win32":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "Open failed", f"Could not open the file:\n{e}")
