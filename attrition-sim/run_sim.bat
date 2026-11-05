@echo off
REM Double-click to rerun the attrition simulator on Windows.
REM Needs Python 3.8+ (python.org installer, "Add to PATH" ticked). No other packages.
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
echo Running tests...
%PY% -m unittest discover -s tests
if errorlevel 1 (
  echo Tests failed - results not regenerated.
  pause
  exit /b 1
)
echo Running experiments (about 2-4 minutes)...
%PY% run_experiments.py %*
if errorlevel 1 (
  echo Experiment run failed.
  pause
  exit /b 1
)
echo.
echo Done. Results in "results\", charts in "charts\" (open the .svg files in a browser).
start "" "%~dp0charts"
pause
