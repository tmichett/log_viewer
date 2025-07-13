#!/bin/bash
## Comprehensive macOS Build Script
## Builds both App Bundle and DMG Package
## Author: tmichett@redhat.com

# Check if we're running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

echo "============================================"
echo "Log Viewer - Complete macOS Build Process"
echo "============================================"

# Parse command line arguments
SKIP_TESTS=false
CLEAN_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-tests    Skip testing steps"
            echo "  --clean         Clean all build artifacts before building"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean build artifacts if requested
if [ "$CLEAN_BUILD" = true ]; then
    echo "Cleaning build artifacts..."
    rm -rf build dist log_viewer_venv
    rm -rf dmg_temp
    rm -f LogViewer-3.0.0-macOS.dmg temp_dmg.dmg
    echo "Clean completed."
fi

# Step 1: Build the app bundle
echo "Step 1: Building macOS App Bundle..."
if ! bash Build_App_MacOS.sh; then
    echo "Error: App bundle build failed"
    exit 1
fi

# Step 2: Create DMG package
echo "Step 2: Creating DMG Package..."
if ! bash Create_DMG_MacOS.sh; then
    echo "Error: DMG creation failed"
    exit 1
fi

# Step 3: Run tests (unless skipped)
if [ "$SKIP_TESTS" != true ]; then
    echo "Step 3: Running Tests..."
    
    # Test app bundle
    echo "  Testing app bundle..."
    if [ -d "dist/Log Viewer.app" ]; then
        echo "    ✓ App bundle exists"
        
        # Test app can be launched
        echo "    Testing app launch..."
        # Use background process with sleep instead of timeout (macOS doesn't have timeout by default)
        open "dist/Log Viewer.app" --args --help &
        sleep 5
        pkill -f "log_viewer" || true
        echo "    ✓ App launch test completed"
        
        # Check app bundle structure
        if [ -f "dist/Log Viewer.app/Contents/MacOS/log_viewer" ]; then
            echo "    ✓ App executable exists"
        else
            echo "    ✗ App executable not found"
            exit 1
        fi
        
        if [ -f "dist/Log Viewer.app/Contents/Info.plist" ]; then
            echo "    ✓ Info.plist exists"
        else
            echo "    ✗ Info.plist not found"
            exit 1
        fi
    else
        echo "    ✗ App bundle not found"
        exit 1
    fi
    
    # Test DMG
    echo "  Testing DMG package..."
    if [ -f "LogViewer-3.0.0-macOS.dmg" ]; then
        echo "    ✓ DMG exists"
        
        # Test DMG can be mounted
        echo "    Testing DMG mount..."
        if hdiutil attach "LogViewer-3.0.0-macOS.dmg" -readonly -noautoopen >/dev/null 2>&1; then
            echo "    ✓ DMG mounted successfully"
            
            # Check DMG contents
            if [ -d "/Volumes/Log Viewer 3.0.0/Log Viewer.app" ]; then
                echo "    ✓ App bundle found in DMG"
            else
                echo "    ✗ App bundle not found in DMG"
                exit 1
            fi
            
            # Unmount DMG
            hdiutil detach "/Volumes/Log Viewer 3.0.0" >/dev/null 2>&1
            echo "    ✓ DMG unmounted"
        else
            echo "    ✗ DMG mount failed"
            exit 1
        fi
    else
        echo "    ✗ DMG not found"
        exit 1
    fi
    
    echo "  ✓ All tests passed"
fi

# Step 4: Generate build summary
echo "Step 4: Build Summary"
echo "===================="

if [ -d "dist/Log Viewer.app" ]; then
    APP_SIZE=$(du -sh "dist/Log Viewer.app" | cut -f1)
    echo "App Bundle: dist/Log Viewer.app (${APP_SIZE})"
else
    echo "App Bundle: NOT FOUND"
fi

if [ -f "LogViewer-3.0.0-macOS.dmg" ]; then
    DMG_SIZE=$(du -sh "LogViewer-3.0.0-macOS.dmg" | cut -f1)
    echo "DMG Package: LogViewer-3.0.0-macOS.dmg (${DMG_SIZE})"
else
    echo "DMG Package: NOT FOUND"
fi

# Step 5: Installation instructions
echo ""
echo "Installation Instructions:"
echo "========================="
echo "1. Double-click LogViewer-3.0.0-macOS.dmg to mount"
echo "2. Drag 'Log Viewer.app' to Applications folder"
echo "3. Launch from Applications or Launchpad"
echo ""
echo "Command-line usage:"
echo "  open -a 'Log Viewer' /path/to/file.log"
echo ""
echo "Distribution files ready:"
echo "  - LogViewer-3.0.0-macOS.dmg (for users)"
echo "  - dist/Log Viewer.app (for developers)"

echo ""
echo "============================================"
echo "macOS Build Completed Successfully!"
echo "============================================" 