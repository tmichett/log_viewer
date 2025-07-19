# Release Process Guide

This document outlines the process for creating releases of Log Viewer using the automated GitHub Actions workflows.

## Overview

The Log Viewer project uses a comprehensive release process that builds artifacts for all platforms and creates a single, unified release. This process ensures all platform-specific builds are included and properly versioned.

## Release Workflow Components

### Platform Build Workflows (Auto-triggered)
When a version tag is pushed, these workflows automatically trigger:

1. **`macos_build_dual.yml`** - Builds macOS applications for both architectures
   - Apple Silicon (arm64): `LogViewer-{VERSION}-macOS-arm64.dmg`
   - Intel (x86_64): `LogViewer-{VERSION}-macOS-x86_64.dmg`

2. **`windows_build.yml`** - Builds Windows applications
   - Portable: `LogViewer-{VERSION}.exe`
   - Installer: `LogViewer-{VERSION}-Setup.exe`

3. **`rpm_build.yml`** - Builds Linux RPM package
   - RPM Package: `LogViewer-{VERSION}-0.rpm`

### Release Creation Workflow (Manual)
The **`manual_comprehensive_release.yml`** workflow creates a unified draft release with all artifacts.

## Step-by-Step Release Process

### 1. Version Preparation

Update the version in the central version file:
```bash
# Update to new version (e.g., 3.2.0)
echo "VERSION=3.2.0" > rpmbuild/SOURCES/Build_Version

# Commit the version change
git add rpmbuild/SOURCES/Build_Version
git commit -m "Bump version to 3.2.0"
git push origin main
```

### 2. Create and Push Version Tag

```bash
# Create the version tag
git tag v3.2.0

# Push the tag to trigger builds
git push origin v3.2.0
```

### 3. Monitor Platform Builds

1. Go to the **Actions** tab in GitHub
2. Monitor the progress of all three platform builds:
   - ✅ Build macOS App - Dual Architecture
   - ✅ Build Windows App
   - ✅ Build RPM

3. Wait for all builds to complete successfully (green checkmarks)

### 4. Create Comprehensive Release

1. Go to **Actions** → **Manual Comprehensive Release**
2. Click **Run workflow**
3. Enter the tag name: `v3.2.0`
4. Ensure "Include all platform artifacts" is checked
5. Click **Run workflow**

This creates a draft release with:
- Professional release description
- Platform-specific installation instructions
- Feature highlights
- System requirements

### 5. Add Artifacts to Release

#### Download Artifacts from Workflows
1. Go to **Actions** → Find the completed workflow runs
2. Download artifacts from each platform build:
   - From **macOS Dual Build**: Download both DMG files
   - From **Windows Build**: Download EXE and installer
   - From **RPM Build**: Download RPM package

#### Upload to Draft Release
1. Go to **Releases** → Find the draft release
2. Drag and drop all downloaded files:
   - `LogViewer-3.2.0-macOS-arm64.dmg`
   - `LogViewer-3.2.0-macOS-x86_64.dmg`
   - `LogViewer-3.2.0-Setup.exe`
   - `LogViewer-3.2.0.exe`
   - `LogViewer-3.2.0-0.rpm`

### 6. Review and Publish

1. **Review the release**:
   - Check that all 5 files are attached
   - Verify the release description is accurate
   - Confirm version numbers are correct

2. **Publish the release**:
   - Click **Publish release**
   - The release becomes public and triggers notifications

## Release Artifacts Summary

Each release includes exactly **5 artifacts**:

| Platform | File | Description |
|----------|------|-------------|
| macOS (Apple Silicon) | `LogViewer-{VERSION}-macOS-arm64.dmg` | Native M1/M2/M3 Mac app |
| macOS (Intel) | `LogViewer-{VERSION}-macOS-x86_64.dmg` | Native Intel Mac app |
| Windows (Installer) | `LogViewer-{VERSION}-Setup.exe` | Windows installer package |
| Windows (Portable) | `LogViewer-{VERSION}.exe` | Standalone Windows executable |
| Linux (RPM) | `LogViewer-{VERSION}-0.rpm` | Red Hat/Fedora package |

## Version Management

### Centralized Versioning
All builds use the version from `rpmbuild/SOURCES/Build_Version`:
```bash
VERSION=3.2.0
```

### Automatic Updates
The build processes automatically update:
- **RPM spec files** (via `update_rpm_version.sh`)
- **Windows installer scripts** (via `update_inno_version.py`)
- **Windows version info** (via `generate_version_info.py`)
- **macOS app bundles** (via PyInstaller spec files)

### Consistent Naming
All artifacts follow the pattern: `LogViewer-{VERSION}-{PLATFORM}.{EXT}`

## Troubleshooting

### Build Failures
If any platform build fails:
1. Check the Actions logs for specific errors
2. Fix the issue and push changes
3. Re-tag if necessary: `git tag -d v3.2.0 && git push origin :refs/tags/v3.2.0`
4. Create a new tag and restart the process

### Missing Artifacts
If artifacts are missing from a workflow:
1. Check if the workflow completed successfully
2. Look for the artifacts in the workflow's artifacts section
3. Re-run the workflow if necessary

### Release Issues
If there are issues with the release:
1. Edit the draft release to fix any problems
2. Re-upload artifacts if needed
3. Ensure all 5 files are present before publishing

## Best Practices

1. **Test Before Release**: Always test builds locally before creating a release
2. **Version Consistency**: Ensure the version in `Build_Version` matches the tag
3. **Complete Builds**: Wait for all platform builds to complete before creating the release
4. **Artifact Verification**: Verify all 5 artifacts are present and correctly named
5. **Release Notes**: Review the auto-generated release description for accuracy

## Support

For issues with the release process:
- Check existing GitHub Issues
- Review workflow logs in the Actions tab
- Contact: tmichett@redhat.com

---

**Organization**: Michette Technologies  
**Project**: Log Viewer  
**Last Updated**: 2024 