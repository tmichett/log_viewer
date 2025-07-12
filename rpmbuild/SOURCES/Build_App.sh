#!/usr/bin/bash
## Script to Build Executable Python App
## Author: tmichett@redhat.com

# Install uv for better Python dependency management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clean up any existing virtual environment
rm -rf log_viewer_venv

# Create and activate virtual environment with different name to avoid conflicts
uv venv log_viewer_venv
source log_viewer_venv/bin/activate

# Install all required dependencies from requirements.txt
uv pip install -r requirements.txt

# Install PyInstaller
uv pip install PyInstaller

# Build the executable
pyinstaller ./log_viewer.spec

# Copy the built executable to current directory (we're already in SOURCES)
cp ./dist/log_viewer ./

echo "Build completed successfully!"
echo "Executable location: $(pwd)/log_viewer"
echo "Executable size: $(du -h log_viewer | cut -f1)" 



