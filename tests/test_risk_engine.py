"""
Tests for NetGuard-IDS Risk Engine.
"""

from core.risk_engine import analyze_port_risk, compute_aggregate_risk

def test_analyze_critical_ports():
    # SMB port 445
    r445 = analyze_port_risk(445)
    assert r445["severity"] == "CRITICAL"
    assert r445["cvss"] >= 9.0
    assert any("EternalBlue" in a or "Ransomware" in a for a in r445["attack_types"])

    # Telnet port 23
    r23 = analyze_port_risk(23)
    assert r23["severity"] == "CRITICAL"

    # SSH port 22
    r22 = analyze_port_risk(22)
    assert r22["severity"] == "LOW"

def test_banner_heuristic_escalation():
    # Regular web port with legacy smbv1 banner
    r80 = analyze_port_risk(80, banner="Vulnerable legacy SMBv1 test")
    assert r80["severity"] == "CRITICAL"
    assert len(r80["banner_alerts"]) > 0

def test_aggregate_risk_computation():
    # Empty scan
    score, verdict, _ = compute_aggregate_risk([])
    assert score == 0.0
    assert verdict == "LOW"

    # Critical findings
    crit_scan = [
        {"port": 445, "severity": "CRITICAL", "cvss": 9.8},
        {"port": 3389, "severity": "CRITICAL", "cvss": 9.8}
    ]
    score, verdict, _ = compute_aggregate_risk(crit_scan)
    assert score >= 75.0
    assert verdict == "CRITICAL"

    # Only low findings
    low_scan = [
        {"port": 443, "severity": "LOW", "cvss": 2.5}
    ]
    score, verdict, _ = compute_aggregate_risk(low_scan)
    assert score < 25.0
    assert verdict == "LOW"
