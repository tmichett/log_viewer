# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for macOS app bundle creation - Intel x86_64

import os
import sys
import platform

# Read version from Build_Version file
def get_version():
    try:
        with open('Build_Version', 'r') as f:
            content = f.read().strip()
            for line in content.split('\n'):
                if line.startswith('VERSION='):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        print("Warning: Build_Version file not found, using default version")
    return "3.9.5"

VERSION = get_version()
print(f"Building version: {VERSION}")

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
    [],
    exclude_binaries=True,
    name='log_viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',  # Explicitly target Intel x86_64
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='log_viewer',
)

app = BUNDLE(
    coll,
    name='Log Viewer.app',
    icon='smallicon.png',  # Pillow will convert PNG to ICNS automatically
    bundle_identifier='com.michette.logviewer',
    version=VERSION,
    info_plist={
        'CFBundleName': 'Log Viewer',
        'CFBundleDisplayName': 'Log Viewer',
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'CFBundleIdentifier': 'com.michette.logviewer',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'LOGV',
        'CFBundleExecutable': 'log_viewer',
        'CFBundleIconFile': 'smallicon.png',
        'NSHumanReadableCopyright': 'Copyright © 2024 Michette Technologies. All rights reserved.',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': ['log', 'out', 'txt'],
                'CFBundleTypeMIMETypes': ['text/plain'],
                'CFBundleTypeRole': 'Viewer',
                'CFBundleTypeDescription': 'Log Files',
                'LSHandlerRank': 'Alternate'
            }
        ],
        'NSAppleScriptEnabled': False,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleInfoDictionaryVersion': '6.0',
        'LSBackgroundOnly': False,
        'LSUIElement': False,
    },
) 