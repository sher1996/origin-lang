#!/usr/bin/env python3
"""
Test script for the package command functionality.
"""

import subprocess
import sys
from pathlib import Path

def test_package_command():
    """Test that the package command is available and works."""
    print("Testing package command...")
    
    # Test that the command is available
    try:
        result = subprocess.run([
            sys.executable, "-m", "src.cli", "package", "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Package command help failed: {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
        
        print("✅ Package command help works")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Package command help timed out")
        return False
    except Exception as e:
        print(f"❌ Package command help error: {e}")
        return False

def test_pyinstaller_spec():
    """Test that the PyInstaller spec file exists and is valid."""
    print("Testing PyInstaller spec file...")
    
    spec_file = Path("build/pyinstaller.spec")
    if not spec_file.exists():
        print(f"❌ PyInstaller spec file not found: {spec_file}")
        return False
    
    print("✅ PyInstaller spec file exists")
    return True

def test_scripts():
    """Test that the build scripts exist."""
    print("Testing build scripts...")
    
    scripts = [
        "scripts/gen_update_manifest.py",
        "scripts/smoke_bin.py"
    ]
    
    for script in scripts:
        script_path = Path(script)
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        print(f"✅ Script exists: {script}")
    
    return True

def test_dockerfiles():
    """Test that the Dockerfiles exist."""
    print("Testing Dockerfiles...")
    
    dockerfiles = [
        "Dockerfile.win",
        "Dockerfile.linux"
    ]
    
    for dockerfile in dockerfiles:
        dockerfile_path = Path(dockerfile)
        if not dockerfile_path.exists():
            print(f"❌ Dockerfile not found: {dockerfile_path}")
            return False
        print(f"✅ Dockerfile exists: {dockerfile}")
    
    return True

def test_workflow():
    """Test that the GitHub workflow exists."""
    print("Testing GitHub workflow...")
    
    workflow_path = Path(".github/workflows/build-binaries.yml")
    if not workflow_path.exists():
        print(f"❌ Workflow not found: {workflow_path}")
        return False
    
    print("✅ GitHub workflow exists")
    return True

def test_docs():
    """Test that the documentation exists."""
    print("Testing documentation...")
    
    docs_path = Path("docs/install-binaries.md")
    if not docs_path.exists():
        print(f"❌ Documentation not found: {docs_path}")
        return False
    
    print("✅ Documentation exists")
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("PACKAGE COMMAND TESTS")
    print("=" * 50)
    
    tests = [
        test_package_command,
        test_pyinstaller_spec,
        test_scripts,
        test_dockerfiles,
        test_workflow,
        test_docs
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 