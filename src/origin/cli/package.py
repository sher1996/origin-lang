#!/usr/bin/env python3
"""
Package CLI module for building standalone Origin executables.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


class PackageBuilder:
    """Builds standalone Origin executables using PyInstaller."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        
    def detect_platform(self) -> str:
        """Detect the current platform."""
        system = platform.system().lower()
        if system == "windows":
            return "win"
        elif system == "darwin":
            return "mac"
        elif system == "linux":
            return "linux"
        else:
            raise ValueError(f"Unsupported platform: {system}")
    
    def get_version(self) -> str:
        """Extract version from setup.py or default to 0.1.0."""
        try:
            # Try to import setup.py and get version
            import setup
            return getattr(setup, 'version', '0.1.0')
        except ImportError:
            # Fallback to reading setup.py manually
            setup_file = self.project_root / "setup.py"
            if setup_file.exists():
                with open(setup_file, 'r') as f:
                    content = f.read()
                    # Simple regex to find version
                    import re
                    match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                    if match:
                        return match.group(1)
            return "0.1.0"
    
    def install_dependencies(self) -> None:
        """Install PyInstaller and other build dependencies."""
        print("Installing build dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pyinstaller>=5.0", "requests>=2.32.0"
        ], check=True)
    
    def build_executable(self, platform_name: str, output_dir: Path) -> Path:
        """Build executable for the specified platform."""
        print(f"Building Origin executable for {platform_name}...")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run PyInstaller
        spec_file = self.project_root / "build" / "pyinstaller.spec"
        if not spec_file.exists():
            raise FileNotFoundError(f"PyInstaller spec file not found: {spec_file}")
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--distpath", str(output_dir),
            "--workpath", str(self.build_dir),
            str(spec_file)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=self.project_root)
        
        # Find the built executable
        if platform_name == "win":
            exe_name = "origin.exe"
        else:
            exe_name = "origin"
        
        exe_path = output_dir / exe_name
        if not exe_path.exists():
            raise FileNotFoundError(f"Built executable not found: {exe_path}")
        
        return exe_path
    
    def create_package_zip(self, exe_path: Path, platform_name: str, version: str, 
                          output_dir: Path) -> Tuple[Path, str]:
        """Create a zip package with the executable and additional files."""
        zip_name = f"origin-{platform_name}-{version}.zip"
        zip_path = output_dir / zip_name
        
        # Files to include in the zip
        files_to_include = [
            (exe_path, exe_path.name),
            (self.project_root / "LICENSE", "LICENSE"),
            (self.project_root / "README.md", "README-binary.md"),
        ]
        
        # Generate third-party licenses
        third_party_file = self.generate_third_party_licenses()
        if third_party_file:
            files_to_include.append((third_party_file, "THIRD_PARTY_LICENSES.txt"))
        
        # Create zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, arc_name in files_to_include:
                if file_path.exists():
                    zf.write(file_path, arc_name)
                    print(f"Added to zip: {arc_name}")
                else:
                    print(f"Warning: File not found: {file_path}")
        
        # Calculate SHA-256
        sha256 = self.calculate_sha256(zip_path)
        
        # Create SHA-256 file
        sha256_file = zip_path.with_suffix('.zip.sha256')
        with open(sha256_file, 'w') as f:
            f.write(f"{sha256}  {zip_path.name}\n")
        
        return zip_path, sha256
    
    def generate_third_party_licenses(self) -> Optional[Path]:
        """Generate THIRD_PARTY_LICENSES.txt using pip-licenses."""
        try:
            # Try to install pip-licenses if not available
            subprocess.run([
                sys.executable, "-m", "pip", "install", "pip-licenses"
            ], check=True, capture_output=True)
            
            # Generate licenses
            result = subprocess.run([
                sys.executable, "-m", "pip_licenses", "--format=plain-text"
            ], check=True, capture_output=True, text=True)
            
            # Write to temporary file
            temp_file = Path(tempfile.mktemp(suffix='.txt'))
            with open(temp_file, 'w') as f:
                f.write(result.stdout)
            
            return temp_file
            
        except (subprocess.CalledProcessError, ImportError):
            print("Warning: Could not generate third-party licenses")
            return None
    
    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def smoke_test(self, exe_path: Path) -> bool:
        """Run a basic smoke test on the built executable."""
        print("Running smoke test...")
        
        try:
            # Test --version
            result = subprocess.run([str(exe_path), "--version"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Smoke test failed: --version returned {result.returncode}")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
            
            # Test --help
            result = subprocess.run([str(exe_path), "--help"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Smoke test failed: --help returned {result.returncode}")
                return False
            
            # Test running a simple example if available
            greeter_example = self.project_root / "examples" / "greeter" / "main.ori"
            if greeter_example.exists():
                result = subprocess.run([str(exe_path), "run", str(greeter_example)], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"Smoke test failed: example run returned {result.returncode}")
                    print(f"stdout: {result.stdout}")
                    print(f"stderr: {result.stderr}")
                    return False
            
            print("Smoke test passed!")
            return True
            
        except subprocess.TimeoutExpired:
            print("Smoke test failed: timeout")
            return False
        except Exception as e:
            print(f"Smoke test failed: {e}")
            return False
    
    def build(self, platform_name: Optional[str] = None, 
              output_dir: Optional[Path] = None, version: Optional[str] = None) -> Dict[str, str]:
        """Build executable for the specified platform."""
        
        # Set defaults
        if platform_name is None:
            platform_name = self.detect_platform()
        
        if output_dir is None:
            output_dir = self.dist_dir
        
        if version is None:
            version = self.get_version()
        
        print(f"Building Origin {version} for {platform_name}")
        print(f"Output directory: {output_dir}")
        
        # Install dependencies
        self.install_dependencies()
        
        # Build executable
        exe_path = self.build_executable(platform_name, output_dir)
        
        # Create package zip
        zip_path, sha256 = self.create_package_zip(exe_path, platform_name, version, output_dir)
        
        # Run smoke test
        if not self.smoke_test(exe_path):
            print("Warning: Smoke test failed, but continuing...")
        
        print(f"Build complete!")
        print(f"Executable: {exe_path}")
        print(f"Package: {zip_path}")
        print(f"SHA-256: {sha256}")
        
        return {
            "platform": platform_name,
            "version": version,
            "executable": str(exe_path),
            "package": str(zip_path),
            "sha256": sha256
        }


def main():
    """Main entry point for the package command."""
    parser = argparse.ArgumentParser(description="Build standalone Origin executables")
    parser.add_argument("--platform", choices=["win", "mac", "linux"], 
                       help="Target platform (defaults to current platform)")
    parser.add_argument("--output", type=Path, help="Output directory (defaults to dist/)")
    parser.add_argument("--version", help="Version string (defaults to setup.py version)")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent.parent
    
    # Build the package
    builder = PackageBuilder(project_root)
    result = builder.build(
        platform_name=args.platform,
        output_dir=args.output,
        version=args.version
    )
    
    # Print result as JSON for CI integration
    print("\n" + "="*50)
    print("BUILD RESULT")
    print("="*50)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 