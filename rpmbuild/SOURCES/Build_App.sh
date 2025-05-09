#!/usr/bin/bash
## Script to Build Executable Python App
## Author: tmichett@redhat.com

curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv log_viewer
source log_viewer/bin/activate
uv pip install PyInstaller PyQt6 PyYA
pyinstaller rpmbuild/SOURCES/log_viewer.spec

cp rpmbuild/SOURCES/dist/log_viewer .



