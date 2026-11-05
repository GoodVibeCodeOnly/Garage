@echo off
REM Runs YOUR lesson 25 pipeline end to end and prints your memo summary.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.bat nopause
".venv\Scripts\python.exe" tools\course.py capstone
pause
