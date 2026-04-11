# Homebrew Publishing Quick Start

## Prerequisites Checklist

- [ ] Create tap repository: `homebrew-logviewer`
- [ ] Create a GitHub personal access token with `repo` scope
- [ ] Add `HOMEBREW_TAP_TOKEN` as a repository secret

## Setup Steps

### 1. Create Tap Repository

Create a public GitHub repository named `homebrew-logviewer`.

Example:

```text
https://github.com/YourOrg/homebrew-logviewer
```

Users will tap it as:

```bash
brew tap YourOrg/logviewer
```

### 2. Add the Token Secret

Add the token to the Log Viewer repository as:

```text
HOMEBREW_TAP_TOKEN
```

### 3. Publish a Release

Publish a GitHub release that includes:

- `LogViewer-VERSION-macOS-arm64.dmg`
- `LogViewer-VERSION-macOS-x86_64.dmg`

### 4. Run the Workflow

The workflow runs automatically on published releases, or manually from GitHub Actions with a tag like `v3.2.0`.

## User Installation

After publishing:

```bash
brew tap YourOrg/logviewer
brew install --cask logviewer
```

## Verify

```bash
open -a "Log Viewer"
```

## Files Added

- [`.github/workflows/publish_homebrew.yml`](.github/workflows/publish_homebrew.yml)
- [`.github/workflows/HOMEBREW_SETUP.md`](.github/workflows/HOMEBREW_SETUP.md)
- [`.github/workflows/HOMEBREW_QUICK_START.md`](.github/workflows/HOMEBREW_QUICK_START.md)

## Success Indicators

- Workflow completes successfully
- [`Casks/logviewer.rb`](.github/workflows/publish_homebrew.yml:173) is pushed to the tap repository
- `brew install --cask logviewer` works on macOS
- Both Intel and Apple Silicon DMGs install correctly