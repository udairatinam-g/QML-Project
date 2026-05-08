@echo off
REM One-click runner for QGCN PowerGrid demo (CPU-friendly)
REM Runs demo, baseline, presentation, writeup and opens outputs/deliverables

echo ------------------------------------------------------------
echo QGCN PowerGrid - One-Click Demo Runner
echo ------------------------------------------------------------

REM Find Python: prefer 'python', fallback to 'py -3'
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set PYCMD=py -3
) else (
    set PYCMD=python
)

setlocal enabledelayedexpansion

echo Using: %PYCMD%

echo Running demo (zero-epoch inference)...
%PYCMD% -u src\demo.py
if %ERRORLEVEL% NEQ 0 (
    echo Demo failed with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo Running baseline comparison...
%PYCMD% -u src\baseline_comparison.py
if %ERRORLEVEL% NEQ 0 (
    echo Baseline comparison failed with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)
echo Skipping presentation generation (user opted out).

echo Generating writeup document...
%PYCMD% -u scripts\create_project_writeup_doc.py
if %ERRORLEVEL% NEQ 0 (
    echo Writeup generation failed with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo Opening outputs and deliverables folders...
start "" "%CD%\outputs"
start "" "%CD%\deliverables"

echo All tasks completed. Press any key to close this window.
pause >nul
