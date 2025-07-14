import os
import urllib.parse
from typing import Dict, Any, Optional
from ..errors import OriginError

# Default max payload size (5MB)
DEFAULT_MAX_FETCH_BYTES = 5 * 1024 * 1024

# Disallowed URL schemes
DISALLOWED_SCHEMES = {'file://', 'ftp://', 'data:'}


def get_max_fetch_bytes() -> int:
    """Get the maximum fetch size from environment or default."""
    return int(os.environ.get('ORIGIN_MAX_FETCH_BYTES', DEFAULT_MAX_FETCH_BYTES))


def validate_url(url: str) -> None:
    """
    Validate URL for security restrictions.
    
    Args:
        url: The URL to validate
        
    Raises:
        OriginError: If URL is not allowed
    """
    parsed = urllib.parse.urlparse(url)
    
    # Check for disallowed schemes
    if parsed.scheme in DISALLOWED_SCHEMES:
        raise OriginError(f"URL scheme '{parsed.scheme}' is not allowed")
    
    # Only allow http and https
    if parsed.scheme not in ('http', 'https'):
        raise OriginError(f"Only HTTP and HTTPS URLs are allowed, got: {parsed.scheme}")


def safe_http_get(url: str, headers: Optional[Dict[str, str]] = None, 
                  timeout: int = 10, max_size: Optional[int] = None) -> str:
    """
    Perform a safe HTTP GET request with security checks.
    
    Args:
        url: The URL to fetch
        headers: Optional request headers
        timeout: Request timeout in seconds
        max_size: Maximum response size in bytes (defaults to env var)
        
    Returns:
        Response body as string
        
    Raises:
        OriginError: On network errors, size limits, or non-2xx status
    """
    # Validate URL first
    validate_url(url)
    
    # Get max size limit
    if max_size is None:
        max_size = get_max_fetch_bytes()
    
    try:
        # Try to import requests
        try:
            import requests
        except ImportError:
            raise OriginError("Network functionality requires 'requests' library. Install with: pip install origin-lang[net]")
        
        # Prepare headers
        if headers is None:
            headers = {}
        
        # Add user agent if not provided
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Origin-Language/1.0'
        
        # Make request
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout,
            allow_redirects=True,
            stream=True  # Stream to check size before downloading
        )
        
        # Check status code
        if not (200 <= response.status_code < 300):
            raise OriginError(f"HTTP {response.status_code}: {response.reason}")
        
        # Check content length if available
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            if size > max_size:
                raise OriginError(f"Response too large: {size} bytes (max: {max_size})")
        
        # Read response with size checking
        content = b""
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > max_size:
                response.close()
                raise OriginError(f"Response too large: {len(content)} bytes (max: {max_size})")
        
        return content.decode('utf-8')
        
    except requests.exceptions.RequestException as e:
        raise OriginError(f"Network error: {e}")
    except Exception as e:
        if isinstance(e, OriginError):
            raise
        raise OriginError(f"Unexpected error: {e}") 