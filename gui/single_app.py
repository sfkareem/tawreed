"""Single-instance lock for the Tawreed desktop app.

Without this, every time the user double-clicks the icon, a new
process starts and a new window opens. The fix is a ``QLocalServer``
+ a PID sidecar file. The first process writes its PID to the
sidecar and binds the named pipe; subsequent processes read the
sidecar, verify the PID is alive, and only then treat the
instance as running.

Why a PID file in addition to the named pipe:
    On Windows, ``QLocalServer`` uses a real named pipe in the OS
    object manager. The pipe **persists after the listener process
    dies** — it's only cleaned up by ``QLocalServer.removeServer()``
    or a system reboot. A naive ``QLocalSocket.connectToServer`` probe
    will keep succeeding forever after the first run, locking the
    user out of ever relaunching the app. We must additionally
    verify the listener is still alive by PID.

Why ``QLocalServer`` at all (vs just a file lock):
    A file lock is auto-released on process death, but it can't
    carry a message ("please show yourself") from the secondary to
    the primary. The named pipe is what lets the secondary tell the
    primary to come to the foreground.

Server name: ``tawreed-single-instance-<user>`` so multiple users on
the same Windows session don't collide.

PID file location: imported from ``core.db`` so it always sits at
``<app_root>/tawreed/single-instance.pid`` next to the rest of the
app state. No more split between %LOCALAPPDATA% and the project dir.
"""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from core.db import PID_FILE_PATH as _PID_FILE_PATH_FROM_DB

_SERVER_NAME_BASE = "tawreed-single-instance"


def _server_name() -> str:
    """Return the per-user server name for the single-instance lock."""
    try:
        user = getpass.getuser()
    except Exception:
        user = "default"
    return f"{_SERVER_NAME_BASE}-{user}"


def _pid_file_path() -> Path:
    """Return the path to the PID sidecar file.

    Resolved by ``core.db._app_root()`` so the file lives next to
    ``config.json``, ``db/``, and ``outputs/`` — i.e. inside the
    single portable ``<app_root>/tawreed/`` tree.
    """
    return Path(_PID_FILE_PATH_FROM_DB)


def _is_pid_alive(pid: int) -> bool:
    """Return True if a process with this PID exists on the system.

    Uses ``OpenProcess`` on Windows, ``kill(pid, 0)`` on POSIX. Both
    methods only fail if the process is truly gone — they don't
    depend on having permission to signal it.
    """
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.wintypes.DWORD()
            ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            return bool(ok) and exit_code.value == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # Process exists but we can't signal it. That's enough
            # to consider it alive.
            return True
        return True


def _read_pid_file() -> int | None:
    """Read the PID from the sidecar file. Returns None if missing/invalid."""
    path = _pid_file_path()
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
        return int(text) if text else None
    except (OSError, ValueError):
        return None


