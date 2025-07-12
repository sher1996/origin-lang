# Origin Package Manager

The Origin Package Manager provides a simple way to manage local and remote libraries in your Origin projects.

## Overview

The package manager allows you to:
- Add local libraries to your project
- Add remote packages from HTTPS URLs
- Add packages from registry using semantic versioning
- Remove installed libraries
- Manage dependencies through a `pkg.json` manifest
- Verify package integrity with SHA-256 checksums
- Lock dependency versions with `origin.lock`

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

Add a package from registry using semantic versioning:

```bash
origin add std/math@^1.2.0
```

This will resolve the highest compatible version and install it to `.origin/libs/`.

### 3. Remove Libraries

Remove an installed library:

```bash
origin remove math_utils
```

## Commands

### `origin add <source> [--checksum <sha256>] [--update]`

Adds a local library, remote package, or registry package to your project.

- **source**: Path to the library folder, URL to remote package, or package spec (e.g., "std/math@^1.2.0")
- **--checksum**: Optional SHA-256 checksum for verification
- **--update**: Update lockfile even if package exists

**Examples:**
```bash
# Local library
origin add ./lib/math_utils
origin add ../shared/string_utils

# Remote package
origin add https://example.com/math_utils-0.2.0.tar.gz
origin add https://example.com/math_utils-0.2.0.tar.gz --checksum 642FB2E16399776F1F352245A3A522DE2BB89969220718CDE0595726CC752F88

# Registry package with semantic versioning
origin add std/math@^1.2.0
origin add std/string@~2.0
origin add std/net@>=1.0 <2.0
origin add std/math@^1.2.0 --update  # Force update
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

## Semantic Versioning

The package manager supports npm-style semantic version ranges:

### Version Range Syntax

- **Exact version**: `1.2.3`
- **Caret ranges**: `^1.2.3` (allows minor and patch updates)
- **Tilde ranges**: `~1.2.3` (allows patch updates only)
- **Comparison operators**: `>=1.2.0`, `<2.0.0`, `=1.2.3`
- **Compound ranges**: `>=1.2.0 <2.0.0`
- **Wildcard**: `*` (matches any version)

### Examples

```bash
# Install latest 1.x version
origin add std/math@^1.0.0

# Install latest 1.2.x version
origin add std/math@~1.2.0

# Install version 1.2.3 or higher, but less than 2.0.0
origin add std/math@>=1.2.3 <2.0.0

# Install exact version
origin add std/math@1.2.3
```

## Lockfile System

The package manager uses `origin.lock` to ensure reproducible builds:

### Lockfile Format

```json
{
  "packages": {
    "math_utils": {
      "version": "1.2.3",
      "checksum": "abc123def456..."
    },
    "string_utils": {
      "version": "2.0.0",
      "checksum": "def456abc789..."
    }
  }
}
```

### Lockfile Behavior

- **First install**: Resolves version range, downloads package, writes to lockfile
- **Subsequent installs**: Uses locked version unless `--update` flag is provided
- **Deterministic**: Lockfile is sorted for consistent output
- **Version pinning**: Ensures all developers use the same package versions

### Update Workflow

```bash
# Install with version range (creates/updates lockfile)
origin add std/math@^1.2.0

# Reinstall from lockfile (no network request)
origin add std/math@^1.2.0

# Force update to latest compatible version
origin add std/math@^1.2.0 --update
```

## Registry System

A simple registry system allows aliasing packages with multiple versions:

```json
{
  "std/math@1.0.0": "https://example.com/math-1.0.0.tar.gz",
  "std/math@1.1.0": "https://example.com/math-1.1.0.tar.gz",
  "std/math@1.2.0": "https://example.com/math-1.2.0.tar.gz",
  "std/string@2.0.0": "https://example.com/string-2.0.0.tar.gz"
}
```

Registry file location: `~/.origin/registry.json`

## Limitations

- Libraries are copied, not symlinked
- No dependency resolution between libraries
- Registry system requires manual setup (no public registry yet)
- Limited to HTTPS URLs for remote packages 