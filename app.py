"""
NetGuard-IDS: Network Intrusion Detection & Port Risk Analyzer
Main Streamlit Entrypoint & Executive Overview Dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.db import init_db, get_recent_port_scans, get_recent_ml_analyses

# Page configuration
st.set_page_config(
    page_title="NetGuard-IDS | Enterprise Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom Styling for modern dark/light cybersecurity console
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00D4B2, #0088FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .metric-card {
        background-color: #1A1D24;
        border: 1px solid #2B303C;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .verdict-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-CRITICAL { background-color: #FF4D4D; color: white; }
    .badge-HIGH { background-color: #FFA500; color: black; }
    .badge-MEDIUM { background-color: #FFD700; color: black; }
    .badge-LOW { background-color: #00D4B2; color: black; }
</style>
""", unsafe_allow_html=True)

# Top Bar
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">🛡️ NetGuard-IDS</div>', unsafe_allow_html=True)
    st.markdown("**Unified Cyber Defense: Multithreaded Port Scanner • Port Risk Analyzer • ML Network Intrusion Detector**")

with col_status:
    st.markdown(
        """
        <div style="text-align: right; margin-top: 10px;">
            <span style="background-color: #123524; color: #00D4B2; border: 1px solid #00D4B2; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                ● SYSTEM OPERATIONAL
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# Load telemetry
scans = get_recent_port_scans(limit=10)
analyses = get_recent_ml_analyses(limit=10)

total_scans_count = len(scans)
total_ml_runs = len(analyses)
total_intrusions_detected = sum(a["attack_count"] for a in analyses) if analyses else 0

# Key Performance & Security Telemetry
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Hosts Audited", value=total_scans_count)
with kpi2:
    st.metric(label="ML Traffic Files Analyzed", value=total_ml_runs)
with kpi3:
    st.metric(label="Malicious Flows Intercepted", value=total_intrusions_detected)
with kpi4:
    last_verdict = scans[0]["risk_verdict"] if scans else "SECURE"
    st.metric(label="Latest Host Security Verdict", value=last_verdict)

st.markdown("### 📊 Security Operations Center (SOC) Feed")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Recent Host Scans")
    if scans:
        df_scans = pd.DataFrame(scans)[["id", "timestamp", "target", "ports_scanned", "open_ports_count", "risk_score", "risk_verdict"]]
        st.dataframe(df_scans, use_container_width=True, hide_index=True)
    else:
        st.info("No host scans recorded yet. Navigate to **Port Scanner** in the sidebar to execute your first authorized scan.")

with col_right:
    st.subheader("Recent ML Flow Analyses")
    if analyses:
        df_ml = pd.DataFrame(analyses)[["id", "timestamp", "filename", "total_records", "attack_count", "top_threat"]]
        st.dataframe(df_ml, use_container_width=True, hide_index=True)
    else:
        st.info("No flow analysis records yet. Head over to **Traffic Analysis (ML)** to evaluate network flows.")

st.divider()

# Quick Navigation cards
st.markdown("### 🚀 Defensive Capabilities")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    #### 🔍 Multithreaded Port Scanner
    Perform authorized, non-root TCP port scans with service identification, banner grabbing, and automated CVSS-style risk assessment.
    """)
with c2:
    st.markdown("""
    #### 🧠 Machine Learning IDS
    Upload live or captured network flow CSVs. Detect **DoS, Probe, R2L, and U2R** intrusions instantly using trained Random Forest & XGBoost pipelines.
    """)
with c3:
    st.markdown("""
    #### 📋 Audit & Executive Reports
    Review comprehensive vulnerability vectors, actionable remediation steps, and download audit reports in PDF, JSON, and CSV.
    """)

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ NetGuard-IDS v1.0.0")
st.sidebar.caption("Defensive Cyber Auditing & AI Threat Detection Platform")
st.sidebar.info("Protected by strict authorized-target validation and ethical compliance policies.")
