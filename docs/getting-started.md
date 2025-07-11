# Getting Started with Origin

## Installation

### Prerequisites
- Python 3.6 or higher
- Git

### Clone the Repository
```bash
git clone https://github.com/sher1996/origin-lang
cd origin-lang
```

## Running Origin Programs

### Basic Usage
```bash
python origin.py <filename.origin>
```

### Examples

#### Hello World
Create `hello.origin`:
```origin
say "Hello, Origin!"
```

Run it:
```bash
python origin.py hello.origin
```

#### Variables and Math
Create `math.origin`:
```origin
let x = 10
let y = 5
say x + y
say x * y
```

#### Loops
Create `loop.origin`:
```origin
repeat 3 times:
    say "Counting..."
```

#### Using Imports
Create `lib.origin`:
```origin
define square(n):
    n * n

let pi = 3.14159
```

Create `main.origin`:
```origin
import "lib.origin"
say square(5)
say pi
```

## Command Line Flags

Currently, Origin supports basic file execution:
- `python origin.py <file>` - Execute an Origin program
- No additional flags implemented yet

## Demo Programs

The repository includes several demo programs:

- `hello.origin` - Basic hello world
- `math_demo.origin` - Arithmetic operations
- `loop_demo.origin` - Loop examples
- `functions_demo.origin` - Function definitions
- `ai_demo.origin` - AI integration examples
- `net_demo.origin` - Network operations

Run any demo:
```bash
python origin.py math_demo.origin
```

## Language Features

### Current Features (v0.1)
- **Statements**: `say`, `let`
- **Expressions**: Arithmetic with `+`, `-`, `*`, `/`
- **Control Flow**: `repeat N times:` blocks
- **Variables**: `let` declarations
- **Comments**: `#` for inline comments
- **Imports**: `import "filename.origin"`

### Syntax Examples

```origin
# This is a comment
let x = 5
let y = x * 2
say y  # prints 10

repeat 3 times:
    say "Hello"

import "lib.origin"
say square(4)  # prints 16
```

## Next Steps

1. **Read the [Language Specification](language.md)** for complete syntax details
2. **Try the demo programs** in the repository
3. **Experiment** with your own Origin programs
4. **Contribute** to the project on GitHub

## Troubleshooting

### Common Issues

**"python: command not found"**
- Install Python from [python.org](https://python.org)
- Make sure Python is in your PATH

**"No module named 'origin'"**
- Make sure you're in the correct directory
- Run `python origin.py` from the repository root

**Import errors**
- Check that imported files exist in the same directory
- Verify file names match exactly (case-sensitive)

## Getting Help

- **Documentation**: Check the [Language Specification](language.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/sher1996/origin-lang/issues)
- **Examples**: Look at the demo files in the repository

---

Ready to write your first Origin program? Start with `hello.origin` and work your way up! 