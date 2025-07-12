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
from src.origin.replayer import Replayer
from src.origin.replay_shell import ReplayShell
from src.transform.blocks_to_ast import main as viz_main

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
    
    # Replay command (new functionality)
    replay_parser = subparsers.add_parser("replay", help="Replay recorded execution")
    replay_parser.add_argument("file", help="Recording file (.orirec) to replay")
    replay_parser.add_argument("--step", action="store_true", help="Start interactive step-by-step replay")
    replay_parser.add_argument("--start", type=int, help="Start at specific event index (0-based)")
    
    # Package management commands
    add_parser = subparsers.add_parser("add", help="Add a local library or remote package")
    add_parser.add_argument("source", type=str, help="Path to library folder or URL/package spec")
    add_parser.add_argument("--checksum", type=str, help="SHA-256 checksum for verification")
    add_parser.add_argument("--update", action="store_true", help="Update lockfile even if package exists")
    
    remove_parser = subparsers.add_parser("remove", help="Remove an installed library")
    remove_parser.add_argument("name", type=str, help="Library name")
    
    # Visual editor commands
    viz_parser = subparsers.add_parser("viz", help="Visual editor commands")
    viz_subparsers = viz_parser.add_subparsers(dest="viz_command", help="Visual editor subcommands")
    
    viz_import_parser = viz_subparsers.add_parser("import", help="Import .origin file to JSON blocks")
    viz_import_parser.add_argument("input", help="Input .origin file")
    viz_import_parser.add_argument("--out", help="Output JSON file (default: input.json)")
    
    viz_export_parser = viz_subparsers.add_parser("export", help="Export JSON blocks to .origin file")
    viz_export_parser.add_argument("input", help="Input JSON file")
    viz_export_parser.add_argument("--out", help="Output .origin file (default: input.origin)")
    
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
        
        elif args.command == "replay":
            # Load the recording file
            recording_path = pathlib.Path(args.file)
            if not recording_path.exists():
                print(f"Error: Recording file not found: {recording_path}")
                sys.exit(1)
            
            try:
                replayer = Replayer.from_file(recording_path)
                
                # Start at specific index if requested
                if args.start is not None:
                    if not replayer.goto(args.start):
                        print(f"Error: Invalid start index {args.start}")
                        sys.exit(1)
                
                if args.step:
                    # Start interactive shell
                    shell = ReplayShell(replayer)
                    shell.run()
                else:
                    # Just show info about the recording
                    info = replayer.get_info()
                    print(f"Recording: {recording_path}")
                    print(f"Total events: {info['total_events']}")
                    print("Use --step for interactive replay")
            
            except Exception as e:
                print(f"Error loading recording: {e}")
                sys.exit(1)
        
        elif args.command == "add":
            PackageManager().add(args.source, args.checksum, args.update)
        
        elif args.command == "remove":
            PackageManager().remove(args.name)
        
        elif args.command == "viz":
            if not args.viz_command:
                viz_parser.print_help()
                sys.exit(1)
            
            # Set up sys.argv for the viz_main function
            original_argv = sys.argv
            if args.viz_command == "import":
                sys.argv = ["blocks_to_ast.py", "import", args.input]
                if args.out:
                    sys.argv.append(args.out)
            elif args.viz_command == "export":
                sys.argv = ["blocks_to_ast.py", "export", args.input]
                if args.out:
                    sys.argv.append(args.out)
            
            try:
                viz_main()
            finally:
                sys.argv = original_argv
    
    except OriginPkgError as e:
        print(f"OriginPkgError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 