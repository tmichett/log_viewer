# Log Viewer Flatpak Package

This directory contains all the files needed to create a Flatpak package for the Log Viewer application (version 3.7.0).

## Quick Start

1. **Install prerequisites** (on Linux):
   ```bash
   # Ubuntu/Debian
   sudo apt install flatpak flatpak-builder
   
   # Fedora
   sudo dnf install flatpak flatpak-builder
   ```

2. **Add Flathub repository**:
   ```bash
   flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
   ```

3. **Build and install**:
   ```bash
   chmod +x build-flatpak.sh
   ./build-flatpak.sh
   ```

4. **Run the application**:
   ```bash
   flatpak run com.michettetech.LogViewer
   ```

## Files Created

- **`com.michettetech.LogViewer.yaml`** - Main Flatpak manifest file
- **`com.michettetech.LogViewer.desktop`** - Desktop entry for application launcher
- **`com.michettetech.LogViewer.appdata.xml`** - AppStream metadata for software centers
- **`build-flatpak.sh`** - Automated build script
- **`FLATPAK_BUILD_GUIDE.md`** - Detailed build and usage instructions
- **`FLATPAK_README.md`** - This file

## About the Application

**Log Viewer** is a powerful GUI application for viewing and searching through log files with the following features:

- **ANSI Color Support**: Proper display of colored terminal output
- **Advanced Search**: Fast search with highlighting and navigation
- **Configurable Highlighting**: Custom color highlighting for specific terms
- **Large File Support**: Efficiently handles multi-GB log files
- **Dark Theme**: Eye-friendly interface optimized for log reading
- **Keyboard Shortcuts**: Quick navigation (Ctrl+F, F3, Escape, etc.)
- **Multiple Formats**: Supports .log, .out, .txt files

## Flatpak Benefits

The Flatpak version provides:

- **Sandboxed Security**: Application runs in a secure container
- **Dependency Management**: All Python dependencies are bundled
- **Universal Compatibility**: Works across all Linux distributions
- **Easy Installation**: Single-file installation without root access
- **Automatic Updates**: Can be updated through Flatpak

## Technical Details

- **Runtime**: org.freedesktop.Platform 23.08
- **Application ID**: com.michettetech.LogViewer
- **Python Version**: 3.8+ compatible
- **GUI Framework**: PyQt6
- **Size**: ~50-60 MB (including all dependencies)

## File Access

The Flatpak has been configured with appropriate permissions:

- Read-only access to home directory and common folders
- Read-only access to `/var/log` for system logs  
- Read-write access to Documents, Desktop, Downloads
- Temporary file access for processing

## Support

- **Developer**: Michette Technologies
- **Contact**: travis@michettetech.com
- **Version**: 3.7.0
- **License**: Proprietary

For detailed instructions, see `FLATPAK_BUILD_GUIDE.md`.
