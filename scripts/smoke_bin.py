#!/usr/bin/env python3
"""
Smoke test script for Origin binaries.
"""

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import requests


class BinarySmokeTester:
    """Tests Origin binaries for basic functionality."""
    
    def __init__(self, zip_url: str):
        self.zip_url = zip_url
        self.temp_dir = None
        self.binary_path = None
        
    def download_and_verify(self) -> bool:
        """Download the binary zip and verify SHA-256."""
        print(f"Downloading: {self.zip_url}")
        
        try:
            # Download the zip file
            response = requests.get(self.zip_url, stream=True)
            response.raise_for_status()
            
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp())
            zip_path = self.temp_dir / "origin.zip"
            
            # Save the zip file
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded to: {zip_path}")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(self.temp_dir)
            
            # Find the executable
            if sys.platform == "win32":
                exe_name = "origin.exe"
            else:
                exe_name = "origin"
            
            if self.temp_dir:
                self.binary_path = self.temp_dir / exe_name
            else:
                print("Error: temp_dir is None")
                return False
            if not self.binary_path.exists():
                print(f"Error: Executable not found: {self.binary_path}")
                return False
            
            # Make executable (Unix-like systems)
            if sys.platform != "win32":
                os.chmod(self.binary_path, 0o755)
            
            print(f"Binary extracted: {self.binary_path}")
            return True
            
        except Exception as e:
            print(f"Error downloading/verifying: {e}")
            return False
    
    def test_version(self) -> bool:
        """Test the --version command."""
        print("Testing --version...")
        
        try:
            result = subprocess.run(
                [str(self.binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Version test failed: {result.returncode}")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
            
            print(f"Version: {result.stdout.strip()}")
            return True
            
        except subprocess.TimeoutExpired:
            print("Version test timed out")
            return False
        except Exception as e:
            print(f"Version test error: {e}")
            return False
    
    def test_help(self) -> bool:
        """Test the --help command."""
        print("Testing --help...")
        
        try:
            result = subprocess.run(
                [str(self.binary_path), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Help test failed: {result.returncode}")
                return False
            
            print("Help command works")
            return True
            
        except subprocess.TimeoutExpired:
            print("Help test timed out")
            return False
        except Exception as e:
            print(f"Help test error: {e}")
            return False
    
    def test_example(self) -> bool:
        """Test running a simple example."""
        print("Testing example execution...")
        
        # Create a simple test file
        if self.temp_dir:
            test_file = self.temp_dir / "test.ori"
            with open(test_file, 'w') as f:
                f.write('print("Hello from Origin binary!")\n')
        else:
            print("Error: temp_dir is None")
            return False
        
        try:
            result = subprocess.run(
                [str(self.binary_path), "run", str(test_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Example test failed: {result.returncode}")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
            
            print(f"Example output: {result.stdout.strip()}")
            return True
            
        except subprocess.TimeoutExpired:
            print("Example test timed out")
            return False
        except Exception as e:
            print(f"Example test error: {e}")
            return False
    
    def run_smoke_test(self) -> bool:
        """Run the complete smoke test."""
        print("=" * 50)
        print("ORIGIN BINARY SMOKE TEST")
        print("=" * 50)
        
        # Download and verify
        if not self.download_and_verify():
            return False
        
        # Test version
        if not self.test_version():
            return False
        
        # Test help
        if not self.test_help():
            return False
        
        # Test example
        if not self.test_example():
            return False
        
        print("=" * 50)
        print("SMOKE TEST PASSED!")
        print("=" * 50)
        return True
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up: {self.temp_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Smoke test Origin binaries")
    parser.add_argument("zip_url", help="URL to the binary zip file")
    parser.add_argument("--keep", action="store_true", help="Keep temporary files")
    
    args = parser.parse_args()
    
    tester = BinarySmokeTester(args.zip_url)
    
    try:
        success = tester.run_smoke_test()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Smoke test failed!")
            sys.exit(1)
    finally:
        if not args.keep:
            tester.cleanup()


if __name__ == "__main__":
    main() 