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
        # Remove accidental double-spaces so “x  +  2” still works
        expr = re.sub(r"\s+", " ", expr.strip())
        return eval(expr, allowed_names)

    for raw in lines:
        # strip comments and leading/trailing whitespace
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("let "):
            # let NAME = EXPR
            _, rest = line.split("let ", 1)
            name, expr = map(str.strip, rest.split("=", 1))
            variables[name] = eval_expr(expr)
        elif line.startswith("say "):
            expr = line[4:].strip()
            result = eval_expr(expr)
            if isinstance(result, float) and result.is_integer():
                print(int(result))
            else:
                print(result)
        else:
            raise SyntaxError(f"Unknown command: {line}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python origin.py <script.origin>")
        sys.exit(1)
    run(sys.argv[1]) 