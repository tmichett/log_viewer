# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Windows executable creation

import os
import sys
import platform

# Read version from Build_Version file
def get_version():
    try:
        with open('Build_Version', 'r') as f:
            for line in f:
                if line.startswith('VERSION='):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        print("Warning: Build_Version file not found, using default version")
    return "3.0.0"

VERSION = get_version()
print(f"Building Windows executable version: {VERSION}")

block_cipher = None

a = Analysis(
    ['log_viewer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yml', '.'),
        ('smallicon.png', '.'),
        ('test.log', '.'),
        ('../../README.md', '.'),
        ('README_Windows.md', '.'),
        ('Build_Version', '.'),
    ],
    hiddenimports=[],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'LogViewer-{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='smallicon.png',  # Windows will convert PNG to ICO automatically
    version='version_info.txt',  # Add version info
    uac_admin=False,  # Don't require admin privileges
    uac_uiaccess=False,
)

# Add Windows-specific metadata
exe.version = VERSION
exe.description = 'Log Viewer - A powerful log file viewer with ANSI color support'
exe.company = 'Michette Technologies'
exe.product = 'Log Viewer'
exe.copyright = '(C) 2024 Michette Technologies' 