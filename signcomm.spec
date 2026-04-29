from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH).resolve()

datas = []
for name in ("models", "assets"):
    source = project_root / name
    if source.exists():
        datas.append((str(source), name))

hiddenimports = []
for package_name in ("mediapipe", "ai_edge_litert", "pyttsx3.drivers"):
    hiddenimports.extend(collect_submodules(package_name))


a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SignComm",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SignComm",
)
