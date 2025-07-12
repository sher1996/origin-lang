import unittest
import tempfile
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from origin.lock import Lockfile
from origin.errors import OriginPkgError


class TestLockfile(unittest.TestCase):
    """Test lockfile functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.lock_path = Path(self.temp_dir) / "origin.lock"
        self.lockfile = Lockfile(self.lock_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_new_lockfile(self):
        """Test creating a new lockfile."""
        data = self.lockfile.load()
        self.assertEqual(data, {})
        self.assertFalse(self.lock_path.exists())
    
    def test_save_and_load(self):
        """Test saving and loading lockfile data."""
        test_data = {
            "packages": {
                "math_utils": {
                    "version": "1.2.3",
                    "checksum": "abc123"
                },
                "string_utils": {
                    "version": "2.0.0",
                    "checksum": "def456"
                }
            }
        }
        
        self.lockfile.save(test_data)
        
        # Verify file was created
        self.assertTrue(self.lock_path.exists())
        
        # Load and verify data
        loaded_data = self.lockfile.load()
        self.assertEqual(loaded_data, test_data)
    
    def test_deterministic_ordering(self):
        """Test that lockfile output is deterministic."""
        test_data = {
            "packages": {
                "zebra": {"version": "1.0.0", "checksum": "z123"},
                "alpha": {"version": "2.0.0", "checksum": "a456"},
                "beta": {"version": "3.0.0", "checksum": "b789"}
            }
        }
        
        self.lockfile.save(test_data)
        
        # Read the file content
        with open(self.lock_path, 'r') as f:
            content = f.read()
        
        # Parse the JSON to verify structure
        parsed = json.loads(content)
        
        # Check that packages are sorted alphabetically
        package_names = list(parsed["packages"].keys())
        self.assertEqual(package_names, ["alpha", "beta", "zebra"])
    
    def test_add_package(self):
        """Test adding a package to the lockfile."""
        self.lockfile.add_package("math_utils", "1.2.3", "abc123")
        
        # Verify package was added
        package_info = self.lockfile.get_package("math_utils")
        self.assertIsNotNone(package_info)
        self.assertEqual(package_info["version"], "1.2.3")
        self.assertEqual(package_info["checksum"], "abc123")
    
    def test_get_package(self):
        """Test getting package information."""
        # Add a package
        self.lockfile.add_package("test_pkg", "1.0.0", "test123")
        
        # Get existing package
        package_info = self.lockfile.get_package("test_pkg")
        self.assertIsNotNone(package_info)
        self.assertEqual(package_info["version"], "1.0.0")
        
        # Get non-existent package
        package_info = self.lockfile.get_package("nonexistent")
        self.assertIsNone(package_info)
    
    def test_has_package(self):
        """Test checking if package exists in lockfile."""
        # Initially no packages
        self.assertFalse(self.lockfile.has_package("test_pkg"))
        
        # Add package
        self.lockfile.add_package("test_pkg", "1.0.0", "test123")
        self.assertTrue(self.lockfile.has_package("test_pkg"))
        
        # Check non-existent package
        self.assertFalse(self.lockfile.has_package("nonexistent"))
    
    def test_remove_package(self):
        """Test removing a package from lockfile."""
        # Add package
        self.lockfile.add_package("test_pkg", "1.0.0", "test123")
        self.assertTrue(self.lockfile.has_package("test_pkg"))
        
        # Remove package
        self.lockfile.remove_package("test_pkg")
        self.assertFalse(self.lockfile.has_package("test_pkg"))
        
        # Try to remove non-existent package (should not error)
        self.lockfile.remove_package("nonexistent")
    
    def test_get_all_packages(self):
        """Test getting all packages from lockfile."""
        # Initially empty
        packages = self.lockfile.get_all_packages()
        self.assertEqual(packages, {})
        
        # Add packages
        self.lockfile.add_package("pkg1", "1.0.0", "abc123")
        self.lockfile.add_package("pkg2", "2.0.0", "def456")
        
        # Get all packages
        packages = self.lockfile.get_all_packages()
        self.assertEqual(len(packages), 2)
        self.assertIn("pkg1", packages)
        self.assertIn("pkg2", packages)
        self.assertEqual(packages["pkg1"]["version"], "1.0.0")
        self.assertEqual(packages["pkg2"]["version"], "2.0.0")
    
    def test_clear(self):
        """Test clearing the lockfile."""
        # Add some packages
        self.lockfile.add_package("pkg1", "1.0.0", "abc123")
        self.lockfile.add_package("pkg2", "2.0.0", "def456")
        
        # Verify packages exist
        self.assertEqual(len(self.lockfile.get_all_packages()), 2)
        
        # Clear lockfile
        self.lockfile.clear()
        
        # Verify lockfile is empty
        self.assertEqual(len(self.lockfile.get_all_packages()), 0)
        
        # If file existed, it should be deleted
        if self.lock_path.exists():
            # File should be empty or deleted
            with open(self.lock_path, 'r') as f:
                content = f.read().strip()
                self.assertEqual(content, "")
    
    def test_corrupt_lockfile(self):
        """Test handling of corrupt lockfile."""
        # Create a corrupt lockfile
        with open(self.lock_path, 'w') as f:
            f.write("invalid json content")
        
        # Should raise error when loading
        with self.assertRaises(OriginPkgError):
            self.lockfile.load()
    
    def test_lockfile_not_object(self):
        """Test handling of lockfile that's not a JSON object."""
        # Create lockfile with array instead of object
        with open(self.lock_path, 'w') as f:
            f.write('["not", "an", "object"]')
        
        # Should raise error when loading
        with self.assertRaises(OriginPkgError):
            self.lockfile.load()


if __name__ == '__main__':
    unittest.main() 