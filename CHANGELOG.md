# Changelog

All notable changes to the Origin Language project will be documented in this file.

## [0.3.0] - 2024-12-08

### Added
- **Semantic version resolver**: npm-style version range parsing and resolution
- **Lockfile system**: `origin.lock` for reproducible builds and version pinning
- **Registry integration**: Resolve packages from registry using semantic versioning
- **Version range support**: `^1.2.0`, `~1.2.3`, `>=1.0 <2.0`, exact versions, and wildcards
- **CLI enhancements**: `--update` flag to force lockfile updates
- **Comprehensive tests**: Unit tests for semver parsing and lockfile operations
- **Demo project**: `examples/semver_demo/` showing semantic versioning usage
- **Updated documentation**: Package manager docs with semver and lockfile sections

### Changed
- **PackageManager.add()**: Now accepts package specs (e.g., "std/math@^1.2.0")
- **Registry.resolve_range()**: New method for semantic version resolution
- **CLI interface**: Enhanced `origin add` command with `--update` option
- **Error handling**: Improved diagnostics for version resolution failures

### Technical Details
- New modules: `src/origin/semver.py`, `src/origin/lock.py`
- Enhanced `src/origin/registry.py` with version range resolution
- Updated `src/origin/pkgmgr.py` with lockfile integration
- Test coverage: `tests/test_semver.py`, `tests/test_lockfile.py`

### Security Features
- Deterministic lockfile generation with sorted keys
- Version pinning prevents supply chain attacks
- Checksum verification for all downloaded packages
- Clear error messages for version resolution failures

### Backward Compatibility
- All existing local and remote package functionality remains unchanged
- Registry system maintains backward compatibility
- No breaking changes to existing APIs

## [0.2.0] - 2024-12-07

## [0.2.0] - 2024-12-07

### Added
- **Remote package support**: Download packages from HTTPS URLs
- **Checksum verification**: SHA-256 verification for package integrity
- **Archive extraction**: Support for `.tar.gz`, `.tar`, and `.zip` archives
- **Network utilities**: Robust download with retry and progress reporting
- **Registry system**: Stub implementation for package aliases (`~/.origin/registry.json`)
- **Enhanced CLI**: `origin add <url> [--checksum <sha256>]` command
- **Comprehensive tests**: Unit tests with mocked network operations
- **Demo project**: `examples/pkg_remote_demo/` showing remote package usage
- **Updated documentation**: Package manager docs with remote package examples

### Changed
- **PackageManager.add()**: Now accepts URLs in addition to local paths
- **CLI interface**: Enhanced `origin add` command with checksum option
- **Error handling**: Improved diagnostics for network and verification failures

### Technical Details
- New modules: `src/origin/net.py`, `src/origin/archive.py`, `src/origin/registry.py`
- Enhanced `src/origin/pkgmgr.py` with remote installation logic
- Updated `src/cli.py` to support remote package commands
- Test fixtures in `tests/fixtures/remote_pkg/` for reproducible testing

### Security Features
- SHA-256 checksum verification prevents tampering
- Automatic retry with exponential backoff for network resilience
- Support for companion `.sha256` files
- Clear error messages for verification failures

### Backward Compatibility
- All existing local package functionality remains unchanged
- Local path installation continues to work as before
- No breaking changes to existing APIs

## [0.1.0] - 2024-12-06

### Added
- **Package Manager**: Local library management with `pkg.json` manifests
- **CLI Commands**: `origin add` and `origin remove` for package management
- **Local Libraries**: Copy libraries to `.origin/libs/` directory
- **Basic Documentation**: Package manager usage guide
- **Demo Project**: `examples/pkg_demo/` showing local library usage

### Technical Details
- Core package manager in `src/origin/pkgmgr.py`
- CLI interface in `src/cli.py`
- Error handling in `src/origin/errors.py`
- Comprehensive unit tests in `tests/test_pkgmgr.py` 