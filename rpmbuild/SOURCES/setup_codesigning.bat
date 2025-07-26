@echo off
REM Code Signing Configuration for Log Viewer
REM Author: travis@michettetech.com
REM This script helps set up code signing environment for Microsoft Store submission

echo ============================================
echo Log Viewer - Code Signing Setup
echo ============================================

echo.
echo This script will help you configure code signing for Microsoft Store submission.
echo Microsoft Store Policy 10.2.9 requires SHA256 or higher code signing certificates.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ Warning: Not running as administrator
    echo   Some certificate store operations may fail
    echo   Consider running as administrator if you encounter issues
    echo.
)

REM Method selection
echo Select your code signing method:
echo 1. Certificate Store (recommended)
echo 2. PFX File
echo 3. Test current configuration
echo 4. Show help and exit
echo.
set /p method="Enter your choice (1-4): "

if "%method%"=="1" goto certificate_store
if "%method%"=="2" goto pfx_file
if "%method%"=="3" goto test_config
if "%method%"=="4" goto show_help
echo Invalid choice. Please run the script again.
pause
exit /b 1

:certificate_store
echo.
echo === Certificate Store Method ===
echo.
echo Available certificates in Current User store:
powershell -Command "Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.EnhancedKeyUsageList -like '*Code Signing*'} | Format-Table Subject, Thumbprint, NotAfter -AutoSize"

echo.
echo Available certificates in Local Machine store:
powershell -Command "Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object {$_.EnhancedKeyUsageList -like '*Code Signing*'} | Format-Table Subject, Thumbprint, NotAfter -AutoSize"

echo.
set /p cert_name="Enter the certificate subject name (e.g., 'Michette Technologies'): "
if "%cert_name%"=="" (
    echo Error: Certificate name cannot be empty
    pause
    exit /b 1
)

REM Set environment variables
set CODESIGN_IDENTITY=%cert_name%
set CODESIGN_TIMESTAMP=http://timestamp.digicert.com

echo.
echo Environment variables set:
echo CODESIGN_IDENTITY=%CODESIGN_IDENTITY%
echo CODESIGN_TIMESTAMP=%CODESIGN_TIMESTAMP%

goto test_signing

:pfx_file
echo.
echo === PFX File Method ===
echo.
set /p pfx_path="Enter the full path to your PFX file: "
if "%pfx_path%"=="" (
    echo Error: PFX path cannot be empty
    pause
    exit /b 1
)

if not exist "%pfx_path%" (
    echo Error: PFX file not found: %pfx_path%
    pause
    exit /b 1
)

set /p pfx_password="Enter PFX password (will not be displayed): "
if "%pfx_password%"=="" (
    echo Error: Password cannot be empty
    pause
    exit /b 1
)

REM Set environment variables
set CODESIGN_PFX_FILE=%pfx_path%
set CODESIGN_PASSWORD=%pfx_password%
set CODESIGN_TIMESTAMP=http://timestamp.digicert.com

echo.
echo Environment variables set:
echo CODESIGN_PFX_FILE=%CODESIGN_PFX_FILE%
echo CODESIGN_PASSWORD=***hidden***
echo CODESIGN_TIMESTAMP=%CODESIGN_TIMESTAMP%

goto test_signing

:test_config
echo.
echo === Testing Current Configuration ===
echo.
if defined CODESIGN_IDENTITY (
    echo ✓ CODESIGN_IDENTITY: %CODESIGN_IDENTITY%
) else if defined CODESIGN_PFX_FILE (
    echo ✓ CODESIGN_PFX_FILE: %CODESIGN_PFX_FILE%
    if exist "%CODESIGN_PFX_FILE%" (
        echo ✓ PFX file exists
    ) else (
        echo ✗ PFX file not found
    )
) else (
    echo ✗ No code signing configuration found
    echo   Run this script and choose option 1 or 2 to configure
    pause
    exit /b 1
)

if defined CODESIGN_TIMESTAMP (
    echo ✓ CODESIGN_TIMESTAMP: %CODESIGN_TIMESTAMP%
) else (
    echo ⚠ CODESIGN_TIMESTAMP not set, using default
    set CODESIGN_TIMESTAMP=http://timestamp.digicert.com
)

goto test_signing

:test_signing
echo.
echo === Testing Code Signing Capability ===
echo.

REM Check if signtool is available
where signtool >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ SignTool not found in PATH
    echo   Install Windows SDK or Visual Studio to get SignTool
    echo   Or add SignTool directory to PATH
    pause
    exit /b 1
) else (
    echo ✓ SignTool found
)

REM Test timestamp server connectivity
echo Testing timestamp server connectivity...
ping -n 1 timestamp.digicert.com >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Timestamp server accessible
) else (
    echo ⚠ Timestamp server connectivity issue
    echo   This may cause signing to fail
)

echo.
echo === Saving Configuration ===
echo.
echo Creating codesign_env.bat file for future use...

REM Create environment file
echo @echo off > codesign_env.bat
echo REM Code signing environment variables >> codesign_env.bat
echo REM Generated on %date% at %time% >> codesign_env.bat
echo. >> codesign_env.bat

if defined CODESIGN_IDENTITY (
    echo set CODESIGN_IDENTITY=%CODESIGN_IDENTITY% >> codesign_env.bat
)
if defined CODESIGN_PFX_FILE (
    echo set CODESIGN_PFX_FILE=%CODESIGN_PFX_FILE% >> codesign_env.bat
    echo set CODESIGN_PASSWORD=%CODESIGN_PASSWORD% >> codesign_env.bat
)
echo set CODESIGN_TIMESTAMP=%CODESIGN_TIMESTAMP% >> codesign_env.bat
echo. >> codesign_env.bat
echo echo Code signing environment loaded >> codesign_env.bat

echo ✓ Configuration saved to codesign_env.bat
echo   Use 'call codesign_env.bat' to load these settings in future sessions

echo.
echo === Next Steps ===
echo.
echo 1. Run: Build_App_Windows.bat
echo 2. The build will automatically sign the executable if configuration is correct
echo 3. Verify signature with: signtool verify /pa LogViewer-{VERSION}.exe
echo 4. Submit signed executable to Microsoft Store
echo.

set /p build_now="Would you like to build the application now? (y/n): "
if /i "%build_now%"=="y" (
    echo.
    echo Starting build process...
    call Build_App_Windows.bat
) else (
    echo.
    echo Configuration complete. Run Build_App_Windows.bat when ready.
)

goto end

:show_help
echo.
echo === Code Signing Help ===
echo.
echo This script helps configure code signing for Microsoft Store submission.
echo.
echo Certificate Options:
echo 1. Certificate Store - Certificate installed in Windows Certificate Store
echo 2. PFX File - Certificate stored in a .pfx/.p12 file
echo.
echo Requirements:
echo - Valid code signing certificate from trusted CA
echo - Windows SDK (for SignTool)
echo - Internet connection (for timestamping)
echo.
echo For more information, see CODE_SIGNING_GUIDE.md
echo.

:end
echo.
echo Script completed.
pause 