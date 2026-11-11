@echo off
setlocal
cd /d "%~dp0"

py -3.11 -m venv .venv-packaging
if errorlevel 1 goto failed

call .venv-packaging\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto failed

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed

python -m PyInstaller --noconfirm --clean GradasiAgregat.spec
if errorlevel 1 goto failed

echo.
echo Build selesai: dist\GradasiAgregat\GradasiAgregat.exe
exit /b 0

:failed
echo.
echo Build gagal. Periksa pesan error di atas.
exit /b 1