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

### Option 3: Build from Source

1. **Install Inno Setup** (for installer creation):
   - Download from https://jrsoftware.org/isinfo.php
   - This is optional if you only want the executable

2. **Build everything**:
   ```cmd
   cd rpmbuild/SOURCES
   Build_All_Windows.bat
   ```

3. **Build only the executable**:
   ```cmd
   cd rpmbuild/SOURCES
   Build_App_Windows.bat
   ```

4. **Manual build with PyInstaller**:
   ```cmd
   cd rpmbuild/SOURCES
   pip install PyInstaller
   pyinstaller --noconfirm log_viewer_windows.spec
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

### File Associations
- The installer can associate .log, .out, and .txt files with Log Viewer
- Right-click any log file and select "Open with Log Viewer"

### Installer Features
- **Easy Installation**: Double-click the installer to install Log Viewer
- **Automatic Updates**: Installer handles upgrading existing installations
- **Desktop Shortcut**: Optional desktop shortcut creation
- **Start Menu Integration**: Adds Log Viewer to the Start Menu
- **Uninstall Support**: Full uninstall capability through Control Panel
- Works well with Windows display scaling settings

### Silent Installation (Unattended)
- **Silent Install**: `LogViewer-{VERSION}-Setup.exe /SILENT`
  - Shows progress dialog but requires no user interaction
  - Installs to default location with default settings
- **Very Silent Install**: `LogViewer-{VERSION}-Setup.exe /VERYSILENT`
  - Completely silent installation with no UI
  - Ideal for automated deployments
- **Silent with Custom Directory**: `LogViewer-{VERSION}-Setup.exe /VERYSILENT /DIR="C:\MyApps\LogViewer"`
  - Installs silently to specified directory
- **Complete Silent Options**: `LogViewer-{VERSION}-Setup.exe /VERYSILENT /NORESTART /SUPPRESSMSGBOXES /DIR="C:\Program Files\LogViewer"`
  - Recommended for enterprise deployments
  - No restarts, no message boxes, custom location

**Enterprise Deployment Notes**:
- Silent installations will NOT launch the application automatically
- Desktop shortcuts are created based on installer defaults
- File associations (.log, .out, .txt) are configured automatically
- Unattended uninstall: `"%ProgramFiles%\Log Viewer\unins000.exe" /SILENT`

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

- Version: 3.2.0
- Compatible with: Windows 10/11, Python 3.8+
- Last Updated: 2024 

## Code Signing for Microsoft Store Submission

### Microsoft Store Requirements
Microsoft Store Policy 10.2.9 requires all applications to be digitally signed with SHA256 or higher code signing certificates. This is mandatory for store submission.

### Obtaining a Code Signing Certificate

**Option 1: Microsoft Trusted Signing (Recommended)**
- Cloud-based signing service
- No hardware requirements
- ~$9/month
- Sign up at: https://learn.microsoft.com/en-us/azure/trusted-signing/

**Option 2: Traditional Code Signing Certificate**
- Purchase from Certificate Authority (DigiCert, Sectigo, etc.)
- $200-400/year
- EV certificates provide instant reputation

### Setting Up Code Signing for Build Process

1. **Set Environment Variables**:
   ```cmd
   # For certificate store signing
   set CODESIGN_IDENTITY="Michette Technologies"
   set CODESIGN_TIMESTAMP=http://timestamp.digicert.com
   
   # For PFX file signing
   set CODESIGN_PFX_FILE=C:\path\to\certificate.pfx
   set CODESIGN_PASSWORD=your_certificate_password
   set CODESIGN_TIMESTAMP=http://timestamp.digicert.com
   ```

2. **Build with Code Signing**:
   ```cmd
   cd rpmbuild/SOURCES
   Build_App_Windows.bat
   ```

3. **Verify Signature**:
   ```cmd
   signtool verify /pa /v LogViewer-{VERSION}.exe
   ```

### Code Signing Notes
- Timestamping is crucial - allows signatures to remain valid after certificate expiry
- Signed executables are required for Microsoft Store submission
- Build process automatically signs if environment variables are set
- Both PyInstaller signing and post-build SignTool signing are supported 