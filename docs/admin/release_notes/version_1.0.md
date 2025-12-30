# v1.0 Release Notes


This document describes all new features and changes in the release `1.0`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned Features
- **Custom Git Repository Support**: Support for user-defined backup and/or intended Git Repository in Nautobot, decoupling the app from Golden Config’s `backup` and `intended` repos. This provides greater flexibility for teams using their own backup or templating processes.
  
- **Expanded Credential Support**: While current versions use Nautobot’s Secrets Groups for device authentication, future versions will support additional credential sources and access methods for broader compatibility.

---
## [2.0.0] - 2025-12-29

### Changed
- Updated to work with Nautobot v3.X

## [1.1.1] - 2025-07-05

### Fixed
- Improved `CredentialsHandler` to dynamically parse access types and secret types from the provided `SecretsGroup`, avoiding hardcoded `"Generic"` assumptions.
- Prevents runtime failures when user-defined secrets don't match the default `"Generic"` type.
- Added fallback logic and structured iteration to extract username/password from any valid association.

---

## [1.1.0] - 2025-07-04

### Changed
- Introduced `CredentialsHandler` class to centralize and simplify credentials parsing from `SecretsGroup`.
- Replaced individual username/password `ObjectVar` entries with a single `SecretsGroup` input.
- Secrets are now dynamically parsed to avoid hardcoding access_type/secret_type combinations.


## [1.0.0] - 2025-07-03

### Added
- Initial public release of the Auto Provisioner Nautobot App.
- Support for pushing full device configurations from:
  - Golden Config backup repo.
  - Golden Config intended config repo.
- `Baseline Existing Device Job` to restore device configs.
- `Replace Existing Device Job` to update hardware while preserving metadata.
- `Provision New Device Job` to create and provision a new device in Nautobot.
- Git repository path resolution using `GitRepoPathResolver`.
- Configuration push logic using `ConfigPusher`.