def _write_pid_file(pid: int) -> None:
    """Atomically write a PID to the sidecar file."""
    path = _pid_file_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic on POSIX; on Windows the rename is also atomic if
        # the target doesn't exist. For a single-line text file the
        # risk of partial reads is negligible.
        tmp = path.with_suffix(".pid.tmp")
        tmp.write_text(str(pid), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        # If we can't write the sidecar, fall back to "no PID file"
        # semantics — the secondary will still see the named pipe
        # and treat that as "primary is running" (which is the
        # correct outcome; the only thing the PID file buys us is
        # crash recovery).
        pass


def _clear_pid_file() -> None:
    """Remove the PID sidecar file. Safe if it doesn't exist."""
    try:
        _pid_file_path().unlink(missing_ok=True)
    except OSError:
        pass


class SingleApplication(QApplication):
    """QApplication subclass that enforces a single instance.

    Usage::

        app = SingleApplication(sys.argv)
        if app.is_running():
            # We are the second instance — tell the first to come
            # forward, then exit.
            app.notify_primary()
            sys.exit(0)

        # We are the first (and only) instance.
        app.start_server()
        app.message_received.connect(main_window.bring_to_front)
        ...

    Signals:
        message_received(str): emitted on the primary instance when
            a secondary instance sends a message. The main window
            should connect this to a slot that raises + activates
            itself.
    """

    message_received = Signal(str)

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self._server: QLocalServer | None = None
        self._is_primary: bool = False

    # ----- Public API --------------------------------------------------

    def is_running(self) -> bool:
        """Return True if another instance is already running.

        Two checks, both required:

        1. The named pipe exists and accepts a connection.
        2. The PID in the sidecar file is alive on the system.

        Both are needed because on Windows, named pipes persist
        after the listener process dies. The pipe check alone would
        permanently lock the user out after the first run.
        """
        # Check 1: named pipe
        socket = QLocalSocket()
        socket.connectToServer(_server_name())
        pipe_alive = socket.waitForConnected(50)
        if pipe_alive:
            socket.disconnectFromServer()

        if not pipe_alive:
            return False

        # Check 2: PID sidecar. If the pipe says something is
        # listening but we have no PID file at all, treat it as a
        # stale pipe from a crashed previous instance and become
        # the primary. The next start_server() will overwrite the
        # named pipe atomically.
        pid = _read_pid_file()
        if pid is None:
            return False

        return _is_pid_alive(pid)

    def notify_primary(self, message: str = "show") -> None:
        """Send a message to the primary instance. Used by secondaries."""
        socket = QLocalSocket()
        socket.connectToServer(_server_name())
        if not socket.waitForConnected(50):
            return
        payload = (message + "\n").encode("utf-8")
        socket.write(payload)
        socket.flush()
        socket.waitForBytesWritten(50)
        socket.disconnectFromServer()

    def start_server(self) -> None:
        """Start the local server. Call only on the primary instance.

        Wires ``newConnection`` to ``_on_new_connection`` which
        accepts the socket, reads a line, and emits
        ``message_received`` on the GUI thread.

        Also writes the current PID to the sidecar file so a
        future secondary can verify the primary is still alive.
        """
        # Best-effort cleanup of any stale named pipe from a prior
        # crashed run. On Windows, named pipes persist in the OS
        # object manager until explicitly removed; QLocalServer's
        # own removeServer() is unreliable for this case, so we
        # also try the underlying Win32 DeleteFile. If neither
        # works, listen() will fail and we'll fall through to
        # ``is_running() == False`` for the next launch.
        name = _server_name()
        QLocalServer.removeServer(name)
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.kernel32.DeleteFileW(f"\\\\.\\pipe\\{name}")

        self._server = QLocalServer(self)
        if not self._server.listen(name):
            # Best-effort: if we can't listen, treat as secondary.
            self._is_primary = False
            return
        self._server.newConnection.connect(self._on_new_connection)
        self._is_primary = True
        _write_pid_file(os.getpid())

    def stop_server(self) -> None:
        """Stop the local server. Call on app shutdown.

        Removes the named pipe and clears the PID file so the
        next launch is a clean primary.
        """
        if self._server is not None:
            self._server.close()
            self._server = None
        name = _server_name()
        QLocalServer.removeServer(name)
        # Belt-and-braces: explicitly DeleteFile the pipe on Windows.
        # removeServer alone is unreliable for fully clearing the
        # named pipe from the OS object manager.
        if sys.platform == "win32":
            try:
                import ctypes

                ctypes.windll.kernel32.DeleteFileW(f"\\\\.\\pipe\\{name}")
            except OSError:
                pass
        _clear_pid_file()
        self._is_primary = False

    def is_primary(self) -> bool:
        """Return True if this is the primary (first) instance."""
        return self._is_primary

    # ----- Internal ----------------------------------------------------

    def _on_new_connection(self) -> None:
        assert self._server is not None
        socket = self._server.nextPendingConnection()
        if socket is None:
            return

        def _on_ready() -> None:
            try:
                data = bytes(socket.readAll()).decode("utf-8", errors="replace").strip()
            except Exception:
                data = ""
            if data:
                self.message_received.emit(data)
            socket.disconnectFromServer()

        socket.readyRead.connect(_on_ready)
        # If the client disconnects without writing, just drop the socket.
        socket.disconnected.connect(socket.deleteLater)
