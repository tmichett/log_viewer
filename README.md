# Log Viewer Application

## Overview

Log Viewer is a powerful, cross-platform GUI application designed for viewing, searching, and analyzing log files. Built with PyQt6, it provides advanced features for handling large log files, ANSI color support, configurable text highlighting, and intuitive search capabilities.

## Features

### Core Functionality
- **Multi-format Support**: Handles `.log`, `.out`, `.txt`, and other text files
- **Large File Handling**: Optimized for files of any size with efficient memory management
- **ANSI Color Support**: Parses and displays ANSI escape sequences with proper colors
- **Asynchronous Loading**: Non-blocking file operations with real-time progress feedback

### Search & Navigation
- **Real-time Search**: Instant search with debounced input (100ms delay)
- **Bidirectional Navigation**: Find Next/Previous functionality
- **Entire Line Highlighting**: Highlights complete lines containing search terms
- **Smart Result Management**: Shows current match position and total count
- **Search Result Caching**: Efficient navigation through large result sets

### Text Highlighting System
- **Configurable Terms**: Add, edit, and remove highlight terms via GUI
- **Custom Colors**: Color picker for each highlight term
- **YAML Configuration**: Save and load highlight configurations
- **Multiple Config Support**: Load different configuration files for different log types

### User Interface
- **Modern Dark Theme**: Complete dark mode with custom styling
- **Adjustable Font Size**: Dynamic font size control (6-72pt range)
- **Responsive Layout**: Optimized for various screen sizes
- **Progress Feedback**: Visual progress indicators for long operations
- **Monospace Font**: Consistent character spacing for structured logs

### Performance Optimizations
- **Chunked File Loading**: Files loaded in 256KB chunks to prevent UI blocking
- **Background Threading**: Non-blocking operations using QThreadPool
- **Memory Management**: Efficient handling of large files without excessive memory usage
- **Debounced Search**: Prevents excessive operations during typing
- **Block Limits**: Prevents excessive memory usage with document block limits

## Installation

### Prerequisites
- Python 3.8 or higher
- Linux, macOS, or Windows operating system

### Dependencies
The application requires the following Python packages:
- PyQt6==6.4.2
- PyYAML==6.0.1
- ansi2html==1.9.2 (optional, for enhanced ANSI support)

### Installation Methods

#### Method 1: Platform-Specific Packages

##### Linux (RPM - Recommended for Red Hat/Fedora)
```bash
# Install the RPM package
sudo rpm -ivh LogViewer-3.1.0-0.rpm

# Launch the application
logviewer
```

##### macOS (DMG - Recommended)
```bash
# Download the appropriate DMG for your Mac:
# Intel Macs: LogViewer-3.1.0-macOS-x86_64.dmg
# Apple Silicon (M1/M2/M3): LogViewer-3.1.0-macOS-arm64.dmg

# Mount the DMG
open LogViewer-3.1.0-macOS-arm64.dmg  # or x86_64 version

# Drag "Log Viewer.app" to Applications folder
# Launch from Applications or Launchpad
```

##### Windows (EXE/Installer)
```bash
# Option 1: Download and run the installer
LogViewer-3.1.0-Setup.exe

# Option 2: Run the portable executable directly
LogViewer.exe
```

#### Method 2: Source Installation
```bash
# Clone the repository
git clone <repository-url>
cd log_viewer

# Install dependencies
pip install -r requirements.txt

# Run the application
python log_viewer.py
```

#### Method 3: Build from Source

##### Linux/General
```bash
# Build the standalone executable
cd rpmbuild/SOURCES
./Build_App.sh

# Run the built executable
./log_viewer
```

##### macOS
```bash
# Build macOS app bundle
cd rpmbuild/SOURCES
./Build_App_MacOS.sh

# Create DMG package
./Create_DMG_MacOS.sh

# Or build everything at once
./Build_All_MacOS.sh
```

##### Windows
```bash
# Use the existing Windows build process
cd rpmbuild/SOURCES
pyinstaller LogViewer.spec
```

## Usage

### Basic Usage

#### Opening Files
1. **GUI Method**: Click "Open Log File" button and select your file
2. **Command Line**: `log_viewer /path/to/logfile.log`
3. **Drag & Drop**: Drag log files into the application window

#### Searching
1. **Basic Search**: Type search term in the search box and press Enter
2. **Navigation**: Use "Find Next" and "Find Previous" buttons
3. **Case Sensitivity**: Search is case-insensitive by default

#### Font Size Adjustment
- Use the "+" and "-" buttons to adjust font size
- Range: 6pt to 72pt
- Changes apply immediately

### Advanced Features

#### Configurable Highlighting
1. Click "Configure Highlighting" button
2. Add highlight terms with custom colors
3. Edit existing terms or remove unwanted ones
4. Save configurations for reuse

#### Custom Configuration Files
1. Click "Load Config" to load different highlight configurations
2. Create project-specific or log-type-specific configurations
3. Share configurations across team members

