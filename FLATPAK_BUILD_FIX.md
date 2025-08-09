# Flatpak Build Fix

## Issues Fixed

### 1. Flathub Remote Configuration
**Problem**: The build was failing with "No remote refs found for 'flathub'" because the Flathub repository wasn't properly configured for flatpak-builder.

**Root Cause**: Using `--user` flag for remotes when flatpak-builder expects system-wide configuration.

**Fix Applied**:
- Changed from user-level (`--user`) to system-wide Flatpak setup
- Use `sudo flatpak remote-add` for system-wide Flathub configuration
- Install runtime and SDK system-wide with `sudo flatpak install`
- Remove `--user` flag from `flatpak-builder` command

### 2. Python Dependencies Installation
**Problem**: The manifest was trying to download specific wheel files from PyPI URLs which can be unreliable in CI environments.

**Fix Applied**:
- Simplified to use `pip3 install` with version constraints
- Added `--share=network` permission to allow internet access during build
- Removed complex file downloading and use direct pip installation

### 3. File Path References
**Problem**: The manifest referenced files that weren't in the expected locations during build.

**Fix Applied**:
- Changed to use `type: dir` source that includes the entire repo
- Updated install commands to use correct paths from `rpmbuild/SOURCES/`

## Updated Workflow

### Before:
```yaml
# User-level setup (problematic)
flatpak --user remote-add flathub ...
flatpak --user install flathub ...
flatpak-builder --user ...
```

### After:
```yaml
# System-level setup (working)
sudo flatpak remote-add flathub ...
sudo flatpak install flathub ...
flatpak-builder --install-deps-from=flathub ...
```

## Updated Manifest

### Before:
```yaml
# Complex wheel file downloads
- name: python3-pyqt6
  buildsystem: simple
  build-commands:
    - pip3 install --no-index --find-links="file://${PWD}" ...
  sources:
    - type: file
      url: https://files.pythonhosted.org/packages/...
```

### After:
```yaml
# Simple pip installation
- name: python3-dependencies
  buildsystem: simple
  build-commands:
    - pip3 install --prefix=${FLATPAK_DEST} PyQt6>=6.4.0 PyYAML>=6.0 Pillow>=9.0.0
```

## Expected Results

The next build should:
1. ✅ Properly configure Flathub repository
2. ✅ Install runtime and SDK successfully  
3. ✅ Build the Flatpak package without dependency errors
4. ✅ Create the `.flatpak` bundle file
5. ✅ Upload the artifact to GitHub Actions

## Testing

To test these fixes:
1. Push the updated workflow files to your repository
2. The next push/merge to main should trigger the Flatpak build
3. Monitor the GitHub Actions logs for successful completion

The build should now complete without the "No remote refs found for 'flathub'" error.
