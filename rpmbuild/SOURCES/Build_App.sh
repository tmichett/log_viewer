#!/usr/bin/bash
## Script to Build Executable Python App
## Author: tmichett@redhat.com

# Install uv for better Python dependency management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv log_viewer
source log_viewer/bin/activate

# Install all required dependencies with correct versions
uv pip install PyInstaller PyQt6 PyYAML argparse

# Build the executable
pyinstaller rpmbuild/SOURCES/log_viewer.spec

# Copy the built executable to SOURCES directory
cp dist/log_viewer rpmbuild/SOURCES/ 



