# Flatpak Icon Fix

## Issue
The Flatpak build is still failing with AppStream validation error:
```
E: icon-not-found
ERROR: appstreamcli compose failed: Child process exited with code 1
```

## Root Cause Analysis
The AppStream system expects the icon to be:
1. **Installed** in the correct location: `/app/share/icons/hicolor/32x32/apps/com.michettetech.LogViewer.png`
2. **Referenced** correctly in the AppData XML
3. **Named** to match the application ID

## Fixes Applied

### 1. Updated Flatpak Manifest (`com.michettetech.LogViewer.yaml`)

**Added proper icon installation with debugging:**
```yaml
# Install icon to proper location for AppStream validation
- install -Dm644 rpmbuild/SOURCES/smallicon.png ${FLATPAK_DEST}/share/icons/hicolor/32x32/apps/com.michettetech.LogViewer.png

# Debug: Verify icon installation
- ls -la ${FLATPAK_DEST}/share/icons/hicolor/32x32/apps/ || echo "Icon directory not found"
- ls -la ${FLATPAK_DEST}/share/icons/hicolor/32x32/apps/com.michettetech.LogViewer.png || echo "Icon file not installed"
```

### 2. Updated AppData XML (`com.michettetech.LogViewer.appdata.xml`)

**Added explicit icon reference:**
```xml
<icon type="cached">com.michettetech.LogViewer</icon>
```

### 3. Enhanced Build Debugging

**Added verification steps in workflow:**
```yaml
# Verify source files exist
echo "Checking required source files:"
ls -la rpmbuild/SOURCES/dist/log_viewer || echo "PyInstaller executable not found"
ls -la rpmbuild/SOURCES/smallicon.png || echo "Icon file not found"
ls -la com.michettetech.LogViewer.desktop || echo "Desktop file not found"
ls -la com.michettetech.LogViewer.appdata.xml || echo "AppData file not found"
```

## Icon Requirements for Flatpak

### Correct File Structure:
```
/app/
├── bin/
│   └── log_viewer                           # Executable
├── share/
│   ├── applications/
│   │   └── com.michettetech.LogViewer.desktop
│   ├── metainfo/
│   │   └── com.michettetech.LogViewer.appdata.xml
│   └── icons/hicolor/32x32/apps/
│       └── com.michettetech.LogViewer.png   # Icon (matches app ID)
```

### Desktop File Reference:
```desktop
Icon=com.michettetech.LogViewer  # Must match icon filename
```

### AppData XML Reference:
```xml
<icon type="cached">com.michettetech.LogViewer</icon>
```

## Why This Should Work

1. **Correct Path**: Icon installed to standard XDG location
2. **Correct Name**: Icon filename matches application ID
3. **Explicit Reference**: AppData XML explicitly declares icon
4. **Debugging**: Added verification steps to catch issues early

## Expected Results

The next Flatpak build should:
1. ✅ Install icon to correct location during build
2. ✅ Pass AppStream validation (icon found)
3. ✅ Complete Flatpak build successfully
4. ✅ Create working `.flatpak` bundle

If the build still fails, the debugging output will show exactly what files are missing or incorrectly placed.

## Comparison with Working RPM

The RPM build now works because it:
- Installs icon to `/usr/share/icons/hicolor/32x32/apps/LogViewer.png`
- References icon as `Icon=LogViewer` in desktop file

The Flatpak should work the same way:
- Installs icon to `/app/share/icons/hicolor/32x32/apps/com.michettetech.LogViewer.png`  
- References icon as `Icon=com.michettetech.LogViewer` in desktop file
- Explicitly declares icon in AppData XML

This fix ensures the Flatpak follows the same pattern as the working RPM build.
