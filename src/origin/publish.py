import json
import pathlib
import hashlib
import tarfile
import tempfile
import os
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import urllib.request
import urllib.error

from .errors import OriginPkgError


class PublishError(OriginPkgError):
    """Custom exception for publishing errors."""
    pass


class GitHubPublisher:
    """Handles publishing packages to GitHub Releases."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise PublishError("GitHub token required. Set GITHUB_TOKEN env var or use --token")
    
    def _make_request(self, url: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an authenticated request to GitHub API."""
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'origin-lang/1.0'
        }
        
        if data:
            headers['Content-Type'] = 'application/json'
            import json
            data_bytes = json.dumps(data).encode('utf-8')
        else:
            data_bytes = None
        
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise PublishError("Invalid GitHub token")
            elif e.code == 404:
                raise PublishError("Repository not found or access denied")
            else:
                raise PublishError(f"GitHub API error: {e.code} - {e.reason}")
        except Exception as e:
            raise PublishError(f"Request failed: {e}")
    
    def create_release(self, owner: str, repo: str, tag: str, name: str, body: str = "") -> Dict[str, Any]:
        """Create a GitHub release."""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        data = {
            "tag_name": tag,
            "name": name,
            "body": body,
            "draft": False,
            "prerelease": False
        }
        return self._make_request(url, method='POST', data=data)
    
    def upload_asset(self, upload_url: str, file_path: pathlib.Path, content_type: str) -> Dict[str, Any]:
        """Upload an asset to a GitHub release."""
        # GitHub's upload URL has a template parameter we need to replace
        upload_url = upload_url.replace('{?name,label}', f'?name={file_path.name}')
        
        headers = {
            'Authorization': f'token {self.token}',
            'Content-Type': content_type,
            'User-Agent': 'origin-lang/1.0'
        }
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        req = urllib.request.Request(upload_url, data=data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise PublishError(f"Failed to upload {file_path.name}: {e.code} - {e.reason}")
        except Exception as e:
            raise PublishError(f"Upload failed: {e}")


def build_tarball(project_path: pathlib.Path, name: str, version: str) -> pathlib.Path:
    """
    Build a tarball from the project directory.
    
    Args:
        project_path: Path to the project directory
        name: Package name
        version: Package version
        
    Returns:
        Path to the created tarball
    """
    # Create tarball in temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        tarball_name = f"{name}-{version}.tar.gz"
        tarball_path = temp_path / tarball_name
        
        # Create tarball
        with tarfile.open(tarball_path, 'w:gz') as tar:
            # Add all files except exclusions
            exclusions = {'.git', '*.orirec', 'node_modules', 'dist', '__pycache__', '.pytest_cache'}
            
            for item in project_path.iterdir():
                if item.name in exclusions or any(item.name.endswith(ext) for ext in ['.orirec']):
                    continue
                tar.add(item, arcname=item.name)
        
        # Move to current directory
        final_path = project_path / tarball_name
        tarball_path.rename(final_path)
        return final_path


def compute_checksum(file_path: pathlib.Path) -> str:
    """Compute SHA-256 checksum of a file."""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def parse_repository_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name.
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        Tuple of (owner, repo_name)
    """
    # Handle various GitHub URL formats
    patterns = [
        r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return match.group(1), match.group(2)
    
    raise PublishError(f"Invalid GitHub repository URL: {repo_url}")


def publish_package(
    project_path: pathlib.Path,
    token: Optional[str] = None,
    dry_run: bool = False,
    tag: Optional[str] = None
) -> None:
    """
    Publish a package to GitHub Releases.
    
    Args:
        project_path: Path to the project directory
        token: GitHub personal access token
        dry_run: If True, only print what would be done
        tag: Custom tag name (defaults to v{version})
    """
    # Read package manifest
    manifest_path = project_path / "pkg.json"
    if not manifest_path.exists():
        raise PublishError("No pkg.json found in project directory")
    
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        raise PublishError(f"Invalid pkg.json: {e}")
    
    # Extract required fields
    name = manifest.get('name')
    version = manifest.get('version')
    repository = manifest.get('repository')
    
    if not name:
        raise PublishError("Missing 'name' field in pkg.json")
    if not version:
        raise PublishError("Missing 'version' field in pkg.json")
    if not repository:
        raise PublishError("Missing 'repository' field in pkg.json")
    
    # Parse repository URL
    try:
        owner, repo = parse_repository_url(repository)
    except PublishError as e:
        raise PublishError(f"Invalid repository URL: {e}")
    
    # Determine tag name
    release_tag = tag or f"v{version}"
    
    if dry_run:
        print(f"DRY RUN: Would publish {name}@{version}")
        print(f"Repository: {owner}/{repo}")
        print(f"Tag: {release_tag}")
        print(f"Project path: {project_path}")
        return
    
    # Build tarball
    print(f"Packing {name}-{version}.tar.gz...")
    tarball_path = build_tarball(project_path, name, version)
    tarball_size = tarball_path.stat().st_size
    print(f"✔ Packed {name}-{version}.tar.gz ({tarball_size} bytes)")
    
    # Compute checksum
    checksum = compute_checksum(tarball_path)
    checksum_path = project_path / f"{name}-{version}.tar.gz.sha256"
    checksum_path.write_text(checksum)
    print(f"✔ SHA-256: {checksum[:8]}…{checksum[-4:]}")
    
    # Create GitHub publisher
    publisher = GitHubPublisher(token)
    
    # Create release
    release_name = f"{name} {version}"
    release_body = f"Release {version} of {name}"
    
    print(f"Creating release {release_tag} on {owner}/{repo}...")
    release = publisher.create_release(owner, repo, release_tag, release_name, release_body)
    print(f"✔ Created release {release_tag}")
    
    # Upload assets
    print("Uploading assets...")
    
    # Upload tarball
    publisher.upload_asset(
        release['upload_url'],
        tarball_path,
        'application/gzip'
    )
    
    # Upload checksum
    publisher.upload_asset(
        release['upload_url'],
        checksum_path,
        'text/plain'
    )
    
    print(f"✔ Uploaded 2 assets")
    print("Publish complete 🎉")
    
    # Clean up local files
    tarball_path.unlink()
    checksum_path.unlink() 