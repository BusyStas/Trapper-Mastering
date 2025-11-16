@echo off
REM _run.bat - Start the Trapper-Mastering 2D GUI using the repository venv
REM This script prints output and waits at the end so the window doesn't immediately close.

echo Starting Trapper-Mastering GUI...
set EXITCODE=0

if exist ".venv\Scripts\python.exe" (
    echo Using .venv\Scripts\python.exe
    call .venv\Scripts\python.exe gui_app.py %*
    set EXITCODE=%ERRORLEVEL%
) else (
    echo Virtual environment not found. Attempting to run with system python.
    call python gui_app.py %*
    set EXITCODE=%ERRORLEVEL%
)

echo.
if %EXITCODE% NEQ 0 (
    echo Program exited with code %EXITCODE%.
    echo If this is a ModuleNotFoundError for pygame, run _setup.bat to install dependencies.
) else (
    echo Program exited normally.
)

echo.
echo Press any key to close this window...
pause >nul
exit /b %EXITCODE%