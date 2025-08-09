#!/usr/bin/env python3
"""
Icon resizing script for Flatpak build
Resizes the source icon to multiple sizes for proper Flatpak compliance
"""

import os
import sys
import subprocess
import shutil

def resize_icons():
    """Resize source icon to multiple sizes with fallback to copying"""
    
    # Check if FLATPAK_DEST is set
    flatpak_dest = os.environ.get('FLATPAK_DEST', '/app')
    
    # Source and destination paths
    source_icon = 'rpmbuild/SOURCES/smallicon.png'
    dest_base = f'{flatpak_dest}/share/icons/hicolor'
    
    # Check if source icon exists
    if not os.path.exists(source_icon):
        print(f"Error: Source icon not found: {source_icon}")
        sys.exit(1)
    
    print(f"Source icon found: {source_icon}")
    
    # Check if convert is available
    convert_available = False
    try:
        subprocess.run(['convert', '--version'], capture_output=True, check=True)
        convert_available = True
        print("ImageMagick convert command available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ImageMagick convert not available, will copy original icon")
    
    # Check original icon size
    if convert_available:
        try:
            result = subprocess.run(['identify', '-format', '%wx%h', source_icon], 
                                  capture_output=True, text=True, check=True)
            print(f"Original icon size: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not identify source icon: {e}")
    
    # Icon sizes to create
    sizes = [32, 48, 64, 128, 256]
    
    # Create icons for each size
    for size in sizes:
        try:
            # Create size directory
            size_dir = f"{dest_base}/{size}x{size}/apps"
            os.makedirs(size_dir, exist_ok=True)
            
            # Destination path
            dest_path = f"{size_dir}/com.michettetech.LogViewer.png"
            
            if convert_available:
                # Use ImageMagick convert to resize
                cmd = ['convert', source_icon, '-resize', f'{size}x{size}', dest_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"Resized icon: {size}x{size} -> {dest_path}")
            else:
                # Fallback: copy original icon (better than failing)
                shutil.copy2(source_icon, dest_path)
                print(f"Copied icon: {size}x{size} -> {dest_path} (original size)")
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {size}x{size} icon: {e}")
            if e.stderr:
                print(f"Command output: {e.stderr}")
            # Try fallback copy
            try:
                shutil.copy2(source_icon, dest_path)
                print(f"Fallback: copied original icon to {dest_path}")
            except Exception as copy_error:
                print(f"Fallback copy also failed: {copy_error}")
                sys.exit(1)
        except Exception as e:
            print(f"Error creating {size}x{size} icon: {e}")
            sys.exit(1)
    
    print("All icons created successfully!")

if __name__ == "__main__":
    resize_icons()
