# Version Management Scripts

This document describes the automated version management scripts used in the Log Viewer project to maintain consistency across all platforms and build artifacts.

## Overview

The Log Viewer project uses centralized version management through the `Build_Version` file, with automated scripts that update platform-specific files to maintain version consistency.

## Central Version File

### Build_Version
**Location**: `rpmbuild/SOURCES/Build_Version`

```bash
VERSION=3.2.0
```

This file serves as the **single source of truth** for the application version across all platforms.

## Version Update Scripts

### 1. update_rpm_version.sh
**Purpose**: Updates RPM spec files with the current version

**Location**: `rpmbuild/SOURCES/update_rpm_version.sh`

**What it updates**:
- `../SPECS/LogViewer.spec` - Updates the `%define version` line

**Usage**:
```bash
cd rpmbuild/SOURCES
./update_rpm_version.sh
```

**Cross-platform compatibility**: Handles both macOS and Linux `sed` syntax differences.

### 2. update_inno_version.py
**Purpose**: Updates Windows Inno Setup installer script with version and executable references

**Location**: `rpmbuild/SOURCES/update_inno_version.py`

**What it updates**:
- `#define MyAppVersion "X.X.X"` - Main version definition
- `#define MyAppExeName "LogViewer-X.X.X.exe"` - Executable name definition
- `Source: "LogViewer-X.X.X.exe"` - Source file reference in [Files] section

**Enhanced Features**:
- **Regex Pattern**: Uses `LogViewer.*\.exe` to match any versioned executable
- **Complete Sync**: Updates all version references in the installer script
- **Backward Compatible**: Handles upgrades from unversioned to versioned executables

**Usage**:
```bash
cd rpmbuild/SOURCES
python3 update_inno_version.py
```

**Example Output**:
```
Updating Inno Setup script for version: 3.2.0
Updated LogViewer_Installer.iss with version 3.2.0 and executable name LogViewer-3.2.0.exe
Inno Setup script updated successfully
```

### 3. generate_version_info.py
**Purpose**: Generates Windows version information file for executable metadata

**Location**: `rpmbuild/SOURCES/generate_version_info.py`

**What it creates**:
- `version_info.txt` - Windows version resource file for PyInstaller

**Version Parsing**:
- Supports formats: `X.Y.Z` or `X.Y.Z.B`
- Defaults to `3.0.0.0` if parsing fails
- Handles missing components gracefully

**Usage**:
```bash
cd rpmbuild/SOURCES
python3 generate_version_info.py
```

## Automated Integration

### Build Process Integration
The version scripts are automatically called during platform builds:

#### macOS Builds
- Version read directly from `Build_Version` in PyInstaller spec files
- `Build_Version` file bundled with app bundle via datas array
- No additional scripts needed (Python handles version reading)

#### Linux Builds
- Version read directly from `Build_Version` in PyInstaller spec file
- `Build_Version` file bundled with executable via datas array  
- RPM spec file updated via `update_rpm_version.sh`

#### Windows Builds

**Local Builds (`Build_App_Windows.bat`)**:
```batch
REM Read version from Build_Version file
for /f "tokens=2 delims==" %%a in ('findstr "VERSION=" Build_Version 2^>nul') do set VERSION=%%a

REM Update version-dependent files
python generate_version_info.py
python update_inno_version.py

REM Build with versioned output
pyinstaller log_viewer_windows.spec
```

**GitHub Actions Workflow (`.github/workflows/windows_build.yml`)**:
Fixed in v3.2.0 - The workflow now calls version scripts in the correct order:
```yaml
# Generate version info
python generate_version_info.py

# Update Inno Setup script BEFORE building
python update_inno_version.py

# Build executable
pyinstaller --noconfirm log_viewer_windows.spec
```

**Previous Issue**: The workflow was calling `update_inno_version.py` **after** PyInstaller, causing Inno Setup to reference non-existent versioned executables.

#### Linux/RPM Builds (`Build_App.sh`)
```bash
# Read version and update RPM spec
./update_rpm_version.sh

# Build executable (includes Build_Version in bundle)
pyinstaller --noconfirm ./log_viewer.spec
```

