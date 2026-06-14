# Tawreed — dev workflow.
#
# `just` is a single-binary command runner (https://just.systems/).
# It's like Make, but the recipes are plain shell with no
# surprising tab/space semantics, and the binary is a 2 MB static
# download on every platform.
#
# Install once:
#     cargo install just
# Or download a release binary from https://github.com/casey/just/releases
#
# Then from the project root:
#     just                  # list all recipes
#     just dev              # run the app
#     just test             # run the test suite
#     just lint             # ruff check
#     just format           # ruff format
#     just build            # pyinstaller onedir
#
# `just` is a single-user tool, not in pyproject.toml. The
# fallback for anyone who doesn't have it installed is the
# direct commands in each recipe (e.g. `pytest -q` instead of
# `just test`).

set dotenv-load := false
set shell := ["bash", "-cu"]

# ----- Meta ----------------------------------------------------------------

# List every recipe.
default:
    @just --list

# ----- Dev -----------------------------------------------------------------

# Run the desktop app from source.
dev:
    ./.venv/Scripts/python.exe main.py

# Run the test suite (fast mode — opt-in REAL_BOQ tests are skipped).
test:
    ./.venv-test/Scripts/python.exe -m pytest -q

# Run ONLY the slow / opt-in tests (requires TAWREED_TEST_BOQ set).
test-slow:
    ./.venv-test/Scripts/python.exe -m pytest -q -m slow

# Run a single test file or test by id.
test-one pattern:
    ./.venv-test/Scripts/python.exe -m pytest -q {{ pattern }}

# ----- Lint + format -------------------------------------------------------

# Run ruff (lint). Use `just format` to auto-fix.
lint:
    ./.venv-test/Scripts/python.exe -m ruff check .

# Auto-fix lint issues.
lint-fix:
    ./.venv-test/Scripts/python.exe -m ruff check --fix .

# Format with ruff format.
format:
    ./.venv-test/Scripts/python.exe -m ruff format .

# Run pre-commit against the whole repo.
pre-commit:
    pre-commit run --all-files

# ----- Build ---------------------------------------------------------------

# PyInstaller onedir build. Output: dist/Tawreed/.
build:
    ./.venv/Scripts/pyinstaller tawreed.spec

# Clean build artefacts.
clean:
    rm -rf build/ dist/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ----- State ---------------------------------------------------------------

# Wipe the per-user state (~/.tawreed/). Destructive — will
# delete the user's history, outputs, and config. Asks for
# confirmation.
reset-state:
    @echo "This will delete: $HOME/.tawreed/"
    @read -p "Type RESET to continue: " ans && [ "$$ans" = "RESET" ] && rm -rf "$HOME/.tawreed" && echo "Done." || echo "Aborted."

# Open the per-user state directory in the system file manager.
open-state:
    @if [ -d "$HOME/.tawreed" ]; then explorer "$HOME/.tawreed" 2>/dev/null || open "$HOME/.tawreed" 2>/dev/null || xdg-open "$HOME/.tawreed" 2>/dev/null; else echo "$HOME/.tawreed does not exist yet. Run the app once to create it."; fi

# Tail the log file (Ctrl-C to exit).
tail-log:
    @if [ -f "$HOME/.tawreed/logs/tawreed.log" ]; then tail -F "$HOME/.tawreed/logs/tawreed.log"; else echo "No log file at $HOME/.tawreed/logs/tawreed.log yet."; fi
