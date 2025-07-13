#!/bin/bash
## Script to Build macOS App Bundle
## Author: tmichett@redhat.com

# Check if we're running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

echo "Building Log Viewer for macOS..."

# Install uv for better Python dependency management
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Clean up any existing virtual environment
rm -rf log_viewer_venv

# Create and activate virtual environment
uv venv log_viewer_venv
source log_viewer_venv/bin/activate

# Install all required dependencies from requirements.txt
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install PyInstaller and Pillow (for icon conversion)
echo "Installing PyInstaller and Pillow..."
uv pip install PyInstaller Pillow

# Clean up any existing build artifacts
rm -rf build dist

# Build the macOS app bundle
echo "Building macOS app bundle..."
pyinstaller --noconfirm log_viewer_macos.spec

# Check if build was successful
if [ -d "dist/Log Viewer.app" ]; then
    echo "Build completed successfully!"
    echo "App bundle location: $(pwd)/dist/Log Viewer.app"
    echo "App bundle size: $(du -sh "dist/Log Viewer.app" | cut -f1)"
    
    # Make the app executable
    chmod +x "dist/Log Viewer.app/Contents/MacOS/log_viewer"
    
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