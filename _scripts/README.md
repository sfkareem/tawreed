# Build & ops scripts

Helper scripts for building, packaging, and operating Tawreed.

- `build-windows.bat` — runs PyInstaller with `tawreed.spec`,
  producing `dist\Tawreed\Tawreed.exe` (onedir).

All scripts assume they're run from the project root with the
`.venv` virtualenv active. Each script is self-contained and
re-runnable; they clean their own previous outputs.
