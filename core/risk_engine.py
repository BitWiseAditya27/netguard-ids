"""
NetGuard-IDS Cybersecurity Port Risk Engine.
Maps open ports, protocols, and grabbed banners to risk profiles,
CVSS-style scoring, likely attack types, and concrete mitigation steps.
Calculates aggregated risk score (0-100) and overarching security verdict.
"""

from typing import List, Dict, Any, Tuple

# Comprehensive knowledge base for port security risks
PORT_RISK_DATABASE: Dict[int, Dict[str, Any]] = {
    21: {
        "service": "FTP",
        "severity": "HIGH",
        "cvss": 7.5,
        "attack_types": ["Cleartext Credential Sniffing", "Brute Force Attack", "Anonymous Access Exploitation"],
        "remediation": "Disable plaintext FTP. Migrate all file transfers to SFTP (SSH Port 22) or FTPS (FTP over TLS/SSL) with strong public-key auth."
    },
    22: {
        "service": "SSH",
        "severity": "LOW",
        "cvss": 3.9,
        "attack_types": ["SSH Credential Brute Force", "Dict Attacks", "Outdated OpenSSH Exploitation"],
        "remediation": "Enforce ed25519 key authentication, disable root login (PermitRootLogin no), and deploy fail2ban or IP allowlisting."
    },
    23: {
        "service": "Telnet",
        "severity": "CRITICAL",
        "cvss": 9.8,
        "attack_types": ["Eavesdropping / Credential Theft", "Man-in-the-Middle (MitM)", "Session Hijacking"],
        "remediation": "Immediately terminate Telnet daemon. Telnet transmits usernames, passwords, and sessions in plain text. Replace with OpenSSH."
    },
    25: {
        "service": "SMTP",
        "severity": "MEDIUM",
        "cvss": 5.3,
        "attack_types": ["Open Mail Relay Abuse", "Spam Amplification", "User Enumeration (VRFY/EXPN)"],
        "remediation": "Require STARTTLS, disable open relays, configure SPF, DKIM, and DMARC DNS records, and disable VRFY/EXPN commands."
    },
    53: {
        "service": "DNS",
        "severity": "MEDIUM",
        "cvss": 5.0,
        "attack_types": ["DNS Amplification DDoS", "DNS Cache Poisoning", "Zone Transfer Leakage"],
        "remediation": "Restrict DNS recursion to internal subnets, disable AXFR zone transfers for external clients, and enable DNSSEC validation."
    },
    80: {
        "service": "HTTP",
        "severity": "MEDIUM",
        "cvss": 5.3,
        "attack_types": ["Unencrypted Web Traffic", "Credential Sniffing", "Web Application Attacks (XSS, SQLi)"],
        "remediation": "Configure HTTP-to-HTTPS automatic 301 redirection and deploy HTTP Strict Transport Security (HSTS) headers."
    },
    110: {
        "service": "POP3",
        "severity": "HIGH",
        "cvss": 7.5,
        "attack_types": ["Plaintext Auth Sniffing", "Mailbox Interception", "Credential Harvest"],
        "remediation": "Disable unencrypted POP3; migrate to POP3S (Port 995) or modern OAuth2-authenticated IMAP/TLS."
    },
    135: {
        "service": "MSRPC / RPC",
        "severity": "HIGH",
        "cvss": 7.8,
        "attack_types": ["Remote Code Execution", "Endpoint Mapping Recon", "DCOM Exploit"],
        "remediation": "Block port 135 at boundary firewalls. Never expose Microsoft RPC endpoints to public networks."
    },
    139: {
        "service": "NetBIOS-SSN",
        "severity": "HIGH",
        "cvss": 7.5,
        "attack_types": ["NetBIOS Poisoning", "SMB Relay", "Workgroup Reconnaissance"],
        "remediation": "Disable NetBIOS over TCP/IP in network adapter settings; isolate internal SMB shares."
    },
    143: {
        "service": "IMAP",
        "severity": "HIGH",
        "cvss": 7.5,
        "attack_types": ["Cleartext Mail Interception", "Brute Force Authentication"],
        "remediation": "Deprecate unencrypted IMAP. Use IMAPS (Port 993) secured with TLS 1.3."
    },
    443: {
        "service": "HTTPS",
        "severity": "LOW",
        "cvss": 2.5,
        "attack_types": ["Web Application Vulnerabilities", "TLS Misconfiguration"],
        "remediation": "Maintain TLS 1.2/1.3 cipher suites, renew SSL certificates, and protect web services behind a Web Application Firewall (WAF)."
    },
    445: {
        "service": "Microsoft-DS / SMB",
        "severity": "CRITICAL",
        "cvss": 9.8,
        "attack_types": ["WannaCry / EternalBlue RCE", "Ransomware Lateral Movement", "NTLM Relay"],
        "remediation": "Block port 445 immediately at perimeter firewalls. Disable SMBv1 across all endpoints, enable SMB signing/encryption."
    },
    1433: {
        "service": "MS SQL Server",
        "severity": "CRITICAL",
        "cvss": 9.0,
        "attack_types": ["Database Credential Brute Force", "SQL Injection / xp_cmdshell RCE", "Data Exfiltration"],
        "remediation": "Bind SQL Server to loopback or private subnet. Do not expose 1433 publicly; enforce VPN/SSH tunneling and strong SA passwords."
    },
    1521: {
        "service": "Oracle DB",
        "severity": "CRITICAL",
        "cvss": 8.9,
        "attack_types": ["TNS Poisoning", "Oracle Credential Brute Force", "Direct Data Theft"],
        "remediation": "Isolate database listener in protected VLAN, require encrypted SQL*Net connections, and filter IP access."
    },
    3306: {
        "service": "MySQL / MariaDB",
        "severity": "HIGH",
        "cvss": 8.5,
        "attack_types": ["Exposed Database Authentication", "SQL Injection", "Data Breach"],
        "remediation": "Bind MySQL to 127.0.0.1 in my.cnf (bind-address = 127.0.0.1), prohibit remote root logins, and restrict client IPs."
    },
    3389: {
        "service": "RDP",
        "severity": "CRITICAL",
        "cvss": 9.8,
        "attack_types": ["BlueKeep RCE (CVE-2019-0708)", "Ransomware Entry Vector", "RDP Brute Force"],
        "remediation": "Remove public RDP exposure. Require VPN gateway + Multi-Factor Authentication (MFA), and enforce Network Level Authentication (NLA)."
    },
    5432: {
        "service": "PostgreSQL",
        "severity": "HIGH",
        "cvss": 8.5,
        "attack_types": ["Database Exploitation", "RCE via pg_read_file/COPY", "Credential Spray"],
        "remediation": "Restrict pg_hba.conf client addresses, enforce TLS encryption, and avoid public exposure."
    },
    5900: {
        "service": "VNC",
        "severity": "CRITICAL",
        "cvss": 9.0,
        "attack_types": ["Unencrypted Remote Desktop Control", "VNC Password Brute Force", "Unauthorized Screen Viewing"],
        "remediation": "Disable direct VNC exposure. Tunnel VNC connections strictly through SSH or commercial VPN with MFA."
    },
    6379: {
        "service": "Redis",
        "severity": "CRITICAL",
        "cvss": 9.8,
        "attack_types": ["Unauthenticated Key-Value Access", "SSH Key Overwrite RCE", "Data Exfiltration"],
        "remediation": "Enable protected-mode, bind to 127.0.0.1, set strong `requirepass` password, and rename dangerous commands (FLUSHALL, CONFIG)."
    },
    8080: {
        "service": "HTTP-Proxy / Alt-HTTP",
        "severity": "MEDIUM",
        "cvss": 5.5,
        "attack_types": ["Exposed Admin Interfaces (Jenkins/Tomcat)", "Authentication Bypass"],
        "remediation": "Audit hosted applications, enforce TLS reverse proxies, and mandate multi-factor authentication for management dashboards."
    },
    27017: {
        "service": "MongoDB",
        "severity": "CRITICAL",
        "cvss": 9.8,
        "attack_types": ["Unauthenticated NoSQL Access", "Database Ransomware Wipe", "Data Exfiltration"],
        "remediation": "Enable `--auth` in MongoDB configuration, disable public interface binding, and isolate database inside private network."
    }
}

