# Remote Package Demo

This demo shows how to use the new remote package functionality in Origin.

## Features Demonstrated

- Downloading packages from HTTPS URLs
- Checksum verification for security
- Automatic archive extraction (.tar.gz, .zip)
- Local package installation (backward compatibility)

## Setup

1. **Install the remote package:**
   ```bash
   cd examples/pkg_remote_demo
   origin add https://github.com/sher1996/origin-pkgs/releases/download/v0.2.0/math_utils-0.2.0.tar.gz --checksum 642FB2E16399776F1F352245A3A522DE2BB89969220718CDE0595726CC752F88
   ```

2. **Run the demo:**
   ```bash
   origin run main.origin
   ```

## Expected Output

```
Math Utils Demo
===============
a = 10
b = 5

a + b = 15
a - b = 5
a * b = 50
a / b = 2
a^2 = 100

All calculations completed successfully!
```

## Package Management Commands

- **Add remote package:** `origin add <url> [--checksum <sha256>]`
- **Add local package:** `origin add <path>`
- **Remove package:** `origin remove <name>`

## Security Features

- SHA-256 checksum verification prevents tampering
- Automatic retry with exponential backoff for network failures
- Support for `.sha256` companion files
- Clear error messages for network and verification failures

## Supported Archive Formats

- `.tar.gz` (gzipped tar)
- `.tar` (uncompressed tar)
- `.zip` (ZIP archive)

## Registry Support

The registry system allows aliasing packages:

```bash
# Add alias to registry
echo '{"std/math@1.0.0": "https://example.com/math-1.0.0.tar.gz"}' > ~/.origin/registry.json

# Use alias (future feature)
origin add std/math@1.0.0
``` 