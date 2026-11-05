@echo off
REM Shortcut: show how many tests pass in every lesson.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.bat nopause
".venv\Scripts\python.exe" tools\course.py progress
pause
