@echo off
REM Double-click to start the lemon camera receiver. Close the window to stop it.
title Lemon camera receiver
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 lemon_receiver.py
) else (
  python lemon_receiver.py
)
echo.
echo The receiver has stopped.
echo If it says Python was not found, see SETUP.md step 1.
pause
