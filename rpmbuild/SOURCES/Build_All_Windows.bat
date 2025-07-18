@echo off
REM Comprehensive Windows Build Script
REM Builds both executable and installer
REM Author: tmichett@redhat.com

echo ============================================
echo Log Viewer - Complete Windows Build Process
echo ============================================

REM Get the directory where this script is located
cd /d "%~dp0"
echo Script directory: %CD%

REM Parse command line arguments
set SKIP_TESTS=false
set CLEAN_BUILD=false
set BUILD_INSTALLER=true

:parse_args
if "%1"=="--skip-tests" (
    set SKIP_TESTS=true
    shift
    goto parse_args
)
if "%1"=="--clean" (
    set CLEAN_BUILD=true
    shift
    goto parse_args
)
if "%1"=="--no-installer" (
    set BUILD_INSTALLER=false
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo Options:
    echo   --skip-tests     Skip application tests
    echo   --clean          Clean build directories before building
    echo   --no-installer   Skip installer creation
    echo   --help           Show this help message
    pause
    exit /b 0
)
if "%1" neq "" (
    shift
    goto parse_args
)

REM Step 1: Build the executable
echo.
echo Step 1: Building Windows Executable...
call Build_App_Windows.bat
if %errorlevel% neq 0 (
    echo Error: Executable build failed
    pause
    exit /b 1
)

REM Step 2: Test the executable (if not skipped)
if "%SKIP_TESTS%"=="false" (
    echo.
    echo Step 2: Testing executable...
    if exist "LogViewer-%VERSION%.exe" (
        echo     Testing executable launch...
        start /wait /b LogViewer-%VERSION%.exe --help
        if %errorlevel% neq 0 (
            echo     Warning: Executable test failed
        ) else (
            echo     ✓ Executable test passed
        )
    ) else (
        echo     Error: LogViewer-%VERSION%.exe not found
        pause
        exit /b 1
    )
) else (
    echo Step 2: Skipping tests (--skip-tests specified)
)

REM Step 3: Create installer (if not skipped)
if "%BUILD_INSTALLER%"=="true" (
    echo.
    echo Step 3: Creating Windows installer...
    
    REM Check if Inno Setup is available
    where iscc >nul 2>&1
    if %errorlevel% neq 0 (
        echo Warning: Inno Setup compiler (iscc) not found in PATH
        echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
        echo Skipping installer creation...
    ) else (
        echo     Compiling installer with Inno Setup...
        iscc LogViewer_Installer.iss
        if %errorlevel% neq 0 (
            echo     Error: Installer compilation failed
            pause
            exit /b 1
        ) else (
            echo     ✓ Installer created successfully
            if exist "installer\LogViewer-3.0.0-Setup.exe" (
                echo     Installer location: %CD%\installer\LogViewer-3.0.0-Setup.exe
                
                REM Get installer size
                for %%A in ("installer\LogViewer-3.0.0-Setup.exe") do (
                    echo     Installer size: %%~zA bytes
                )
            )
        )
    )
) else (
    echo Step 3: Skipping installer creation (--no-installer specified)
)

REM Step 4: Summary
echo.
echo ============================================
echo Build Summary
echo ============================================
if exist "LogViewer-%VERSION%.exe" (
    echo ✓ Executable: LogViewer-%VERSION%.exe
    for %%A in ("LogViewer-%VERSION%.exe") do (
        echo   Size: %%~zA bytes
    )
) else (
    echo ✗ Executable: Not found
)

if exist "installer\LogViewer-3.0.0-Setup.exe" (
    echo ✓ Installer: installer\LogViewer-3.0.0-Setup.exe
    for %%A in ("installer\LogViewer-3.0.0-Setup.exe") do (
        echo   Size: %%~zA bytes
    )
) else (
    echo ✓ Installer: Not created (or failed)
)

echo.
echo Build process completed successfully!
echo.
echo You can now:
echo 1. Run LogViewer-%VERSION%.exe directly
echo 2. Install using installer\LogViewer-%VERSION%-Setup.exe
echo 3. Distribute the installer to other Windows computers
echo.
pause 