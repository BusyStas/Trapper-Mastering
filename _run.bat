@echo off
REM _run.bat - Start the Trapper-Mastering 2D GUI using the repository venv if available
SETLOCAL
echo Starting Trapper-Mastering GUI...
if exist ".venv\Scripts\python.exe" (
    echo Using .venv\Scripts\python.exe
    .venv\Scripts\python.exe gui_app.py %*
) else (
    echo Virtual environment not found. Attempting to run with system python.
    python gui_app.py %*
)
ENDLOCAL
