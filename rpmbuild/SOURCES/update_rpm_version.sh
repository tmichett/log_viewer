#!/bin/bash
## Script to update RPM spec file with version from Build_Version
## Author: tmichett@redhat.com

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
echo "Updating RPM spec file with version: $VERSION"

# Update the spec file (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires empty string for -i flag
    sed -i "" "s/%define version.*/%define version $VERSION/" ../SPECS/LogViewer.spec
else
    # Linux version
    sed -i "s/%define version.*/%define version $VERSION/" ../SPECS/LogViewer.spec
fi

echo "RPM spec file updated successfully" 