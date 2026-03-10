import pytest
import ipaddress
import urllib.parse
from markdrop.utils import is_safe_url

def test_is_safe_url_http_https():
    """Test that only HTTP and HTTPS schemes are allowed."""
    assert is_safe_url("https://example.com/file.pdf") is True
    assert is_safe_url("http://example.com/file.pdf") is True
    assert is_safe_url("ftp://example.com/file.pdf") is False
    assert is_safe_url("file:///etc/passwd") is False

def test_is_safe_url_blocks_private_ips(monkeypatch):
    """Test that private IPs and localhost are blocked."""
    def mock_gethostbyname(hostname):
        if hostname == "localhost":
            return "127.0.0.1"
        elif hostname == "private.internal":
            return "192.168.1.5"
        elif hostname == "public.com":
            return "8.8.8.8"
        return "127.0.0.1"
        
    import socket
    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname)

    assert is_safe_url("https://localhost/file.pdf") is False
    assert is_safe_url("http://private.internal/file.pdf") is False
    assert is_safe_url("https://public.com/file.pdf") is True
