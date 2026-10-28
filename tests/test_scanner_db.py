"""
Tests for NetGuard-IDS Port Scanner and Database Persistence.
"""

import os
from core.scanner import get_simulated_scan_results, scan_single_port
from core.db import init_db, save_port_scan, get_recent_port_scans, save_ml_analysis, get_recent_ml_analyses

TEST_DB = "test_guard.db"

def test_simulated_scan_returns_structured_data():
    res = get_simulated_scan_results("127.0.0.1")
    assert res["target"] == "127.0.0.1"
    assert res["ports_scanned"] > 0
    assert res["open_ports_count"] > 0
    assert res["risk_verdict"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert res["is_demo"] is True

def test_single_port_closed():
    # Typically closed random high port
    res = scan_single_port("127.0.0.1", 54321, timeout=0.1)
    # May be None or dict
    if res:
        assert "port" in res

def test_db_operations():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    init_db(TEST_DB)
    
    # Save scan
    scan_id = save_port_scan(
        target="127.0.0.1",
        scan_mode="Quick",
        ports_scanned=100,
        open_ports_count=2,
        risk_score=45.0,
        risk_verdict="MEDIUM",
        open_ports=[{"port": 80, "service": "http", "severity": "MEDIUM"}],
        duration_seconds=1.2,
        db_path=TEST_DB
    )
    assert scan_id == 1
    
    scans = get_recent_port_scans(5, db_path=TEST_DB)
    assert len(scans) == 1
    assert scans[0]["target"] == "127.0.0.1"
    
    # Save ML analysis
    ml_id = save_ml_analysis(
        filename="test.csv",
        total_records=100,
        normal_count=80,
        attack_count=20,
        attack_breakdown={"DoS": 20},
        top_threat="DoS",
        db_path=TEST_DB
    )
    assert ml_id == 1
    
    analyses = get_recent_ml_analyses(5, db_path=TEST_DB)
    assert len(analyses) == 1
    assert analyses[0]["top_threat"] == "DoS"
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