#### Command Line Options
```bash
# Open specific file
log_viewer /path/to/file.log

# Use custom configuration
log_viewer --config /path/to/config.yml /path/to/file.log

# Show help
log_viewer --help
```

### Configuration Files

#### Default Configuration
The application looks for `config.yml` in the current directory. Example:
```yaml
highlight_terms:
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING"
    color: "#ffff00"
  - term: "INFO"
    color: "#00ff00"
  - "DEBUG"  # Uses default color
```

#### Configuration Structure
- **term**: The text to highlight
- **color**: Hex color code (optional, defaults to cornflower blue)
- **Simple format**: Just the term string for default highlighting

## Technical Details

### Architecture
- **Main Window**: QMainWindow with dark theme
- **Text Editor**: Optimized QPlainTextEdit for large files
- **Background Processing**: QThreadPool with custom workers
- **Highlighting**: Custom QSyntaxHighlighter implementation
- **ANSI Parser**: Custom parser for ANSI escape sequences

### Performance Characteristics
- **File Loading**: Chunked loading with 256KB chunks
- **Memory Usage**: Efficient with document block limits (100,000 blocks)
- **Search Performance**: Cached results for fast navigation
- **UI Responsiveness**: Non-blocking operations with progress feedback

### Platform Compatibility

| Platform | Support | Package Format | Configuration Path |
|----------|---------|----------------|-------------------|
| **Linux** | ✅ Full | RPM, Source | `./config.yml` |
| **macOS** | ✅ Full | DMG (App Bundle) - Dual Architecture | `~/Library/Application Support/LogViewer/` |
| **Windows** | ✅ Full | EXE, Source | `%APPDATA%\LogViewer\` |

### macOS Architecture Support
- **Intel x86_64**: `LogViewer-{VERSION}-macOS-x86_64.dmg`
- **Apple Silicon arm64**: `LogViewer-{VERSION}-macOS-arm64.dmg`
- **Cross-compatibility**: Both versions work on either architecture via Rosetta 2

### Version Management
All builds use centralized version management from `rpmbuild/SOURCES/Build_Version`:
```bash
# Update version for all platforms
echo "VERSION=3.2.0" > rpmbuild/SOURCES/Build_Version
```
- **Automatic Updates**: Build scripts automatically update RPM specs, Windows installers, and macOS bundles
- **Consistent Naming**: All artifacts use the same version across platforms
- **Single Source**: No need to update multiple files manually

### System Requirements
- **Linux**: Any modern distribution, Python 3.8+
- **macOS**: macOS 10.14 (Mojave) or later, Intel/Apple Silicon
- **Windows**: Windows 10 or later, Python 3.8+ (for source)

### Technical Compatibility
- **PyQt Versions**: Compatible with PyQt6 and PyQt5 (with compatibility layer)
- **Python Versions**: 3.8+ supported
- **File Formats**: Any text-based format (.log, .out, .txt, etc.)
- **File Encoding**: UTF-8, UTF-16, CP1252, Latin-1 with auto-detection

### Version Management Scripts
The following utility scripts maintain version consistency across platforms:

#### Version Update Scripts
```bash
cd rpmbuild/SOURCES

# Update RPM spec file version
./update_rpm_version.sh

# Update Windows installer version
python update_inno_version.py

# Update Windows version info
python generate_version_info.py
```

These scripts are automatically called during the build process but can be run manually if needed.

## Development

### Project Structure
```
log_viewer/
├── log_viewer.py          # Main application
├── requirements.txt       # Dependencies
├── config.yml            # Default configuration
├── README.md             # This file
├── rpmbuild/
│   ├── SOURCES/          # Build sources
│   │   ├── Build_App.sh  # Build script
│   │   └── log_viewer.spec # PyInstaller spec
│   └── SPECS/           # RPM spec files
└── documentation/        # Additional docs
```

### Building for Different Platforms

#### Linux
```bash
# Build standalone executable (includes automatic RPM spec version update)
cd rpmbuild/SOURCES
./Build_App.sh

# Build RPM package
cd ../..
./RPM_Build.sh
```

**Note**: The build process automatically updates the RPM spec file with the current version from `Build_Version`.

#### macOS
```bash
# Build both architectures (Intel x86_64 + Apple Silicon arm64)
cd rpmbuild/SOURCES
./Build_All_MacOS_Dual.sh

# Or build specific architecture:
./Build_All_MacOS_Dual.sh --x86_64-only    # Intel only
./Build_All_MacOS_Dual.sh --arm64-only     # Apple Silicon only

# Legacy single architecture build:
./Build_All_MacOS.sh      # Uses current system architecture
./Build_App_MacOS.sh      # Creates app bundle
./Create_DMG_MacOS.sh     # Creates DMG installer
```

#### Windows
```bash
# Build executable and installer (includes automatic version updates)
cd rpmbuild/SOURCES
Build_All_Windows.bat

