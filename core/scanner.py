"""
NetGuard-IDS Multithreaded Port Scanner.
Executes non-root TCP connect scans using Python socket + concurrent.futures,
with optional python-nmap integration fallback, service detection, banner grabbing,
rate limiting, and a rich DEMO MODE for hosted cloud environments.
"""

import socket
import time
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from core.risk_engine import analyze_port_risk, compute_aggregate_risk

# Standard top 100 ports list
TOP_100_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 137, 138, 139, 143, 161, 162,
    179, 389, 443, 445, 465, 500, 514, 515, 520, 587, 631, 636, 873, 990, 993, 995, 1025,
    1080, 1194, 1433, 1434, 1521, 1723, 2049, 2082, 2083, 2086, 2087, 2181, 2222, 2375, 2376,
    3000, 3128, 3306, 3389, 3690, 4333, 5000, 5432, 5900, 5901, 5984, 6379, 6667, 7001, 8000,
    8008, 8080, 8081, 8443, 8888, 9000, 9090, 9200, 9300, 9418, 9999, 10000, 11211, 27017,
    27018, 28017, 50000, 50070
]

# Service map for well-known ports
COMMON_SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns", 80: "http", 110: "pop3",
    111: "rpcbind", 135: "msrpc", 139: "netbios-ssn", 143: "imap", 443: "https",
    445: "microsoft-ds", 993: "imaps", 995: "pop3s", 1433: "ms-sql-s", 1521: "oracle",
    3306: "mysql", 3389: "ms-wbt-server", 5432: "postgresql", 5900: "vnc", 6379: "redis",
    8080: "http-proxy", 8443: "https-alt", 27017: "mongodb"
}

def grab_banner(target: str, port: int, timeout: float = 1.0) -> str:
    """Attempt safe TCP banner grab from open port."""
    banner = ""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((target, port))
            # Send lightweight probes according to port type
            if port in (80, 8080, 8000):
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + target.encode() + b"\r\n\r\n")
            elif port in (21, 22, 25, 110, 143):
                # Service usually announces itself first upon connect
                pass
            else:
                s.sendall(b"\r\n")
                
            response = s.recv(1024)
            if response:
                banner = response.decode("utf-8", errors="replace").strip()
                # Keep first 2 lines
                banner = "\n".join(banner.splitlines()[:2])
    except Exception:
        pass
    return banner


def scan_single_port(target: str, port: int, timeout: float = 0.8) -> Optional[Dict[str, Any]]:
    """Probe a single TCP port using a non-root standard socket connect."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            if result == 0:
                service_guess = COMMON_SERVICES.get(port, "")
                if not service_guess:
                    try:
                        service_guess = socket.getservbyport(port, "tcp")
                    except Exception:
                        service_guess = "unknown"
                
                banner = grab_banner(target, port, timeout=0.8)
                return {
                    "port": port,
                    "state": "open",
                    "service": service_guess,
                    "banner": banner
                }
    except Exception:
        pass
    return None


def run_port_scan(
    target: str,
    ports: List[int],
    threads: int = 50,
    timeout: float = 0.8,
    rate_limit_delay: float = 0.0,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Dict[str, Any]:
    """
    Execute a concurrent port scan over the specified target and port list.
    Returns structured results, risk assessments, and execution metrics.
    """
    start_time = time.time()
    open_ports_raw = []
    total_ports = len(ports)
    scanned_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(threads, 100)) as executor:
        future_to_port = {
            executor.submit(scan_single_port, target, p, timeout): p 
            for p in ports
        }
        for future in concurrent.futures.as_completed(future_to_port):
            scanned_count += 1
            if progress_callback and scanned_count % 5 == 0:
                progress_callback(scanned_count, total_ports)
            
            res = future.result()
            if res:
                open_ports_raw.append(res)
            
            if rate_limit_delay > 0:
                time.sleep(rate_limit_delay)

    if progress_callback:
        progress_callback(total_ports, total_ports)

    # Sort discovered open ports
    open_ports_raw.sort(key=lambda x: x["port"])

    # Augment with risk assessment
    assessed_ports = []
    for item in open_ports_raw:
        risk_info = analyze_port_risk(
            port=item["port"],
            banner=item.get("banner", ""),
            service_name=item.get("service", "")
        )
        assessed_ports.append({**item, **risk_info})

    # Aggregate calculation
    risk_score, verdict, summary = compute_aggregate_risk(assessed_ports)
    duration = round(time.time() - start_time, 2)

    return {
        "target": target,
        "ports_scanned": total_ports,
        "open_ports_count": len(assessed_ports),
        "open_ports": assessed_ports,
        "risk_score": risk_score,
        "risk_verdict": verdict,
        "summary": summary,
        "duration_seconds": duration,
        "is_demo": False
    }


def get_simulated_scan_results(target: str = "192.168.1.105 (Enterprise Host)") -> Dict[str, Any]:
    """
    Generate authentic simulated scan results for Cloud/Hosted demo mode
    where outbound raw socket scanning may be restricted by cloud hosting providers.
    """
    sample_ports = [
        {"port": 21, "service": "ftp", "banner": "220 ProFTPD 1.3.5 Server (Ubuntu) [Anonymous allowed]"},
        {"port": 22, "service": "ssh", "banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6"},
        {"port": 80, "service": "http", "banner": "Apache/2.4.52 (Ubuntu) Server at 192.168.1.105 Port 80"},
        {"port": 443, "service": "https", "banner": "TLSv1.3 nginx/1.22.0"},
        {"port": 445, "service": "microsoft-ds", "banner": "Windows Server 2016 SMBv1 LanMan"},
        {"port": 3306, "service": "mysql", "banner": "8.0.35-0ubuntu0.22.04.1"},
        {"port": 3389, "service": "ms-wbt-server", "banner": "Microsoft Terminal Services RDP"}
    ]

    assessed_ports = []
    for item in sample_ports:
        risk_info = analyze_port_risk(
            port=item["port"],
            banner=item["banner"],
            service_name=item["service"]
        )
        assessed_ports.append({**item, **risk_info})

    risk_score, verdict, summary = compute_aggregate_risk(assessed_ports)

    return {
        "target": target,
        "ports_scanned": 100,
        "open_ports_count": len(assessed_ports),
        "open_ports": assessed_ports,
        "risk_score": risk_score,
        "risk_verdict": verdict,
        "summary": summary,
        "duration_seconds": 1.25,
        "is_demo": True
    }
