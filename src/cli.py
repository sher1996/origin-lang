#!/usr/bin/env python3
import argparse
import pathlib
import sys
import os

# Import the existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lexer
import parser

from src.origin.pkgmgr import PackageManager
from src.origin.errors import OriginPkgError
from src.origin.registry import Registry, parse_package_spec
from src.origin.net import is_url
from src.origin.evaluator import Evaluator
from src.origin.recorder import Recorder
from src.origin.utils import get_recording_path

def run(filename: str, net_allowed: bool = False, files_allowed: bool = True, record: bool = False) -> None:
    with open(filename) as f:
        source = f.read()
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    
    # Set up recorder if requested
    recorder = None
    if record:
        script_path = pathlib.Path(filename)
        recording_path = get_recording_path(script_path)
        recorder = Recorder(recording_path)
        print(f"Recording to {recording_path}")
    
    # Use evaluator instead of runtime
    evaluator = Evaluator(recorder)
    try:
        evaluator.execute(ast, base_path=None, net_allowed=net_allowed, files_allowed=files_allowed)
    finally:
        if recorder:
            recorder.close()

def main():
    arg_parser = argparse.ArgumentParser(description="Origin Language Interpreter")
    subparsers = arg_parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command (existing functionality)
    run_parser = subparsers.add_parser("run", help="Run an Origin file")
    run_parser.add_argument("file", help="Origin file to run")
    run_parser.add_argument("--allow-net", action="store_true", help="Allow network operations")
    run_parser.add_argument("--allow-files", action="store_true", default=True, help="Allow file operations")
    run_parser.add_argument("--deny-files", action="store_true", help="Deny file operations")
    run_parser.add_argument("--record", action="store_true", help="Record execution to .orirec file")
    
    # Package management commands
    add_parser = subparsers.add_parser("add", help="Add a local library or remote package")
    add_parser.add_argument("source", type=str, help="Path to library folder or URL/package spec")
    add_parser.add_argument("--checksum", type=str, help="SHA-256 checksum for verification")
    add_parser.add_argument("--update", action="store_true", help="Update lockfile even if package exists")
    
    remove_parser = subparsers.add_parser("remove", help="Remove an installed library")
    remove_parser.add_argument("name", type=str, help="Library name")
    
    args = arg_parser.parse_args()
    
    if not args.command:
        arg_parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "run":
            files_allowed = args.allow_files
            if args.deny_files:
                files_allowed = False
            
            run(args.file, net_allowed=args.allow_net, files_allowed=files_allowed, record=args.record)
        
        elif args.command == "add":
            PackageManager().add(args.source, args.checksum, args.update)
        
        elif args.command == "remove":
            PackageManager().remove(args.name)
    
    except OriginPkgError as e:
        print(f"OriginPkgError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 