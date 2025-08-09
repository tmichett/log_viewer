#!/usr/bin/env python3
"""
Icon resizing script for Flatpak build
Resizes the source icon to multiple sizes for proper Flatpak compliance
"""

import os
import sys
from PIL import Image

def resize_icons():
    """Resize source icon to multiple sizes"""
    
    # Check if FLATPAK_DEST is set
    flatpak_dest = os.environ.get('FLATPAK_DEST', '/app')
    
    # Source and destination paths
    source_icon = 'rpmbuild/SOURCES/smallicon.png'
    dest_base = f'{flatpak_dest}/share/icons/hicolor'
    
    # Check if source icon exists
    if not os.path.exists(source_icon):
        print(f"Error: Source icon not found: {source_icon}")
        sys.exit(1)
    
    # Open source image
    try:
        img = Image.open(source_icon)
        print(f"Original icon size: {img.size}")
    except Exception as e:
        print(f"Error opening source icon: {e}")
        sys.exit(1)
    
    # Icon sizes to create
    sizes = [(32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create icons for each size
    for size in sizes:
        try:
            # Create size directory
            size_dir = f"{dest_base}/{size[0]}x{size[1]}/apps"
            os.makedirs(size_dir, exist_ok=True)
            
            # Resize image
            resized = img.resize(size, Image.Resampling.LANCZOS)
            
            # Save resized icon
            dest_path = f"{size_dir}/com.michettetech.LogViewer.png"
            resized.save(dest_path, 'PNG')
            
            print(f"Created icon: {size[0]}x{size[1]} -> {dest_path}")
            
        except Exception as e:
            print(f"Error creating {size[0]}x{size[1]} icon: {e}")
            sys.exit(1)
    
    print("All icons created successfully!")

if __name__ == "__main__":
    resize_icons()