**Recent Fix (v3.2.0)**: Updated `log_viewer.spec` to include `Build_Version` in the `datas` array:
```python
datas=[('config.yml', '.'), ('help_content.md', '.'), ('Build_Version', '.'), ...]
```
This ensures the Linux executable can read the version dynamically for the About dialog, fixing the issue where Linux builds were stuck at version 3.0.0.

**Recent Fixes (v3.3.0)**: 
- **Windows Installer Version Mismatch**: Fixed critical issue where `update_inno_version.py` was called after PyInstaller in the GitHub Actions workflow, causing Inno Setup to reference non-existent versioned executables. The workflow now correctly calls version scripts before building.
- **Enhanced Regex Pattern**: Improved `update_inno_version.py` to handle both versioned and unversioned executables by changing the regex pattern from `LogViewer\.exe` to `LogViewer.*\.exe`, ensuring automatic version updates work regardless of previous state.
- **GitHub Actions Workflow Fix**: Corrected YAML syntax error in `automated_comprehensive_release.yml` that was causing workflow validation failures.
- **Contact Information**: Updated all author and support email addresses from `tmichett@redhat.com` to `travis@michettetech.com` across the entire codebase.

## Version Consistency Verification

### Manual Verification
To verify all components are using the correct version:

```bash
cd rpmbuild/SOURCES

# Check central version
grep "VERSION=" Build_Version

# Check RPM spec
grep "%define version" ../SPECS/LogViewer.spec

# Check Windows installer script
grep -E "(MyAppVersion|MyAppExeName|Source.*LogViewer.*\.exe)" LogViewer_Installer.iss

# Check Windows version info
grep "FileVersion.*VERSION" version_info.txt
```

### Troubleshooting Version Mismatches

If you encounter version mismatch errors:

1. **Verify Central Version**:
   ```bash
   cat rpmbuild/SOURCES/Build_Version
   ```

2. **Re-run All Version Scripts**:
   ```bash
   cd rpmbuild/SOURCES
   ./update_rpm_version.sh
   python3 update_inno_version.py
   python3 generate_version_info.py
   ```

3. **Check Updates Were Applied**:
   ```bash
   # Verify RPM spec
   grep "%define version" ../SPECS/LogViewer.spec
   
   # Verify Inno Setup script
   grep "MyAppVersion\|Source.*LogViewer" LogViewer_Installer.iss
   ```

4. **Commit Changes**:
   ```bash
   git add ../SPECS/LogViewer.spec LogViewer_Installer.iss version_info.txt
   git commit -m "Update version references to $(grep VERSION= Build_Version | cut -d= -f2)"
   ```

## Common Issues and Solutions

### Issue: "Source file LogViewer-X.X.X.exe does not exist"
**Cause**: Version mismatch between PyInstaller output and Inno Setup script expectations

**Solution**:
1. Run `python3 update_inno_version.py` to sync versions
2. Ensure `Build_Version` contains the correct version
3. Rebuild the Windows executable

### Issue: RPM version not updating
**Cause**: RPM spec file not updated with new version

**Solution**:
1. Run `./update_rpm_version.sh` manually
2. Check for `sed` command compatibility (macOS vs Linux)
3. Verify permissions on spec file

### Issue: Windows version info incorrect
**Cause**: `version_info.txt` not regenerated with new version

**Solution**:
1. Run `python3 generate_version_info.py`
2. Verify `Build_Version` format is correct (`X.Y.Z`)
3. Check for Python script execution errors

## Best Practices

1. **Always Update Build_Version First**: Before any release, update the central version file
2. **Run Scripts After Version Changes**: Manually run version scripts when changing versions outside of builds
3. **Verify Cross-Platform**: Test version updates on different operating systems
4. **Commit Version Updates**: Always commit version file changes before tagging releases
5. **Use Semantic Versioning**: Follow `MAJOR.MINOR.PATCH` format for consistency

## Script Maintenance

### Regular Updates
- Review regex patterns for compatibility with new naming conventions
- Test scripts with edge cases (pre-release versions, build numbers)
- Ensure cross-platform compatibility for shell scripts

### Adding New Platforms
When adding support for new platforms:
1. Create a version update script following the existing pattern
2. Integrate into the platform's build process
3. Add verification commands to troubleshooting documentation
4. Test version consistency across all platforms

---

**Organization**: Michette Technologies  
**Project**: Log Viewer  
**Last Updated**: 2024 