@echo off
REM Shortcut: check one lesson's exercises. Double-click me and type a lesson number.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.bat nopause
if not exist ".venv\Scripts\python.exe" (
  pause
  exit /b 1
)
set /p N=Which lesson number do you want to check? 
".venv\Scripts\python.exe" tools\course.py check %N%
echo.
pause
