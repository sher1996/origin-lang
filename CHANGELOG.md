# Changelog

All notable changes to the Origin Language project will be documented in this file.

## [0.5.0] - 2024-12-10

### Added
- **Enhanced Block Registry**: Centralized block management with singleton pattern and extensible architecture
- **Comprehensive Import/Export**: Support for Origin code (.origin) and JSON blocks (.json) formats
- **Advanced Auto-Layout**: Multiple layout algorithms (vertical, grid, smart, flow, compact)
- **Improved Error Handling**: Graceful error display with status messages and fallback mechanisms
- **Block Categories**: Organized palette with categorized blocks (Output, Variables, Data, System, Control, Functions)
- **Enhanced Block Types**: Added support for numbers, if statements, and function definitions
- **Validation System**: Round-trip validation to ensure code ↔ blocks ↔ code equivalence
- **JSON Serialization**: Full serialization/deserialization of block data for storage and sharing
- **CLI Enhancements**: Added `validate` command for round-trip testing
- **Comprehensive Testing**: New test suite for visual mode functionality

### Changed
- **Block Registry**: Migrated from static array to singleton registry pattern
- **Transform Logic**: Enhanced with better error handling and support for complex AST structures
- **UI Components**: Improved Canvas and Palette with better visual feedback and organization
- **Toolbar**: Enhanced with JSON import/export, validation, and clear functionality
- **Auto-Layout**: Replaced simple vertical layout with intelligent layout selection
- **Error Handling**: Added comprehensive error handling throughout the transform pipeline

### Technical Details
- **Frontend**: Enhanced `visual/src/blocks/definitions.ts` with registry pattern
- **Transform**: Improved `visual/src/lib/transform.ts` with better AST handling
- **Layout**: Enhanced `visual/src/lib/autoLayout.ts` with multiple algorithms
- **Backend**: Updated `src/transform/blocks_to_ast.py` with registry and validation
- **CLI**: Enhanced `src/cli.py` with validation command
- **Tests**: New `tests/test_visual_roundtrip.py` for comprehensive testing
- **Documentation**: Updated `docs/visual-mode.md` with comprehensive guide

### New Block Types
- **Number**: Literal number values with purple color coding
- **If**: Conditional statements with yellow color coding
- **Function**: Function definitions with teal color coding

### Import/Export Features
- **File Import**: Load `.origin` files with automatic block conversion
- **JSON Import**: Load block data from JSON files
- **Paste Import**: Direct code pasting with real-time conversion
- **Code Export**: Save canvas as `.origin` files
- **JSON Export**: Save block data as JSON files
- **Validation**: Test round-trip conversion integrity

### Layout Algorithms
- **Vertical**: Simple stack layout for small programs
- **Grid**: Organized grid layout for medium programs
- **Smart**: Grouped by block type for better organization
- **Flow**: Execution order layout
- **Compact**: Dense arrangement for space efficiency
- **Auto-Choose**: Intelligent algorithm selection based on block count

### Backward Compatibility
- All existing visual editor functionality remains unchanged
- Block definitions maintain backward compatibility
- Core compiler and runtime untouched
- Package manager functionality unchanged

## [0.4.0] - 2024-12-09

### Added
- **AST ↔ Blocks Mapper (Chapter 23)**: Bidirectional transformation between Origin AST and visual blocks
- **Visual Editor Import/Export**: Import `.origin` files and export canvas as code
- **Block Registry**: Type-rich block definitions with serialize/deserialize functions
- **Auto-layout**: Simple vertical flow layout for imported blocks
- **CLI Integration**: `origin viz import` and `origin viz export` commands
- **Round-trip Guarantee**: `code.origin → blocks → code'` where `code'` is semantically identical
- **Color-coded Blocks**: Visual distinction between block types (Say=blue, Let=green, etc.)
- **Input Fields**: Editable inputs for block parameters
- **Comprehensive Tests**: Backend roundtrip tests and frontend import tests
- **Demo Files**: `examples/mapper_demo/` with hello world and arithmetic examples

### Changed
- **Visual Editor**: Upgraded from static blocks to dynamic block registry
- **Block Structure**: Enhanced with inputs, outputs, and AST mapping
- **Palette**: Dynamic rendering from block definitions
- **Canvas**: Support for block inputs and color coding
- **CLI**: Added `viz` subcommand for visual editor operations

### Technical Details
- New modules: `visual/src/blocks/definitions.ts`, `visual/src/lib/transform.ts`, `visual/src/lib/autoLayout.ts`
- Backend transform: `src/transform/blocks_to_ast.py`
- Enhanced CLI: `src/cli.py` with viz subcommands
- Shared types: Updated `src/types/ast.d.ts` with block interfaces
- Tests: `tests/test_transform_roundtrip.py` for backend validation

### Visual Editor Features
- **Import**: File upload and paste functionality
- **Export**: Download canvas as `.origin` file
- **Toolbar**: Import/Export buttons with block count
- **Auto-layout**: Vertical positioning for imported blocks
- **Input Editing**: Real-time block parameter editing

### Backward Compatibility
- All existing visual editor functionality remains unchanged
- Core compiler and runtime untouched
- Package manager tracks unchanged

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