"""
NetGuard-IDS Database Layer (SQLite).
Persists port scan history and traffic analysis reports.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "scan_history.db"

def get_db_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Create a thread-safe connection to SQLite with row factory."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_FILE) -> None:
    """Initialize database tables for scans and ML analysis runs."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS port_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target TEXT NOT NULL,
            scan_mode TEXT NOT NULL,
            ports_scanned INTEGER NOT NULL,
            open_ports_count INTEGER NOT NULL,
            risk_score REAL NOT NULL,
            risk_verdict TEXT NOT NULL,
            open_ports_json TEXT NOT NULL,
            duration_seconds REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            filename TEXT NOT NULL,
            total_records INTEGER NOT NULL,
            normal_count INTEGER NOT NULL,
            attack_count INTEGER NOT NULL,
            attack_breakdown_json TEXT NOT NULL,
            top_threat TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_port_scan(
    target: str,
    scan_mode: str,
    ports_scanned: int,
    open_ports_count: int,
    risk_score: float,
    risk_verdict: str,
    open_ports: List[Dict[str, Any]],
    duration_seconds: float,
    db_path: str = DB_FILE
) -> int:
    """Persist a port scan record."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO port_scans 
        (timestamp, target, scan_mode, ports_scanned, open_ports_count, risk_score, risk_verdict, open_ports_json, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now, target, scan_mode, ports_scanned, open_ports_count,
        risk_score, risk_verdict, json.dumps(open_ports), duration_seconds
    ))

    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id

def get_recent_port_scans(limit: int = 20, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve recent port scan history."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM port_scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "target": r["target"],
            "scan_mode": r["scan_mode"],
            "ports_scanned": r["ports_scanned"],
            "open_ports_count": r["open_ports_count"],
            "risk_score": r["risk_score"],
            "risk_verdict": r["risk_verdict"],
            "open_ports": json.loads(r["open_ports_json"]),
            "duration_seconds": r["duration_seconds"]
        })
    conn.close()
    return results

def save_ml_analysis(
    filename: str,
    total_records: int,
    normal_count: int,
    attack_count: int,
    attack_breakdown: Dict[str, int],
    top_threat: str,
    db_path: str = DB_FILE
) -> int:
    """Persist an ML traffic analysis report summary."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO ml_analyses
        (timestamp, filename, total_records, normal_count, attack_count, attack_breakdown_json, top_threat)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        now, filename, total_records, normal_count, attack_count,
        json.dumps(attack_breakdown), top_threat
    ))

    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id

def get_recent_ml_analyses(limit: int = 20, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve recent traffic analysis history."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ml_analyses ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "filename": r["filename"],
            "total_records": r["total_records"],
            "normal_count": r["normal_count"],
            "attack_count": r["attack_count"],
            "attack_breakdown": json.loads(r["attack_breakdown_json"]),
            "top_threat": r["top_threat"]
        })
    conn.close()
    return results
