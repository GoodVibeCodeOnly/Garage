@echo off
REM The main entry point. Double-click me.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run detected - running setup first.
  call setup.bat nopause
  if not exist ".venv\Scripts\python.exe" (
    pause
    exit /b 1
  )
)
".venv\Scripts\python.exe" tools\course.py
