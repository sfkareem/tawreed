MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #0d0e15;
    }
    QWidget#mainContainer {
        background-color: rgba(20, 21, 33, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
    }
    QTextEdit {
        background-color: rgba(10, 11, 18, 0.6);
        color: #e2e4f3;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 12px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
    }
    QScrollBar:vertical {
        border: none;
        background: rgba(255, 255, 255, 0.02);
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: rgba(137, 180, 250, 0.4);
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(137, 180, 250, 0.7);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QPushButton {
        background-color: rgba(137, 180, 250, 0.08);
        color: #89b4fa;
        border: 1px solid rgba(137, 180, 250, 0.3);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: rgba(137, 180, 250, 0.18);
        border: 1px solid rgba(137, 180, 250, 0.5);
    }
    QPushButton#primaryBtn {
        background-color: #89b4fa;
        color: #0d0e15;
        border: none;
    }
    QPushButton#primaryBtn:hover {
        background-color: #b4befe;
    }
    QPushButton#primaryBtn:disabled {
        background-color: rgba(137, 180, 250, 0.3);
        color: rgba(13, 14, 21, 0.6);
    }
    QLabel#titleLabel {
        color: #ffffff;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    QLabel {
        font-size: 13px;
    }
"""

SETTINGS_DIALOG_STYLE = """
    QDialog {
        background-color: #131420;
        color: #e2e4f3;
    }
    QLabel {
        color: #e2e4f3;
        font-weight: bold;
        font-size: 13px;
    }
    QLineEdit {
        background-color: rgba(255, 255, 255, 0.05);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 1px solid #89b4fa;
        background-color: rgba(255, 255, 255, 0.08);
    }
    QPushButton {
        background-color: rgba(137, 180, 250, 0.08);
        color: #89b4fa;
        border: 1px solid rgba(137, 180, 250, 0.3);
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: rgba(137, 180, 250, 0.18);
    }
    QPushButton#saveBtn {
        background-color: #89b4fa;
        color: #11111b;
        border: none;
    }
    QPushButton#saveBtn:hover {
        background-color: #b4befe;
    }
"""
