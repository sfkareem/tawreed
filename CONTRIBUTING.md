# Contributing

Thanks for your interest in Tawreed. The project is small and the
contribution model is intentionally simple.

## Setup

```bash
git clone https://github.com/sfkareem/tawreed
cd tawreed
python -m venv .venv
. .venv/Scripts/activate      # Windows
# . .venv/bin/activate        # macOS / Linux
pip install -e ".[dev]"
```

## Run

```bash
python main.py
```

## Test

```bash
pytest -q
```

To run the optional end-to-end regression test against a real BOQ:

```bash
TAWREED_TEST_BOQ="C:/path/to/a/real/boq.xlsx" pytest -q
```

## Pull requests

- One change per PR. Split unrelated changes into separate PRs.
- Branch from `master` with a descriptive name:
  `feat/...`, `fix/...`, `chore/...`, `docs/...`, `test/...`.
- Squash-merge to `master` with a descriptive commit message
  (this repo uses `gh pr merge --squash --delete-branch`).
- All PRs run the CI matrix (Ubuntu + Windows, Python 3.10/3.11/3.12)
  before they can be merged.
- Add a test for any behaviour change. Bug fixes should include a
  regression test that fails on `master` and passes on the branch.

## Coding style

- Python 3.10+. No walrus abuse, no match/case where a plain `if` is
  clearer. Use type hints on public functions.
- Logging via `logging.getLogger(__name__)`, never `print()`.
- No new top-level `print()` statements. If you need a startup
  message before logging is configured, use `sys.stderr.write()`.
- Never commit API keys, tokens, or any secret. The pre-commit
  hooks (`.pre-commit-config.yaml`) block commits that contain
  known-secret patterns.

## Project layout

See [README.md](README.md#project-structure) for the full tree. In
short: backend code in `core/`, Qt code in `gui/`, tests in `tests/`,
console entry in `tawreed_app/`.

## Release process

1. Cut a feature freeze branch.
2. Bump the version in `pyproject.toml` and `tawreed_app/__init__.py`
   (the splash imports the version from the latter, so they should
   never drift).
3. Tag `vX.Y.Z` and push — `.github/workflows/release.yml` builds
   Windows / macOS / Linux artifacts and attaches them to the
   GitHub release.
4. Edit the GitHub release notes from the auto-generated draft.

## Questions?

Open an issue or email kareem@kareemsafwat.com.
