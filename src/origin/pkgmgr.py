import json
import shutil
import pathlib
import hashlib
import tempfile
from urllib.parse import urlparse
from .errors import OriginPkgError
from .net import download, download_checksum, is_url
from .archive import extract_archive, is_archive_file
from .registry import Registry, parse_package_spec

LIB_DIR = pathlib.Path(".origin") / "libs"

class PackageManager:
    def __init__(self, cwd: pathlib.Path = pathlib.Path.cwd()):
        self.cwd = cwd
        self.manifest_path = cwd / "pkg.json"
        if not self.manifest_path.exists():
            raise OriginPkgError("No pkg.json found in this directory.")

        self.manifest = json.loads(self.manifest_path.read_text())

    # public API -----------------------------------------------------------

    def add(self, src: str, checksum: str | None = None):
        """
        Add a library from local path or remote URL.
        
        Args:
            src: Local path or remote URL
            checksum: Optional SHA-256 checksum for verification
        """
        LIB_DIR.mkdir(parents=True, exist_ok=True)
        
        if is_url(src):
            self._install_remote(src, checksum)
        else:
            src_path = pathlib.Path(src)
            if src_path.is_file() and is_archive_file(src_path):
                self._install_local_archive(src_path, checksum)
            else:
                self._install_local(src_path)
    
    def _install_local(self, src: pathlib.Path):
        """Install a local library."""
        if not src.exists():
            raise OriginPkgError(f"Cannot find library at {src}")

        dest = LIB_DIR / src.name
        if dest.exists():
            raise OriginPkgError(f"Library '{src.name}' already installed.")

        shutil.copytree(src, dest)
        print(f"✔ Installed {src.name} → {dest}")
    
    def _install_local_archive(self, archive_path: pathlib.Path, checksum: str | None = None):
        """Install a local archive file as a library."""
        if not archive_path.exists():
            raise OriginPkgError(f"Archive file not found: {archive_path}")
        if not is_archive_file(archive_path):
            raise OriginPkgError(f"Unsupported archive format: {archive_path.suffix}")
        # Verify checksum if provided
        if checksum:
            self._verify_checksum(archive_path, checksum)
        # Extract to temporary location
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            extract_archive(archive_path, temp_path)
            # Find top-level dirs
            items = [p for p in temp_path.iterdir() if p.is_dir()]
            if len(items) != 1:
                raise OriginPkgError(f"Archive must contain exactly one top-level directory, found {len(items)}.")
            lib_dir = items[0]
            # Use base name (strip version if present)
            base = archive_path.stem
            if base.endswith('.tar'):
                base = pathlib.Path(base).stem
            # Remove version suffix if present (e.g. math_utils-0.2.0 → math_utils)
            name = base.split('-')[0] if '-' in base else base
            dest = LIB_DIR / name
            if dest.exists():
                raise OriginPkgError(f"Library '{name}' already installed.")
            shutil.copytree(lib_dir, dest)
            print(f"✔ Installed {name} → {dest}")
    
    def _install_remote(self, url: str, checksum: str | None = None):
        """Install a remote library from URL."""
        # Parse URL to get filename
        parsed_url = urlparse(url)
        filename = pathlib.Path(parsed_url.path).name
        
        if not filename:
            raise OriginPkgError(f"Could not determine filename from URL: {url}")
        
        # Check if already installed
        dest = LIB_DIR / filename
        if dest.exists():
            raise OriginPkgError(f"Library '{filename}' already installed.")
        
        # Download to temporary location
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir) / filename
            download(url, temp_path)
            
            # Verify checksum if provided
            if checksum:
                self._verify_checksum(temp_path, checksum)
            else:
                # Try to download checksum file
                checksum_url = f"{url}.sha256"
                downloaded_checksum = download_checksum(checksum_url)
                if downloaded_checksum:
                    self._verify_checksum(temp_path, downloaded_checksum)
            
            # Extract if it's an archive
            if is_archive_file(temp_path):
                extract_dir = temp_path.parent / temp_path.stem
                extract_archive(temp_path, extract_dir)
                
                # Find the actual library directory
                extracted_items = list(extract_dir.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    # Single directory, use it as the library
                    lib_dir = extracted_items[0]
                else:
                    # Multiple items or files, use the extract directory
                    lib_dir = extract_dir
                
                # Copy to final location
                final_dest = LIB_DIR / lib_dir.name
                shutil.copytree(lib_dir, final_dest)
                print(f"✔ Installed {lib_dir.name} → {final_dest}")
            else:
                # Not an archive, copy directly
                shutil.copy2(temp_path, dest)
                print(f"✔ Installed {filename} → {dest}")
    
    def _verify_checksum(self, file_path: pathlib.Path, expected_checksum: str):
        """Verify SHA-256 checksum of a file (case-insensitive)."""
        with open(file_path, 'rb') as f:
            actual_checksum = hashlib.sha256(f.read()).hexdigest()
        if actual_checksum.lower() != expected_checksum.lower():
            raise OriginPkgError(
                f"Checksum verification failed for {file_path.name}. "
                f"Expected: {expected_checksum}, Got: {actual_checksum}"
            )
        print(f"✓ Checksum verified for {file_path.name}")

    def remove(self, name: str):
        target = LIB_DIR / name
        if not target.exists():
            raise OriginPkgError(f"No installed lib named '{name}'.")
        shutil.rmtree(target)
        print(f"✖ Removed {name}") 