@echo off
REM _setup.bat - Create virtualenv (if missing) and install dependencies for Trapper-Mastering
SETLOCAL
echo ----------------------------------------
echo Trapper-Mastering - Setup
echo ----------------------------------------

REM Create venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Ensure Python is installed and in PATH.
        pause
        exit /b 1
    )
) else (
    echo Using existing virtual environment at .venv
)

echo Upgrading pip, setuptools, wheel in venv...
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

echo Installing requirements from requirements.txt (if present)...
if exist requirements.txt (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo requirements.txt not found; installing pygame as fallback...
    .venv\Scripts\python.exe -m pip install pygame
)

if errorlevel 1 (
    echo.
    echo Some packages failed to install. Typical issues:
    echo - Pygame may not have prebuilt wheels for very new Python versions (e.g., 3.14).
    echo - If installation fails with build errors, install Python 3.10 or 3.11 and recreate the venv.
    echo.
    echo Suggested next steps:
    echo 1) Install Python 3.11 from https://www.python.org/downloads/
    echo 2) Remove the venv folder: rmdir /s /q .venv
    echo 3) Re-run this script: _setup.bat
    pause
) else (
    echo Setup completed successfully.
)
ENDLOCAL
pause
