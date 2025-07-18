@echo off
REM Log Viewer Launcher
REM Simple batch file to launch the Log Viewer executable

echo Starting Log Viewer...
echo.

REM Look for LogViewer executable with version number
for %%f in (LogViewer*.exe) do (
    if exist "%%f" (
        echo Found Log Viewer: %%f
        start "" "%%f"
        echo Log Viewer started successfully!
        exit /b 0
    )
)

REM If no versioned executable found, try the old naming
if exist "LogViewer.exe" (
    echo Found Log Viewer: LogViewer.exe
    start "" "LogViewer.exe"
    echo Log Viewer started successfully!
    exit /b 0
)

REM No executable found
echo ERROR: LogViewer executable not found in the current directory
echo Please make sure this batch file is in the same folder as LogViewer-{VERSION}.exe
pause
exit /b 1 