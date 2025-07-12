import json
import pathlib
from typing import Optional, Dict, Any, List
from .errors import OriginPkgError
from .semver import find_highest_compatible_version


class Registry:
    """Registry for resolving package aliases to URLs."""
    
    def __init__(self, registry_path: Optional[pathlib.Path] = None):
        """
        Initialize the registry.
        
        Args:
            registry_path: Path to registry.json file. Defaults to ~/.origin/registry.json
        """
        if registry_path is None:
            home = pathlib.Path.home()
            registry_path = home / ".origin" / "registry.json"
        
        self.registry_path = registry_path
        self._cache: Optional[Dict[str, Any]] = None
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load the registry from JSON file."""
        if self._cache is not None:
            return self._cache
        
        if not self.registry_path.exists():
            # Return empty registry if file doesn't exist
            self._cache = {}
            return self._cache
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._cache = data
                    return self._cache
                else:
                    raise OriginPkgError(f"Registry file {self.registry_path} must contain a JSON object")
        except json.JSONDecodeError as e:
            raise OriginPkgError(f"Invalid registry file {self.registry_path}: {e}")
        except Exception as e:
            raise OriginPkgError(f"Failed to load registry {self.registry_path}: {e}")
    
    def resolve(self, package_name: str, version: str) -> Optional[str]:
        """
        Resolve a package name and version to a URL.
        
        Args:
            package_name: Name of the package (e.g., "std/math")
            version: Version string (e.g., "1.0.0")
            
        Returns:
            URL string if found, None otherwise
        """
        registry = self._load_registry()
        
        # Look for exact match: package_name@version
        key = f"{package_name}@{version}"
        if key in registry:
            return registry[key]
        
        return None
    
    def resolve_range(self, package_name: str, version_range: str) -> Optional[tuple[str, str]]:
        """
        Resolve a package name and version range to the highest compatible version and URL.
        
        Args:
            package_name: Name of the package (e.g., "std/math")
            version_range: Version range string (e.g., "^1.2.0", "~1.1", ">=1.2 <2.0")
            
        Returns:
            Tuple of (version, url) if found, None otherwise
        """
        registry = self._load_registry()
        
        # Collect all available versions for this package
        available_versions = []
        version_urls = {}
        
        for reg_key, url in registry.items():
            if reg_key.startswith(f"{package_name}@"):
                # Extract version from key
                version_part = reg_key[len(f"{package_name}@"):]
                available_versions.append(version_part)
                version_urls[version_part] = url
        
        if not available_versions:
            return None
        
        # Find the highest compatible version
        resolved_version = find_highest_compatible_version(available_versions, version_range)
        
        if resolved_version is None:
            return None
        
        url = version_urls[resolved_version]
        return resolved_version, url
    
    def add_alias(self, alias: str, url: str) -> None:
        """
        Add a new alias to the registry.
        
        Args:
            alias: Package alias (e.g., "std/math@1.0.0")
            url: URL for the package
        """
        registry = self._load_registry()
        registry[alias] = url
        
        # Ensure directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write updated registry
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            # Update cache
            self._cache = registry
            
        except Exception as e:
            raise OriginPkgError(f"Failed to write registry {self.registry_path}: {e}")
    
    def list_aliases(self) -> Dict[str, str]:
        """
        List all registered aliases.
        
        Returns:
            Dictionary mapping aliases to URLs
        """
        return self._load_registry().copy()


def parse_package_spec(spec: str) -> tuple[str, Optional[str]]:
    """
    Parse a package specification string.
    
    Args:
        spec: Package specification (e.g., "std/math@1.0.0" or "std/math")
        
    Returns:
        Tuple of (package_name, version)
    """
    if '@' in spec:
        package_name, version = spec.rsplit('@', 1)
        return package_name, version
    else:
        return spec, None 