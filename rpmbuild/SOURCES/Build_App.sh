#!/usr/bin/bash
## Script to Build Executable Python App
## Author: tmichett@redhat.com

pip3 install PyInstaller PyQt6 PyYAML
pyinstaller rpmbuild/SOURCES/log_viewer.spec

cp rpmbuild/SOURCES/dist/log_viewer .



