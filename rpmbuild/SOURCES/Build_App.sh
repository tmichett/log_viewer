#!/usr/bin/bash
## Script to Build Executable Python App
## Author: travis@michettetech.com

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"

# Change to the SOURCES directory where the files are located
cd "$SCRIPT_DIR"
echo "Working directory: $(pwd)"

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
echo "Building Log Viewer version: $VERSION"

# Update RPM spec file with current version
echo "Updating RPM spec file..."
./update_rpm_version.sh

# Install uv for better Python dependency management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clean up any existing virtual environment
rm -rf log_viewer_venv

# Create and activate virtual environment with different name to avoid conflicts
uv venv log_viewer_venv
source log_viewer_venv/bin/activate

# Install all required dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

# Install PyInstaller
echo "Installing PyInstaller..."
uv pip install PyInstaller

# Build the executable
echo "Building executable with PyInstaller..."
pyinstaller --noconfirm ./log_viewer.spec

# Copy the built executable to current directory (we're already in SOURCES)
if [ -f "./dist/log_viewer" ]; then
    cp ./dist/log_viewer ./
    echo "Build completed successfully!"
    echo "Executable location: $(pwd)/log_viewer"
    echo "Executable size: $(du -h log_viewer | cut -f1)"
else
    echo "Error: Build failed - executable not found in dist/"
    exit 1
fi 



