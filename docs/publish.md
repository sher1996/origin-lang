# Publishing Packages

The `origin publish` command allows you to publish your Origin packages to GitHub Releases.

## Prerequisites

1. **GitHub Personal Access Token**: You need a GitHub token with `repo` permissions to create releases and upload assets.

2. **Valid Package Manifest**: Your project must have a `pkg.json` file with the following fields:
   - `name`: Package name
   - `version`: Package version (semantic versioning)
   - `repository`: GitHub repository URL

## Usage

### Basic Publishing

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Publish from the current directory
origin publish
```

### Command Options

```bash
origin publish [--token TOKEN] [--dry-run] [--tag TAG]
```

- `--token TOKEN`: GitHub personal access token (overrides GITHUB_TOKEN env var)
- `--dry-run`: Show what would be done without actually publishing
- `--tag TAG`: Custom release tag (defaults to `v{version}`)

### Examples

```bash
# Dry run to see what would be published
origin publish --dry-run

# Publish with custom tag
origin publish --tag release-v1.0.0

# Publish with explicit token
origin publish --token ghp_your_token_here
```

## Package Manifest (pkg.json)

Your `pkg.json` file must contain:

```json
{
  "name": "my-package",
  "version": "1.0.0",
  "repository": "https://github.com/username/repo-name"
}
```

### Repository URL Formats

The following repository URL formats are supported:

- `https://github.com/username/repo-name`
- `https://github.com/username/repo-name.git`
- `git@github.com:username/repo-name.git`

## What Gets Published

The publish process:

1. **Builds a tarball** containing all files in your project directory
2. **Excludes** common files/directories:
   - `.git/`
   - `*.orirec` (recording files)
   - `node_modules/`
   - `dist/`
   - `__pycache__/`
   - `.pytest_cache/`

3. **Computes SHA-256 checksum** of the tarball
4. **Creates a GitHub release** with tag `v{version}` (or custom tag)
5. **Uploads both files**:
   - `{name}-{version}.tar.gz` (application/gzip)
   - `{name}-{version}.tar.gz.sha256` (text/plain)

## Example Output

```
Packing greeter-0.2.0.tar.gz...
✔ Packed greeter-0.2.0.tar.gz (18 KB)
✔ SHA-256: 4b30…98d7
Creating release v0.2.0 on sher1996/origin-lang-examples...
✔ Created release v0.2.0
Uploading assets...
✔ Uploaded 2 assets
Publish complete 🎉
```

## Error Handling

Common errors and solutions:

- **"GitHub token required"**: Set `GITHUB_TOKEN` environment variable or use `--token`
- **"Invalid GitHub token"**: Check your token permissions and validity
- **"Repository not found"**: Verify the repository URL and your access permissions
- **"No pkg.json found"**: Ensure you're in a directory with a valid `pkg.json`

## CI/CD Integration

For automated publishing in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Publish Package
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    cd my-package
    origin publish
```

## Security Notes

- Never commit your GitHub token to version control
- Use environment variables or CI/CD secrets
- Consider using GitHub's built-in `GITHUB_TOKEN` for repository actions 