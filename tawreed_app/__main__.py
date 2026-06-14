"""Entry point for ``python -m tawreed``.

Delegates to ``main._run()`` in the project root. Kept as a thin
shim so we don't duplicate the launch logic.
"""

import sys

from main import _run

if __name__ == "__main__":
    sys.exit(_run())
