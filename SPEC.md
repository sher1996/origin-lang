# Origin Language — Specification v0.1

## 0. Version scope
This spec covers features implemented up to commit 9339634.

## 1. File encoding & line endings
- UTF-8 text files, LF line endings preferred.

## 2. Statements

### 2.1 `say`
```origin
say "Hello, Origin."
say x + 2           # prints numeric result
```

### 2.2 Variable declaration `let`

```origin
let x = 5
let y = x * 3 - 4
```

### 2.3 Arithmetic expressions

* Operators: `+  -  *  /`
* Left-to-right evaluation, integers or floats.
* Variables may appear in expressions.
* No parentheses, strings, or booleans yet.

### 2.4 `repeat N times:` block

```origin
repeat 3 times:
    say "Hi"
```

* `N` must be an integer literal.
* Body = lines indented 4 spaces.

## 3. Comments

* `#` starts an inline comment; the rest of the line is ignored.

## 4. Reserved keywords

`say`, `let`, `repeat`, `times`

## 5. Future roadmap (confirmed but **not** implemented)

* **Functions** — `define name(param):` blocks
* **Import / module system** — `import math`
* **Permission flags** — runtime options like `--allow-net`
* **AI hooks** — `ai.ask`, `ai.classify`

(End of v0.1 spec) 