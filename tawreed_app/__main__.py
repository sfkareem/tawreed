"""Entry point for ``python -m tawreed``.

Delegates to ``main._run()`` in the project root. Kept as a thin
shim so we don't duplicate the launch logic.
"""
from main import _run
import sys

if __name__ == "__main__":
    sys.exit(_run())
