import json
import pathlib
from typing import Dict, Any, Optional
from .errors import OriginPkgError


class Lockfile:
    """Helper class for managing origin.lock files."""
    
    def __init__(self, lock_path: pathlib.Path):
        """
        Initialize lockfile helper.
        
        Args:
            lock_path: Path to the lockfile
        """
        self.lock_path = lock_path
        self._data: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """Load the lockfile data."""
        if self._data is not None:
            return self._data
        
        if not self.lock_path.exists():
            self._data = {}
            return self._data
        
        try:
            with open(self.lock_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._data = data
                    return self._data
                else:
                    raise OriginPkgError(f"Lockfile {self.lock_path} must contain a JSON object")
        except json.JSONDecodeError as e:
            raise OriginPkgError(f"Invalid lockfile {self.lock_path}: {e}")
        except Exception as e:
            raise OriginPkgError(f"Failed to load lockfile {self.lock_path}: {e}")
    
    def save(self, data: Dict[str, Any]) -> None:
        """
        Save data to the lockfile with deterministic ordering.
        
        Args:
            data: Dictionary to save
        """
        try:
            # Ensure directory exists
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort keys for deterministic output
            sorted_data = self._sort_dict(data)
            
            with open(self.lock_path, 'w') as f:
                json.dump(sorted_data, f, indent=2, sort_keys=True)
            
            # Update cache
            self._data = data
            
        except Exception as e:
            raise OriginPkgError(f"Failed to write lockfile {self.lock_path}: {e}")
    
    def _sort_dict(self, obj: Any) -> Any:
        """Recursively sort dictionary keys for deterministic output."""
        if isinstance(obj, dict):
            return {k: self._sort_dict(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [self._sort_dict(item) for item in obj]
        else:
            return obj
    
    def add_package(self, name: str, version: str, checksum: str) -> None:
        """
        Add a package to the lockfile.
        
        Args:
            name: Package name
            version: Resolved version
            checksum: SHA-256 checksum
        """
        data = self.load()
        
        if 'packages' not in data:
            data['packages'] = {}
        
        data['packages'][name] = {
            'version': version,
            'checksum': checksum
        }
        
        self.save(data)
    
    def get_package(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get package information from lockfile.
        
        Args:
            name: Package name
            
        Returns:
            Package info dict or None if not found
        """
        data = self.load()
        packages = data.get('packages', {})
        return packages.get(name)
    
    def has_package(self, name: str) -> bool:
        """
        Check if a package is in the lockfile.
        
        Args:
            name: Package name
            
        Returns:
            True if package exists in lockfile
        """
        return self.get_package(name) is not None
    
    def remove_package(self, name: str) -> None:
        """
        Remove a package from the lockfile.
        
        Args:
            name: Package name
        """
        data = self.load()
        packages = data.get('packages', {})
        
        if name in packages:
            del packages[name]
            self.save(data)
    
    def clear(self) -> None:
        """Clear all lockfile data."""
        self._data = {}
        if self.lock_path.exists():
            self.lock_path.unlink()
    
    def get_all_packages(self) -> Dict[str, Dict[str, str]]:
        """
        Get all packages from lockfile.
        
        Returns:
            Dictionary mapping package names to their info
        """
        data = self.load()
        return data.get('packages', {}).copy() 