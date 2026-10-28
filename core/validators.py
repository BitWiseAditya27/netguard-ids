"""
NetGuard-IDS Input & Authorization Validator.
Ensures strict defensive safety constraints, preventing arbitrary target scans
in hosted environments and enforcing authorized target policies.
"""

import ipaddress
import re
import socket
from typing import Tuple, Optional

# Public target specifically permitted by nmap project for testing
ALLOWED_PUBLIC_HOSTS = {
    "scanme.nmap.org",
    "45.33.32.156",
}

def is_valid_hostname_or_ip(target: str) -> bool:
    """Validate target string is a legitimate domain name or IPv4 address."""
    if not target or not isinstance(target, str):
        return False
    target = target.strip()
    if len(target) > 255:
        return False
    
    # Check IP
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    
    # Check Hostname / Domain (RFC 1123)
    regex = r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*$"
    return bool(re.match(regex, target))


def is_authorized_target(target: str, demo_mode: bool = False) -> Tuple[bool, str]:
    """
    Enforce safety policy:
    Only localhost, private RFC1918/loopback ranges, and scanme.nmap.org are scanned.
    Arbitrary external public IPs are blocked to protect external networks and prevent abuse.
    """
    if not target or not isinstance(target, str):
        return False, "Target address cannot be empty."

    clean_target = target.strip().lower()

    if not is_valid_hostname_or_ip(clean_target):
        return False, f"Invalid IP address or hostname format: '{target}'."

    # In DEMO MODE, simulated scanning is always safe
    if demo_mode:
        return True, "Authorized (Demo Mode active)."

    # Explicit whitelist check
    if clean_target in ALLOWED_PUBLIC_HOSTS:
        return True, f"Authorized public research target: {clean_target}"

    # Resolve IP
    try:
        ip_str = socket.gethostbyname(clean_target)
        ip_obj = ipaddress.ip_address(ip_str)
    except Exception as e:
        return False, f"Could not resolve target host '{clean_target}': {str(e)}"

    # Check if target resolves to scanme.nmap.org IP
    if str(ip_obj) in ALLOWED_PUBLIC_HOSTS:
        return True, f"Authorized public research target: {clean_target} ({ip_obj})"

    # Check loopback and private network ranges (RFC 1918)
    if ip_obj.is_loopback:
        return True, f"Authorized local loopback target: {ip_str}"

    if ip_obj.is_private:
        return True, f"Authorized private RFC1918 network target: {ip_str}"

    return False, (
        f"Scanning blocked: '{clean_target}' ({ip_str}) is a public internet address. "
        f"For security & ethical compliance, scans are restricted to localhost (127.0.0.1), "
        f"private subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), and scanme.nmap.org."
    )


def validate_port_range(start_port: int, end_port: int, max_ports: Optional[int] = 1024) -> Tuple[bool, str]:
    """Validate port range boundaries."""
    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
        return False, "Port numbers must be between 1 and 65535."
    if start_port > end_port:
        return False, f"Start port ({start_port}) cannot be greater than end port ({end_port})."
    
    total = end_port - start_port + 1
    if max_ports and total > max_ports:
        return False, f"Requested port count ({total}) exceeds safe limit of {max_ports} ports."

    return True, f"Valid port range: {start_port}-{end_port} ({total} ports)."
