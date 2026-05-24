# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('.venv/Scripts/msvcp140.dll', '.'),
        ('.venv/Scripts/msvcp140_1.dll', '.'),
        ('.venv/Scripts/msvcp140_2.dll', '.'),
        ('.venv/Scripts/vcruntime140.dll', '.'),
        ('.venv/Scripts/vcruntime140_1.dll', '.'),
        ('.venv/Scripts/vcruntime140_threads.dll', '.'),
    ],
    datas=[('gui', 'gui'), ('SKILL.md', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tawreed',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
