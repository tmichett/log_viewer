#!/bin/bash
## Script to Build macOS App Bundle for Intel x86_64
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
echo "Building Log Viewer for macOS Intel x86_64 - Version: $VERSION"

# Set architecture
ARCH="x86_64"
echo "Target architecture: $ARCH"

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

if [ ! -f "log_viewer_macos_x86_64.spec" ]; then
    echo "Error: log_viewer_macos_x86_64.spec not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

if [ ! -f "Build_Version" ]; then
    echo "Error: Build_Version file not found!"
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

# Set environment variables for x86_64 cross-compilation
export ARCHFLAGS="-arch x86_64"
export _PYTHON_HOST_PLATFORM="macosx-10.14-x86_64"
export MACOSX_DEPLOYMENT_TARGET="10.14"

# Install uv for better Python dependency management (only in interactive mode)
if [[ "$USE_UV" == "true" ]] && ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Clean up any existing virtual environment
rm -rf log_viewer_venv_x86_64

if [[ "$USE_UV" == "true" ]] && command -v uv &> /dev/null; then
    echo "Using uv for dependency management with x86_64 architecture..."
    # Create and activate virtual environment using x86_64 Python
    arch -x86_64 python -m venv log_viewer_venv_x86_64
    source log_viewer_venv_x86_64/bin/activate
    
    # Install all required dependencies from requirements.txt for x86_64
    echo "Installing dependencies for x86_64 architecture..."
    arch -x86_64 pip install --upgrade pip
    arch -x86_64 pip install --only-binary=:all: --platform macosx_10_14_x86_64 --target ./temp_packages_x86_64 -r requirements.txt
    arch -x86_64 pip install --find-links ./temp_packages_x86_64 --no-index -r requirements.txt
    
    # Install PyInstaller and Pillow (for icon conversion) for x86_64
    echo "Installing PyInstaller and Pillow for x86_64 architecture..."
    arch -x86_64 pip install PyInstaller Pillow
    
    # Clean up temporary packages
    rm -rf temp_packages_x86_64
else
    echo "Using standard pip for dependency management with x86_64 architecture..."
    # Create and activate virtual environment using x86_64 Python
    arch -x86_64 python -m venv log_viewer_venv_x86_64
    source log_viewer_venv_x86_64/bin/activate
    
    # Upgrade pip using x86_64 architecture
    arch -x86_64 pip install --upgrade pip
    
    # Install dependencies with x86_64 constraints
    echo "Installing dependencies for x86_64 architecture..."
    arch -x86_64 pip install --only-binary=:all: -r requirements.txt
    
    # Install PyInstaller and Pillow (for icon conversion) for x86_64
    echo "Installing PyInstaller and Pillow for x86_64 architecture..."
    arch -x86_64 pip install PyInstaller Pillow
fi

# Verify PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller not found after installation"
    exit 1
fi

echo "PyInstaller version: $(pip show pyinstaller | grep Version)"

# Clean up any existing build artifacts for this architecture
rm -rf build_x86_64 dist_x86_64

# Build the macOS app bundle using x86_64 architecture
echo "Building macOS app bundle for $ARCH..."
arch -x86_64 pyinstaller --noconfirm --distpath dist_x86_64 --workpath build_x86_64 log_viewer_macos_x86_64.spec

# Check PyInstaller exit code
if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build failed"
    echo "Build directory contents:"
    ls -la build_x86_64/ || echo "build_x86_64 directory does not exist"
    echo "Dist directory contents:"
    ls -la dist_x86_64/ || echo "dist_x86_64 directory does not exist"
    exit 1
fi

# Check if build was successful
if [ -d "dist_x86_64/Log Viewer.app" ]; then
    echo "Build completed successfully!"
    echo "App bundle location: $(pwd)/dist_x86_64/Log Viewer.app"
    echo "App bundle size: $(du -sh "dist_x86_64/Log Viewer.app" | cut -f1)"
    
    # Make the app executable
    chmod +x "dist_x86_64/Log Viewer.app/Contents/MacOS/log_viewer"
    
    # Check architecture of the built binary
    echo "Checking binary architecture..."
    if command -v file &> /dev/null; then
        file "dist_x86_64/Log Viewer.app/Contents/MacOS/log_viewer"
    fi
    if command -v lipo &> /dev/null; then
        echo "Architecture details:"
        lipo -info "dist_x86_64/Log Viewer.app/Contents/MacOS/log_viewer" || echo "Could not get architecture info"
    fi
    
    echo ""
    echo "NOTE: This app is built for Intel x86_64 architecture."
    echo "Apple Silicon Macs will run this app automatically using Rosetta 2 translation."
    
    # Test the app can be launched
    echo "Testing app launch..."
    open "dist_x86_64/Log Viewer.app" --args --help &
    sleep 2
    pkill -f "log_viewer" || true
    
    echo "macOS x86_64 app bundle created successfully!"
    echo "You can now run: open 'dist_x86_64/Log Viewer.app'"
else
    echo "Error: Build failed - app bundle not found"
    exit 1
fi 