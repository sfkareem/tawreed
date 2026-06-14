"""Tawreed — entry point.

Two ways to launch:

    python main.py            (development)
    python -m tawreed         (after `pip install -e .`)
    dist\\Tawreed\\Tawreed.exe  (PyInstaller onedir build)

The launcher does four things in order:
    1. Initialise the database (fast, <100ms).
    2. Build the SingleApplication. If another instance is running,
       signal it to come to the foreground and exit.
    3. Show the splash screen with "Loading...".
    4. Build the main window, show it, and finish the splash.

qasync is set up around the Qt event loop so the AI streaming
QThread worker can integrate cleanly.
"""
from __future__ import annotations

import asyncio
import sys

import qasync
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core import db
from core.logging_setup import setup_logging
from gui.main_window import MainWindow
from gui.single_app import SingleApplication
from gui import splash as splash_mod
from gui.assets import APP_ICON_PATH


def _run() -> int:
    # 0. Logging — must be the very first thing, so any failure in
    # db.init_db() or single-instance handshake ends up in the log
    # file even when the GUI never starts (frozen build with
    # console=False).
    setup_logging()

    # 1. Database (synchronous, fast — no splash needed for this).
    db.init_db()

    # 2. Single-instance check.
    app = SingleApplication(sys.argv)
    # Set QApplication identity before anything else that might
    # use QStandardPaths — otherwise paths resolve to
    # %LOCALAPPDATA%\python\... instead of %LOCALAPPDATA%\sfkareem\Tawreed\...
    from tawreed_app import __appname__, __version__
    app.setOrganizationName("sfkareem")
    app.setApplicationName(__appname__)
    app.setApplicationVersion(__version__)
    # Set the application icon globally. This is what actually
    # shows up in the title bar and taskbar at runtime — the
    # `icon=` arg in tawreed.spec only embeds the icon in the
    # Windows EXE resource section (file properties, Explorer).
    # Without this setWindowIcon call, Windows falls back to the
    # generic "unknown app" icon.
    app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    if app.is_running():
        # Another instance owns the window — ask it to come forward
        # and exit. We don't even need to build a window ourselves.
        app.notify_primary("show")
        return 0

    # 3. Splash. Visible from this point onward.
    splash = splash_mod.show()

    # 4. Main window — built behind the splash, then revealed.
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()
    splash.finish(window)

    # Wire the single-app signal so a future double-click focuses us.
    app.message_received.connect(window.bring_to_front)
    # Make sure the server is up — we already know we're primary
    # because is_running() returned False, but start_server is what
    # actually begins accepting new-connection attempts.
    app.start_server()

    try:
        with loop:
            loop.run_forever()
    finally:
        # Release the named pipe and the PID file so a future launch
        # is a clean primary, not a stale-secondary-recovery.
        app.stop_server()

    return 0


if __name__ == "__main__":
    sys.exit(_run())
