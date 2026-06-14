import sys
import os

print("Verifying imports for Tawreed...")
try:
    from core import db, ai, excel
    print("Core imports: OK")
    from gui.styles import MAIN_WINDOW_STYLE
    print("Styles imports: OK")
    from gui.worker import BOQProcessor
    print("Worker imports: OK")
    from gui.main_window import MainWindow
    print("MainWindow imports: OK")
    from gui.pages.workspace_page import WorkspacePage
    from gui.pages.history_page import HistoryPage
    from gui.pages.settings_page import SettingsPage
    from gui.pages.about_page import AboutPage
    print("Page imports: OK")
    import main
    print("Main module import: OK")
    print("All imports verified successfully!")
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
