#!/bin/bash
## Script to Create macOS DMG Package for Apple Silicon arm64
## Author: tmichett@redhat.com

# Check if we're running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Read version from Build_Version file
get_version() {
    if [ -f "Build_Version" ]; then
        VERSION=$(grep "VERSION=" Build_Version | cut -d'=' -f2)
        echo "$VERSION"
    else
        echo "3.0.0"
    fi
}

VERSION=$(get_version)
echo "Creating DMG for Log Viewer version $VERSION (Apple Silicon arm64)"

# Configuration
APP_NAME="Log Viewer"
ARCH="arm64"
DMG_NAME="LogViewer-${VERSION}-macOS-${ARCH}"
VOLUME_NAME="Log Viewer ${VERSION}"
DMG_BACKGROUND_IMG="smallicon.png"
APP_PATH="dist_arm64/Log Viewer.app"

# Detect if running in CI environment
if [[ -n "$CI" || -n "$GITHUB_ACTIONS" || -n "$RUNNER_OS" ]]; then
    echo "Detected CI environment - using headless DMG creation"
    CI_MODE=true
else
    echo "Detected interactive environment - using full DMG customization"
    CI_MODE=false
fi

# Check if app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: App bundle not found at $APP_PATH"
    echo "Please run ./Build_App_MacOS_arm64.sh first"
    exit 1
fi

echo "Creating DMG package for $APP_NAME ($ARCH)..."

# Clean up any existing DMG artifacts
rm -rf dmg_temp_arm64
rm -f "$DMG_NAME.dmg"
rm -f temp_dmg_arm64.dmg

# Create temporary DMG directory
mkdir -p dmg_temp_arm64

# Copy app bundle to DMG temp directory
echo "Copying app bundle..."
cp -R "$APP_PATH" dmg_temp_arm64/

# Create Applications symlink for easy installation
echo "Creating Applications symlink..."
ln -s /Applications dmg_temp_arm64/Applications

# Copy additional files
echo "Copying additional files..."
cp ../../README.md dmg_temp_arm64/README.txt
cp config.yml dmg_temp_arm64/
cp test.log dmg_temp_arm64/

# Create a proper README for the DMG
cat > dmg_temp_arm64/INSTALL.txt << EOF
Log Viewer ${VERSION} - macOS Installation (Apple Silicon arm64)

INSTALLATION:
1. Drag "Log Viewer.app" to the Applications folder
2. Launch from Applications or Launchpad

COMPATIBILITY:
- This version is optimized for Apple Silicon Macs (arm64)
- Will run on Intel-based Macs using Rosetta 2 translation
- Requires macOS 10.14 (Mojave) or later

USAGE:
- Double-click the app to launch
- Use Cmd+O to open log files
- Supports .log, .out, and .txt files
- Configuration is stored in ~/Library/Application Support/LogViewer/

SUPPORT:
Email: tmichett@redhat.com
Organization: Michette Technologies

Copyright © 2024 Michette Technologies. All rights reserved.
EOF

# Calculate DMG size (app size + 50MB buffer)
echo "Calculating DMG size..."
APP_SIZE=$(du -sk "$APP_PATH" | cut -f1)
DMG_SIZE=$((APP_SIZE + 51200))  # Add 50MB buffer

if [[ "$CI_MODE" == "true" ]]; then
    echo "Creating simple DMG for CI environment..."
    
    # Create DMG directly in compressed format for CI
    hdiutil create -srcfolder dmg_temp_arm64 -volname "$VOLUME_NAME" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDZO -imagekey zlib-level=9 -size ${DMG_SIZE}k "$DMG_NAME.dmg"
    
    if [ $? -eq 0 ]; then
        echo "DMG created successfully in CI mode!"
    else
        echo "Error: DMG creation failed in CI mode"
        exit 1
    fi
    
else
    echo "Creating customized DMG for interactive environment..."
    
    # Create DMG
    echo "Creating DMG..."
    hdiutil create -srcfolder dmg_temp_arm64 -volname "$VOLUME_NAME" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${DMG_SIZE}k temp_dmg_arm64.dmg
    
    if [ $? -ne 0 ]; then
        echo "Error: Initial DMG creation failed"
        exit 1
    fi
    
    # Mount the DMG
    echo "Mounting DMG for customization..."
    DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen temp_dmg_arm64.dmg | egrep '^/dev/' | sed 1q | awk '{print $1}')
    MOUNT_POINT="/Volumes/$VOLUME_NAME"
    
    # Wait for mount and verify
    sleep 3
    if [ ! -d "$MOUNT_POINT" ]; then
        echo "Error: DMG mount failed"
        exit 1
    fi
    
    # Customize DMG appearance (only in interactive mode)
    echo "Customizing DMG appearance..."
    osascript << EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 920, 440}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set position of item "Log Viewer.app" of container window to {130, 120}
        set position of item "Applications" of container window to {390, 120}
        set position of item "README.txt" of container window to {130, 250}
        set position of item "INSTALL.txt" of container window to {390, 250}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

    # Unmount the DMG with retry logic
    echo "Unmounting DMG..."
    for i in {1..5}; do
        if hdiutil detach "$DEVICE"; then
            echo "Successfully unmounted DMG"
            break
        else
            echo "Attempt $i: Failed to unmount, retrying in 2 seconds..."
            sleep 2
            if [ $i -eq 5 ]; then
                echo "Error: Could not unmount DMG after 5 attempts"
                exit 1
            fi
        fi
    done
    
    # Convert to compressed read-only DMG
    echo "Converting to compressed DMG..."
    hdiutil convert temp_dmg_arm64.dmg -format UDZO -imagekey zlib-level=9 -o "$DMG_NAME.dmg"
    
    if [ $? -ne 0 ]; then
        echo "Error: DMG conversion failed"
        exit 1
    fi
    
    # Clean up temporary DMG
    rm -f temp_dmg_arm64.dmg
fi

# Clean up temporary files
rm -rf dmg_temp_arm64

# Check if DMG was created successfully
if [ -f "$DMG_NAME.dmg" ]; then
    echo "DMG package created successfully!"
    echo "DMG location: $(pwd)/$DMG_NAME.dmg"
    echo "DMG size: $(du -sh "$DMG_NAME.dmg" | cut -f1)"
    
    # Test DMG can be mounted
    echo "Testing DMG mount..."
    if hdiutil attach "$DMG_NAME.dmg" -readonly -noautoopen >/dev/null 2>&1; then
        echo "✓ DMG mounts successfully"
        hdiutil detach "/Volumes/$VOLUME_NAME" >/dev/null 2>&1
    else
        echo "✗ Warning: DMG mount test failed"
    fi
    
    echo ""
    echo "Installation Instructions:"
    echo "1. Double-click $DMG_NAME.dmg to mount"
    echo "2. Drag 'Log Viewer.app' to Applications folder"
    echo "3. Launch from Applications or Launchpad"
    echo ""
    echo "DMG package created successfully for Apple Silicon arm64!"
else
    echo "Error: DMG creation failed"
    exit 1
fi 