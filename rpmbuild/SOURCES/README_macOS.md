# Log Viewer - macOS Setup Guide

A powerful log file viewer with ANSI color support and configurable highlighting features, optimized for macOS.

## System Requirements

- macOS 10.14 (Mojave) or later
- 64-bit Intel or Apple Silicon Mac
- 100MB RAM minimum
- 50MB free disk space

## Installation Methods

### Option 1: DMG Installation (Recommended)

1. Download the appropriate DMG file for your Mac:
   - **Intel Macs**: `LogViewer-3.2.0-macOS-x86_64.dmg`
- **Apple Silicon (M1/M2/M3)**: `LogViewer-3.2.0-macOS-arm64.dmg`
2. Double-click the DMG file to mount it
3. Drag "Log Viewer.app" to the Applications folder
4. Launch from Applications or Launchpad
5. On first launch, you may need to right-click and select "Open" to bypass Gatekeeper

**Note**: Both versions work on either architecture via Rosetta 2, but choose the native version for best performance.

### Option 2: Build from Source

1. **Install Python 3.11+**:
   ```bash
   brew install python@3.11
   ```

2. **Install dependencies**:
   ```bash
   pip3 install PyQt6 PyYAML
   ```

3. **Run the application**:
   ```bash
   python3 log_viewer.py
   ```

### Option 3: Build App Bundle

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd log_viewer/rpmbuild/SOURCES
   ```

2. **Build the app bundle**:
   ```bash
   # Build both architectures (recommended)
   ./Build_All_MacOS_Dual.sh
   
   # Or build specific architecture:
   ./Build_All_MacOS_Dual.sh --x86_64-only    # Intel only
   ./Build_All_MacOS_Dual.sh --arm64-only     # Apple Silicon only
   
   # Legacy single architecture build:
   ./Build_App_MacOS.sh
   ```

3. **Create DMG package**:
   ```bash
   # DMG creation is included in Build_All_MacOS_Dual.sh
   # Or create manually:
   ./Create_DMG_MacOS.sh          # Current architecture
   ./Create_DMG_MacOS_x86_64.sh   # Intel specific
   ./Create_DMG_MacOS_arm64.sh    # Apple Silicon specific
   ```

## macOS-Specific Features

### Dual Architecture Support
- **Intel x86_64**: Native performance on Intel-based Macs
- **Apple Silicon arm64**: Native performance on M1/M2/M3 Macs
- **Rosetta 2 Compatibility**: Either version runs on both architectures
- **Optimized Binaries**: Each architecture gets specifically compiled binaries

### Configuration Storage
- Configuration files are stored in `~/Library/Application Support/LogViewer/`
- Persistent settings across app launches
- Automatic directory creation

### Font Optimization
- Automatically uses macOS-preferred monospace fonts:
  - Monaco (recommended)
  - Menlo
  - Courier New

### Retina Display Support
- Optimized for high-resolution displays
- Crisp text rendering on Retina screens
- Automatic scaling support

### Native macOS Integration
- Proper app bundle with Info.plist
- Document type associations for .log, .out, .txt files
- macOS-style menus and shortcuts
- Supports dark mode themes

## Usage

### Opening Files
- **GUI**: Use Cmd+O or File → Open
- **Command Line**: `open -a "Log Viewer" /path/to/file.log`
- **Drag & Drop**: Drag files onto the app icon or window
- **Finder**: Right-click log files and select "Open With → Log Viewer"

### Supported File Types
- `.log` - Log files
- `.out` - Output files  
- `.txt` - Text files
- Any text-based file

### Keyboard Shortcuts
- `Cmd+O` - Open file
- `Cmd+F` - Search
- `F3` - Find next
- `Shift+F3` - Find previous
- `Escape` - Clear search
- `Cmd+Q` - Quit application
- `Cmd+,` - Preferences (when available)

### Configurable Highlighting
1. Click "Configure Highlighting" button
2. Add terms to highlight with custom colors
3. Save configurations for different log types
4. Use "Load Config" to switch between configurations

## Terminal Integration

### Command Line Usage
```bash
# Open a specific file
open -a "Log Viewer" /var/log/system.log

