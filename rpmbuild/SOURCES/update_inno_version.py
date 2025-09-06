#!/usr/bin/env python3
"""
Update Inno Setup installer script with version from Build_Version file
Author: travis@michettetech.com
"""

import os
import sys

def read_version_from_file():
    """Read version from Build_Version file"""
    try:
        with open('Build_Version', 'r') as f:
            for line in f:
                if line.startswith('VERSION='):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        print("Warning: Build_Version file not found, using default version")
    return "4.0.1"

def update_inno_script(version):
    """Update the Inno Setup script with the new version and executable name"""
    script_path = 'LogViewer_Installer.iss'
    
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found")
        return False
    
    # Read the script
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Replace the version line
    import re
    content = re.sub(r'#define MyAppVersion ".*"', f'#define MyAppVersion "{version}"', content)
    
    # Replace the executable name to include version
    versioned_exe_name = f'LogViewer-{version}.exe'
    content = re.sub(r'#define MyAppExeName ".*"', f'#define MyAppExeName "{versioned_exe_name}"', content)
    
    # Replace the source file reference in [Files] section (handles both versioned and unversioned)
    content = re.sub(r'Source: "LogViewer.*\.exe"', f'Source: "{versioned_exe_name}"', content)
    
    # Write back the updated script
    with open(script_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {script_path} with version {version} and executable name {versioned_exe_name}")
    return True

def main():
    """Main function"""
    # Read version
    version = read_version_from_file()
    print(f"Updating Inno Setup script for version: {version}")
    
    # Update the script
    if update_inno_script(version):
        print("Inno Setup script updated successfully")
    else:
        print("Failed to update Inno Setup script")
        sys.exit(1)

if __name__ == "__main__":
    main() 