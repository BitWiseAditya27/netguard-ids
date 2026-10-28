"""
NetGuard-IDS: Port Scanner & Service Risk Identification Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.validators import is_authorized_target, validate_port_range
from core.scanner import run_port_scan, get_simulated_scan_results, TOP_100_PORTS
from core.db import save_port_scan

st.set_page_config(page_title="Port Scanner | NetGuard-IDS", page_icon="🔍", layout="wide")

st.title("🔍 Port Scanner & Risk Analyzer")
st.markdown("Scan authorized targets to discover exposed services, grab application banners, and compute cyber risk scores.")

# Authorization & Safety Section (Mandatory)
st.warning("⚠️ **Safety & Authorization Policy:** Scanning unauthorized third-party infrastructure is illegal. You must verify ownership or explicit written authorization.")

authorized_consent = st.checkbox("✅ **I confirm that I own this target system or have explicit written authorization to scan it.**")

col_params1, col_params2 = st.columns([2, 1])

with col_params1:
    target_host = st.text_input("Target IP or Hostname", value="127.0.0.1", help="e.g. 127.0.0.1, 192.168.1.1, scanme.nmap.org")
    scan_mode = st.selectbox(
        "Scan Mode",
        ["Quick (Top 100 Common Ports)", "Common (Ports 1-1024)", "Custom Range", "Full Scan (1-65535)"]
    )

with col_params2:
    demo_mode = st.toggle("⚡ Hosted Demo Mode (Simulated Data)", value=False, help="Recommended for cloud environments where raw outbound socket scanning is blocked by hosting provider.")
    thread_count = st.slider("Concurrent Worker Threads", min_value=10, max_value=100, value=50, step=10)
    timeout_val = st.slider("Socket Connect Timeout (seconds)", min_value=0.2, max_value=2.0, value=0.6, step=0.1)

# Handle Custom Port ranges
ports_to_scan = []
if scan_mode == "Quick (Top 100 Common Ports)":
    ports_to_scan = TOP_100_PORTS
elif scan_mode == "Common (Ports 1-1024)":
    ports_to_scan = list(range(1, 1025))
elif scan_mode == "Custom Range":
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        start_p = st.number_input("Start Port", min_value=1, max_value=65535, value=20)
    with col_c2:
        end_p = st.number_input("End Port", min_value=1, max_value=65535, value=100)
    ports_to_scan = list(range(start_p, end_p + 1))
elif scan_mode == "Full Scan (1-65535)":
    st.error("⚠️ Warning: Full port scans take several minutes. Ensure rate limits and network capacity allow it.")
    ports_to_scan = list(range(1, 65536))

# Scan Execution Trigger
if st.button("🚀 Launch Port Audit", type="primary", use_container_width=True):
    if not authorized_consent:
        st.error("❌ Permission denied: You must check the authorization consent box before initiating a scan.")
    else:
        # Validate target compliance
        is_auth, auth_msg = is_authorized_target(target_host, demo_mode=demo_mode)
        if not is_auth:
            st.error(f"❌ Policy Enforcement Block: {auth_msg}")
        else:
            progress_bar = st.progress(0, text="Initializing scan engine...")

            def update_progress(scanned: int, total: int):
                pct = int((scanned / total) * 100)
                progress_bar.progress(min(pct, 100), text=f"Scanned {scanned}/{total} ports ({pct}%)...")

            if demo_mode:
                update_progress(100, 100)
                results = get_simulated_scan_results(target_host)
            else:
                results = run_port_scan(
                    target=target_host,
                    ports=ports_to_scan,
                    threads=thread_count,
                    timeout=timeout_val,
                    progress_callback=update_progress
                )

            # Store in session state and SQLite
            st.session_state["latest_scan"] = results
            save_port_scan(
                target=results["target"],
                scan_mode=scan_mode,
                ports_scanned=results["ports_scanned"],
                open_ports_count=results["open_ports_count"],
                risk_score=results["risk_score"],
                risk_verdict=results["risk_verdict"],
                open_ports=results["open_ports"],
                duration_seconds=results["duration_seconds"]
            )
            st.success(f"Audit completed in {results['duration_seconds']}s! Findings recorded.")

# Render Results
if "latest_scan" in st.session_state:
    scan = st.session_state["latest_scan"]
    st.divider()

    st.subheader(f"📊 Audit Results for `{scan['target']}`")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ports Scanned", scan["ports_scanned"])
    m2.metric("Open Services Found", scan["open_ports_count"])
    m3.metric("Aggregate Risk Score", f"{scan['risk_score']} / 100")
    m4.metric("Security Verdict", scan["risk_verdict"])

    # Visualizations
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        # Gauge chart for risk score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=scan["risk_score"],
            title={'text': "Aggregate Cyber Risk Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00D4B2"},
                'steps': [
                    {'range': [0, 25], 'color': "#1a472a"},
                    {'range': [25, 50], 'color': "#8a7500"},
                    {'range': [50, 75], 'color': "#a05200"},
                    {'range': [75, 100], 'color': "#8b0000"}
                ]
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_chart2:
        # Donut chart for severity
        if scan["open_ports"]:
            sev_counts = pd.DataFrame(scan["open_ports"])["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            colors = {"CRITICAL": "#FF4D4D", "HIGH": "#FFA500", "MEDIUM": "#FFD700", "LOW": "#00D4B2"}
            fig_donut = px.pie(
                sev_counts, names="Severity", values="Count", hole=0.5,
                color="Severity", color_discrete_map=colors,
                title="Service Vulnerability Breakdown"
            )
            fig_donut.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No open ports found to plot.")

    # Detailed Port Table
    st.markdown("### 📋 Discovered Open Ports & Threat Vectors")
    if scan["open_ports"]:
        display_ports = []
        for p in scan["open_ports"]:
            display_ports.append({
                "Port": p["port"],
                "Service": p.get("service", "Unknown"),
                "Severity": p.get("severity", "LOW"),
                "CVSS Base": p.get("cvss", 0.0),
                "Banner Grabbed": p.get("banner", "")[:60] if p.get("banner") else "None",
                "Remediation Guidance": p.get("remediation", "")
            })
        st.dataframe(pd.DataFrame(display_ports), use_container_width=True, hide_index=True)
    else:
        st.success("Target host returned no open ports in this scan range.")
