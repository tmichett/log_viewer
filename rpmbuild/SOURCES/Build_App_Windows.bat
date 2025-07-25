@echo off
REM Script to Build Windows Executable
REM Author: travis@michettetech.com

REM Read version from Build_Version file
for /f "tokens=2 delims==" %%a in ('findstr "VERSION=" Build_Version 2^>nul') do set VERSION=%%a
if "%VERSION%"=="" set VERSION=3.0.0

echo ============================================
echo Log Viewer - Windows Build Process
echo Version: %VERSION%
echo ============================================

REM Get the directory where this script is located
cd /d "%~dp0"
echo Script directory: %CD%

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

REM Clean up any existing build artifacts
echo Cleaning up previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "LogViewer*.exe" del /f /q "LogViewer*.exe"
if exist "log_viewer_venv" rmdir /s /q "log_viewer_venv"

REM Create virtual environment
echo Creating virtual environment...
python -m venv log_viewer_venv

REM Activate virtual environment
echo Activating virtual environment...
call log_viewer_venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Install PyInstaller
echo Installing PyInstaller...
pip install PyInstaller

REM Generate updated version_info.txt
echo Generating version info for version %VERSION%...
python generate_version_info.py

REM Update Inno Setup installer script with current version
echo Updating Inno Setup installer script for version %VERSION%...
python update_inno_version.py

REM Build the executable
echo Building Windows executable with version %VERSION%...
pyinstaller --noconfirm log_viewer_windows.spec

REM Check if build was successful
if exist "dist\LogViewer-%VERSION%.exe" (
    echo Copying executable to current directory...
    copy "dist\LogViewer-%VERSION%.exe" "LogViewer-%VERSION%.exe"
    
    echo.
    echo Build completed successfully!
    echo Executable location: %CD%\LogViewer-%VERSION%.exe
    
    REM Get file size
    for %%A in ("LogViewer-%VERSION%.exe") do (
        echo Executable size: %%~zA bytes
    )
    
    echo.
    echo You can now run LogViewer-%VERSION%.exe
) else (
    echo Error: Build failed - executable not found in dist/
    echo Expected: dist\LogViewer-%VERSION%.exe
    echo Contents of dist directory:
    dir dist\ /b
    pause
    exit /b 1
)

REM Deactivate virtual environment
deactivate

echo.
echo Build process completed!
pause 