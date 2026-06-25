@echo off
title ETF Tournament
echo.
echo  ========================================
echo   ETF Tournament -- localhost:3002
echo  ========================================
echo.

cd /d "%~dp0"

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Could not create virtual environment.
        echo Make sure Python 3.11+ is installed and on your PATH.
        pause
        exit /b 1
    )
)

:: Install / update dependencies
echo [2/3] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: Open browser after a short delay
echo [3/3] Starting server at http://localhost:3002 ...
echo.
echo  NOTE: First run downloads price data for hundreds of ETFs.
echo  This takes a few minutes. The browser will show a progress bar.
echo.
start "" /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:3002"

:: Start Flask app
python app.py

pause