# Open with custom config
open -a "Log Viewer" --args --config ~/my-config.yml /path/to/file.log

# Launch app and let user choose file
open -a "Log Viewer"
```

### Shell Aliases
Add to your `~/.zshrc` or `~/.bash_profile`:
```bash
alias logview='open -a "Log Viewer"'
alias lv='open -a "Log Viewer"'
```

## Performance Tips

### For Large Files (>100MB)
- Files load in chunks - be patient during initial load
- Search is fast once the file is loaded
- Close other memory-intensive apps if needed

### Optimization Settings
- The app uses the Fusion style for better performance
- Automatic memory management for large files
- Efficient search indexing

## File Associations

### Set Log Viewer as Default
1. Right-click any `.log` file in Finder
2. Select "Get Info" (Cmd+I)
3. In "Open with" section, select "Log Viewer"
4. Click "Change All..." to apply to all .log files

### Supported MIME Types
- `text/plain`
- `text/x-log`
- `application/octet-stream` (for binary logs with text content)

## Troubleshooting

### App Won't Open
- **"App is damaged"**: Right-click app and select "Open"
- **Python not found**: Install Python 3.11+ via Homebrew
- **Permission denied**: Check file permissions: `chmod +x "Log Viewer.app"`

### Large Files
- Expected behavior: chunked loading with progress bar
- Memory usage is optimized for files up to several GB
- For extremely large files, consider using `tail` or `head` first

### Search Issues
- Ensure the file has finished loading (check progress bar)
- Search is case-insensitive by default
- Use specific terms for better performance

### Configuration Issues
- Check `~/Library/Application Support/LogViewer/config.yml`
- Verify YAML syntax is correct
- Try resetting by deleting the config directory

## Development

### Building from Source
```bash
# Install dependencies
pip3 install -r requirements.txt

# Update version if needed
echo "VERSION=3.2.0" > Build_Version

# Build both architectures (recommended)
./Build_All_MacOS_Dual.sh

# Output files (versioned):
# - LogViewer-{VERSION}-macOS-arm64.dmg (Apple Silicon)
# - LogViewer-{VERSION}-macOS-x86_64.dmg (Intel)

# Or build specific architecture
./Build_All_MacOS_Dual.sh --x86_64-only    # Intel only
./Build_All_MacOS_Dual.sh --arm64-only     # Apple Silicon only

# Legacy single architecture build
./Build_App_MacOS.sh    # Build app bundle
./Create_DMG_MacOS.sh   # Create DMG
```

### Code Signing (Optional)
For distribution, you may want to code sign the app:
```bash
codesign --force --deep --sign "Developer ID Application: Your Name" "Log Viewer.app"
```

### Notarization (Optional)
For App Store or notarized distribution:
```bash
# Create zip for notarization
ditto -c -k --sequesterRsrc --keepParent "Log Viewer.app" "Log Viewer.zip"

# Submit for notarization
xcrun notarytool submit "Log Viewer.zip" --keychain-profile "AC_PASSWORD" --wait
```

## Security

- **Safe**: Built from open-source Python code
- **No Network**: Application works completely offline
- **Sandboxed**: Can be run in macOS sandbox mode
- **Privacy**: No data collection or telemetry

## Support

For technical support, bug reports, or feature requests:
- **Email**: travis@michettetech.com
- **Organization**: Michette Technologies
- **License**: Proprietary

## Version History

### Version 3.2.0 (Current)
- **NEW**: Dual architecture support (Intel x86_64 + Apple Silicon arm64)
- **NEW**: Architecture-specific DMG files with -x86_64 and -arm64 suffixes
- **NEW**: Native performance optimization for each architecture
- **NEW**: Comprehensive build scripts for dual architecture development
- **NEW**: Centralized version management from Build_Version file
- **NEW**: Automatic version updates across all build processes

### Version 3.0.0
- Added macOS app bundle support
- Enhanced search with line highlighting
- Improved cross-platform compatibility
- Added DMG packaging
- Retina display optimization

---

Copyright © 2024 Michette Technologies. All rights reserved. 