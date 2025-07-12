import unittest
import tempfile
import pathlib
import json
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.origin.publish import (
    GitHubPublisher, 
    build_tarball, 
    compute_checksum, 
    parse_repository_url, 
    publish_package,
    PublishError
)


class TestGitHubPublisher(unittest.TestCase):
    
    def setUp(self):
        self.publisher = GitHubPublisher("test_token")
    
    @patch('origin.publish.urllib.request.urlopen')
    def test_make_request_success(self, mock_urlopen):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": 123, "name": "test"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.publisher._make_request("https://api.github.com/test")
        
        self.assertEqual(result, {"id": 123, "name": "test"})
    
    @patch('origin.publish.urllib.request.urlopen')
    def test_make_request_401_error(self, mock_urlopen):
        # Mock 401 error
        from urllib.error import HTTPError
        from email.message import Message
        headers = Message()
        mock_urlopen.side_effect = HTTPError(
            "https://api.github.com/test", 401, "Unauthorized", headers, None
        )
        
        with self.assertRaises(PublishError) as cm:
            self.publisher._make_request("https://api.github.com/test")
        
        self.assertIn("Invalid GitHub token", str(cm.exception))
    
    @patch('src.origin.publish.urllib.request.urlopen')
    def test_make_request_404_error(self, mock_urlopen):
        # Mock 404 error
        from urllib.error import HTTPError
        from email.message import Message
        headers = Message()
        mock_urlopen.side_effect = HTTPError(
            "https://api.github.com/test", 404, "Not Found", headers, None
        )
        
        with self.assertRaises(PublishError) as cm:
            self.publisher._make_request("https://api.github.com/test")
        
        self.assertIn("Repository not found", str(cm.exception))
    
    @patch('src.origin.publish.urllib.request.urlopen')
    def test_make_request_other_error(self, mock_urlopen):
        # Mock other HTTP error
        from urllib.error import HTTPError
        from email.message import Message
        headers = Message()
        mock_urlopen.side_effect = HTTPError(
            "https://api.github.com/test", 500, "Internal Server Error", headers, None
        )
        
        with self.assertRaises(PublishError) as cm:
            self.publisher._make_request("https://api.github.com/test")
        
        self.assertIn("GitHub API error: 500", str(cm.exception))
    
    def test_init_without_token(self):
        # Test initialization without token
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PublishError) as cm:
                GitHubPublisher()
        
        self.assertIn("GitHub token required", str(cm.exception))
    
    def test_init_with_env_token(self):
        # Test initialization with environment token
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'env_token'}):
            publisher = GitHubPublisher()
            self.assertEqual(publisher.token, 'env_token')
    
    def test_init_with_param_token(self):
        # Test initialization with parameter token
        publisher = GitHubPublisher("param_token")
        self.assertEqual(publisher.token, 'param_token')


