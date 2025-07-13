@echo off
REM Log Viewer Launcher
REM Simple batch file to launch the Log Viewer executable

echo Starting Log Viewer...
echo.

REM Check if the executable exists
if not exist "LogViewer.exe" (
    echo ERROR: LogViewer.exe not found in the current directory
    echo Please make sure this batch file is in the same folder as LogViewer.exe
    pause
    exit /b 1
)

REM Launch the Log Viewer
start "" "LogViewer.exe"

REM Optional: Uncomment the line below if you want the batch window to stay open
REM pause

echo Log Viewer started successfully! 