@echo off
setlocal

cd /d "%~dp0"

py -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

py -m pip install pyinstaller
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean signcomm.spec
