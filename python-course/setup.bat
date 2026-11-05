@echo off
REM One-time setup. Double-click me. Safe to run again any time.
cd /d "%~dp0"
echo.
echo ============================================================
echo   Setting up the Python course (one time, takes 1-3 minutes)
echo ============================================================
echo.

set "PY="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY goto nopython

echo Found Python:
%PY% --version
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Creating a private Python environment in the .venv folder...
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)

echo Installing the libraries the course uses ^(pandas, numpy, matplotlib, scipy, pytest, requests^)...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 goto failed

".venv\Scripts\python.exe" -c "import pandas, numpy, matplotlib, scipy, pytest, requests; print('All libraries import fine.')"
if errorlevel 1 goto failed

echo.
echo Setup complete. From now on, double-click course.bat to use the course.
goto end

:nopython
echo Python was not found on this computer.
echo.
echo   1. Go to https://www.python.org/downloads/ and click the big yellow
echo      "Download Python" button.
echo   2. Run the installer. On the FIRST screen, tick the box
echo      "Add python.exe to PATH", then click "Install Now".
echo   3. When it finishes, double-click this setup.bat again.
echo.
echo See SETUP.md for screenshots-in-words of each step.
goto end

:failed
echo.
echo Something went wrong during setup. Scroll up for the first red/error line.
echo The most common causes and fixes are listed in SETUP.md under "If setup fails".

:end
echo.
if not "%~1"=="nopause" pause
