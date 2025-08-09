#!/bin/bash
# Wrapper script to set up Qt environment for Flatpak

# Set Qt environment variables
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export QT_ACCESSIBILITY=1

# Debug output
echo "Qt environment:"
echo "QT_QPA_PLATFORM=$QT_QPA_PLATFORM"
echo "DISPLAY=$DISPLAY"
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"

# Try to set display if not set
if [ -z "$DISPLAY" ] && [ -n "$WAYLAND_DISPLAY" ]; then
    echo "No DISPLAY set, but WAYLAND_DISPLAY available, trying wayland-egl platform"
    export QT_QPA_PLATFORM=wayland-egl
fi

# Show available Qt platform plugins
echo "Available Qt platforms:"
/app/bin/log_viewer -platform help 2>&1 || echo "Could not list platforms"

# Run the actual application
echo "Starting LogViewer..."
exec /app/bin/log_viewer "$@"
