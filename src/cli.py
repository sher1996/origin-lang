#!/usr/bin/env python3
import argparse
import pathlib
import sys
import os
import json
from typing import cast, List, Any

# Import the existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lexer
import parser
from src.origin.parser.optimizations import constant_fold

from src.origin.pkgmgr import PackageManager
from src.origin.errors import OriginPkgError, PublishError
from src.origin.registry import Registry, parse_package_spec
from src.origin.net import is_url
from src.origin.evaluator import Evaluator
from src.origin.recorder import Recorder
from src.origin.utils import get_recording_path
from src.origin.replayer import Replayer
from src.origin.replay_shell import ReplayShell
from src.origin.publish import publish_package

def run(filename: str, net_allowed: bool = False, files_allowed: bool = True, record: bool = False, args: list = None, profile: bool = False) -> None:
    with open(filename) as f:
        source = f.read()
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    if ast is None:
        ast = []
    # Apply constant folding optimization
    ast = [constant_fold(node) for node in ast]
    
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
        evaluator.execute(ast, base_path=None, net_allowed=net_allowed, files_allowed=files_allowed, args=args)
        
        # Print profiling information if requested
        if profile:
            print("\n" + "="*50)
            print("PROFILING RESULTS")
            print("="*50)
            print("Profiling not yet implemented in current evaluator")
            print("Use the visitor-based evaluator for detailed profiling")
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
    run_parser.add_argument("--profile", action="store_true", help="Print execution profiling statistics")
    
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
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish package to GitHub Releases")
    publish_parser.add_argument("--token", type=str, help="GitHub personal access token")
    publish_parser.add_argument("--dry-run", action="store_true", help="Show what would be done without publishing")
    publish_parser.add_argument("--tag", type=str, help="Custom release tag (defaults to v{version})")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit dependency tree for conflicts and outdated packages")
    audit_parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    audit_parser.add_argument("--level", choices=["info", "warn", "crit"], default="warn", 
                             help="Minimum severity level to report (default: warn)")
    audit_parser.add_argument("--ignore", nargs="+", help="Packages to ignore during audit")
    # Visual editor commands
    viz_parser = subparsers.add_parser("viz", help="Visual editor commands")
    viz_subparsers = viz_parser.add_subparsers(dest="viz_command", help="Available viz commands")
    
    viz_import_parser = viz_subparsers.add_parser("import", help="Import .origin file to JSON blocks")
    viz_import_parser.add_argument("input", help="Input .origin file")
    viz_import_parser.add_argument("--out", help="Output JSON file (default: stdout)")
    
    viz_export_parser = viz_subparsers.add_parser("export", help="Export JSON blocks to .origin file")
    viz_export_parser.add_argument("input", help="Input JSON file")
    viz_export_parser.add_argument("--out", help="Output .origin file (default: stdout)")
    
    viz_save_parser = viz_subparsers.add_parser("save", help="Save current project as .originproj file")
    viz_save_parser.add_argument("output", help="Output .originproj file")
    
    viz_open_parser = viz_subparsers.add_parser("open", help="Open .originproj file and extract to current directory")
    viz_open_parser.add_argument("input", help="Input .originproj file")
    
    args = arg_parser.parse_args()
    
    if not args.command:
        arg_parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "run":
            files_allowed = args.allow_files
            if args.deny_files:
                files_allowed = False
            
            # Pass extra command line arguments as ARGS
            file_index = sys.argv.index(args.file)
            extra_args = sys.argv[file_index+1:]
            run(args.file, net_allowed=args.allow_net, files_allowed=files_allowed, record=args.record, args=extra_args, profile=args.profile)
        
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
        
        elif args.command == "publish":
            try:
                publish_package(
                    project_path=pathlib.Path.cwd(),
                    token=args.token,
                    dry_run=args.dry_run,
                    tag=args.tag
                )
            except PublishError as e:
                print(f"PublishError: {e}")
                sys.exit(1)
        
        elif args.command == "audit":
            try:
                from src.origin.audit import DependencyAuditor, Severity
                
                # Parse severity level
                severity_map = {
                    "info": Severity.INFO,
                    "warn": Severity.WARN,
                    "crit": Severity.CRIT
                }
                level = severity_map[args.level]
                
                # Run audit
                auditor = DependencyAuditor()
                issues = auditor.audit(level=level, ignore_packages=args.ignore)
                
                # Format and output report
                report = auditor.format_report(issues, json_output=args.json)
                print(report)
                
                # Set exit code based on severity
                if any(issue.severity == Severity.CRIT for issue in issues):
                    sys.exit(2)
                elif any(issue.severity == Severity.WARN for issue in issues):
                    sys.exit(1)
                else:
                    sys.exit(0)
                    
            except Exception as e:
                print(f"AuditError: {e}")
                sys.exit(1)
        
        elif args.command == "viz":
            # Import the transform modules
            from src.transform.blocks_to_ast import code_to_blocks, blocks_to_code
            from src.transform.project_zip import save_current_project, extract_project_zip
            
            if args.viz_command == "import":
                with open(args.input, 'r') as f:
                    code = f.read()
                
                blocks = code_to_blocks(code)
                output = json.dumps(blocks, indent=2)
                
                if args.out:
                    with open(args.out, 'w') as f:
                        f.write(output)
                else:
                    print(output)
            
            elif args.viz_command == "export":
                with open(args.input, 'r') as f:
                    blocks = json.load(f)
                
                code = blocks_to_code(blocks)
                
                if args.out:
                    with open(args.out, 'w') as f:
                        f.write(code)
                else:
                    print(code)
            
            elif args.viz_command == "save":
                try:
                    save_current_project(args.output)
                    print(f"Project saved to {args.output}")
                except Exception as e:
                    print(f"Error saving project: {e}")
                    sys.exit(1)
            
            elif args.viz_command == "open":
                try:
                    # Extract to current directory
                    project_data = extract_project_zip(args.input, '.')
                    print(f"Project extracted from {args.input}")
                    print(f"Project: {project_data['metadata'].get('name', 'Unknown')}")
                    print(f"Version: {project_data['metadata'].get('version', '1.0.0')}")
                except Exception as e:
                    print(f"Error opening project: {e}")
                    sys.exit(1)
            
            else:
                viz_parser.print_help()
                sys.exit(1)
    
    except OriginPkgError as e:
        print(f"OriginPkgError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 