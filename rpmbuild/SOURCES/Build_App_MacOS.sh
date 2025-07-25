#!/bin/bash
## Script to Build macOS App Bundle
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
        echo "3.0.0"
    fi
}

VERSION=$(get_version)
echo "Building Log Viewer for macOS - Version: $VERSION"

# Debug information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Contents of current directory:"
ls -la

# Check if required files exist
if [ ! -f "log_viewer.py" ]; then
    echo "Error: log_viewer.py not found!"
    exit 1
fi

if [ ! -f "log_viewer_macos.spec" ]; then
    echo "Error: log_viewer_macos.spec not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Check if we're in CI environment
if [[ -n "$CI" || -n "$GITHUB_ACTIONS" || -n "$RUNNER_OS" ]]; then
    echo "Detected CI environment - using standard pip"
    USE_UV=false
else
    echo "Detected interactive environment - trying uv first"
    USE_UV=true
fi

# Install uv for better Python dependency management (only in interactive mode)
if [[ "$USE_UV" == "true" ]] && ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Clean up any existing virtual environment
rm -rf log_viewer_venv

if [[ "$USE_UV" == "true" ]] && command -v uv &> /dev/null; then
    echo "Using uv for dependency management..."
    # Create and activate virtual environment
    uv venv log_viewer_venv
    source log_viewer_venv/bin/activate
    
    # Install all required dependencies from requirements.txt
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
    
    # Install PyInstaller and Pillow (for icon conversion)
    echo "Installing PyInstaller and Pillow..."
    uv pip install PyInstaller Pillow
else
    echo "Using standard pip for dependency management..."
    # Create and activate virtual environment
    python -m venv log_viewer_venv
    source log_viewer_venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install all required dependencies from requirements.txt
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Install PyInstaller and Pillow (for icon conversion) 
    echo "Installing PyInstaller and Pillow..."
    pip install PyInstaller Pillow
fi

# Verify PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller not found after installation"
    exit 1
fi

echo "PyInstaller version: $(pip show pyinstaller | grep Version)"

# Clean up any existing build artifacts
rm -rf build dist

# Build the macOS app bundle
echo "Building macOS app bundle..."
pyinstaller --noconfirm log_viewer_macos.spec

# Check PyInstaller exit code
if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build failed"
    echo "Build directory contents:"
    ls -la build/ || echo "build directory does not exist"
    echo "Dist directory contents:"
    ls -la dist/ || echo "dist directory does not exist"
    exit 1
fi

# Check if build was successful
if [ -d "dist/Log Viewer.app" ]; then
    echo "Build completed successfully!"
    echo "App bundle location: $(pwd)/dist/Log Viewer.app"
    echo "App bundle size: $(du -sh "dist/Log Viewer.app" | cut -f1)"
    
    # Make the app executable
    chmod +x "dist/Log Viewer.app/Contents/MacOS/log_viewer"
    
    # Check architecture of the built binary
    echo "Checking binary architecture..."
    if command -v file &> /dev/null; then
        file "dist/Log Viewer.app/Contents/MacOS/log_viewer"
    fi
    if command -v lipo &> /dev/null; then
        echo "Architecture details:"
        lipo -info "dist/Log Viewer.app/Contents/MacOS/log_viewer" || echo "Could not get architecture info"
    fi
    
    echo ""
    echo "NOTE: This app is built for ARM64 (Apple Silicon) architecture."
    echo "Intel-based Macs will run this app automatically using Rosetta 2 translation."
    echo "Rosetta 2 is included with macOS Big Sur (11.0) and later."
    
    # Test the app can be launched
    echo "Testing app launch..."
    open "dist/Log Viewer.app" --args --help &
    sleep 2
    pkill -f "log_viewer"
    
    echo "macOS app bundle created successfully!"
    echo "You can now run: open 'dist/Log Viewer.app'"
else
    echo "Error: Build failed - app bundle not found"
    exit 1
fi 