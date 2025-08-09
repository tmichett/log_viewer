#!/bin/bash
# Icon resizing script for Flatpak build
# Creates properly sized icons for Flatpak compliance

set -e

# Check if FLATPAK_DEST is set
FLATPAK_DEST=${FLATPAK_DEST:-/app}

# Source and destination paths
SOURCE_ICON="rpmbuild/SOURCES/smallicon.png"
DEST_BASE="${FLATPAK_DEST}/share/icons/hicolor"

# Check if source icon exists
if [[ ! -f "$SOURCE_ICON" ]]; then
    echo "Error: Source icon not found: $SOURCE_ICON"
    exit 1
fi

echo "Source icon found: $SOURCE_ICON"

# Check if ImageMagick convert is available
if command -v convert >/dev/null 2>&1; then
    echo "ImageMagick convert available - will resize icons"
    CONVERT_AVAILABLE=true
else
    echo "ImageMagick convert not available - will copy original (may cause size warnings)"
    CONVERT_AVAILABLE=false
fi

# Icon sizes to create
SIZES=(32 48 64 128 256)

# Create icons for each size
for size in "${SIZES[@]}"; do
    # Create size directory
    size_dir="${DEST_BASE}/${size}x${size}/apps"
    mkdir -p "$size_dir"
    
    # Destination path
    dest_path="${size_dir}/com.michettetech.LogViewer.png"
    
    if $CONVERT_AVAILABLE; then
        # Use ImageMagick to resize
        if convert "$SOURCE_ICON" -resize "${size}x${size}" "$dest_path"; then
            echo "Resized icon: ${size}x${size} -> $dest_path"
        else
            echo "Convert failed, copying original instead"
            cp "$SOURCE_ICON" "$dest_path"
        fi
    else
        # Fallback: copy original icon
        cp "$SOURCE_ICON" "$dest_path"
        echo "Copied icon: ${size}x${size} -> $dest_path (original size)"
    fi
done

echo "All icons created successfully!"

# Debug: Show what we created
echo "Created icon files:"
find "${DEST_BASE}" -name "com.michettetech.LogViewer.png" -ls 2>/dev/null || true
