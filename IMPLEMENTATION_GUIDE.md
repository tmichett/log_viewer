# Log Viewer - Dual Architecture Build Implementation Guide

## Overview

This guide documents the implementation of dual macOS architecture support (Intel x86_64 and Apple Silicon arm64) with centralized version management for the Log Viewer application.

## Summary of Changes

### 🎯 Key Achievements

1. **Dual Architecture Support**: Two separate macOS apps are now built
   - Intel x86_64 optimized for Intel-based Macs
   - Apple Silicon arm64 optimized for M1/M2/M3 Macs

2. **Architecture-Specific Naming**: All build artifacts include architecture suffix
   - `LogViewer-{VERSION}-macOS-x86_64.dmg`
   - `LogViewer-{VERSION}-macOS-arm64.dmg`

3. **Centralized Version Management**: All builds read from `rpmbuild/SOURCES/Build_Version`
   - Single source of truth: `VERSION=3.2.0` (current version)
   - Automatically propagates to all build artifacts

4. **Enhanced GitHub Actions**: New workflow supports parallel dual builds
   - ARM64 builds on `macos-latest` (Apple Silicon)
   - x86_64 builds on `macos-13` (Intel)
   - Automatic release creation with both architectures

## 📁 New Files Created

### Architecture-Specific PyInstaller Specs
- `rpmbuild/SOURCES/log_viewer_macos_x86_64.spec` - Intel x86_64 build configuration
- `rpmbuild/SOURCES/log_viewer_macos_arm64.spec` - Apple Silicon arm64 build configuration

### Architecture-Specific Build Scripts
- `rpmbuild/SOURCES/Build_App_MacOS_x86_64.sh` - Intel x86_64 app builder
- `rpmbuild/SOURCES/Build_App_MacOS_arm64.sh` - Apple Silicon arm64 app builder
- `rpmbuild/SOURCES/Create_DMG_MacOS_x86_64.sh` - Intel x86_64 DMG creator
- `rpmbuild/SOURCES/Create_DMG_MacOS_arm64.sh` - Apple Silicon arm64 DMG creator

### Comprehensive Build Scripts
- `rpmbuild/SOURCES/Build_All_MacOS_Dual.sh` - Builds both architectures
- `rpmbuild/SOURCES/generate_version_info.py` - Dynamic version info generator

### GitHub Actions
- `.github/workflows/macos_build_dual.yml` - Dual architecture CI/CD workflow

## 📋 Modified Files

### Existing Build Scripts (Now Version-Aware)
- `rpmbuild/SOURCES/Build_App_MacOS.sh` - Updated to read from Build_Version
- `rpmbuild/SOURCES/Create_DMG_MacOS.sh` - Updated for dynamic versioning
- `rpmbuild/SOURCES/Build_App.sh` - Updated for version management
- `rpmbuild/SOURCES/log_viewer_macos.spec` - Updated with version function

### Version Management
- `rpmbuild/SOURCES/version_info.txt` - Now auto-generated from Build_Version
- `rpmbuild/SOURCES/Build_Version` - Central version configuration

## 🚀 Usage Instructions

### Building Locally

#### Build Both Architectures
```bash
cd rpmbuild/SOURCES
./Build_All_MacOS_Dual.sh
```

#### Build Specific Architecture
```bash
# Intel x86_64 only
./Build_All_MacOS_Dual.sh --x86_64-only

# Apple Silicon arm64 only  
./Build_All_MacOS_Dual.sh --arm64-only
```

#### Individual Component Builds
```bash
# Intel x86_64
./Build_App_MacOS_x86_64.sh
./Create_DMG_MacOS_x86_64.sh

# Apple Silicon arm64
./Build_App_MacOS_arm64.sh
./Create_DMG_MacOS_arm64.sh
```

### Build Options
```bash
# Clean build (removes all artifacts)
./Build_All_MacOS_Dual.sh --clean

# Skip testing phase
./Build_All_MacOS_Dual.sh --skip-tests

# Combined options
./Build_All_MacOS_Dual.sh --clean --arm64-only --skip-tests
```

### Updating Version

Simply edit `rpmbuild/SOURCES/Build_Version`:
```bash
echo "VERSION=3.2.0" > rpmbuild/SOURCES/Build_Version
```

All build methods will automatically use the new version.

## 📦 Build Artifacts

### Directory Structure After Build
```
rpmbuild/SOURCES/
├── dist_x86_64/
│   └── Log Viewer.app          # Intel x86_64 app bundle
├── dist_arm64/
│   └── Log Viewer.app          # Apple Silicon arm64 app bundle
├── LogViewer-3.2.0-macOS-x86_64.dmg
├── LogViewer-3.2.0-macOS-arm64.dmg
└── version_info.txt            # Auto-generated for Windows builds
```

### File Naming Convention
- **App Bundles**: `Log Viewer.app` (stored in architecture-specific directories)
- **DMG Files**: `LogViewer-{VERSION}-macOS-{ARCH}.dmg`
- **Architecture Values**: `x86_64`, `arm64`

