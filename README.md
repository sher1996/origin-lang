<div align="center">
  <img src="Origin logo.png" alt="Origin Language Logo" width="120">
</div>

# Origin Language
A programming language designed to bridge the gap between human intent and machine execution.

[![Build Status](https://github.com/origin-lang/origin/workflows/CI/badge.svg)](https://github.com/origin-lang/origin/actions)
[![Visual Debugger](https://img.shields.io/badge/Visual%20Debugger-Available-brightgreen)](docs/visual_debugger_overlay.md)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue)](docs/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

### Current syntax
say "text"
let name = number
say expression

## Chapter 9: Import System

You can now import definitions from another .origin file using:

```
import "lib.origin"
```

This loads and executes the given file once before continuing. Functions and global let variables defined there become available. Only string-literal filenames in the same folder are supported. Circular imports are not handled.

**Example:**

lib.origin:
```
define square(n):
    n * n
let answer = 42
```

main.origin:
```
import "lib.origin"
say square(answer)   # prints 1764
```

Running `python origin.py main.origin` prints:
```
1764
```

## Chapter 18: Remote Package Manager

The Origin Package Manager now supports both local and remote libraries in your projects.

### Quick Start

1. Create a `pkg.json` manifest:
```json
{
  "name": "my-project",
  "version": "0.1.0",
  "dependencies": {
    "math_utils": "./lib/math_utils"
  }
}
```

2. Add libraries:
```bash
# Local library
python src/cli.py add ./lib/math_utils

# Remote package
python src/cli.py add https://example.com/math_utils-0.2.0.tar.gz --checksum <sha256>
```

3. Remove libraries:
```bash
python src/cli.py remove math_utils
```

### Demo Projects

See `examples/pkg_demo/` for local library examples and `examples/pkg_remote_demo/` for remote package examples with:
- `pkg.json` manifest with remote dependencies
- Sample remote package with checksum verification
- Usage examples

For detailed documentation, see [docs/package-manager.md](docs/package-manager.md).

## Chapter 20: Execution Recorder

The Origin debugger now supports execution recording for debugging and analysis.

### Quick Start

Record execution of your Origin program:

```bash
origin run main.origin --record
```

This creates a timestamped `.orirec` file with detailed execution traces.

### Features

- **Zero overhead when disabled** - No performance impact without `--record`
- **Environment snapshots** - Track variable state at each execution step
- **Size-capped recordings** - Large values automatically truncated
- **JSONL format** - Easy to parse and analyze

### Example

```origin
LET x = 5
LET y = 10
SAY x + y
```

Running with `--record`:
```bash
$ origin run example.origin --record
Recording to example-20241201-143022.orirec
15
```

For detailed documentation, see [docs/debugger.md](docs/debugger.md).

- **Replay & step-back debugging:** Step through execution history interactively ([see docs](docs/debugger.md#replay--step-back)).

## Chapter 22: Visual Editor

The Origin Language now includes a visual editor for building programs using a drag-and-drop interface.

### Quick Start

Start the visual editor development server:

```bash
# From the project root
make dev

# Or directly
cd visual && npm run dev
```

The visual editor will be available at http://localhost:5173/

### Features

- **Blocks Palette** - Drag blocks (Variable, Add, Print) from the left sidebar
- **Canvas** - Drop blocks onto the main canvas to build your program
- **Drag and Drop** - Simple block positioning (no snapping/grids yet)

### Build for Production

```bash
make build
make preview
```

For detailed documentation, see [docs/visual-mode.md](docs/visual-mode.md).
# CI Test
