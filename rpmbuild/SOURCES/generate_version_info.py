#!/usr/bin/env python3
"""
Generate version_info.txt for Windows builds from Build_Version file
Author: travis@michettetech.com
"""

import os
import sys

def read_version_from_file():
    """Read version from Build_Version file"""
    try:
        with open('Build_Version', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('VERSION='):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        print("Warning: Build_Version file not found, using default version")
    return "3.0.0"

def parse_version(version_str):
    """Parse version string into major, minor, patch, build"""
    try:
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 3
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        build = int(parts[3]) if len(parts) > 3 else 0
        return major, minor, patch, build
    except (ValueError, IndexError):
        print(f"Warning: Could not parse version '{version_str}', using defaults")
        return 3, 0, 0, 0

def generate_version_info(version_str):
    """Generate version_info.txt content"""
    major, minor, patch, build = parse_version(version_str)
    
    return f"""# Version information for Windows executable
# This file is used by PyInstaller to embed version information into the EXE
# Generated from Build_Version file: VERSION={version_str}

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'Michette Technologies'),
            StringStruct(u'FileDescription', u'Log Viewer - A powerful log file viewer with ANSI color support'),
            StringStruct(u'FileVersion', u'{version_str}'),
            StringStruct(u'InternalName', u'LogViewer'),
            StringStruct(u'LegalCopyright', u'(C) 2024 Michette Technologies'),
            StringStruct(u'OriginalFilename', u'LogViewer.exe'),
            StringStruct(u'ProductName', u'Log Viewer'),
            StringStruct(u'ProductVersion', u'{version_str}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

def main():
    """Main function"""
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Read version
    version = read_version_from_file()
    print(f"Generating version_info.txt for version: {version}")
    
    # Generate version info
    version_info_content = generate_version_info(version)
    
    # Write to file with UTF-8 encoding
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    print("version_info.txt generated successfully")

if __name__ == "__main__":
    main() 