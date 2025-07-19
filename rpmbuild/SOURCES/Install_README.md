# Log Viewer Installation Guide

## Overview
Log Viewer is a GUI application for viewing and searching through log files. It supports ANSI color codes and provides features like text search, font size adjustment, and configurable term highlighting. The application can open .log, .out, and .txt files.

## Prerequisites
- Python 3.x
- PyInstaller
- PyQt6
- PyYAML

## Building the Application

1. Install the required dependencies:
```bash
pip3 install PyInstaller PyQt6 PyYAML
```

2. **Version Management**: Update the version in `Build_Version` file:
```bash
echo "VERSION=3.2.0" > Build_Version
```

3. Build the application:

### macOS (Dual Architecture)
```bash
# Build both Intel x86_64 and Apple Silicon arm64
./Build_All_MacOS_Dual.sh

# Or build specific architecture:
./Build_All_MacOS_Dual.sh --x86_64-only    # Intel only
./Build_All_MacOS_Dual.sh --arm64-only     # Apple Silicon only

# Legacy single architecture build:
pyinstaller log_viewer_macos.spec
```

### Linux/Windows
```bash
pyinstaller log_viewer.spec
```

The executable will be created in the `dist` directory (or `dist_x86_64`/`dist_arm64` for macOS dual builds).

## Version Management

All builds automatically read the version from `Build_Version` file:
```bash
# Update version for all platforms
echo "VERSION=3.2.0" > Build_Version
```

The build processes automatically update:
- RPM spec files (`update_rpm_version.sh`)
- Windows installer scripts (`update_inno_version.py`) 
- Windows version info (`generate_version_info.py`)

## Installation

### macOS/Linux
1. Copy the executable to your desired location:
```bash
cp dist/log_viewer /usr/local/bin/
```

### Windows
1. Copy the `log_viewer.exe` from the `dist` directory to your desired location
2. Add the location to your system's PATH if needed

## Configuration
The application uses a `config.yml` file for customizing highlight terms. There are several ways to use custom configurations:

1. Command-line argument:
```bash
log_viewer --config /path/to/your/config.yml
```

2. GUI interface:
   - Click the "Load Config" button to select a custom config file
   - Click the "Configure Highlighting" button to create or modify highlight terms interactively

3. Default location:
   - Place a `config.yml` file in the same directory as the application

Example `config.yml`:
```yaml
highlight_terms:
  - ERROR
  - WARNING
  - CRITICAL
  - term: FATAL
    color: "#FF0000"  # Custom color (red)
```

### Highlight Term Configuration
You can configure highlight terms in two formats:
1. Simple format: Just specify the term as a string (default highlight color will be used)
2. Advanced format: Specify both the term and a custom color in hex format

## Usage
1. Launch the application:
```bash
log_viewer [--config /path/to/config.yml] [logfile]
```

2. Use the "Open Log File" button to select a log file to view
   - Supported file types: .log, .out, .txt, and any text file
3. Use the search bar to find specific text in the log
4. Adjust font size using the + and - buttons
5. Configure highlighting:
   - Click "Configure Highlighting" to open the configuration dialog
   - Add, edit, or remove terms to highlight
   - Set custom colors for each term
   - Save your configuration for future use
6. The application will automatically parse and display ANSI color codes in the log file

## Features
- ANSI color code support
- Text search functionality
- Font size adjustment
- Configurable term highlighting with custom colors
- Custom configuration management through GUI
- Dark mode interface
- Support for large files with asynchronous loading
- Progress indicator for file loading operations
- Command-line arguments for config and file loading

## Troubleshooting
If you encounter any issues:
1. Ensure the application has proper permissions to read log files
2. Check that the log file is readable
3. Verify the config.yml file format if using custom highlighting
4. Check the application's error messages in the terminal
5. For very large files, the application will load them asynchronously with a progress bar - please be patient during loading

## Support
For issues or feature requests, please contact the maintainer or open an issue in the project repository. 