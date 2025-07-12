import pytest
import pathlib
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, mock_open
from src.origin.pkgmgr import PackageManager
from src.origin.errors import OriginPkgError
from src.origin.registry import Registry, parse_package_spec


class TestRemotePackageManager:
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
        self._orig_cwd = pathlib.Path.cwd()
        # Change to temp dir for .origin/libs
        self._old_cwd = pathlib.Path.cwd
        pathlib.Path.cwd = lambda: self.cwd
    
    def teardown_method(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
        pathlib.Path.cwd = self._old_cwd
    
    @patch('src.origin.net.download')
    @patch('src.origin.archive.extract_archive')
    @patch('src.origin.archive.is_archive_file')
    def test_add_remote_url_success(self, mock_is_archive, mock_extract, mock_download):
        """Test successfully adding a remote package from URL."""
        pm = PackageManager(self.cwd)
        
        # Mock archive detection and extraction
        mock_is_archive.return_value = True
        
        # Create a mock extracted directory structure
        with tempfile.TemporaryDirectory() as temp_extract:
            extract_path = pathlib.Path(temp_extract)
            lib_dir = extract_path / "math_utils-0.2.0"
            lib_dir.mkdir()
            (lib_dir / "math_utils.origin").write_text("fn add(a, b) { a + b }")
            
            # Mock the extraction to create our test structure
            def mock_extract_side_effect(archive_path, extract_to):
                shutil.copytree(extract_path, extract_to)
            
            mock_extract.side_effect = mock_extract_side_effect
        
        pm.add("https://example.com/math_utils-0.2.0.tar.gz")
        
        # Verify download was called
        mock_download.assert_called_once()
        
        # Check that library was installed
        dest = pathlib.Path(".origin") / "libs" / "math_utils-0.2.0"
        assert dest.exists()
        assert (dest / "math_utils.origin").exists()
    
    @patch('src.origin.net.download')
    def test_add_remote_url_download_failure(self, mock_download):
        """Test handling of download failures."""
        pm = PackageManager(self.cwd)
        
        # Mock download to raise an exception
        mock_download.side_effect = OriginPkgError("Network error")
        
        with pytest.raises(OriginPkgError, match="Network error"):
            pm.add("https://example.com/math_utils-0.2.0.tar.gz")
    
    @patch('src.origin.net.download')
    @patch('src.origin.archive.is_archive_file')
    def test_add_remote_url_checksum_verification(self, mock_is_archive, mock_download):
        """Test checksum verification for remote packages."""
        pm = PackageManager(self.cwd)
        
        # Mock non-archive file
        mock_is_archive.return_value = False
        
        # Create a temporary file for the mock download
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = pathlib.Path(temp_file.name)
        
        try:
            # Mock download to write to our temp file
            def mock_download_side_effect(url, dest, progress=True):
                shutil.copy2(temp_file_path, dest)
            
            mock_download.side_effect = mock_download_side_effect
            
            # Test with valid checksum
            valid_checksum = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
            pm.add("https://example.com/test.tar.gz", valid_checksum)
            
            # Test with invalid checksum
            with pytest.raises(OriginPkgError, match="Checksum verification failed"):
                pm.add("https://example.com/test.tar.gz", "invalid_checksum")
                
        finally:
            temp_file_path.unlink()
    
    @patch('src.origin.net.download')
    @patch('src.origin.net.download_checksum')
    @patch('src.origin.archive.is_archive_file')
    def test_add_remote_url_auto_checksum(self, mock_is_archive, mock_download_checksum, mock_download):
        """Test automatic checksum download and verification."""
        pm = PackageManager(self.cwd)
        
        # Mock non-archive file
        mock_is_archive.return_value = False
        
        # Create a temporary file for the mock download
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = pathlib.Path(temp_file.name)
        
        try:
            # Mock download to write to our temp file
            def mock_download_side_effect(url, dest, progress=True):
                shutil.copy2(temp_file_path, dest)
            
            mock_download.side_effect = mock_download_side_effect
            
            # Mock checksum download
            valid_checksum = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
            mock_download_checksum.return_value = valid_checksum
            
            pm.add("https://example.com/test.tar.gz")
            
            # Verify checksum download was attempted
            mock_download_checksum.assert_called_once_with("https://example.com/test.tar.gz.sha256")
            
        finally:
            temp_file_path.unlink()
    
    def test_add_local_path_still_works(self):
        """Test that local path installation still works."""
        pm = PackageManager(self.cwd)
        
        # Create a test library
        lib_dir = self.cwd / "test_lib"
        lib_dir.mkdir()
        (lib_dir / "test.origin").write_text("fn test() { 42 }")
        
        pm.add(str(lib_dir))
        
        # Check that library was copied
        dest = pathlib.Path(".origin") / "libs" / "test_lib"
        assert dest.exists()
        assert (dest / "test.origin").exists()
    
    def test_add_duplicate_remote_package(self):
        """Test that adding a duplicate remote package fails."""
        pm = PackageManager(self.cwd)
        
        # Create a mock library directory
        lib_dir = pathlib.Path(".origin") / "libs" / "math_utils-0.2.0"
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / "math_utils.origin").write_text("fn add(a, b) { a + b }")
        
        with pytest.raises(OriginPkgError, match="already installed"):
            pm.add("https://example.com/math_utils-0.2.0.tar.gz")

    def test_add_local_archive_happy_path(self):
        pm = PackageManager(self.cwd)
        # Use the real fixture
        archive = pathlib.Path(self._orig_cwd) / "tests/fixtures/remote_pkg/math_utils-0.2.0.tar.gz"
        checksum = "642FB2E16399776F1F352245A3A522DE2BB89969220718CDE0595726CC752F88"
        pm.add(str(archive), checksum)
        dest = self.cwd / ".origin" / "libs" / "math_utils"
        assert dest.exists()
        assert (dest / "math_utils.origin").exists()

    def test_add_local_archive_checksum_mismatch(self):
        pm = PackageManager(self.cwd)
        archive = pathlib.Path(self._orig_cwd) / "tests/fixtures/remote_pkg/math_utils-0.2.0.tar.gz"
        bad_checksum = "deadbeef"
        with pytest.raises(OriginPkgError, match="Checksum verification failed"):
            pm.add(str(archive), bad_checksum)

    def test_add_local_archive_unsupported_type(self):
        pm = PackageManager(self.cwd)
        # Create a fake .rar file
        with tempfile.NamedTemporaryFile(suffix=".rar", delete=False) as temp_file:
            temp_file.write(b"not a real archive")
            temp_path = pathlib.Path(temp_file.name)
        try:
            with pytest.raises(OriginPkgError, match="Unsupported archive format"):
                pm.add(str(temp_path), "deadbeef")
        finally:
            temp_path.unlink()


