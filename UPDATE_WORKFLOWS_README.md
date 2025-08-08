# GitHub Workflows Update Summary

## What Was Updated

The GitHub Actions workflows have been updated to include Flatpak package building and distribution. This update ensures that when releases are created, they now include 6 artifacts instead of 5:

### New Flatpak Build Workflow
- **Created**: `.github/workflows/flatpak_build.yml`
- **Triggers**: On version tag push (v*) or manual dispatch
- **Output**: `LogViewer-{VERSION}.flatpak` artifact

### Updated Release Workflows

#### 1. `automated_comprehensive_release.yml`
- **Added**: "Build Flatpak Package" to workflow triggers
- **Added**: Flatpak artifact downloading
- **Updated**: Release description to include Flatpak installation instructions

#### 2. `release_on_tag.yml`
- **Added**: Flatpak artifact downloading from "Build Flatpak Package" workflow
- **Added**: Flatpak file copying to final artifacts
- **Updated**: Release description to include Flatpak installation instructions

#### 3. `manual_comprehensive_release.yml`
- **Added**: Flatpak build to the list of required builds
- **Updated**: Release description to include Flatpak installation instructions
- **Added**: Flatpak file to the list of artifacts to upload manually

## Release Artifacts Summary

Each release now includes **6 artifacts**:

| Platform | File | Description |
|----------|------|-------------|
| macOS (Apple Silicon) | `LogViewer-{VERSION}-macOS-arm64.dmg` | Native M1/M2/M3 Mac app |
| macOS (Intel) | `LogViewer-{VERSION}-macOS-x86_64.dmg` | Native Intel Mac app |
| Windows (Installer) | `LogViewer-{VERSION}-Setup.exe` | Windows installer package |
| Windows (Portable) | `LogViewer-{VERSION}.exe` | Standalone Windows executable |
| Linux (RPM) | `LogViewer-{VERSION}-0.rpm` | Red Hat/Fedora package |
| **Linux (Flatpak)** | `LogViewer-{VERSION}.flatpak` | **Universal Linux package** |

## Installation Instructions Added

The release descriptions now include Flatpak installation instructions:

```bash
# Install Flatpak package
flatpak install LogViewer-{VERSION}.flatpak

# Run the application
flatpak run com.michettetech.LogViewer
```

## System Requirements Updated

The system requirements section now distinguishes between:
- **Linux RPM**: Red Hat/Fedora-based distributions
- **Linux Flatpak**: Any Linux distribution with Flatpak support

## Workflow Dependencies

The automated release workflow now waits for all 4 build workflows:
1. Build macOS App - Dual Architecture
2. Build Windows App
3. Build RPM Package
4. **Build Flatpak Package** (NEW)

## Testing the Updated Workflows

To test the updated workflows:

1. **Update version**: 
   ```bash
   echo "VERSION=3.2.0" > rpmbuild/SOURCES/Build_Version
   git add rpmbuild/SOURCES/Build_Version
   git commit -m "Bump version to 3.2.0"
   git push origin main
   ```

2. **Create and push tag**:
   ```bash
   git tag v3.2.0
   git push origin v3.2.0
   ```

3. **Monitor Actions tab** for all 4 build workflows to complete

4. **Verify release** contains all 6 artifacts

## Benefits of Flatpak Addition

- **Universal Linux Support**: Works on all Linux distributions
- **Sandboxed Security**: Isolated application environment
- **Easy Installation**: Single package with all dependencies
- **No Root Required**: User-level installation
- **Automatic Updates**: Through Flatpak update mechanism

## Maintenance Notes

- The Flatpak build uses Ubuntu latest with Flatpak runtime 23.08
- Python dependencies are bundled during the build process
- The Flatpak manifest is located at `com.michettetech.LogViewer.yaml`
- Desktop integration files are automatically included

This update ensures comprehensive Linux support while maintaining the existing workflow structure and release process.
