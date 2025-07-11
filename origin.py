#!/usr/bin/env python3
import sys
import lexer
import parser
import runtime

def run(filename: str) -> None:
    with open(filename) as f:
        source = f.read()
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    runtime.execute(ast)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python origin.py <script.origin>")
        sys.exit(1)
    run(sys.argv[1]) 