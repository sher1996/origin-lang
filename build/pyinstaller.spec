# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
std_dir = project_root / "std"

# Collect all .ori files from std directory
std_files = []
if std_dir.exists():
    for ori_file in std_dir.glob("*.ori"):
        std_files.append((str(ori_file), f"origin_std/{ori_file.name}"))

# Add the logo if it exists
logo_file = project_root / "Origin logo.png"
icon_file = None
if logo_file.exists():
    # For Windows, we'll need to convert PNG to ICO
    if sys.platform == "win32":
        icon_file = str(logo_file)  # PyInstaller will handle conversion
    else:
        icon_file = str(logo_file)

a = Analysis(
    [str(src_dir / "cli.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=std_files,
    hiddenimports=[
        "src.origin.evaluator",
        "src.origin.parser.ast_nodes",
        "src.origin.parser.optimizations",
        "src.origin.pkgmgr",
        "src.origin.registry",
        "src.origin.net",
        "src.origin.errors",
        "src.origin.recorder",
        "src.origin.replayer",
        "src.origin.replay_shell",
        "src.origin.publish",
        "src.origin.audit",
        "src.origin.utils",
        "src.origin.lock",
        "src.origin.snapshot",
        "src.origin.archive",
        "src.origin.diff",
        "src.origin.semver",
        "src.origin.builtins.json",
        "src.transform.blocks_to_ast",
        "src.transform.project_zip",
        "lexer",
        "parser",
        "runtime",
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="origin",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
) 