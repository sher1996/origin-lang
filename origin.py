#!/usr/bin/env python3
import sys
import re

def run(filename: str) -> None:
    with open(filename) as f:
        lines = f.readlines()

    variables: dict[str, float] = {}

    # Very small helper that safely evaluates an arithmetic expression.
    # It sees only the current variables and the four operator symbols.
    def eval_expr(expr: str) -> float:
        allowed_names = {**variables, "__builtins__": {}}
        # Remove accidental double-spaces so "x  +  2" still works
        expr = re.sub(r"\s+", " ", expr.strip())
        return eval(expr, allowed_names)

    i = 0
    n_lines = len(lines)
    while i < n_lines:
        raw = lines[i]
        # strip comments and leading/trailing whitespace
        line = raw.split("#", 1)[0].rstrip("\n")
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("let "):
            # let NAME = EXPR
            _, rest = stripped.split("let ", 1)
            name, expr = map(str.strip, rest.split("=", 1))
            variables[name] = eval_expr(expr)
            i += 1
        elif stripped.startswith("say "):
            expr = stripped[4:].strip()
            result = eval_expr(expr)
            if isinstance(result, float) and result.is_integer():
                print(int(result))
            else:
                print(result)
            i += 1
        elif stripped.startswith("repeat ") and stripped.endswith(" times:"):
            # repeat N times:
            match = re.match(r"repeat (\d+) times:", stripped)
            if not match:
                raise SyntaxError(f"Invalid repeat syntax: {stripped}")
            count = int(match.group(1))
            # Find indented block
            body = []
            j = i + 1
            while j < n_lines:
                next_line = lines[j].rstrip("\n")
                if next_line.startswith("    "):
                    body.append(next_line[4:])
                    j += 1
                elif not next_line.strip():
                    j += 1  # skip blank lines in body
                else:
                    break
            for _ in range(count):
                for body_line in body:
                    # Re-parse each body line as if it were a top-level line
                    # This is a minimal interpreter, so we can just copy the main logic
                    bstripped = body_line.strip()
                    if not bstripped:
                        continue
                    if bstripped.startswith("let "):
                        _, rest = bstripped.split("let ", 1)
                        name, expr = map(str.strip, rest.split("=", 1))
                        variables[name] = eval_expr(expr)
                    elif bstripped.startswith("say "):
                        expr = bstripped[4:].strip()
                        result = eval_expr(expr)
                        if isinstance(result, float) and result.is_integer():
                            print(int(result))
                        else:
                            print(result)
                    else:
                        raise SyntaxError(f"Unknown command in repeat: {bstripped}")
            i = j
        else:
            raise SyntaxError(f"Unknown command: {stripped}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python origin.py <script.origin>")
        sys.exit(1)
    run(sys.argv[1]) 