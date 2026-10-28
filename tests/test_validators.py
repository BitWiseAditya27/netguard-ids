"""
Tests for NetGuard-IDS Authorization and Input Validators.
"""

import pytest
from core.validators import is_valid_hostname_or_ip, is_authorized_target, validate_port_range

def test_valid_hostname_and_ip():
    assert is_valid_hostname_or_ip("127.0.0.1") is True
    assert is_valid_hostname_or_ip("192.168.1.1") is True
    assert is_valid_hostname_or_ip("scanme.nmap.org") is True
    assert is_valid_hostname_or_ip("localhost") is True
    assert is_valid_hostname_or_ip("") is False
    assert is_valid_hostname_or_ip("invalid;; injection") is False

def test_authorized_target_enforcement():
    # Loopback
    auth, _ = is_authorized_target("127.0.0.1")
    assert auth is True

    # Private RFC1918
    auth, _ = is_authorized_target("192.168.1.100")
    assert auth is True

    auth, _ = is_authorized_target("10.0.0.1")
    assert auth is True

    # Allowed research target
    auth, _ = is_authorized_target("scanme.nmap.org")
    assert auth is True

    # Arbitrary public targets MUST be blocked
    auth, msg = is_authorized_target("8.8.8.8")
    assert auth is False
    assert "Scanning blocked" in msg

    auth, msg = is_authorized_target("1.1.1.1")
    assert auth is False

    # Demo Mode overrides safely
    auth, _ = is_authorized_target("8.8.8.8", demo_mode=True)
    assert auth is True

def test_port_range_validation():
    valid, _ = validate_port_range(1, 100)
    assert valid is True

    # Inverted range
    valid, msg = validate_port_range(500, 100)
    assert valid is False
    assert "Start port" in msg

    # Out of range
    valid, msg = validate_port_range(0, 80)
    assert valid is False

    # Exceeding safe cap
    valid, msg = validate_port_range(1, 2000, max_ports=1000)
    assert valid is False