## 🔧 GitHub Actions Workflow

### Automatic Builds
The new workflow (`.github/workflows/macos_build_dual.yml`) automatically:

1. **Triggers on**:
   - Push to `main` or `FIX--3.0.5` branches
   - Pull requests to `main`
   - Manual dispatch
   - Git tags starting with `v*`

2. **Parallel Jobs**:
   - `build-macos-arm64`: Runs on `macos-latest` (Apple Silicon)
   - `build-macos-x86_64`: Runs on `macos-13` (Intel)

3. **Artifacts Created**:
   - App bundles for both architectures
   - DMG files for both architectures
   - Retention: 30 days

4. **Release Creation** (on tags):
   - Downloads both DMG files
   - Creates draft release with both architectures
   - Includes detailed architecture guidance

### Workflow Features
- **Version Detection**: Automatically reads from `Build_Version` file
- **Architecture Verification**: Checks binary architecture with `lipo -info`
- **Testing**: Mounts/unmounts DMGs and launches apps
- **Cross-Compatibility Notes**: Explains Rosetta 2 support

## 🎯 Architecture Targeting

### PyInstaller Configuration
```python
# Intel x86_64
target_arch='x86_64'

# Apple Silicon arm64  
target_arch='arm64'
```

### Build Environment
- **Intel builds**: Use `macos-13` runners or Intel Macs
- **ARM64 builds**: Use `macos-latest` runners or Apple Silicon Macs
- **Cross-compilation**: Not currently supported

## 🧪 Testing

### Automated Tests
All build scripts include:
- App bundle structure verification
- Binary architecture confirmation
- DMG mount/unmount testing
- Application launch testing

### Manual Testing
```bash
# Check architecture of built binary
lipo -info "dist_x86_64/Log Viewer.app/Contents/MacOS/log_viewer"
lipo -info "dist_arm64/Log Viewer.app/Contents/MacOS/log_viewer"

# Test DMG mounting
hdiutil attach "LogViewer-3.2.0-macOS-x86_64.dmg"
hdiutil attach "LogViewer-3.2.0-macOS-arm64.dmg"
```

## 🔄 Migration from Single Architecture

### For Users
- **Intel Mac users**: Download `LogViewer-{VERSION}-macOS-x86_64.dmg`
- **Apple Silicon users**: Download `LogViewer-{VERSION}-macOS-arm64.dmg`
- **Either version works on both**: Rosetta 2 provides compatibility

### For Developers
- **Legacy scripts still work**: `Build_App_MacOS.sh` and `Create_DMG_MacOS.sh` updated with versioning
- **New scripts available**: Architecture-specific build options
- **CI/CD enhanced**: Parallel builds reduce total build time

## 📊 Performance Benefits

### Native Performance
- **Intel Macs**: x86_64 version runs natively
- **Apple Silicon**: arm64 version runs natively
- **Cross-platform**: Rosetta 2 translation (slight performance impact)

### Build Efficiency
- **Parallel CI builds**: Both architectures build simultaneously
- **Selective building**: Choose specific architecture for faster local builds
- **Incremental builds**: Architecture-specific directories prevent conflicts

## 🛠️ Troubleshooting

### Common Issues

#### Version Not Updating
```bash
# Check Build_Version file
cat rpmbuild/SOURCES/Build_Version

# Regenerate version_info.txt for Windows
cd rpmbuild/SOURCES
python3 generate_version_info.py
```

#### Wrong Architecture Built
```bash
# Verify target architecture in PyInstaller spec
grep "target_arch" rpmbuild/SOURCES/log_viewer_macos_*.spec

# Check actual binary architecture
lipo -info "dist_*/Log Viewer.app/Contents/MacOS/log_viewer"
```

#### Build Failures
```bash
# Clean all build artifacts
cd rpmbuild/SOURCES
./Build_All_MacOS_Dual.sh --clean

# Check Python and PyInstaller versions
python --version
pip show pyinstaller
```

### Build Script Options
```bash
# Get help for any script
./Build_All_MacOS_Dual.sh --help
./Build_App_MacOS_x86_64.sh --help
```

## 🔮 Future Enhancements

### Potential Improvements
1. **Universal Binaries**: Single app supporting both architectures
2. **Code Signing**: Automated signing for distribution
3. **Notarization**: Apple notarization for enhanced security
4. **Windows Architecture**: Similar x86_64/arm64 support for Windows
5. **Linux Architectures**: Multi-arch Linux support (x86_64, arm64, etc.)

### Integration Points
- **Package Managers**: Homebrew support with architecture detection
- **Update System**: In-app updates with architecture awareness
- **Metrics**: Architecture usage analytics

---

## 📞 Support

For technical support or questions about the dual architecture implementation:
- **Email**: travis@michettetech.com
- **Organization**: Michette Technologies

## 📄 License

This implementation maintains the same proprietary license as the original Log Viewer application.

---

*Generated: December 2024*
*Version: 3.2.0*
*Implementation: Dual Architecture macOS Support* 