@echo off
REM Oddsify Props - MLB | Windows Setup & Run Script
REM This file sets up and launches the app on Windows

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════
echo         ODDSIFY PROPS - MLB  ^|  Windows Setup
echo ════════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if venv exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create venv
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
    echo.
)

REM Activate venv
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate venv
    pause
    exit /b 1
)
echo ✅ Activated
echo.

REM Install requirements
if exist "requirements.txt" (
    echo 📥 Installing packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install packages
        pause
        exit /b 1
    )
    echo ✅ Packages installed
    echo.
)

REM Run the app
echo 🚀 Launching Oddsify Props...
echo.
python main.py

REM Keep window open if app crashes
if errorlevel 1 (
    echo.
    echo ❌ App crashed. See error above.
    pause
)

exit /b 0
