@echo off
REM Double-click to make a time-lapse video from the photos so far.
title Lemon time-lapse
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 timelapse.py
) else (
  python timelapse.py
)
echo.
echo The video is in your Pictures\LemonTree folder (lemon-timelapse.avi).
echo If it says Python was not found, see SETUP.md step 1.
pause
