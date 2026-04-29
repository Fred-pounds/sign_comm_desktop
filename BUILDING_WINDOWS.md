# Building The Windows EXE

Build on a Windows machine from the project root:

```bat
build_windows.bat
```

That script installs the Python dependencies, installs `pyinstaller`, and builds from `signcomm.spec`.

The packaged app will be created at:

```text
dist\SignComm\SignComm.exe
```

## Required runtime files

These folders must exist before building:

- `models\`
- `assets\`

The spec file bundles them automatically when present.

## What changed for PyInstaller

The app now resolves resources through `app.paths.resource_path(...)`, which works in both cases:

- normal source checkout
- PyInstaller bundle via `sys._MEIPASS`

## Optional cleanup

To remove previous build artifacts before rebuilding:

```bat
rmdir /s /q build
rmdir /s /q dist
del /q signcomm.spec
```