class TestRegistry:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = pathlib.Path(self.temp_dir) / "registry.json"
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_registry_init_default_path(self):
        """Test registry initialization with default path."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = pathlib.Path("/fake/home")
            registry = Registry()
            assert registry.registry_path == pathlib.Path("/fake/home/.origin/registry.json")
    
    def test_registry_init_custom_path(self):
        """Test registry initialization with custom path."""
        registry = Registry(self.registry_path)
        assert registry.registry_path == self.registry_path
    
    def test_registry_load_empty_file(self):
        """Test loading registry from non-existent file."""
        registry = Registry(self.registry_path)
        aliases = registry.list_aliases()
        assert aliases == {}
    
    def test_registry_load_valid_json(self):
        """Test loading registry from valid JSON file."""
        registry_data = {
            "std/math@1.0.0": "https://example.com/math-1.0.0.tar.gz",
            "std/string@2.0.0": "https://example.com/string-2.0.0.tar.gz"
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(registry_data, f)
        
        registry = Registry(self.registry_path)
        aliases = registry.list_aliases()
        assert aliases == registry_data
    
    def test_registry_resolve_exact_match(self):
        """Test resolving exact package@version match."""
        registry_data = {
            "std/math@1.0.0": "https://example.com/math-1.0.0.tar.gz"
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(registry_data, f)
        
        registry = Registry(self.registry_path)
        url = registry.resolve("std/math", "1.0.0")
        assert url == "https://example.com/math-1.0.0.tar.gz"
    
    def test_registry_resolve_no_match(self):
        """Test resolving non-existent package."""
        registry = Registry(self.registry_path)
        url = registry.resolve("nonexistent", "1.0.0")
        assert url is None
    
    def test_registry_add_alias(self):
        """Test adding a new alias to registry."""
        registry = Registry(self.registry_path)
        registry.add_alias("std/math@1.0.0", "https://example.com/math-1.0.0.tar.gz")
        
        # Verify alias was added
        aliases = registry.list_aliases()
        assert aliases["std/math@1.0.0"] == "https://example.com/math-1.0.0.tar.gz"
        
        # Verify file was written
        assert self.registry_path.exists()
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
            assert data["std/math@1.0.0"] == "https://example.com/math-1.0.0.tar.gz"


class TestPackageSpecParsing:
    def test_parse_package_spec_with_version(self):
        """Test parsing package spec with version."""
        package_name, version = parse_package_spec("std/math@1.0.0")
        assert package_name == "std/math"
        assert version == "1.0.0"
    
    def test_parse_package_spec_without_version(self):
        """Test parsing package spec without version."""
        package_name, version = parse_package_spec("std/math")
        assert package_name == "std/math"
        assert version is None
    
    def test_parse_package_spec_multiple_at_signs(self):
        """Test parsing package spec with multiple @ signs."""
        package_name, version = parse_package_spec("std/math@1.0.0@beta")
        assert package_name == "std/math@1.0.0"
        assert version == "beta" 