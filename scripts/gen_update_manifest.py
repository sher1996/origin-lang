#!/usr/bin/env python3
"""
Generate auto-update manifest for Origin binaries.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests


class UpdateManifestGenerator:
    """Generates auto-update manifest for Origin binaries."""
    
    def __init__(self, version: str, github_repo: str = "origin-lang/origin"):
        self.version = version
        self.github_repo = github_repo
        self.base_url = f"https://github.com/{github_repo}/releases/download/v{version}"
        
    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def find_binaries(self, dist_dir: Path) -> Dict[str, Path]:
        """Find built binaries in the dist directory."""
        binaries = {}
        
        if not dist_dir.exists():
            print(f"Warning: Dist directory not found: {dist_dir}")
            return binaries
        
        # Look for zip files
        for zip_file in dist_dir.glob("origin-*-*.zip"):
            # Parse filename: origin-{platform}-{version}.zip
            parts = zip_file.stem.split("-")
            if len(parts) >= 3:
                platform = parts[1]  # win, mac, linux
                binaries[platform] = zip_file
        
        return binaries
    
    def generate_manifest(self, dist_dir: Path, output_file: Path) -> Dict[str, Any]:
        """Generate the update manifest."""
        binaries = self.find_binaries(dist_dir)
        
        manifest = {
            "version": self.version,
            "release_date": self._get_release_date(),
            "platforms": {}
        }
        
        for platform, zip_path in binaries.items():
            if zip_path.exists():
                sha256 = self.calculate_sha256(zip_path)
                download_url = f"{self.base_url}/{zip_path.name}"
                
                manifest["platforms"][platform] = {
                    "version": self.version,
                    "sha256": sha256,
                    "url": download_url,
                    "filename": zip_path.name,
                    "size": zip_path.stat().st_size
                }
                
                print(f"Added {platform}: {zip_path.name} ({sha256[:8]}...)")
            else:
                print(f"Warning: Binary not found for {platform}: {zip_path}")
        
        # Write manifest
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Manifest written to: {output_file}")
        return manifest
    
    def _get_release_date(self) -> str:
        """Get current date in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validate the generated manifest."""
        required_fields = ["version", "platforms"]
        for field in required_fields:
            if field not in manifest:
                print(f"Error: Missing required field '{field}' in manifest")
                return False
        
        if not manifest["platforms"]:
            print("Warning: No platforms found in manifest")
            return False
        
        for platform, info in manifest["platforms"].items():
            required_platform_fields = ["version", "sha256", "url"]
            for field in required_platform_fields:
                if field not in info:
                    print(f"Error: Missing required field '{field}' for platform '{platform}'")
                    return False
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate auto-update manifest for Origin binaries")
    parser.add_argument("--version", required=True, help="Version string (e.g., 0.30.0)")
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"), 
                       help="Directory containing built binaries (default: dist/)")
    parser.add_argument("--output", type=Path, default=Path("releases/update.json"),
                       help="Output manifest file (default: releases/update.json)")
    parser.add_argument("--github-repo", default="origin-lang/origin",
                       help="GitHub repository (default: origin-lang/origin)")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate existing manifest, don't generate new one")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / args.dist_dir
    output_file = project_root / args.output
    
    generator = UpdateManifestGenerator(args.version, args.github_repo)
    
    if args.validate_only:
        if not output_file.exists():
            print(f"Error: Manifest file not found: {output_file}")
            sys.exit(1)
        
        with open(output_file, 'r') as f:
            manifest = json.load(f)
        
        if generator.validate_manifest(manifest):
            print("Manifest validation passed!")
            sys.exit(0)
        else:
            print("Manifest validation failed!")
            sys.exit(1)
    else:
        # Generate new manifest
        manifest = generator.generate_manifest(dist_dir, output_file)
        
        if generator.validate_manifest(manifest):
            print("Manifest generated and validated successfully!")
            sys.exit(0)
        else:
            print("Manifest validation failed!")
            sys.exit(1)


if __name__ == "__main__":
    main() 