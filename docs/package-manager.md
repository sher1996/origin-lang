# Origin Package Manager

The Origin Package Manager provides a simple way to manage local and remote libraries in your Origin projects.

## Overview

The package manager allows you to:
- Add local libraries to your project
- Add remote packages from HTTPS URLs
- Remove installed libraries
- Manage dependencies through a `pkg.json` manifest
- Verify package integrity with SHA-256 checksums

## Quick Start

### 1. Create a Package Manifest

Create a `pkg.json` file in your project root:

```json
{
  "name": "my-project",
  "version": "0.1.0",
  "dependencies": {
    "math_utils": "./lib/math_utils"
  }
}
```

### 2. Add Libraries

Add a local library to your project:

```bash
origin add ./lib/math_utils
```

This will copy the library to `.origin/libs/math_utils/`.

Add a remote package from URL:

```bash
origin add https://example.com/math_utils-0.2.0.tar.gz --checksum <sha256>
```

This will download, verify, and install the package to `.origin/libs/`.

### 3. Remove Libraries

Remove an installed library:

```bash
origin remove math_utils
```

## Commands

### `origin add <source> [--checksum <sha256>]`

Adds a local library or remote package to your project.

- **source**: Path to the library folder or URL to remote package
- **--checksum**: Optional SHA-256 checksum for verification

**Examples:**
```bash
# Local library
origin add ./lib/math_utils
origin add ../shared/string_utils

# Remote package
origin add https://example.com/math_utils-0.2.0.tar.gz
origin add https://example.com/math_utils-0.2.0.tar.gz --checksum 642FB2E16399776F1F352245A3A522DE2BB89969220718CDE0595726CC752F88
```

### `origin remove <name>`

Removes an installed library from your project.

- **name**: Name of the library to remove

**Examples:**
```bash
origin remove math_utils
origin remove string_utils
```

## Error Handling

The package manager provides clear error messages for common issues:

- **Missing manifest**: "No pkg.json found in this directory."
- **Library not found**: "Cannot find library at <path>"
- **Duplicate library**: "Library '<name>' already installed."
- **Unknown library**: "No installed lib named '<name>'."
- **Network error**: "Failed to download <url>: <error>"
- **Checksum mismatch**: "Checksum verification failed for <file>"
- **Invalid archive**: "Unsupported archive format: <format>"

## Project Structure

After adding libraries, your project structure will look like:

```
my-project/
├── pkg.json
├── main.origin
├── lib/
│   └── math_utils/
│       └── math.origin
└── .origin/
    └── libs/
        └── math_utils/
            └── math.origin
```

## Best Practices

1. **Use relative paths** in your `pkg.json` dependencies
2. **Keep libraries organized** in a `lib/` or `libraries/` directory
3. **Version your projects** in the `pkg.json` manifest
4. **Document your libraries** with clear naming and structure

## Remote Packages

### Supported Formats

- **Archives**: `.tar.gz`, `.tar`, `.zip`
- **Protocols**: HTTPS URLs
- **Verification**: SHA-256 checksums

### Security Features

- **Checksum verification**: Prevents tampering and corruption
- **Automatic retry**: Network failures with exponential backoff
- **Companion files**: Support for `.sha256` files alongside packages
- **Clear diagnostics**: Helpful error messages for network issues

### Registry System

A simple registry system allows aliasing packages:

```json
{
  "std/math@1.0.0": "https://example.com/math-1.0.0.tar.gz",
  "std/string@2.0.0": "https://example.com/string-2.0.0.tar.gz"
}
```

Registry file location: `~/.origin/registry.json`

## Limitations

- Libraries are copied, not symlinked
- No dependency resolution between libraries
- No version management for individual libraries
- Registry system is stub-only (no CLI integration yet) 