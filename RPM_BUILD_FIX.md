# RPM Build Fix

## Issues Fixed

### 1. Wrong Operating System
**Problem**: The RPM build was running on Ubuntu (Debian-based) instead of a Fedora/RHEL-based system.

**Error Messages**:
```
E: Unable to locate package rpmbuild
E: Unable to locate package rpmdevtools
apt list --upgradable
```

**Root Cause**: RPM packages must be built on RPM-based distributions, not Debian/Ubuntu.

**Fix Applied**:
```yaml
# Before (Broken)
runs-on: ubuntu-latest

# After (Fixed)
runs-on: ubuntu-latest
container: fedora:latest  # Use Fedora container
```

### 2. Wrong Package Manager
**Problem**: Using `apt` commands on a system that needs `dnf`.

**Fix Applied**:
```yaml
# Before (Broken)
sudo apt update
sudo apt install -y rpm rpmbuild rpmdevtools

# After (Fixed)
dnf update -y
dnf install -y rpm-build rpmdevtools python3-pip git which findutils
```

### 3. AppStream Icon Issues
**Problem**: AppStream validation failing with "icon-not-found" error.

**Root Cause**: Icon wasn't installed in the standard system location.

**Fix Applied**:
- Added icon installation to standard location: `/usr/share/icons/hicolor/32x32/apps/LogViewer.png`
- Updated desktop file to use standard icon name: `Icon=LogViewer`
- Added icon to RPM spec file installation

## Changes Made

### 1. Updated Workflow (`.github/workflows/rpm_build.yml`)

**Container and Package Management**:
```yaml
container: fedora:latest  # Run in Fedora container

steps:
- name: Install RPM build tools
  run: |
    dnf update -y  # Use dnf instead of apt
    dnf install -y rpm-build rpmdevtools python3-pip git which findutils
```

**Python Dependencies**:
```yaml
- name: Install Python dependencies
  run: |
    dnf install -y python3-devel python3-pip
    pip3 install PyInstaller PyQt6 PyYAML Pillow
```

### 2. Updated RPM Spec (`rpmbuild/SPECS/LogViewer.spec`)

**Icon Installation**:
```spec
# Create icon directory
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/32x32/apps

# Install icon to standard location
cp -p %{_sourcedir}/smallicon.png $RPM_BUILD_ROOT/usr/share/icons/hicolor/32x32/apps/LogViewer.png

# Include icon in package
/usr/share/icons/hicolor/32x32/apps/LogViewer.png
```

### 3. Updated Desktop File (`rpmbuild/SOURCES/LogViewer.desktop`)

**Icon Reference**:
```desktop
# Before (Absolute path)
Icon=/opt/LogViewer/smallicon.png

# After (Standard icon name)
Icon=LogViewer
```

## How It Works Now

1. **Fedora Container**: Runs RPM build in proper RPM-based environment
2. **DNF Package Manager**: Uses correct package manager for Fedora
3. **Standard Icon Installation**: Installs icon where AppStream expects it
4. **PyInstaller Build**: Creates standalone executable like other platforms
5. **Proper RPM Creation**: Builds valid RPM package with all files

## Expected Results

The next RPM build should:
1. ✅ Run in Fedora container (proper RPM environment)
2. ✅ Install dependencies with dnf (correct package manager)
3. ✅ Build PyInstaller executable successfully
4. ✅ Create valid RPM package
5. ✅ Pass AppStream validation (icon found)
6. ✅ Upload artifact successfully

## Benefits

- ✅ **Correct Environment**: RPM built on RPM-based system
- ✅ **Standard Compliance**: Icon follows XDG icon theme specification
- ✅ **AppStream Compatible**: Passes validation for software centers
- ✅ **Consistent Approach**: Same PyInstaller process as other platforms

This fix ensures the RPM build works correctly in the proper Fedora environment while maintaining consistency with your other platform builds.
