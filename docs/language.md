# Origin Language Specification

## Version Scope
This specification covers features implemented up to commit 9339634.

## File Encoding & Line Endings
- UTF-8 text files, LF line endings preferred.

## Statements

### `say`
```origin
say "Hello, Origin."
say x + 2           # prints numeric result
```

### Variable Declaration `let`
```origin
let x = 5
let y = x * 3 - 4
```

### Arithmetic Expressions
- **Operators**: `+`, `-`, `*`, `/`
- **Evaluation**: Left-to-right evaluation, integers or floats
- **Variables**: May appear in expressions
- **Limitations**: No parentheses, strings, or booleans yet

### `repeat N times:` Block
```origin
repeat 3 times:
    say "Hi"
```

- `N` must be an integer literal
- Body consists of lines indented 4 spaces

## Comments
- `#` starts an inline comment; the rest of the line is ignored

## Reserved Keywords
`say`, `let`, `repeat`, `times`

## Import System
```origin
import "filename.origin"
```

- Loads and executes the given file once before continuing
- Functions and global `let` variables defined there become available
- Only string-literal filenames in the same folder are supported
- Circular imports are not handled

### Import Example

**lib.origin:**
```origin
define square(n):
    n * n
let answer = 42
```

**main.origin:**
```origin
import "lib.origin"
say square(answer)   # prints 1764
```

Running `python origin.py main.origin` prints:
```
1764
```

## Future Roadmap

The following features are confirmed but **not yet implemented**:

- **Functions** — `define name(param):` blocks
- **Permission flags** — Runtime options like `--allow-net`
- **AI hooks** — `ai.ask`, `ai.classify`
- **Web integration** — Built-in HTTP client
- **Type system** — Gradual typing with inference

---

*End of v0.1 specification* 