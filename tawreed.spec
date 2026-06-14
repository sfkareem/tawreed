# -*- mode: python ; coding: utf-8 -*-
#
# Tawreed — PyInstaller spec, onedir build.
#
# Onedir (vs onefile) drops cold start from ~12s to ~1.5s because
# the bootloader no longer has to unpack a 80MB blob to %TEMP% on
# every launch. The trade-off is a folder instead of a single .exe
# (~250MB), which is the right choice for an internal tool.
#
# Build:
#     .venv\Scripts\pyinstaller tawreed.spec
#
# Output:
#     dist\Tawreed\Tawreed.exe          <- entry point
#     dist\Tawreed\*.dll, *.pyd, ...    <- runtime
#     dist\Tawreed\_internal\            <- Python + dependencies
#
# Ship:
#     Zip the whole dist\Tawreed\ folder. User unzips and runs
#     Tawreed.exe.

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Logo assets — APP_ICON_PATH (ICO) is used by QApplication.setWindowIcon
        # so the title bar / taskbar / Alt-Tab show the brand icon instead of
        # the generic Windows app icon. The PNG is used by the nav rail / splash.
        ('tawreed_logo.ico', '.'),
        ('tawreed_logo_transparent.png', '.'),
        # Theme files — loaded at runtime by gui.styles.load_stylesheet.
        ('gui/themes', 'gui/themes'),
    ],
    hiddenimports=[
        # Third-party
        'openpyxl',
        'openai',
        'qasync',
        # Project packages — PyInstaller's static analyser can miss
        # dynamically imported submodules.
        'gui',
        'gui.pages',
        'gui.pages.workspace_page',
        'gui.pages.history_page',
        'gui.pages.settings_page',
        'gui.pages.about_page',
        'gui.splash',
        'gui.single_app',
        'tawreed_app',
        # Optional LLM SDKs (no longer used — Anthropic is implemented
        # via raw httpx in core/ai.py; Google Gemini goes through the
        # OpenAI-compat endpoint, so no SDK is needed at runtime).
        # 'anthropic',
        # 'google.generativeai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Onedir: COLLECT bundles the EXE + all .dll/.pyd files into a
# single folder. The user runs the EXE inside that folder.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,        # binaries go in _internal/, not next to the EXE
    name='Tawreed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                # Release: no console window. Toggle to True when debugging the EXE bootstrap.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['tawreed_logo.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Tawreed',
)
