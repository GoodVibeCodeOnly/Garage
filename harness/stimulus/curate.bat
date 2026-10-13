@echo off
REM Olorin board curation -- double-click to run the nightly pass in a visible window.
REM Watch the first live run before trusting it unattended.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0curate.ps1" -Force
REM -Force: a double-click always runs a pass. The 6 AM task runs without it and
REM skips a night when nothing has landed on the board (board_pending.py).
echo.
echo === curation finished -- review above, then close this window ===
pause