# Output files (versioned):
# - LogViewer-{VERSION}.exe (portable executable)
# - LogViewer-{VERSION}-Setup.exe (installer)

# Or build individually:
Build_App_Windows.bat          # Creates LogViewer-{VERSION}.exe with dynamic versioning
# Then use Inno Setup to compile LogViewer_Installer.iss for installer

# Manual build using PyInstaller:
python update_inno_version.py  # Update installer script version
pyinstaller --noconfirm log_viewer_windows.spec
```

**Note**: The build process automatically:
- Updates `version_info.txt` with current version
- Updates Inno Setup installer script with current version
- Generates versioned installer: `LogViewer-{VERSION}-Setup.exe`

#### Cross-Platform GitHub Actions
- **Linux RPM**: `.github/workflows/rpm_build.yml`
- **macOS DMG (Dual Architecture)**: `.github/workflows/macos_build_dual.yml`
- **Windows EXE/Installer**: `.github/workflows/windows_build.yml`
- **Comprehensive Release**: `.github/workflows/manual_comprehensive_release.yml`

#### Release Process
1. **Update Version**: `echo "VERSION=3.2.0" > rpmbuild/SOURCES/Build_Version`
2. **Create Tag**: Push a version tag (e.g., `v3.2.0`) to trigger all platform builds
3. **Wait for Builds**: Monitor the Actions tab until all 3 platform workflows complete
4. **Create Release**: Go to Actions → "Manual Comprehensive Release" → Run workflow
5. **Add Artifacts**: Download artifacts from completed builds and upload to the draft release
6. **Publish**: Review and publish the comprehensive release

📋 **Detailed Process**: See [`RELEASE_PROCESS.md`](RELEASE_PROCESS.md) for complete instructions

#### Artifacts Included in Release
- `LogViewer-{VERSION}-macOS-arm64.dmg` (Apple Silicon)
- `LogViewer-{VERSION}-macOS-x86_64.dmg` (Intel)
- `LogViewer-{VERSION}-Setup.exe` (Windows installer)
- `LogViewer-{VERSION}.exe` (Windows portable)
- `LogViewer-{VERSION}-0.rpm` (Linux RPM)

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

#### Application Won't Start
- Check Python version (3.8+ required)
- Verify PyQt6 installation: `pip show PyQt6`
- Try running with verbose output: `python log_viewer.py --verbose`

#### Large Files Loading Slowly
- This is expected behavior for very large files
- The application loads files in chunks to remain responsive
- Progress is shown during loading

#### Search Not Working
- Ensure search term is spelled correctly
- Check if the file has loaded completely
- Try clearing the search box and typing again

#### Highlighting Not Showing
- Verify the configuration file is valid YAML
- Check that highlight terms exist in the file
- Try reloading the configuration

### Performance Tips
- Close other applications to free memory when viewing very large files
- Use specific search terms to reduce result sets
- Consider splitting extremely large files if performance is an issue
- Use the configuration system to highlight only relevant terms

## License

This software is proprietary to Michette Technologies. All rights reserved.

## Support

For technical support, bug reports, or feature requests, please contact:
- **Email**: tmichett@redhat.com
- **Organization**: Michette Technologies

## Version History

### Version 3.1.0 (Current)
- **NEW**: Dual macOS architecture support (Intel x86_64 + Apple Silicon arm64)
- **NEW**: Centralized version management from Build_Version file
- **NEW**: Architecture-specific DMG naming (LogViewer-{VERSION}-macOS-{ARCH}.dmg)
- **NEW**: Enhanced GitHub Actions workflow with parallel builds
- **NEW**: Comprehensive dual architecture build scripts
- **NEW**: Automatic RPM spec and Windows installer version updates
- **NEW**: Unified release workflow for all platforms
- **NEW**: Dynamic versioning across all build processes

### Version 3.0.0
- Enhanced search functionality with entire line highlighting
- Added bidirectional search navigation (Find Next/Find Previous)
- Improved search highlighting with proper cleanup of previous highlights
- Added comprehensive help system with integrated Help menu
- Added professional About dialog with version and company information
- Implemented keyboard shortcuts (Ctrl+F, F1, F3, Shift+F3, Escape)
- Added File menu with Open and Exit options
- Created comprehensive README documentation with installation and usage guides
- Fixed build script issues and improved build process reliability
- Enhanced PyQt version compatibility with multiple fallback approaches

### Version 1.3.1
- Major performance improvements for file loading
- Switched to QPlainTextEdit for better large file handling
- Implemented chunked file loading
- Added debounced search functionality

### Version 1.2.5
- Added configuration GUI for highlighting terms
- Custom configuration file support
- Command-line argument support
- Improved documentation

### Version 1.0.0
- Initial release
- Basic file viewing and search functionality
- ANSI color support
- Dark theme implementation