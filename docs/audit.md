# Dependency Tree Audit

The `origin audit` command analyzes your project's dependency tree to identify version conflicts and outdated packages.

## Usage

```bash
origin audit [--json] [--level LEVEL] [--ignore PKG...]
```

### Options

- `--json`: Output results in JSON format instead of human-readable text
- `--level LEVEL`: Minimum severity level to report (`info`, `warn`, or `crit`, default: `warn`)
- `--ignore PKG...`: Packages to ignore during audit (can specify multiple)

### Exit Codes

- `0`: No issues found or only info-level issues
- `1`: Warnings found (but no critical issues)
- `2`: Critical issues found

## Examples

### Basic Audit

```bash
$ origin audit
✖ react (parent: server) – Conflicting version ranges: ^18.0.0, ^9.0.0
✖ ws (parent: server) – Conflicting version ranges: ^8.0.0, ^9.0.0
⚠ lodash – Outdated: 4.17.21 → 4.18.0

3 issues found (2 critical, 1 warning)
```

### JSON Output

```bash
$ origin audit --json
{
  "issues": [
    {
      "package": "react",
      "severity": "crit",
      "message": "Conflicting version ranges: ^18.0.0, ^9.0.0",
      "details": {
        "ranges": ["^18.0.0", "^9.0.0"],
        "installed_version": "18.0.2",
        "parent_packages": ["server"]
      },
      "parent_package": "server"
    }
  ],
  "summary": {
    "total": 1,
    "critical": 1,
    "warnings": 0,
    "info": 0
  }
}
```

### Filter by Severity

```bash
# Only show critical issues
$ origin audit --level crit

# Show all issues including info-level
$ origin audit --level info
```

### Ignore Specific Packages

```bash
# Ignore lodash during audit
$ origin audit --ignore lodash

# Ignore multiple packages
$ origin audit --ignore react ws
```

## Issue Types

### Version Conflicts (Critical)

Version conflicts occur when different parts of your dependency tree require incompatible versions of the same package. This can lead to runtime errors or unexpected behavior.

**Example:**
- Package A requires `react@^18.0.0`
- Package B requires `react@^9.0.0`

These ranges are incompatible and will cause a conflict.

### Outdated Packages

Packages that have newer versions available in the registry:

- **Critical**: Major version updates available
- **Warning**: Minor version updates available  
- **Info**: Patch version updates available

## Integration with CI/CD

You can integrate audit checks into your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Audit Dependencies
  run: |
    origin audit --level crit
  # This will fail the build if critical issues are found
```

```bash
# Pre-commit hook example
#!/bin/bash
origin audit --level warn
if [ $? -eq 2 ]; then
  echo "Critical dependency issues found!"
  exit 1
fi
```

## Best Practices

1. **Run regularly**: Include audit checks in your development workflow
2. **Fix critical issues first**: Address version conflicts before other issues
3. **Review updates carefully**: Test thoroughly when updating major versions
4. **Use ignore sparingly**: Only ignore packages when absolutely necessary
5. **Monitor over time**: Track how your dependency health improves

## Troubleshooting

### No Issues Found

If `origin audit` reports no issues but you expect some:

1. Check that your `pkg.json` and `origin.lock` files exist
2. Verify that packages are properly listed in dependencies
3. Ensure the registry has up-to-date version information

### False Positives

If you see conflicts that shouldn't exist:

1. Check the version ranges in your `pkg.json`
2. Verify that the lockfile accurately reflects installed versions
3. Consider using `--ignore` for known false positives

### Registry Issues

If outdated package detection isn't working:

1. Check your registry configuration
2. Verify that packages exist in the registry
3. Ensure network connectivity for registry queries 