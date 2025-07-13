# Log Viewer - macOS Setup Guide

A powerful log file viewer with ANSI color support and configurable highlighting features, optimized for macOS.

## System Requirements

- macOS 10.14 (Mojave) or later
- 64-bit Intel or Apple Silicon Mac
- 100MB RAM minimum
- 50MB free disk space

## Installation Methods

### Option 1: DMG Installation (Recommended)

1. Download the `LogViewer-3.0.0-macOS.dmg` file
2. Double-click the DMG file to mount it
3. Drag "Log Viewer.app" to the Applications folder
4. Launch from Applications or Launchpad
5. On first launch, you may need to right-click and select "Open" to bypass Gatekeeper

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
   ./Build_App_MacOS.sh
   ```

3. **Create DMG package**:
   ```bash
   ./Create_DMG_MacOS.sh
   ```

## macOS-Specific Features

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

# Build app bundle
./Build_App_MacOS.sh

# Create DMG
./Create_DMG_MacOS.sh
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
- **Email**: tmichett@redhat.com
- **Organization**: Michette Technologies
- **License**: Proprietary

## Version History

### Version 3.0.0 (Current)
- Added macOS app bundle support
- Enhanced search with line highlighting
- Improved cross-platform compatibility
- Added DMG packaging
- Retina display optimization

---

Copyright © 2024 Michette Technologies. All rights reserved. 