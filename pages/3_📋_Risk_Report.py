"""
NetGuard-IDS: Security Audit Reports & Export Page.
"""

import streamlit as st
import json
import pandas as pd
from core.report import export_scan_to_json, export_scan_to_csv, generate_markdown_report
from core.db import get_recent_port_scans

st.set_page_config(page_title="Audit Reports | NetGuard-IDS", page_icon="📋", layout="wide")

st.title("📋 Security Audit & Vulnerability Reports")
st.markdown("Review executive assessment summaries, remediation playbooks, and export audit artifacts for compliance.")

scans = get_recent_port_scans(limit=25)

if not scans and "latest_scan" not in st.session_state:
    st.info("No audit reports recorded yet. Perform a scan in the **Port Scanner** module to generate a report.")
    st.stop()

# Select audit record
scan_options = {}
if "latest_scan" in st.session_state:
    scan_options["Latest Active Scan"] = st.session_state["latest_scan"]

for s in scans:
    key = f"Scan #{s['id']} - {s['target']} ({s['timestamp']}) - Score: {s['risk_score']}"
    scan_options[key] = s

selected_key = st.selectbox("Select Audit Session to Review", list(scan_options.keys()))
scan_data = scan_options[selected_key]

# Display summary card
st.markdown("---")
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.metric("Risk Score", f"{scan_data['risk_score']} / 100")
with c2:
    st.metric("Security Verdict", scan_data["risk_verdict"])
with c3:
    st.markdown(f"**Target Host:** `{scan_data['target']}`")
    st.markdown(f"**Audited Services Count:** `{scan_data['open_ports_count']}`")

st.markdown("### 🛡️ Remediation Advice & Hardening Playbook")
ports = scan_data.get("open_ports", [])
if ports:
    for p in ports:
        with st.expander(f"Port {p.get('port')} ({p.get('service', 'unknown').upper()}) - Severity: {p.get('severity')}"):
            st.markdown(f"**CVSS Base Score:** `{p.get('cvss', 0.0)}`")
            st.markdown(f"**Potential Exploit Vectors:** {', '.join(p.get('attack_types', []))}")
            st.markdown(f"**Actionable Mitigation:** {p.get('remediation')}")
else:
    st.success("Target perimeter appears fully closed or filtered. No immediate remediation actions required.")

# Export Artifacts
st.markdown("### 💾 Export Audit Records")
col_e1, col_e2, col_e3 = st.columns(3)

json_str = export_scan_to_json(scan_data)
csv_str = export_scan_to_csv(ports)
md_str = generate_markdown_report(scan_data)

with col_e1:
    st.download_button(
        "📥 Download Report (JSON)",
        data=json_str,
        file_name=f"netguard_audit_{scan_data['target']}.json",
        mime="application/json",
        use_container_width=True
    )

with col_e2:
    st.download_button(
        "📥 Download Open Ports (CSV)",
        data=csv_str,
        file_name=f"netguard_ports_{scan_data['target']}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_e3:
    st.download_button(
        "📥 Download Executive Summary (MD / Doc)",
        data=md_str,
        file_name=f"netguard_summary_{scan_data['target']}.md",
        mime="text/markdown",
        use_container_width=True
    )
