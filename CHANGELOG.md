# Changelog

All notable changes to the Origin Language project will be documented in this file.

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