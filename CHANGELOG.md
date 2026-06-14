# Changelog

All notable changes to Tawreed will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-14

### Added
- Initial public release of the Python/PySide6 rewrite.
- Work-package categorisation of Arabic + English construction BOQ
  spreadsheets via large language models.
- Multi-provider LLM support: OpenAI, Anthropic Claude, Google
  Gemini (via the OpenAI-compat endpoint), and any OpenAI-compatible
  custom base URL.
- Calibri-formatted output Excel with `wrap_text`, currency-formatted
  Amounts (`=IFERROR(D*E,0)` formulas), frozen header row, dark
  slate headers, zebra stripes, and a 60-character cap on the
  description column width.
- Single-instance desktop app via `QLocalServer` + a PID file at
  `~/.tawreed/single-instance.pid`.
- Per-user state at `~/.tawreed/` (config, history, outputs, logs,
  PID file). One-shot migration of legacy state from
  `%LOCALAPPDATA%\Tawreed` and `<exe-dir>/tawreed` runs on first
  launch of the new version.
- Settings reset (clears config + history + outputs + window state).
- Streaming LLM responses with `__DONE__` sentinel protocol.
- Rotating file logger to `~/.tawreed/logs/tawreed.log` (1 MB × 3).
- PyInstaller onedir Windows / macOS / Linux build.
- 80+ pytest tests, ~3 s runtime.

### Security
- API keys are entered in the GUI Settings page and stored at
  `~/.tawreed/config.json` (plaintext). On shared machines, restrict
  access to that file. See `SECURITY.md` for the disclosure policy.

[Unreleased]: https://github.com/sfkareem/tawreed/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sfkareem/tawreed/releases/tag/v0.1.0