SEVERITY_WEIGHTS = {
    "CRITICAL": 30.0,
    "HIGH": 18.0,
    "MEDIUM": 8.0,
    "LOW": 3.0,
    "INFO": 1.0
}

def analyze_port_risk(port: int, banner: str = "", service_name: str = "") -> Dict[str, Any]:
    """Analyze an individual open port and banner for risk metrics."""
    if port in PORT_RISK_DATABASE:
        base = PORT_RISK_DATABASE[port].copy()
    else:
        # Generic heuristic for unrecognized ports
        base = {
            "service": service_name or f"Port-{port}",
            "severity": "LOW" if port > 1024 else "MEDIUM",
            "cvss": 3.5 if port > 1024 else 5.0,
            "attack_types": ["Unknown Service Reconnaissance", "Potential Custom Daemon Exploitation"],
            "remediation": f"Verify whether port {port} is required for legitimate operations. If not, close or firewall it."
        }

    # Inspect grabbed banner for outdated / risky flags
    banner_lower = banner.lower()
    banner_alerts = []
    
    if "smbv1" in banner_lower:
        base["severity"] = "CRITICAL"
        base["cvss"] = 10.0
        banner_alerts.append("Vulnerable legacy SMBv1 protocol identified in banner!")
    elif "telnet" in banner_lower and base["severity"] != "CRITICAL":
        base["severity"] = "CRITICAL"
        base["cvss"] = 9.8
        banner_alerts.append("Telnet service detected in banner response.")
    elif "anonymous" in banner_lower and "ftp" in banner_lower:
        base["severity"] = "HIGH"
        banner_alerts.append("Anonymous FTP access permitted according to banner!")
    elif any(old in banner_lower for old in ["openssh_4", "openssh_5", "apache/2.2", "nginx/1.4"]):
        base["severity"] = "HIGH"
        banner_alerts.append("Potentially obsolete/unsupported software version detected in banner.")

    base["port"] = port
    base["banner"] = banner
    base["banner_alerts"] = banner_alerts
    return base


