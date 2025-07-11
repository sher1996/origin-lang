# ![logo](logo.png)

**Origin** is a human-friendly, AI-native programming language.

## Why Origin?

- **One language for web, AI, scripts** — Write once, run anywhere
- **Safe by default** — Built-in permissions and security
- **AI helpers built-in** — Natural language processing capabilities
- **Simple syntax** — Easy to learn and read

## Quick start

```bash
git clone https://github.com/sher1996/origin-lang
cd origin-lang
python origin.py hello.origin
```

→ See **[Getting Started](getting-started.md)** for details.

## Features

### Current (v0.1)
- **Basic statements**: `say`, `let`, arithmetic expressions
- **Control flow**: `repeat N times:` blocks
- **Import system**: Load definitions from other files
- **Comments**: `#` for inline comments

### Roadmap
- **Functions** — `define name(param):` blocks
- **Permission flags** — Runtime options like `--allow-net`
- **AI hooks** — `ai.ask`, `ai.classify`
- **Web integration** — Built-in HTTP client
- **Type system** — Gradual typing with inference

## Language Reference

See **[Language Specification](language.md)** for the complete syntax reference.

## Examples

### Hello World
```origin
say "Hello, Origin!"
```

### Variables and Math
```origin
let x = 5
let y = x * 3 - 4
say y  # prints 11
```

### Loops
```origin
repeat 3 times:
    say "Hi"
```

### Imports
```origin
import "lib.origin"
say square(5)  # prints 25
```

## Contributing

Origin is open source! Check out the [GitHub repository](https://github.com/sher1996/origin-lang) to contribute.

---

*Origin — Bridging human intent and machine execution* 