#!/usr/bin/env python3
import sys
import lexer
import parser
import runtime
import os

def run(filename: str, net_allowed: bool = False, files_allowed: bool = True) -> None:
    with open(filename) as f:
        source = f.read()
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    runtime.execute(ast, base_path=None, net_allowed=net_allowed, files_allowed=files_allowed)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python origin.py <file.origin> [--allow-net] [--allow-files]")
        sys.exit(1)
    
    # Parse CLI flags
    net_allowed = False
    files_allowed = True
    
    args = sys.argv[1:]
    filename = None
    
    for arg in args:
        if arg == "--allow-net":
            net_allowed = True
        elif arg == "--allow-files":
            files_allowed = True
        elif arg == "--deny-files":
            files_allowed = False
        elif not arg.startswith("--"):
            filename = arg
    
    if filename is None:
        print("Usage: python origin.py <file.origin> [--allow-net] [--allow-files]")
        sys.exit(1)
    
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    base_path = os.path.dirname(os.path.abspath(filename))
    runtime.execute(ast, base_path=base_path, net_allowed=net_allowed, files_allowed=files_allowed) 