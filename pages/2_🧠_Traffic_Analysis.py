"""
NetGuard-IDS: Machine Learning Network Traffic Intrusion Analysis Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from core.ml_detector import MLIntrusionDetector
from core.db import save_ml_analysis

st.set_page_config(page_title="Traffic Analysis (ML) | NetGuard-IDS", page_icon="🧠", layout="wide")

st.title("🧠 ML-Powered Network Intrusion Detection")
st.markdown("Analyze network flow telemetry with trained **Random Forest & XGBoost** models to detect **DoS, Probes, R2L, and U2R** attacks in real time.")

detector = MLIntrusionDetector()

if not detector.is_ready():
    st.error("ML Model artifacts not detected in `models/`. Run `python scripts/train_model.py` to train and build models.")
    st.stop()

col_up1, col_up2 = st.columns([2, 1])

with col_up1:
    uploaded_file = st.file_uploader("Upload Network Flow CSV", type=["csv"], help="Upload CSV containing flow characteristics (duration, protocol_type, src_bytes, etc.)")

with col_up2:
    st.markdown("#### ⚡ Quick Demo Sample")
    load_sample = st.button("📥 Load Bundled Benchmark CSV (50 Flows)", use_container_width=True)

df_to_analyze = None
source_name = ""

if load_sample:
    sample_path = "data/sample_network_flows.csv"
    try:
        df_to_analyze = pd.read_csv(sample_path)
        source_name = "sample_network_flows.csv"
        st.session_state["ml_df"] = df_to_analyze
        st.session_state["ml_src"] = source_name
    except Exception as e:
        st.error(f"Error loading sample dataset: {e}")
elif uploaded_file is not None:
    try:
        df_to_analyze = pd.read_csv(uploaded_file)
        source_name = uploaded_file.name
        st.session_state["ml_df"] = df_to_analyze
        st.session_state["ml_src"] = source_name
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
elif "ml_df" in st.session_state:
    df_to_analyze = st.session_state["ml_df"]
    source_name = st.session_state.get("ml_src", "Loaded Dataset")

if df_to_analyze is not None:
    st.info(f"Loaded **{len(df_to_analyze)}** network flow records from `{source_name}`.")
    
    with st.spinner("Executing ML Inference Pipeline..."):
        df_results, summary = detector.predict_flow(df_to_analyze)

    # Save to history DB
    save_ml_analysis(
        filename=source_name,
        total_records=summary["total_records"],
        normal_count=summary["normal_count"],
        attack_count=summary["intrusion_count"],
        attack_breakdown=summary["class_distribution"],
        top_threat=summary["top_threat"]
    )

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Analyzed Flows", summary["total_records"])
    m2.metric("Benign / Normal Flows", summary["normal_count"])
    m3.metric("Malicious Intrusions", summary["intrusion_count"], delta=f"{summary['intrusion_rate_pct']}% threat rate", delta_color="inverse")
    m4.metric("Dominant Attack Vector", summary["top_threat"])

    st.divider()

    # Visualizations
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        # Attack class distribution bar chart
        dist_df = pd.DataFrame(list(summary["class_distribution"].items()), columns=["Category", "Count"])
        fig_bar = px.bar(
            dist_df, x="Category", y="Count", color="Category",
            color_discrete_map={
                "Normal": "#00D4B2", "DoS": "#FF4D4D", "Probe": "#FFA500",
                "R2L": "#9370DB", "U2R": "#DC143C"
            },
            title="Classification Distribution Across Attack Taxonomies"
        )
        fig_bar.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        # Threat vs Benign Donut
        threat_df = pd.DataFrame({
            "Traffic Type": ["Benign Traffic", "Malicious Intrusion"],
            "Volume": [summary["normal_count"], summary["intrusion_count"]]
        })
        fig_pie = px.pie(
            threat_df, names="Traffic Type", values="Volume", hole=0.5,
            color="Traffic Type", color_discrete_map={"Benign Traffic": "#00D4B2", "Malicious Intrusion": "#FF4D4D"},
            title="Benign vs. Threat Flow Ratio"
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Per-row Dataframe Display
    st.markdown("### 📋 Flow Inspection & Prediction Records")
    cols_to_show = ["protocol_type", "service", "src_bytes", "dst_bytes", "count", "Predicted_Class", "Confidence_%", "Is_Intrusion"]
    valid_cols = [c for c in cols_to_show if c in df_results.columns]
    
    st.dataframe(df_results[valid_cols], use_container_width=True, hide_index=True)

    # Download Results CSV
    csv_data = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Annotated Predictions CSV",
        data=csv_data,
        file_name="netguard_ids_predictions.csv",
        mime="text/csv",
        use_container_width=True
    )
