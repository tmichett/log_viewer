#!/bin/bash
## Comprehensive macOS Build Script - Dual Architecture
## Builds both Intel x86_64 and Apple Silicon arm64 App Bundles and DMG Packages
## Author: travis@michettetech.com

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
        echo "4.0.1"
    fi
}

VERSION=$(get_version)

echo "============================================"
echo "Log Viewer - Complete macOS Build Process"
echo "Version: $VERSION"
echo "Building Dual Architecture (x86_64 + arm64)"
echo "============================================"

# Parse command line arguments
SKIP_TESTS=false
CLEAN_BUILD=false
BUILD_ARM64=true
BUILD_X86_64=true

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
        --arm64-only)
            BUILD_X86_64=false
            shift
            ;;
        --x86_64-only)
            BUILD_ARM64=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-tests     Skip testing steps"
            echo "  --clean          Clean all build artifacts before building"
            echo "  --arm64-only     Build only ARM64 version"
            echo "  --x86_64-only    Build only x86_64 version"
            echo "  -h, --help       Show this help message"
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
    rm -rf build_x86_64 dist_x86_64 log_viewer_venv_x86_64
    rm -rf build_arm64 dist_arm64 log_viewer_venv_arm64
    rm -rf build dist log_viewer_venv
    rm -rf dmg_temp_x86_64 dmg_temp_arm64 dmg_temp
    rm -f LogViewer-${VERSION}-macOS-x86_64.dmg LogViewer-${VERSION}-macOS-arm64.dmg
    rm -f LogViewer-${VERSION}-macOS.dmg temp_dmg*.dmg
    echo "Clean completed."
fi

# Step 1: Build ARM64 version (if enabled)
if [ "$BUILD_ARM64" = true ]; then
    echo ""
    echo "Step 1a: Building macOS App Bundle (ARM64)..."
    if ! bash Build_App_MacOS_arm64.sh; then
        echo "Error: ARM64 app bundle build failed"
        exit 1
    fi

    echo "Step 1b: Creating ARM64 DMG Package..."
    if ! bash Create_DMG_MacOS_arm64.sh; then
        echo "Error: ARM64 DMG creation failed"
        exit 1
    fi
else
    echo "Step 1: Skipping ARM64 build (--x86_64-only specified)"
fi

# Step 2: Build x86_64 version (if enabled)
if [ "$BUILD_X86_64" = true ]; then
    echo ""
    echo "Step 2a: Building macOS App Bundle (x86_64)..."
    if ! bash Build_App_MacOS_x86_64.sh; then
        echo "Error: x86_64 app bundle build failed"
        exit 1
    fi

    echo "Step 2b: Creating x86_64 DMG Package..."
    if ! bash Create_DMG_MacOS_x86_64.sh; then
        echo "Error: x86_64 DMG creation failed"
        exit 1
    fi
else
    echo "Step 2: Skipping x86_64 build (--arm64-only specified)"
fi

# Step 3: Run tests (unless skipped)
if [ "$SKIP_TESTS" != true ]; then
    echo ""
    echo "Step 3: Running Tests..."
    
    # Test ARM64 version
    if [ "$BUILD_ARM64" = true ]; then
        echo "  Testing ARM64 build..."
        if [ -d "dist_arm64/Log Viewer.app" ]; then
            echo "    ✓ ARM64 app bundle exists"
            
            # Test app can be launched
            echo "    Testing ARM64 app launch..."
            open "dist_arm64/Log Viewer.app" --args --help &
            sleep 5
            pkill -f "log_viewer" || true
            echo "    ✓ ARM64 app launch test completed"
            
            # Check app bundle structure
            if [ -f "dist_arm64/Log Viewer.app/Contents/MacOS/log_viewer" ]; then
                echo "    ✓ ARM64 app executable exists"
            else
                echo "    ✗ ARM64 app executable not found"
                exit 1
            fi
        else
            echo "    ✗ ARM64 app bundle not found"
            exit 1
        fi
        
        # Test ARM64 DMG
        if [ -f "LogViewer-${VERSION}-macOS-arm64.dmg" ]; then
            echo "    ✓ ARM64 DMG exists"
            
            # Test DMG can be mounted
            echo "    Testing ARM64 DMG mount..."
            if hdiutil attach "LogViewer-${VERSION}-macOS-arm64.dmg" -readonly -noautoopen >/dev/null 2>&1; then
                echo "    ✓ ARM64 DMG mounted successfully"
                hdiutil detach "/Volumes/Log Viewer ${VERSION}" >/dev/null 2>&1
                echo "    ✓ ARM64 DMG unmounted"
            else
                echo "    ✗ ARM64 DMG mount failed"
                exit 1
            fi
        else
            echo "    ✗ ARM64 DMG not found"
            exit 1
        fi
    fi
    
    # Test x86_64 version
    if [ "$BUILD_X86_64" = true ]; then
        echo "  Testing x86_64 build..."
        if [ -d "dist_x86_64/Log Viewer.app" ]; then
            echo "    ✓ x86_64 app bundle exists"
            
            # Test app can be launched
            echo "    Testing x86_64 app launch..."
            open "dist_x86_64/Log Viewer.app" --args --help &
            sleep 5
            pkill -f "log_viewer" || true
            echo "    ✓ x86_64 app launch test completed"
            
            # Check app bundle structure
            if [ -f "dist_x86_64/Log Viewer.app/Contents/MacOS/log_viewer" ]; then
                echo "    ✓ x86_64 app executable exists"
            else
                echo "    ✗ x86_64 app executable not found"
                exit 1
            fi
        else
            echo "    ✗ x86_64 app bundle not found"
            exit 1
        fi
        
        # Test x86_64 DMG
        if [ -f "LogViewer-${VERSION}-macOS-x86_64.dmg" ]; then
            echo "    ✓ x86_64 DMG exists"
            
            # Test DMG can be mounted
            echo "    Testing x86_64 DMG mount..."
            if hdiutil attach "LogViewer-${VERSION}-macOS-x86_64.dmg" -readonly -noautoopen >/dev/null 2>&1; then
                echo "    ✓ x86_64 DMG mounted successfully"
                hdiutil detach "/Volumes/Log Viewer ${VERSION}" >/dev/null 2>&1
                echo "    ✓ x86_64 DMG unmounted"
            else
                echo "    ✗ x86_64 DMG mount failed"
                exit 1
            fi
        else
            echo "    ✗ x86_64 DMG not found"
            exit 1
        fi
    fi
    
    echo "  ✓ All tests passed"