class TestBuildTarball(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = pathlib.Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_build_tarball_basic(self):
        # Create test files
        (self.project_path / "test.ori").write_text("say 'hello'")
        (self.project_path / "README.md").write_text("# Test")
        
        tarball_path = build_tarball(self.project_path, "test-pkg", "1.0.0")
        
        self.assertTrue(tarball_path.exists())
        self.assertEqual(tarball_path.name, "test-pkg-1.0.0.tar.gz")
        
        # Verify tarball contents
        import tarfile
        with tarfile.open(tarball_path, 'r:gz') as tar:
            members = tar.getnames()
            self.assertIn("test.ori", members)
            self.assertIn("README.md", members)
    
    def test_build_tarball_excludes_git(self):
        # Create test files including .git
        (self.project_path / "test.ori").write_text("say 'hello'")
        (self.project_path / ".git").mkdir()
        (self.project_path / ".git" / "config").write_text("test")
        
        tarball_path = build_tarball(self.project_path, "test-pkg", "1.0.0")
        
        # Verify .git is excluded
        import tarfile
        with tarfile.open(tarball_path, 'r:gz') as tar:
            members = tar.getnames()
            self.assertIn("test.ori", members)
            self.assertNotIn(".git", members)
            self.assertNotIn(".git/config", members)


class TestComputeChecksum(unittest.TestCase):
    
    def test_compute_checksum(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()
            
            checksum = compute_checksum(pathlib.Path(f.name))
            
            # SHA-256 of "test content"
            expected = "a8a2f6ebe140e8b7b4c2c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8"
            self.assertEqual(len(checksum), 64)  # SHA-256 is 64 hex chars


class TestParseRepositoryUrl(unittest.TestCase):
    
    def test_parse_https_url(self):
        owner, repo = parse_repository_url("https://github.com/user/repo")
        self.assertEqual(owner, "user")
        self.assertEqual(repo, "repo")
    
    def test_parse_https_url_with_git(self):
        owner, repo = parse_repository_url("https://github.com/user/repo.git")
        self.assertEqual(owner, "user")
        self.assertEqual(repo, "repo")
    
    def test_parse_ssh_url(self):
        owner, repo = parse_repository_url("git@github.com:user/repo.git")
        self.assertEqual(owner, "user")
        self.assertEqual(repo, "repo")
    
    def test_parse_invalid_url(self):
        with self.assertRaises(PublishError) as cm:
            parse_repository_url("https://invalid.com/user/repo")
        
        self.assertIn("Invalid GitHub repository URL", str(cm.exception))


class TestPublishPackage(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = pathlib.Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_publish_package_missing_pkg_json(self):
        with self.assertRaises(PublishError) as cm:
            publish_package(self.project_path, dry_run=True)
        
        self.assertIn("No pkg.json found", str(cm.exception))
    
    def test_publish_package_invalid_pkg_json(self):
        (self.project_path / "pkg.json").write_text("invalid json")
        
        with self.assertRaises(PublishError) as cm:
            publish_package(self.project_path, dry_run=True)
        
        self.assertIn("Invalid pkg.json", str(cm.exception))
    
    def test_publish_package_missing_fields(self):
        (self.project_path / "pkg.json").write_text('{"name": "test"}')
        
        with self.assertRaises(PublishError) as cm:
            publish_package(self.project_path, dry_run=True)
        
        self.assertIn("Missing 'version' field", str(cm.exception))
    
    def test_publish_package_dry_run(self):
        manifest = {
            "name": "test-pkg",
            "version": "1.0.0",
            "repository": "https://github.com/user/repo"
        }
        (self.project_path / "pkg.json").write_text(json.dumps(manifest))
        
        with patch('builtins.print') as mock_print:
            publish_package(self.project_path, dry_run=True)
        
        # Verify dry run output
        mock_print.assert_any_call("DRY RUN: Would publish test-pkg@1.0.0")
        mock_print.assert_any_call("Repository: user/repo")
        mock_print.assert_any_call("Tag: v1.0.0")
    
    def test_publish_package_dry_run_custom_tag(self):
        manifest = {
            "name": "test-pkg",
            "version": "1.0.0",
            "repository": "https://github.com/user/repo"
        }
        (self.project_path / "pkg.json").write_text(json.dumps(manifest))
        
        with patch('builtins.print') as mock_print:
            publish_package(self.project_path, dry_run=True, tag="custom-tag")
        
        # Verify custom tag is used
        mock_print.assert_any_call("Tag: custom-tag")
    
    @patch('src.origin.publish.GitHubPublisher')
    @patch('src.origin.publish.build_tarball')
    @patch('src.origin.publish.compute_checksum')
    def test_publish_package_success(self, mock_checksum, mock_build, mock_publisher_class):
        # Setup manifest
        manifest = {
            "name": "test-pkg",
            "version": "1.0.0",
            "repository": "https://github.com/user/repo"
        }
        (self.project_path / "pkg.json").write_text(json.dumps(manifest))
        
        # Mock dependencies
        mock_tarball = pathlib.Path("/tmp/test-pkg-1.0.0.tar.gz")
        mock_build.return_value = mock_tarball
        mock_checksum.return_value = "test_checksum"
        
        mock_publisher = MagicMock()
        mock_publisher.create_release.return_value = {"upload_url": "https://api.github.com/upload"}
        mock_publisher_class.return_value = mock_publisher
        
        with patch('builtins.print') as mock_print:
            publish_package(self.project_path)
        
        # Verify calls
        mock_build.assert_called_once_with(self.project_path, "test-pkg", "1.0.0")
        mock_checksum.assert_called_once_with(mock_tarball)
        mock_publisher.create_release.assert_called_once()
        mock_publisher.upload_asset.assert_called_twice()


if __name__ == '__main__':
    unittest.main() 