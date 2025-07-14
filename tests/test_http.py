import pytest
import responses
import os
from unittest.mock import patch
from src.origin.runtime.net import safe_http_get, validate_url, get_max_fetch_bytes
from src.origin.errors import OriginError


class TestHTTPValidation:
    """Test URL validation and security restrictions."""
    
    def test_validate_url_https_allowed(self):
        """Test that HTTPS URLs are allowed."""
        validate_url("https://api.example.com/data")
        # Should not raise
    
    def test_validate_url_http_allowed(self):
        """Test that HTTP URLs are allowed."""
        validate_url("http://api.example.com/data")
        # Should not raise
    
    def test_validate_url_file_disallowed(self):
        """Test that file:// URLs are disallowed."""
        with pytest.raises(OriginError, match="file://.*not allowed"):
            validate_url("file:///etc/passwd")
    
    def test_validate_url_ftp_disallowed(self):
        """Test that ftp:// URLs are disallowed."""
        with pytest.raises(OriginError, match="ftp://.*not allowed"):
            validate_url("ftp://example.com/file")
    
    def test_validate_url_data_disallowed(self):
        """Test that data: URLs are disallowed."""
        with pytest.raises(OriginError, match="data:.*not allowed"):
            validate_url("data:text/plain,hello")
    
    def test_validate_url_unknown_scheme(self):
        """Test that unknown schemes are disallowed."""
        with pytest.raises(OriginError, match="Only HTTP and HTTPS"):
            validate_url("gopher://example.com")


class TestHTTPGet:
    """Test HTTP GET functionality."""
    
    @responses.activate
    def test_successful_get(self):
        """Test successful HTTP GET request."""
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"message": "success"},
            status=200
        )
        
        result = safe_http_get("https://api.example.com/data")
        assert result == '{"message": "success"}'
    
    @responses.activate
    def test_get_with_headers(self):
        """Test HTTP GET with custom headers."""
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"message": "success"},
            status=200
        )
        
        headers = {"Authorization": "Bearer token123"}
        result = safe_http_get("https://api.example.com/data", headers=headers)
        assert result == '{"message": "success"}'
    
    @responses.activate
    def test_404_error(self):
        """Test handling of 404 errors."""
        responses.add(
            responses.GET,
            "https://api.example.com/notfound",
            status=404
        )
        
        with pytest.raises(OriginError, match="HTTP 404"):
            safe_http_get("https://api.example.com/notfound")
    
    @responses.activate
    def test_500_error(self):
        """Test handling of 500 errors."""
        responses.add(
            responses.GET,
            "https://api.example.com/error",
            status=500
        )
        
        with pytest.raises(OriginError, match="HTTP 500"):
            safe_http_get("https://api.example.com/error")
    
    @responses.activate
    def test_timeout(self):
        """Test timeout handling."""
        responses.add(
            responses.GET,
            "https://api.example.com/slow",
            body=Exception("timeout")
        )
        
        with pytest.raises(OriginError, match="Network error"):
            safe_http_get("https://api.example.com/slow")
    
    @responses.activate
    def test_size_limit_exceeded(self):
        """Test response size limit enforcement."""
        # Create a large response
        large_data = "x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        
        responses.add(
            responses.GET,
            "https://api.example.com/large",
            body=large_data,
            status=200,
            headers={"content-length": str(len(large_data))}
        )
        
        with pytest.raises(OriginError, match="Response too large"):
            safe_http_get("https://api.example.com/large")
    
    @responses.activate
    def test_size_limit_without_content_length(self):
        """Test size limit when content-length header is missing."""
        # Create a large response without content-length header
        large_data = "x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        
        responses.add(
            responses.GET,
            "https://api.example.com/large",
            body=large_data,
            status=200
        )
        
        with pytest.raises(OriginError, match="Response too large"):
            safe_http_get("https://api.example.com/large")
    
    @responses.activate
    def test_custom_size_limit(self):
        """Test custom size limit parameter."""
        # Create a response larger than custom limit
        data = "x" * 1025  # 1KB + 1 byte
        
        responses.add(
            responses.GET,
            "https://api.example.com/medium",
            body=data,
            status=200
        )
        
        with pytest.raises(OriginError, match="Response too large"):
            safe_http_get("https://api.example.com/medium", max_size=1024)
    
    def test_requests_not_installed(self):
        """Test graceful handling when requests is not installed."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'requests'")):
            with pytest.raises(OriginError, match="requires 'requests' library"):
                safe_http_get("https://api.example.com/data")


class TestEnvironmentConfig:
    """Test environment variable configuration."""
    
    def test_default_max_fetch_bytes(self):
        """Test default max fetch bytes when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_max_fetch_bytes() == 5 * 1024 * 1024  # 5MB
    
    def test_custom_max_fetch_bytes(self):
        """Test custom max fetch bytes from environment."""
        with patch.dict(os.environ, {"ORIGIN_MAX_FETCH_BYTES": "1048576"}):
            assert get_max_fetch_bytes() == 1024 * 1024  # 1MB 