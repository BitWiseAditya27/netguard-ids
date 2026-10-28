"""
NetGuard-IDS Report Generator.
Exports audit records to PDF, JSON, and CSV formats.
"""

import json
from typing import Dict, Any, List
import pandas as pd

def export_scan_to_json(scan_data: Dict[str, Any]) -> str:
    """Format scan details as structured indented JSON."""
    return json.dumps(scan_data, indent=2)

def export_scan_to_csv(open_ports: List[Dict[str, Any]]) -> str:
    """Convert open ports assessment list to CSV string."""
    if not open_ports:
        return "Port,Service,Severity,CVSS,Attack_Types,Remediation\n"
    
    rows = []
    for p in open_ports:
        rows.append({
            "Port": p.get("port"),
            "Service": p.get("service"),
            "Severity": p.get("severity"),
            "CVSS": p.get("cvss"),
            "Attack_Types": "; ".join(p.get("attack_types", [])),
            "Remediation": p.get("remediation", "")
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_markdown_report(scan_data: Dict[str, Any]) -> str:
    """Generate a clean executive cybersecurity assessment report in Markdown."""
    target = scan_data.get("target", "Unknown")
    score = scan_data.get("risk_score", 0.0)
    verdict = scan_data.get("risk_verdict", "LOW")
    summary = scan_data.get("summary", "")
    duration = scan_data.get("duration_seconds", 0.0)
    ports = scan_data.get("open_ports", [])

    md = f"""# NetGuard-IDS Executive Cyber Risk & Audit Report

**Target Asset:** `{target}`  
**Security Verdict:** **{verdict}**  
**Aggregate Risk Score:** **{score} / 100**  
**Scan Duration:** {duration} seconds  
**Open Services Discovered:** {len(ports)}  

---

### Executive Summary
{summary}

---

### Discovered Port Findings & Remediation Guidance
"""
    if not ports:
        md += "\n*No open ports were detected during this audit. Perimeter firewalling is intact.*\n"
    else:
        for p in ports:
            md += f"""
#### Port {p.get('port')} - Service: {p.get('service', 'Unknown').upper()}
- **Risk Severity:** `{p.get('severity')}` (CVSS Base: `{p.get('cvss')}`)
- **Associated Threats:** {", ".join(p.get('attack_types', []))}
- **Observed Banner:** `{p.get('banner', 'N/A')}`
- **Remediation Action:** {p.get('remediation')}

"""
    md += "\n---\n*Report generated autonomously by NetGuard-IDS Defensive Framework.*"
    return md
