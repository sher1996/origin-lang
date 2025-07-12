# Changelog

All notable changes to the Origin Language project will be documented in this file.

## [Unreleased]

### Added
- **Chapter 25: Save/Export functionality**
  - Added `.originproj` project file format (ZIP with blocks, connections, metadata)
  - Added "Save Project" and "Open Project" buttons to visual editor toolbar
  - Added auto-save functionality with localStorage (every 10 seconds)
  - Added CLI commands: `origin viz save` and `origin viz open`
  - Added project metadata support (name, description, version, timestamps)
  - Added automatic README.md generation for projects
  - Added round-trip testing for save/open functionality

### Changed
- Updated visual editor toolbar with new save/load buttons
- Enhanced project structure with proper metadata handling

### Technical
- Added JSZip dependency for project file compression
- Added ProjectExporter class for frontend save/load
- Added project_zip.py module for backend CLI functionality
- Added useAutosave hook for browser-based session persistence
- Added comprehensive test coverage for save/load functionality

## [0.5.0] - 2024-12-10

## [0.5.0] - 2024-12-10

### Added
- **Live Preview Pane (Chapter 24)**: Real-time code execution with sandboxed iframe
- **Three-Column Layout**: Palette ▸ Canvas ▸ Preview with responsive design
- **Debounced Code Generation**: 300ms delay for smooth preview updates
- **Connection System**: Visual data flow with SVG connection lines between blocks
- **Grid Snapping**: 10px grid background for precise block positioning
- **Error Overlay**: Red overlay with error messages for syntax/runtime errors
- **Constant Block**: New numeric constant block for testing preview functionality
- **Preview Sandbox**: Safe execution environment with console.log capture
- **Connection Hooks**: `useConnections` hook for managing block connections
- **Connection Lines Component**: SVG-based connection rendering with arrows
- **Error Handling**: Comprehensive error display in preview pane
- **Testing Infrastructure**: Vitest setup with React Testing Library

### Changed
- **Visual Editor Layout**: Upgraded from two-column to three-column design
- **Canvas Component**: Added grid background and connection line rendering
- **Block Rendering**: Enhanced with input/output connection dots
- **App Component**: Integrated preview pane and error overlay
- **Transform Functions**: Added error handling for code generation
- **Documentation**: Updated visual mode docs with live preview features

### Technical Details
- New components: `PreviewPane.tsx`, `ConnectionLines.tsx`, `ErrorOverlay.tsx`
- New hooks: `useConnections.ts`, `useDebounce.ts`
- Enhanced transform: `blocksToCodeWithErrorHandling()` function
- Testing setup: Vitest configuration with React Testing Library
- Updated dependencies: Added testing libraries and vitest

### Live Preview Features
- **Real-time Execution**: Code updates automatically with debouncing
- **Sandboxed Environment**: Safe execution in iframe with console capture
- **Error Display**: Syntax and runtime errors with red overlay
- **Output Capture**: Console.log results displayed in preview pane
- **Connection Visualization**: SVG lines showing data flow between blocks

### Backward Compatibility
- All existing visual editor functionality remains unchanged
- Import/export workflow continues to work
- Block definitions and transform functions maintain compatibility
- No breaking changes to existing APIs

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