def compute_aggregate_risk(open_ports_analysis: List[Dict[str, Any]]) -> Tuple[float, str, str]:
    """
    Compute aggregate risk score (0-100) and overarching security verdict.
    Formula balances highest individual severity with cumulative threat volume.
    """
    if not open_ports_analysis:
        return 0.0, "LOW", "No open ports detected. The target host exhibits a hardened network surface."

    raw_score = 0.0
    severities = [p.get("severity", "LOW") for p in open_ports_analysis]
    cvss_scores = [p.get("cvss", 3.0) for p in open_ports_analysis]

    for sev in severities:
        raw_score += SEVERITY_WEIGHTS.get(sev, 3.0)

    # Boost by peak CVSS
    max_cvss = max(cvss_scores) if cvss_scores else 0.0
    combined_score = min(100.0, (raw_score * 0.8) + (max_cvss * 3.5))

    if "CRITICAL" in severities or combined_score >= 70.0:
        verdict = "CRITICAL"
        summary = "CRITICAL SECURITY RISK: Host exposes dangerous services (e.g., SMB 445, Telnet 23, RDP 3389, unauthenticated DBs) vulnerable to direct compromise or ransomware."
    elif "HIGH" in severities or combined_score >= 45.0:
        verdict = "HIGH"
        summary = "HIGH SECURITY RISK: High-risk services (e.g., FTP, exposed SQL servers, RPC) exposed. Attackers can leverage these for lateral movement or credential theft."
    elif "MEDIUM" in severities or combined_score >= 25.0:
        verdict = "MEDIUM"
        summary = "MEDIUM RISK: Standard services detected without complete transport security or isolation. Review configuration and encryption controls."
    else:
        verdict = "LOW"
        summary = "LOW RISK: Target presents minimal exposure. Services observed (e.g., HTTPS, hardened SSH) align with standard operational baselines."

    return round(combined_score, 1), verdict, summary
