# Log Viewer - Windows Setup Guide

A powerful log file viewer with ANSI color support and configurable highlighting features, now optimized for Windows.

## System Requirements

- Windows 10 or later
- Python 3.8 or later
- Internet connection (for initial package installation)

## Quick Start

### Option 1: Using the Batch File (Recommended)

1. Double-click `log_viewer.bat` to run the application
2. The batch file will automatically:
   - Check if Python is installed
   - Install required packages if needed
   - Start the log viewer

### Option 2: Manual Installation

1. **Install Python** (if not already installed):
   - Download from https://www.python.org/
   - During installation, check "Add Python to PATH"

2. **Install required packages**:
   ```cmd
   pip install PyQt6 PyYAML
   ```

3. **Run the application**:
   ```cmd
   python log_viewer.py
   ```

## Windows-Specific Features

### Configuration Storage
- Configuration files are automatically stored in `%APPDATA%\LogViewer\`
- No need to worry about file permissions

### Font Optimization
- Automatically uses Windows-preferred monospace fonts:
  - Consolas (recommended)
  - Courier New
  - Lucida Console

### High DPI Support
- Automatically scales for high DPI displays
- Works well with Windows display scaling settings

### File Encoding
- Automatically detects file encoding (UTF-8, UTF-16, CP1252, Latin-1)
- Handles Windows-specific text formats

## Usage

### Opening Files
- **GUI**: Click "Open Log File" button
- **Command Line**: `python log_viewer.py C:\path\to\your\file.log`
- **Drag & Drop**: Drag a log file onto the batch file

### Supported File Types
- `.log` - Log files
- `.out` - Output files
- `.txt` - Text files
- Any text-based file

### Keyboard Shortcuts
- `Ctrl+O` - Open file
- `Ctrl+F` - Search
- `F3` - Find next
- `Shift+F3` - Find previous
- `Escape` - Clear search
- `Ctrl+Q` - Quit

### Configurable Highlighting
1. Click "Configure Highlighting" button
2. Add terms to highlight
3. Choose custom colors
4. Save configuration for future use

## Troubleshooting

### Python Not Found
- Reinstall Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### Package Installation Issues
- Open Command Prompt as Administrator
- Run: `pip install --upgrade pip`
- Then: `pip install PyQt6 PyYAML`

### Performance Issues
- For very large files (>100MB), the application loads in chunks
- Progress bar shows loading status
- Close other applications if memory usage is high

### Display Issues
- Right-click on the application → Properties → Compatibility
- Check "Override high DPI scaling behavior"
- Set scaling to "Application"

## File Association (Optional)

To associate log files with the viewer:

1. Right-click on a `.log` file
2. Select "Open with" → "Choose another app"
3. Browse to `log_viewer.bat`
4. Check "Always use this app to open .log files"

## Silent Installation (For IT Deployments)

If you obtained this software via the installer (`LogViewer-{VERSION}-Setup.exe`), it supports silent installation for enterprise deployments:

### Silent Installation Options
```cmd
# Basic silent installation (shows progress)
LogViewer-3.3.0-Setup.exe /SILENT

# Completely silent installation (no UI)
LogViewer-3.3.0-Setup.exe /VERYSILENT

# Silent with custom directory
LogViewer-3.3.0-Setup.exe /VERYSILENT /DIR="C:\Apps\LogViewer"

# Enterprise deployment (recommended)
LogViewer-3.3.0-Setup.exe /VERYSILENT /NORESTART /SUPPRESSMSGBOXES /DIR="C:\Program Files\LogViewer"
```

### Silent Uninstallation
```cmd
# Uninstall silently
"%ProgramFiles%\Log Viewer\unins000.exe" /SILENT
```

**Notes**:
- Silent installations automatically configure file associations
- No user interaction required during installation
- Application will not auto-launch after silent install
- Ideal for Group Policy deployment or system imaging

## Advanced Configuration

### Custom Config File
```cmd
python log_viewer.py --config "C:\path\to\custom_config.yml"
```

### Example Config File
```yaml
highlight_terms:
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING"
    color: "#ffff00"
  - term: "INFO"
    color: "#00ff00"
```

## Support

For issues or questions:
- Email: travis@michettetech.com
- Organization: Michette Technologies

## Version Information

- Version: 3.7.0
- Compatible with: Windows 10/11, Python 3.8+
- Last Updated: 2024 