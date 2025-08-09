# GitHub Workflow Trigger Fix

## Issue Identified
The Flatpak and RPM build workflows were only configured to trigger on version tags (`v*`), but the existing macOS and Windows workflows trigger on push to `main` branch. This caused them not to build when PRs were merged to main.

## Changes Made

### Updated Trigger Configuration
Both `.github/workflows/flatpak_build.yml` and `.github/workflows/rpm_build.yml` now trigger on:

```yaml
on:
  push:
    branches:
      - main           # ✅ NEW: Triggers on push/merge to main
    tags:
      - 'v*'          # ✅ Still triggers on version tags
  pull_request:
    branches:
      - main           # ✅ NEW: Triggers on PRs to main
  workflow_dispatch:    # ✅ Still allows manual triggering
```

### Updated Version Detection
- Changed from tag-based version extraction to reading from `Build_Version` file
- Added logic to detect if build is from a tag push or regular push
- Only uploads to releases when triggered by version tags

### Key Benefits
1. **Consistent Behavior**: All 4 workflows (macOS, Windows, RPM, Flatpak) now trigger on the same events
2. **Automatic Building**: Flatpak and RPM packages build automatically on every merge to main
3. **Release Integration**: Still uploads to GitHub releases when version tags are pushed
4. **PR Testing**: Builds run on pull requests for testing

## Expected Behavior

### On Push/Merge to Main:
- ✅ macOS build runs
- ✅ Windows build runs  
- ✅ RPM build runs
- ✅ Flatpak build runs

### On Version Tag Push (e.g., `v3.2.0`):
- ✅ All 4 builds run
- ✅ Automated release workflow collects all 6 artifacts
- ✅ Draft release created with all packages

### On Pull Request:
- ✅ All 4 builds run for testing
- ❌ No release artifacts uploaded

## Testing
The next time you:
1. Merge a PR to main, or
2. Push commits to main

All 4 build workflows should trigger automatically, including the new Flatpak and RPM builds.

This fix ensures your Flatpak package will be built consistently alongside your other platform packages.
