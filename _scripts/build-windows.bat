@echo off
REM ---------------------------------------------------------------------------
REM Tawreed — reproducible Windows build.
REM
REM Usage:
REM     .venv\Scripts\python -m pip install -e .[dev]
REM     _scripts\build-windows.bat
REM
REM Output: dist\Tawreed\Tawreed.exe (onedir).
REM ---------------------------------------------------------------------------

setlocal

REM Resolve the project root (parent of this script) so the script
REM works regardless of the caller's cwd.
pushd "%~dp0\.."

echo [build] cleaning previous build outputs...
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist

echo [build] running PyInstaller...
.venv\Scripts\pyinstaller tawreed.spec

if errorlevel 1 (
    echo [build] PyInstaller failed.
    popd
    exit /b 1
)

echo.
echo [build] success.
echo [build] executable: dist\Tawreed\Tawreed.exe
echo [build] folder:      dist\Tawreed\
echo.

popd
endlocal
