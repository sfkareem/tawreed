import os
import asyncio
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QFileDialog, QDialog, 
    QLineEdit, QFormLayout, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor

from core import db
from gui.styles import MAIN_WINDOW_STYLE, SETTINGS_DIALOG_STYLE
from gui.worker import BOQProcessor, WorkerSignals, check_connection

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Settings")
        self.setMinimumWidth(455)
        self.setStyleSheet(SETTINGS_DIALOG_STYLE)
        
        self.layout = QFormLayout(self)
        self.layout.setSpacing(12)
        
        self.base_url_input = QLineEdit()
        self.model_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        self.layout.addRow("Base URL:", self.base_url_input)
        self.layout.addRow("Model ID:", self.model_input)
        self.layout.addRow("API Key:", self.api_key_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(self.test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        
        self.layout.addRow(btn_layout)
        
        self.load_settings()

    def load_settings(self):
        settings = db.get_settings()
        self.api_key_input.setText(settings.get("api_key", ""))
        self.model_input.setText(settings.get("model_id", "MiniMax-M3"))
        self.base_url_input.setText(settings.get("base_url", "https://api.minimax.io/v1"))

    def test_connection(self):
        api_key = self.api_key_input.text()
        base_url = self.base_url_input.text()
        model_id = self.model_input.text()
        
        self.test_btn.setText("Testing...")
        self.test_btn.setEnabled(False)
        
        loop = asyncio.get_event_loop()
        task = loop.create_task(asyncio.to_thread(check_connection, api_key, base_url, model_id))
        
        def on_done(future):
            self.test_btn.setText("Test Connection")
            self.test_btn.setEnabled(True)
            try:
                success = future.result()
                if success:
                    QMessageBox.information(self, "Success", "Connection successful!")
                else:
                    QMessageBox.critical(self, "Error", "Connection failed. Check API key and URL.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Connection test error: {e}")
                
        task.add_done_callback(on_done)

    def save_settings(self):
        settings = {
            "api_key": self.api_key_input.text(),
            "model_id": self.model_input.text(),
            "base_url": self.base_url_input.text()
        }
        db.save_settings(settings)
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tawreed - AI BOQ Processing")
        self.resize(1000, 700)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tawreed_logo_transparent.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("TAWREED")
            logo_label.setStyleSheet("font-size: 26px; color: #89b4fa; font-weight: bold; padding: 20px;")
            logo_label.setAlignment(Qt.AlignCenter)
            
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.open_settings)
        
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(settings_btn)
        
        # Content panel
        content_panel = QWidget()
        content_panel.setObjectName("mainContainer")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 110))
        shadow.setOffset(0, 6)
        content_panel.setGraphicsEffect(shadow)
        
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)
        
        title = QLabel("BOQ Processor")
        title.setObjectName("titleLabel")
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        
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
        
        console_label = QLabel("Live Console")
        console_label.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 14px; margin-top: 10px;")
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        
        content_layout.addWidget(title)
        content_layout.addSpacing(10)
        content_layout.addLayout(controls_layout)
        content_layout.addWidget(console_label)
        content_layout.addWidget(self.console)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_panel, stretch=1)
        
        self.selected_file = None

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select BOQ Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.process_btn.setEnabled(True)

    def log(self, text):
        self.console.insertPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_processing(self):
        if not self.selected_file:
            return
            
        settings = db.get_settings()
        if not settings or not settings.get('api_key'):
            QMessageBox.warning(self, "Settings Required", "Please configure an API key in settings first.")
            return

        self.process_btn.setEnabled(False)
        self.console.clear()
        self.log("Initializing processor...\n")
        
        self.signals = WorkerSignals()
        self.signals.log.connect(self.log)
        self.signals.finished.connect(self.on_processing_finished)
        self.signals.error.connect(self.on_processing_error)
        
        processor = BOQProcessor(self.selected_file, self.signals)
        
        loop = asyncio.get_event_loop()
        loop.create_task(processor.process())

    def on_processing_finished(self, output_path):
        self.log(f"\n\n🎉 Processing complete!\nOutput saved to: {output_path}\n")
        self.process_btn.setEnabled(True)
        QMessageBox.information(self, "Complete", f"Successfully generated Work Packages!\nSaved to:\n{output_path}")

    def on_processing_error(self, error_msg):
        self.log(f"\n\n❌ Error during processing:\n{error_msg}\n")
        self.process_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to process BOQ:\n{error_msg}")
