"""
Tests for NetGuard-IDS ML Intrusion Detection Engine.
"""

import pandas as pd
from core.ml_detector import MLIntrusionDetector

def test_ml_detector_inference():
    detector = MLIntrusionDetector()
    assert detector.is_ready() is True

    # Test inference with sample CSV
    df = pd.read_csv("data/sample_network_flows.csv")
    df_res, summary = detector.predict_flow(df)

    assert "Predicted_Class" in df_res.columns
    assert "Confidence_%" in df_res.columns
    assert len(df_res) == len(df)
    assert summary["total_records"] == len(df)
    assert summary["normal_count"] + summary["intrusion_count"] == len(df)
    assert summary["top_threat"] in ["DoS", "Probe", "R2L", "U2R", "None Detected"]
