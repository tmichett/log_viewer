#!/bin/bash

# Log Viewer Flatpak Build Script
# This script builds the Log Viewer application as a Flatpak package

set -e

APP_ID="com.michettetech.LogViewer"
MANIFEST_FILE="${APP_ID}.yaml"
BUILD_DIR="flatpak-build"
REPO_DIR="flatpak-repo"

echo "=== Log Viewer Flatpak Build Script ==="
echo "Building Flatpak for: $APP_ID"

# Check if flatpak-builder is installed
if ! command -v flatpak-builder &> /dev/null; then
    echo "Error: flatpak-builder is not installed."
    echo "Please install it with: sudo apt install flatpak-builder (Ubuntu/Debian)"
    echo "                   or: sudo dnf install flatpak-builder (Fedora)"
    exit 1
fi

# Check if required runtime is installed
if ! flatpak list --runtime | grep -q "org.freedesktop.Platform.*23.08"; then
    echo "Installing required Flatpak runtime and SDK..."
    flatpak install --user -y flathub org.freedesktop.Platform//23.08
    flatpak install --user -y flathub org.freedesktop.Sdk//23.08
fi

# Create directories
mkdir -p "$BUILD_DIR"
mkdir -p "$REPO_DIR"

# Build the Flatpak
echo "Building Flatpak package..."
flatpak-builder --user --install-deps-from=flathub --repo="$REPO_DIR" "$BUILD_DIR" "$MANIFEST_FILE"

# Install the built package
echo "Installing the built package..."
flatpak --user remote-add --no-gpg-verify --if-not-exists logviewer-origin "$REPO_DIR"
flatpak --user install -y logviewer-origin "$APP_ID"

echo ""
echo "=== Build completed successfully! ==="
echo ""
echo "To run the application:"
echo "  flatpak run $APP_ID"
echo ""
echo "To uninstall:"
echo "  flatpak --user uninstall $APP_ID"
echo ""
echo "To create a bundle for distribution:"
echo "  flatpak build-bundle $REPO_DIR ${APP_ID}.flatpak $APP_ID"
echo ""

# Optionally create a bundle
read -p "Create a .flatpak bundle for distribution? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating bundle..."
    flatpak build-bundle "$REPO_DIR" "${APP_ID}.flatpak" "$APP_ID"
    echo "Bundle created: ${APP_ID}.flatpak"
fi

echo "Done!"
