@echo off
REM _setup.bat - Create virtualenv (if missing) and install dependencies for Trapper-Mastering
SETLOCAL
echo ----------------------------------------
echo Trapper-Mastering - Setup
echo ----------------------------------------
echo.

REM Create venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Ensure Python is installed and in PATH.
        echo.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
) else (
    echo Using existing virtual environment at .venv
)

echo.
echo Upgrading pip, setuptools, wheel in venv...
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

echo.
echo Installing requirements from requirements.txt...
if exist requirements.txt (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo requirements.txt not found; installing pygame as fallback...
    .venv\Scripts\python.exe -m pip install pygame
)

echo.
if errorlevel 1 (
    echo Some packages failed to install. Typical issues:
    echo - Pygame may not have prebuilt wheels for very new Python versions (e.g., 3.14+).
    echo - If you see build errors, install Python 3.11 from https://www.python.org/downloads/
    echo.
    echo Suggested fix:
    echo 1) Install Python 3.11
    echo 2) Delete .venv: rmdir /s /q .venv
    echo 3) Re-run this script: _setup.bat
    echo.
) else (
    echo Setup completed successfully!
)

echo.
echo Press any key to close this window...
pause >nul
ENDLOCAL
