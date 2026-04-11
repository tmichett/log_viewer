# Homebrew Publishing Setup Guide

This document explains how to set up and use the Homebrew publishing workflow for Log Viewer.

## Overview

The [`publish_homebrew.yml`](.github/workflows/publish_homebrew.yml) workflow automatically publishes a Homebrew cask for Log Viewer when a new release is created. It:

1. Downloads release assets for macOS
2. Calculates SHA256 checksums
3. Generates a Homebrew cask
4. Publishes to a custom Homebrew tap repository
5. Creates installation documentation

## Prerequisites

### 1. Create a Homebrew Tap Repository

A Homebrew tap is a GitHub repository that contains Homebrew formulas or casks. Create one with:

1. Go to GitHub and create a new repository
2. Name it `homebrew-logviewer`
3. Make it public
4. Initialize it with a README

If your organization is `MichetteTech`, the repository would be:

- `MichetteTech/homebrew-logviewer`
- `https://github.com/MichetteTech/homebrew-logviewer`

Users will then install from it with:

```bash
brew tap MichetteTech/logviewer
```

### 2. Create a GitHub Personal Access Token

The workflow needs permission to push to the tap repository.

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token
3. Give it a descriptive name such as `Log Viewer Homebrew Publisher`
4. Enable the `repo` scope
5. Copy the token

### 3. Add the Token as a Repository Secret

Add the token to the main repository:

1. Open the Log Viewer repository on GitHub
2. Go to Settings → Secrets and variables → Actions
3. Create a new repository secret
4. Name it `HOMEBREW_TAP_TOKEN`
5. Paste the token value

## How It Works

### Automatic Publishing

The workflow triggers automatically when a GitHub release is published.

It expects these macOS release assets to already exist:

- `LogViewer-{VERSION}-macOS-arm64.dmg`
- `LogViewer-{VERSION}-macOS-x86_64.dmg`

The workflow then:

1. Downloads both DMG files
2. Computes SHA256 for each architecture
3. Generates [`logviewer.rb`](.github/workflows/publish_homebrew.yml:122)
4. Pushes the generated cask to the tap repository under [`Casks/logviewer.rb`](.github/workflows/publish_homebrew.yml:173)

### Manual Publishing

You can also run the workflow manually from GitHub Actions:

1. Open Actions
2. Select `Publish to Homebrew`
3. Click `Run workflow`
4. Enter a tag such as `v3.2.0`

## Generated Cask

The workflow publishes a Homebrew cask named `logviewer`.

Installation command:

```bash
brew install --cask logviewer
```

The cask selects the correct DMG automatically based on CPU architecture and installs `Log Viewer.app`.

## User Installation

Once published, users install Log Viewer with:

```bash
brew tap MichetteTech/logviewer
brew install --cask logviewer
```

## Troubleshooting

### Tap repository does not exist

Create the public tap repository first.

### Authentication failure

Verify that the `HOMEBREW_TAP_TOKEN` secret exists and that the token has `repo` scope.

### Release assets are missing

Make sure the GitHub release includes both DMG files before running the workflow.

### Cask fails to install

Test locally with:

```bash
brew install --cask --debug ./logviewer.rb
```

## Notes

This workflow only publishes the macOS application through Homebrew because Homebrew distribution is cask-based for GUI apps such as `Log Viewer.app`.

The workflow also uploads the generated cask as a workflow artifact even if publishing to the tap is not configured yet.