else
    echo "Step 3: Skipping tests (--skip-tests specified)"
fi

# Step 4: Generate build summary
echo ""
echo "Step 4: Build Summary"
echo "===================="
echo "Version: $VERSION"

if [ "$BUILD_ARM64" = true ]; then
    if [ -d "dist_arm64/Log Viewer.app" ]; then
        APP_SIZE_ARM64=$(du -sh "dist_arm64/Log Viewer.app" | cut -f1)
        echo "ARM64 App Bundle: dist_arm64/Log Viewer.app (${APP_SIZE_ARM64})"
    else
        echo "ARM64 App Bundle: NOT FOUND"
    fi

    if [ -f "LogViewer-${VERSION}-macOS-arm64.dmg" ]; then
        DMG_SIZE_ARM64=$(du -sh "LogViewer-${VERSION}-macOS-arm64.dmg" | cut -f1)
        echo "ARM64 DMG Package: LogViewer-${VERSION}-macOS-arm64.dmg (${DMG_SIZE_ARM64})"
    else
        echo "ARM64 DMG Package: NOT FOUND"
    fi
fi

if [ "$BUILD_X86_64" = true ]; then
    if [ -d "dist_x86_64/Log Viewer.app" ]; then
        APP_SIZE_X86_64=$(du -sh "dist_x86_64/Log Viewer.app" | cut -f1)
        echo "x86_64 App Bundle: dist_x86_64/Log Viewer.app (${APP_SIZE_X86_64})"
    else
        echo "x86_64 App Bundle: NOT FOUND"
    fi

    if [ -f "LogViewer-${VERSION}-macOS-x86_64.dmg" ]; then
        DMG_SIZE_X86_64=$(du -sh "LogViewer-${VERSION}-macOS-x86_64.dmg" | cut -f1)
        echo "x86_64 DMG Package: LogViewer-${VERSION}-macOS-x86_64.dmg (${DMG_SIZE_X86_64})"
    else
        echo "x86_64 DMG Package: NOT FOUND"
    fi
fi

# Step 5: Installation instructions
echo ""
echo "Installation Instructions:"
echo "========================="
if [ "$BUILD_ARM64" = true ]; then
    echo "Apple Silicon Macs (M1/M2/M3):"
    echo "  1. Double-click LogViewer-${VERSION}-macOS-arm64.dmg to mount"
    echo "  2. Drag 'Log Viewer.app' to Applications folder"
    echo ""
fi
if [ "$BUILD_X86_64" = true ]; then
    echo "Intel Macs:"
    echo "  1. Double-click LogViewer-${VERSION}-macOS-x86_64.dmg to mount"
    echo "  2. Drag 'Log Viewer.app' to Applications folder"
    echo ""
fi
echo "Both versions will work on either architecture via Rosetta 2"
echo "For best performance, choose the version that matches your Mac's processor"
echo ""
echo "Command-line usage:"
echo "  open -a 'Log Viewer' /path/to/file.log"

echo ""
echo "============================================"
echo "Dual architecture macOS build completed!"
echo "============================================" 