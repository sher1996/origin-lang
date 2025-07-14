# Installing Origin from Binaries

This guide explains how to install Origin from pre-built binaries, which is the recommended method for most users.

## Download Links

### Latest Release
- **Windows**: [origin-win-latest.zip](https://github.com/origin-lang/origin/releases/latest/download/origin-win-latest.zip)
- **macOS**: [origin-mac-latest.zip](https://github.com/origin-lang/origin/releases/latest/download/origin-mac-latest.zip)
- **Linux**: [origin-linux-latest.zip](https://github.com/origin-lang/origin/releases/latest/download/origin-linux-latest.zip)

### Specific Versions
Visit [GitHub Releases](https://github.com/origin-lang/origin/releases) for all available versions.

## Installation Steps

### 1. Download and Extract

**Windows:**
```powershell
# Download
Invoke-WebRequest -Uri "https://github.com/origin-lang/origin/releases/latest/download/origin-win-latest.zip" -OutFile "origin.zip"

# Extract
Expand-Archive -Path "origin.zip" -DestinationPath "C:\origin" -Force

# Add to PATH (optional)
$env:PATH += ";C:\origin"
```

**macOS/Linux:**
```bash
# Download
curl -L -o origin.zip "https://github.com/origin-lang/origin/releases/latest/download/origin-linux-latest.zip"

# Extract
unzip origin.zip

# Make executable
chmod +x origin

# Move to a directory in PATH (optional)
sudo mv origin /usr/local/bin/
```

### 2. Verify Installation

Test that Origin is working:

```bash
origin --version
origin --help
```

### 3. Run Your First Program

Create a simple test file:

```bash
echo 'print("Hello, Origin!")' > hello.ori
origin run hello.ori
```

## Verification

### SHA-256 Checksums

Always verify the integrity of downloaded files:

**Windows:**
```powershell
Get-FileHash origin-win-latest.zip -Algorithm SHA256
```

**macOS/Linux:**
```bash
sha256sum origin-linux-latest.zip
```

Compare the output with the checksums published on the [GitHub release page](https://github.com/origin-lang/origin/releases).

### Automated Verification

Use our smoke test script:

```bash
python scripts/smoke_bin.py https://github.com/origin-lang/origin/releases/latest/download/origin-linux-latest.zip
```

## Air-Gapped Installation

For environments without internet access:

1. Download the binary on a machine with internet access
2. Transfer the zip file to the target machine
3. Extract and verify the checksum
4. Follow the installation steps above

## PATH Configuration

### Windows
Add the Origin directory to your system PATH:
1. Open System Properties → Advanced → Environment Variables
2. Edit the PATH variable
3. Add the directory containing `origin.exe`

### macOS/Linux
Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export PATH="$HOME/bin:$PATH"
```

Then move the binary:
```bash
mkdir -p ~/bin
mv origin ~/bin/
```

## Troubleshooting

### Permission Denied (Linux/macOS)
```bash
chmod +x origin
```

### "Command not found"
Ensure the binary is in your PATH or use the full path:
```bash
./origin --version
```

### Missing Dependencies
The binary is self-contained and includes all dependencies. If you encounter issues:

1. Check the [GitHub Issues](https://github.com/origin-lang/origin/issues)
2. Try running with verbose output: `origin --help`
3. Verify your system architecture (x86_64 is supported)

## Differences from pip Installation

| Aspect | Binary | pip install |
|--------|--------|-------------|
| **Dependencies** | Self-contained | Requires Python + dependencies |
| **Updates** | Manual download | `pip install --upgrade origin-lang` |
| **Size** | ~50MB | ~5MB + Python runtime |
| **Portability** | Works without Python | Requires Python 3.8+ |
| **Network** | Works offline | May require internet for packages |

## Auto-Updates

Origin binaries support auto-updates via the update manifest:

```bash
# Check for updates
origin check-updates

# Download and install latest version
origin update
```

The update manifest is available at: `https://raw.githubusercontent.com/origin-lang/origin/releases/update.json`

## Support

- **Documentation**: [docs/](https://github.com/origin-lang/origin/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/origin-lang/origin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/origin-lang/origin/discussions)

## License

Origin is released under the MIT License. See [LICENSE](https://github.com/origin-lang/origin/blob/main/LICENSE) for details.

Third-party licenses are included in `THIRD_PARTY_LICENSES.txt` in the binary distribution. 