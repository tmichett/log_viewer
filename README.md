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

#### Method 1: RPM Package (Recommended for Red Hat/Fedora)
```bash
# Install the RPM package
sudo rpm -ivh LogViewer-2.0.0-0.rpm

# Launch the application
logviewer
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
```bash
# Build the standalone executable
cd rpmbuild/SOURCES
./Build_App.sh

# Run the built executable
./log_viewer
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

### Compatibility
- **PyQt Versions**: Compatible with PyQt6 and PyQt5 (with compatibility layer)
- **Python Versions**: 3.8+ supported
- **Operating Systems**: Linux, macOS, Windows
- **File Formats**: Any text-based format

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

### Building the Application
```bash
# Build standalone executable
cd rpmbuild/SOURCES
./Build_App.sh

# Build RPM package
cd ../..
./RPM_Build.sh
```

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

### Version 2.0.0 (Current)
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