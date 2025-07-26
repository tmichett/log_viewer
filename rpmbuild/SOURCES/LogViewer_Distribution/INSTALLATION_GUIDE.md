# Log Viewer - Windows Executable Installation Guide

## 📦 What's Included

This package contains everything you need to run the Log Viewer application on Windows:

- **LogViewer.exe** - The main application (no Python required!)
- **config.yml** - Sample configuration file
- **test.log** - Sample log file for testing
- **README_Windows.md** - Detailed documentation
- **INSTALLATION_GUIDE.md** - This file

## 🚀 Quick Start

### 1. Simple Installation
1. Extract this folder to any location (e.g., `C:\Program Files\LogViewer\`)
2. Double-click `LogViewer.exe` to run the application
3. That's it! No Python or dependencies needed.

### 2. Test the Application
1. Run `LogViewer.exe`
2. Click "Open Log File" and select `test.log`
3. Try searching for "ERROR" or "INFO" to see highlighting

## 📋 System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **Memory**: 100MB RAM minimum, 256MB recommended
- **Storage**: 50MB free space
- **No Python installation required!**

## 🎯 Features

### File Support
- ✅ `.log` files
- ✅ `.out` files  
- ✅ `.txt` files
- ✅ Any text-based files

### Key Features
- 🔍 **Fast Search** - Find text instantly with highlighting
- 🎨 **Color Highlighting** - Configure custom colors for different terms
- 📁 **Large File Support** - Handles files up to several GB
- 🌙 **Dark Theme** - Easy on the eyes
- ⚡ **Performance Optimized** - Loads files in chunks for responsiveness

## 🛠 Usage

### Opening Files
- **Method 1**: Run `LogViewer.exe` then click "Open Log File"
- **Method 2**: Drag and drop a log file onto `LogViewer.exe`
- **Method 3**: Right-click a log file → "Open with" → Browse to `LogViewer.exe`

### Search & Navigation
- **Search**: Type in the search box and press Enter
- **Find Next**: Press F3 or click "Find Next"
- **Find Previous**: Press Shift+F3 or click "Find Previous"
- **Clear Search**: Press Escape

### Keyboard Shortcuts
- `Ctrl+O` - Open file
- `Ctrl+F` - Focus search box
- `F3` - Find next
- `Shift+F3` - Find previous
- `Escape` - Clear search
- `Ctrl+Q` - Quit application

### Configuration
1. Click "Configure Highlighting" to add custom highlight terms
2. Choose colors for different log levels (ERROR, WARNING, INFO, etc.)
3. Save configurations for reuse

## 🔧 Advanced Setup

### File Association (Optional)
To make `.log` files open automatically with LogViewer:

1. Right-click any `.log` file
2. Select "Open with" → "Choose another app"
3. Click "More apps" → "Look for another app on this PC"
4. Browse to `LogViewer.exe` and select it
5. Check "Always use this app to open .log files"
6. Click OK

### Desktop Shortcut
1. Right-click `LogViewer.exe`
2. Select "Create shortcut"
3. Drag the shortcut to your desktop
4. Rename it to "Log Viewer" if desired

### Start Menu Integration
1. Copy the entire `LogViewer_Distribution` folder to:
   `C:\Program Files\LogViewer\`
2. Right-click `LogViewer.exe` → "Pin to Start"

## 🤖 Automated/Silent Installation

### Using the Windows Installer (Recommended for IT Deployments)
If you have the installer version (`LogViewer-{VERSION}-Setup.exe`), you can deploy silently:

```cmd
# Basic silent installation
LogViewer-3.3.0-Setup.exe /SILENT

# Completely silent installation (no UI)
LogViewer-3.3.0-Setup.exe /VERYSILENT

# Silent with custom directory
LogViewer-3.3.0-Setup.exe /VERYSILENT /DIR="C:\Apps\LogViewer"

# Enterprise deployment (recommended)
LogViewer-3.3.0-Setup.exe /VERYSILENT /NORESTART /SUPPRESSMSGBOXES /DIR="C:\Program Files\LogViewer"
```

### Portable Deployment
For environments where you can't use installers:

1. **Network Deployment**: Copy the entire distribution folder to a shared location
2. **Script Deployment**: Use PowerShell or batch scripts to copy files
3. **USB/Portable**: Run directly from removable media

```powershell
# PowerShell deployment script example
$source = "\\server\share\LogViewer_Distribution"
$destination = "C:\Program Files\LogViewer"

if (!(Test-Path $destination)) {
    New-Item -ItemType Directory -Path $destination -Force
}

Copy-Item -Path "$source\*" -Destination $destination -Recurse -Force
Write-Host "LogViewer deployed to $destination"

# Create desktop shortcut
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Log Viewer.lnk")
$shortcut.TargetPath = "$destination\LogViewer.exe"
$shortcut.WorkingDirectory = $destination
$shortcut.Save()
```

### Silent Uninstallation
```cmd
# Uninstall silently (if installed via installer)
"%ProgramFiles%\Log Viewer\unins000.exe" /SILENT

# Complete silent uninstall
"%ProgramFiles%\Log Viewer\unins000.exe" /VERYSILENT /NORESTART
```

## 📊 Performance Tips

### For Large Files (>100MB)
- The application loads files in chunks - be patient during initial load
- Search is optimized and will be fast once the file is loaded
- Close other memory-intensive applications if needed

### For Better Performance
- Place frequently used log files on an SSD if available
- Keep the application folder on a fast drive
- Configure Windows to exclude the application folder from antivirus real-time scanning

## 🔒 Security

- **Safe**: This executable is created from Python source code using PyInstaller
- **No Internet Required**: Application works completely offline
- **No Registry Changes**: Application doesn't modify Windows registry
- **Portable**: Can be run from any location (USB drive, network share, etc.)

### Digital Signatures and Microsoft Store Compliance
This executable is digitally signed with a SHA256 code signing certificate to meet Microsoft Store Policy 10.2.9 requirements. You can verify the signature:

```cmd
# Verify digital signature
signtool verify /pa /v LogViewer.exe

# View certificate details
signtool verify /pa /v /all LogViewer.exe
```

**Certificate Information:**
- **Publisher**: Michette Technologies
- **Algorithm**: SHA256 or higher
- **Timestamp**: RFC 3161 timestamped for long-term validity
- **Trust Chain**: Chains to a trusted root certificate authority

**Why Digital Signing Matters:**
- **Authenticity**: Confirms the software comes from Michette Technologies
- **Integrity**: Ensures the executable hasn't been modified since signing
- **Trust**: Meets enterprise security policies and Microsoft Store requirements
- **Reputation**: Builds trust with Windows Defender SmartScreen

## 📝 Configuration Files

The application stores configuration in:
- **Windows**: `%APPDATA%\LogViewer\config.yml`
- **Portable**: You can also place `config.yml` in the same folder as the executable

### Sample Configuration
```yaml
highlight_terms:
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING"  
    color: "#ffff00"
  - term: "INFO"
    color: "#00ff00"
  - term: "DEBUG"
    color: "#0080ff"
```

## 🐛 Troubleshooting

### Application Won't Start
- **Check Windows Version**: Requires Windows 10 or later
- **Run as Administrator**: Right-click `LogViewer.exe` → "Run as administrator"
- **Antivirus**: Add the application folder to antivirus exclusions

### File Won't Open
- **Check File Size**: Very large files (>1GB) may take time to load
- **Check File Type**: Ensure it's a text-based file
- **File Permissions**: Ensure you have read access to the file

### Performance Issues
- **Close Other Apps**: Free up system memory
- **Check Disk Space**: Ensure sufficient free space
- **Restart Application**: Close and reopen if sluggish

### Display Issues
- **High DPI**: Right-click app → Properties → Compatibility → "Override high DPI scaling"
- **Font Issues**: The app automatically selects the best monospace font

## 📞 Support

For help or to report issues:
- **Email**: travis@michettetech.com
- **Organization**: Michette Technologies

## 📜 License & Version

- **Version**: 3.0.0
- **Build Date**: 2024
- **Platform**: Windows 10/11 (64-bit)
- **Built with**: Python 3.12, PyQt6, PyInstaller

## 🎉 Enjoy!

The Log Viewer is designed to make log analysis fast and efficient. Whether you're debugging applications, analyzing system logs, or reviewing output files, this tool will help you find what you need quickly.

**Happy Log Viewing!** 🔍📝 