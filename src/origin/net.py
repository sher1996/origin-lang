import urllib.request
import urllib.error
import hashlib
import pathlib
import time
from typing import Optional
from .errors import OriginPkgError


def download(url: str, dest: pathlib.Path, progress: bool = True) -> None:
    """
    Download a file from URL to destination path.
    
    Args:
        url: The URL to download from
        dest: Destination path for the downloaded file
        progress: Whether to show download progress
    
    Raises:
        OriginPkgError: On network errors or invalid URLs
    """
    try:
        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with retry logic
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if progress:
                    print(f"Downloading {url}...")
                
                urllib.request.urlretrieve(url, dest)
                
                if progress:
                    print(f"✓ Downloaded to {dest}")
                return
                
            except urllib.error.URLError as e:
                if attempt < max_retries - 1:
                    if progress:
                        print(f"Download failed, retrying in {retry_delay}s... ({e})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise OriginPkgError(f"Failed to download {url}: {e}")
            except Exception as e:
                raise OriginPkgError(f"Unexpected error downloading {url}: {e}")
                
    except Exception as e:
        if not isinstance(e, OriginPkgError):
            raise OriginPkgError(f"Download failed: {e}")


def download_checksum(url: str) -> Optional[str]:
    """
    Download and return the SHA-256 checksum from a .sha256 file.
    
    Args:
        url: The URL of the .sha256 file
        
    Returns:
        The checksum string, or None if download fails
    """
    try:
        with urllib.request.urlopen(url) as response:
            checksum = response.read().decode('utf-8').strip()
            # Handle both "checksum filename" and "checksum" formats
            if ' ' in checksum:
                checksum = checksum.split(' ')[0]
            return checksum
    except Exception:
        return None


def is_url(string: str) -> bool:
    """
    Check if a string looks like a URL.
    
    Args:
        string: The string to check
        
    Returns:
        True if the string appears to be a URL
    """
    return string.startswith(('http://', 'https://', 'file://')) 