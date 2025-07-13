@echo off
REM Log Viewer Windows Batch Script
REM This script makes it easy to run the log viewer on Windows

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if the log_viewer.py file exists
if not exist "log_viewer.py" (
    echo log_viewer.py not found in the current directory
    echo Please make sure this batch file is in the same directory as log_viewer.py
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking for required packages...
python -c "import PyQt6, yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo Required packages not found. Installing...
    pip install PyQt6 PyYAML
    if %errorlevel% neq 0 (
        echo Failed to install required packages
        echo Please run: pip install PyQt6 PyYAML
        pause
        exit /b 1
    )
)

REM Run the log viewer with any command line arguments
if "%~1"=="" (
    echo Starting Log Viewer...
    python log_viewer.py
) else (
    echo Starting Log Viewer with file: %1
    python log_viewer.py "%~1"
)

REM Keep the window open if there was an error
if %errorlevel% neq 0 (
    pause
) 