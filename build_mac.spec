# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 - Mac 版本
YouTube 影片下載器
"""

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'yt_dlp',
        'imageio_ffmpeg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YouTube下載器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Mac 需要這個
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Mac App Bundle
app = BUNDLE(
    exe,
    name='YouTube下載器.app',
    icon=None,
    bundle_identifier='com.ytdownloader.app',
    info_plist={
        'CFBundleName': 'YouTube下載器',
        'CFBundleDisplayName': 'YouTube下載器',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
)

