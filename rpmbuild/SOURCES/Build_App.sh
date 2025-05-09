#!/usr/bin/bash
## Script to Build Executable Python App
## Author: tmichett@redhat.com

pip3 install PyInstaller PyQt6 PyYAML
pyinstaller log_viewer.spec

cp dist/log_viewer .



