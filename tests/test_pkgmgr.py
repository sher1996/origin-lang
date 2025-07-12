import pytest
import pathlib
import tempfile
import shutil
import json
from src.origin.pkgmgr import PackageManager
from src.origin.errors import OriginPkgError

class TestPackageManager:
    def setup_method(self):
        # Create a temporary directory for each test
        self.temp_dir = tempfile.mkdtemp()
        self.cwd = pathlib.Path(self.temp_dir)
        
        # Create a pkg.json file
        manifest = {
            "name": "test-project",
            "version": "0.1.0",
            "dependencies": {}
        }
        with open(self.cwd / "pkg.json", "w") as f:
            json.dump(manifest, f)
    
    def teardown_method(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_manifest(self):
        """Test PackageManager initialization with valid pkg.json"""
        pm = PackageManager(self.cwd)
        assert pm.manifest["name"] == "test-project"
    
    def test_init_without_manifest(self):
        """Test PackageManager initialization without pkg.json"""
        # Remove pkg.json
        (self.cwd / "pkg.json").unlink()
        
        with pytest.raises(OriginPkgError, match="No pkg.json found"):
            PackageManager(self.cwd)
    
    def test_add_library_success(self):
        """Test successfully adding a library"""
        pm = PackageManager(self.cwd)
        
        # Create a test library
        lib_dir = self.cwd / "test_lib"
        lib_dir.mkdir()
        (lib_dir / "test.origin").write_text("fn test() { 42 }")
        
        pm.add(lib_dir)
        
        # Check that library was copied
        dest = pathlib.Path(".origin") / "libs" / "test_lib"
        assert dest.exists()
        assert (dest / "test.origin").exists()
    
    def test_add_nonexistent_library(self):
        """Test adding a library that doesn't exist"""
        pm = PackageManager(self.cwd)
        
        with pytest.raises(OriginPkgError, match="Cannot find library"):
            pm.add(pathlib.Path("nonexistent"))
    
    def test_add_duplicate_library(self):
        """Test adding a library that's already installed"""
        pm = PackageManager(self.cwd)
        
        # Create and add library first time
        lib_dir = self.cwd / "test_lib"
        lib_dir.mkdir()
        (lib_dir / "test.origin").write_text("fn test() { 42 }")
        pm.add(lib_dir)
        
        # Try to add again
        with pytest.raises(OriginPkgError, match="already installed"):
            pm.add(lib_dir)
    
    def test_remove_library_success(self):
        """Test successfully removing a library"""
        pm = PackageManager(self.cwd)
        
        # Create and add library
        lib_dir = self.cwd / "test_lib"
        lib_dir.mkdir()
        (lib_dir / "test.origin").write_text("fn test() { 42 }")
        pm.add(lib_dir)
        
        # Remove library
        pm.remove("test_lib")
        
        # Check that library was removed
        dest = pathlib.Path(".origin") / "libs" / "test_lib"
        assert not dest.exists()
    
    def test_remove_nonexistent_library(self):
        """Test removing a library that doesn't exist"""
        pm = PackageManager(self.cwd)
        
        with pytest.raises(OriginPkgError, match="No installed lib named"):
            pm.remove("nonexistent")
    
    def test_lib_directory_creation(self):
        """Test that .origin/libs directory is created when needed"""
        pm = PackageManager(self.cwd)
        
        # Create a test library
        lib_dir = self.cwd / "test_lib"
        lib_dir.mkdir()
        (lib_dir / "test.origin").write_text("fn test() { 42 }")
        
        pm.add(lib_dir)
        
        # Check that .origin/libs directory exists
        libs_dir = pathlib.Path(".origin") / "libs"
        assert libs_dir.exists()
        assert libs_dir.is_dir()
    
    def test_manifest_parsing(self):
        """Test that manifest is properly parsed"""
        # Create a more complex manifest
        manifest = {
            "name": "complex-project",
            "version": "1.2.3",
            "dependencies": {
                "lib1": "./libs/lib1",
                "lib2": "./libs/lib2"
            }
        }
        
        with open(self.cwd / "pkg.json", "w") as f:
            json.dump(manifest, f)
        
        pm = PackageManager(self.cwd)
        assert pm.manifest["name"] == "complex-project"
        assert pm.manifest["version"] == "1.2.3"
        assert "lib1" in pm.manifest["dependencies"]
    
    def test_invalid_json_manifest(self):
        """Test handling of invalid JSON in pkg.json"""
        # Write invalid JSON
        with open(self.cwd / "pkg.json", "w") as f:
            f.write("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            PackageManager(self.cwd)
    
    def test_library_with_subdirectories(self):
        """Test adding a library with subdirectories"""
        pm = PackageManager(self.cwd)
        
        # Create a library with subdirectories
        lib_dir = self.cwd / "complex_lib"
        lib_dir.mkdir()
        (lib_dir / "main.origin").write_text("fn main() { 42 }")
        
        subdir = lib_dir / "utils"
        subdir.mkdir()
        (subdir / "helper.origin").write_text("fn helper() { 21 }")
        
        pm.add(lib_dir)
        
        # Check that entire structure was copied
        dest = pathlib.Path(".origin") / "libs" / "complex_lib"
        assert dest.exists()
        assert (dest / "main.origin").exists()
        assert (dest / "utils").exists()
        assert (dest / "utils" / "helper.origin").exists() 