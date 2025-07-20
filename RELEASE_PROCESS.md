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

### Release Creation Workflows

#### Automated Release (Recommended)
The **`release_on_tag.yml`** workflow automatically creates releases when tags are pushed:
- Triggers on tag push (e.g., `v3.2.0`)
- Waits for all platform builds to complete
- Downloads artifacts from completed workflows
- Creates a draft release with all artifacts attached
- No manual intervention required

#### Manual Release (Alternative)
The **`manual_comprehensive_release.yml`** workflow creates a unified draft release with all artifacts when triggered manually.

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

# Push the tag to trigger builds and automated release
git push origin v3.2.0
```

### 3. Automated Release Process (Default)

When you push a tag, the automated workflow handles everything:

1. **Platform Builds Trigger**: All three build workflows start automatically
2. **Automated Waiting**: The release workflow waits for builds to complete
3. **Artifact Collection**: Downloads all artifacts using GitHub CLI
4. **Draft Release Creation**: Creates a comprehensive draft release with:
   - Professional release description
   - Platform-specific installation instructions
   - All 5 artifacts automatically attached

**No manual intervention required!** Just monitor the **Actions** tab for completion.

### 4. Manual Release Process (Alternative)

If you prefer manual control or the automated process fails:

1. **Wait for Platform Builds**: Monitor the **Actions** tab until all builds complete
2. **Trigger Manual Release**:
   - Go to **Actions** → **Manual Comprehensive Release**
   - Click **Run workflow**
   - Enter the tag name: `v3.2.0`
   - Click **Run workflow**

3. **Manual Artifact Upload** (if needed):
   - Download artifacts from completed workflow runs
   - Upload to the draft release manually

### 5. Review and Publish

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
- **Linux executables** (via PyInstaller spec file with bundled Build_Version)

### Consistent Naming
All artifacts follow the pattern: `LogViewer-{VERSION}-{PLATFORM}.{EXT}`

## Troubleshooting

### Build Failures
If any platform build fails:
1. Check the Actions logs for specific errors
2. Fix the issue and push changes
3. Re-tag if necessary: `git tag -d v3.2.0 && git push origin :refs/tags/v3.2.0`
4. Create a new tag and restart the process

### Version Sync Issues
If you encounter version mismatch errors (e.g., "Source file LogViewer-X.X.X.exe does not exist"):

#### Recent Fix: Windows Build Timing Issue (Fixed in v3.2.0)
This error was caused by a timing issue in the GitHub Actions Windows build workflow where `update_inno_version.py` was called **after** PyInstaller instead of before. This has been **fixed** by:
- Moving `update_inno_version.py` call to **before** PyInstaller in the workflow
- Adding `generate_version_info.py` call in the correct sequence
- Ensuring Inno Setup script is updated before the executable is built

#### If the issue persists:
1. **Check Build_Version**: Ensure the version is correct in `rpmbuild/SOURCES/Build_Version`
2. **Re-run Version Scripts**: Manually run the version update scripts:
   ```bash
   cd rpmbuild/SOURCES
   python3 update_inno_version.py    # Updates Windows installer script
   python3 generate_version_info.py  # Updates Windows version info
   ./update_rpm_version.sh           # Updates RPM spec file
   ```
3. **Verify Updates**: Check that all files reference the same version
4. **Commit and Re-build**: Commit the version updates and trigger a new build

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
- Contact: travis@michettetech.com

---

**Organization**: Michette Technologies  
**Project**: Log Viewer  
**Last Updated**: 2024 