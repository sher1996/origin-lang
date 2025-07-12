# Changelog

All notable changes to the Origin Language project will be documented in this file.

## [0.4.0] - 2024-12-09

### Added
- **AST ↔ Blocks Mapper (Chapter 23)**: Bidirectional transform between Origin AST and visual blocks
- **Block Registry**: Type-rich block definitions with serialize/deserialize functions
- **Import/Export UI**: File import, paste code, and export functionality in visual editor
- **Auto-layout**: Simple vertical flow positioning for imported blocks
- **CLI Integration**: `origin viz import` and `origin viz export` commands
- **Transform Library**: Shared logic between frontend and backend
- **Round-trip Guarantee**: Code → blocks → code maintains semantic equivalence
- **Comprehensive Tests**: Backend PyTest and frontend Jest tests
- **Demo Files**: `examples/mapper_demo/` with hello world and arithmetic examples
- **Updated Documentation**: Visual mode docs with import/export workflow

### Changed
- **Visual Editor**: Upgraded from static blocks to dynamic registry-based system
- **Block Definitions**: Enhanced with inputs/outputs and AST mapping
- **Palette Component**: Now shows block details and input/output counts
- **Canvas Component**: Displays block inputs and supports BlockInstance interface
- **CLI Interface**: Added `viz` sub-command for visual editor operations

### Technical Details
- New modules: `visual/src/blocks/definitions.ts`, `visual/src/lib/transform.ts`, `visual/src/lib/autoLayout.ts`
- Backend transform: `src/transform/blocks_to_ast.py`
- CLI enhancement: `src/cli.py` with viz sub-commands
- Test coverage: `tests/test_transform_roundtrip.py`, `visual/src/__tests__/import.test.tsx`
- Documentation: Updated `docs/visual-mode.md` with import/export workflow

### Visual Editor Features
- **Block Types**: Say, Let, Repeat, Define, Call, Import, String
- **Import Methods**: File upload and paste code
- **Export**: Download as `.origin` file
- **Auto-layout**: Vertical stacking with proper spacing
- **Block Count**: Real-time display of canvas blocks

### Backward Compatibility
- All existing visual editor functionality remains unchanged
- Core compiler and runtime untouched
- Package manager tracks unchanged
- No breaking changes to existing APIs

## [0.3.0] - 2024-12-08

### Added
- **Replay & step-back debugger (Chapter 21)**: Step through execution history interactively with `origin replay ... --step`.
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