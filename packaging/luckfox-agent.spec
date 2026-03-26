# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules
import sys
from pathlib import Path

# Build paths relative to the spec file
spec_dir = Path('.').resolve()
agent_root = spec_dir.parent

# Include all submodules from agent package
hidden_imports = collect_submodules('agent') + [
    'uvicorn', 'fastapi', 'aiohttp', 'pydantic'
]

# We are building in one-dir mode so tools and img folders can sit alongside the exe
# The tools directory contains the external .exe and .dlls required
datas = [
    (str(agent_root / 'tools'), 'tools'),
]

a = Analysis(
    [str(agent_root / 'agent' / 'server.py')],
    pathex=[str(agent_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 1. Background Service Executable (No Console)
exe_silent = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='luckfox-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 2. Debug Executable (With Console)
exe_debug = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='luckfox-agent-debug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Bundle both executables into the target directory
coll = COLLECT(
    exe_silent,
    exe_debug,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='luckfox-agent',
)
