# Log Viewer Installation Guide

## Overview
Log Viewer is a GUI application for viewing and searching through log files. It supports ANSI color codes and provides features like text search, font size adjustment, and configurable term highlighting.

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

2. Build the application:
```bash
pyinstaller log_viewer.spec
```

The executable will be created in the `dist` directory.

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
The application can use a `config.yml` file for customizing highlight terms. You can specify the full path to the config file when launching the application:

```bash
log_viewer --config /path/to/your/config.yml
```

Example `config.yml`:
```yaml
highlight_terms:
  - ERROR
  - WARNING
  - CRITICAL
```

## Usage
1. Launch the application:
```bash
log_viewer
```

2. Use the "Open Log File" button to select a log file to view
3. Use the search bar to find specific text in the log
4. Adjust font size using the + and - buttons
5. The application will automatically parse and display ANSI color codes in the log file

## Features
- ANSI color code support
- Text search functionality
- Font size adjustment
- Configurable term highlighting
- Dark mode interface
- Support for large log files

## Troubleshooting
If you encounter any issues:
1. Ensure the application has proper permissions to read log files
2. Check that the log file is readable
3. Verify the config.yml file format if using custom highlighting
4. Check the application's error messages in the terminal

## Support
For issues or feature requests, please contact the maintainer or open an issue in the project repository. 