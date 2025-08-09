# Log Viewer Flatpak Build Guide

This guide explains how to create and build a Flatpak package for the Log Viewer application.

## Prerequisites

### 1. Install Flatpak and flatpak-builder

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install flatpak flatpak-builder
```

**Fedora:**
```bash
sudo dnf install flatpak flatpak-builder
```

**Arch Linux:**
```bash
sudo pacman -S flatpak flatpak-builder
```

### 2. Add Flathub Repository
```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

### 3. Install Required Runtime and SDK
```bash
flatpak install flathub org.freedesktop.Platform//23.08
flatpak install flathub org.freedesktop.Sdk//23.08
```

## Files Created for Flatpak

The following files have been created for the Flatpak build:

1. **`com.michettetech.LogViewer.yaml`** - Main Flatpak manifest
2. **`com.michettetech.LogViewer.desktop`** - Desktop entry file
3. **`com.michettetech.LogViewer.appdata.xml`** - AppStream metadata
4. **`build-flatpak.sh`** - Automated build script

## Building the Flatpak

### Method 1: Using the Build Script (Recommended)

```bash
# Make the script executable (Linux/macOS)
chmod +x build-flatpak.sh

# Run the build script
./build-flatpak.sh
```

### Method 2: Manual Build

```bash
# Create build directories
mkdir -p flatpak-build flatpak-repo

# Build the Flatpak
flatpak-builder --user --install-deps-from=flathub --repo=flatpak-repo flatpak-build com.michettetech.LogViewer.yaml

# Install locally
flatpak --user remote-add --no-gpg-verify --if-not-exists logviewer-origin flatpak-repo
flatpak --user install -y logviewer-origin com.michettetech.LogViewer
```

## Running the Application

```bash
# Run the Flatpak
flatpak run com.michettetech.LogViewer

# Or run with a specific log file
flatpak run com.michettetech.LogViewer /path/to/logfile.log
```

## Distribution

### Create a Bundle for Distribution

```bash
# Create a .flatpak bundle
flatpak build-bundle flatpak-repo com.michettetech.LogViewer.flatpak com.michettetech.LogViewer

# Install the bundle on another system
flatpak install com.michettetech.LogViewer.flatpak
```

### Publish to Flathub (Optional)

To publish to Flathub, you would need to:

1. Fork the [Flathub repository](https://github.com/flathub/flathub)
2. Submit a pull request with your manifest
3. Follow the [Flathub submission guidelines](https://docs.flathub.org/docs/for-app-authors/submission)

## Flatpak Features Configured

### Permissions
The Flatpak has been configured with the following permissions:

- **Display**: X11 and Wayland support
- **GPU**: Hardware acceleration for better performance
- **File System Access**:
  - Read-only access to home directory
  - Read-only access to `/var/log` for system logs
  - Read-write access to Documents, Desktop, and Downloads folders
  - Read-write access to `/tmp`

### Dependencies
The following Python packages are bundled:

- **PyQt6** (>= 6.4.0) - GUI framework
- **PyYAML** (>= 6.0) - Configuration file handling
- **Pillow** (>= 9.0.0) - Image processing

## File Structure in Flatpak

```
/app/
├── bin/
│   └── log_viewer.py           # Main application script
├── share/
│   ├── applications/
│   │   └── com.michettetech.LogViewer.desktop
│   ├── metainfo/
│   │   └── com.michettetech.LogViewer.appdata.xml
│   ├── icons/hicolor/32x32/apps/
│   │   └── com.michettetech.LogViewer.png
│   ├── logviewer/
│   │   └── config.yml          # Default configuration
│   └── doc/logviewer/
│       └── README.md           # Documentation
```

## Troubleshooting

### Common Issues

1. **Runtime not found**
   ```bash
   # Install the required runtime
   flatpak install flathub org.freedesktop.Platform//23.08
   ```

2. **Build fails with dependency errors**
   ```bash
   # Update Flatpak and try again
   flatpak update
   ```

3. **Application won't start**
   ```bash
   # Check logs
   flatpak logs com.michettetech.LogViewer
   ```

4. **File access issues**
   - The application can read files from your home directory, Documents, Downloads, and Desktop
   - For files in other locations, use `flatpak run --filesystem=/path/to/files com.michettetech.LogViewer`

### Debug Mode

```bash
# Run with debug output
flatpak run --devel com.michettetech.LogViewer

# Run with shell access for debugging
flatpak run --devel --command=bash com.michettetech.LogViewer
```

## Updating the Flatpak

To update the application:

1. Modify the source files or manifest
2. Rebuild using the build script or manual commands
3. The new version will be installed automatically

## Uninstalling

```bash
# Uninstall the application
flatpak --user uninstall com.michettetech.LogViewer

# Remove the repository
flatpak --user remote-delete logviewer-origin
```

## Notes

- The Flatpak uses the same Python source code as the original application
- Configuration files are stored in the Flatpak's sandboxed environment
- The application maintains the same functionality as the native version
- All keyboard shortcuts and features work identically

For additional help or issues, contact: travis@michettetech.com
