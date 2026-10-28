"""
NetGuard-IDS Machine Learning Intrusion Detection System.
Loads trained models (Random Forest / XGBoost) and performs multi-class
attack classification on flow traffic records (Normal, DoS, Probe, R2L, U2R).
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

# Core features selected for the robust IDS model
FEATURE_COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes",
    "dst_bytes", "land", "wrong_fragment", "urgent", "hot",
    "num_failed_logins", "logged_in", "num_compromised", "root_shell",
    "su_attempted", "num_root", "num_file_creations", "num_shells",
    "num_access_files", "is_host_login", "is_guest_login", "count",
    "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate",
    "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate"
]

CATEGORICAL_FEATURES = ["protocol_type", "service", "flag"]

NUMERIC_FEATURES = [col for col in FEATURE_COLUMNS if col not in CATEGORICAL_FEATURES]

# Mapping NSL-KDD specific attack labels to 5 core classes
ATTACK_MAPPING = {
    "normal": "Normal",
    
    # DoS
    "neptune": "DoS", "back": "DoS", "land": "DoS", "pod": "DoS", 
    "smurf": "DoS", "teardrop": "DoS", "mailbomb": "DoS", "apache2": "DoS", 
    "processtable": "DoS", "udpstorm": "DoS",
    
    # Probe
    "ipsweep": "Probe", "nmap": "Probe", "portsweep": "Probe", "satan": "Probe", 
    "mscan": "Probe", "saint": "Probe",
    
    # R2L (Remote to Local)
    "ftp_write": "R2L", "guess_passwd": "R2L", "imap": "R2L", "multihop": "R2L", 
    "phf": "R2L", "spy": "R2L", "warezclient": "R2L", "warezmaster": "R2L", 
    "sendmail": "R2L", "named": "R2L", "snmpgetattack": "R2L", "snmpguess": "R2L", 
    "xlock": "R2L", "xsnoop": "R2L", "worm": "R2L",
    
    # U2R (User to Root)
    "buffer_overflow": "U2R", "loadmodule": "U2R", "perl": "U2R", "rootkit": "U2R", 
    "httptunnel": "U2R", "ps": "U2R", "sqlattack": "U2R", "xterm": "U2R"
}

CLASSES = ["Normal", "DoS", "Probe", "R2L", "U2R"]

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_ids_model.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "feature_metadata.joblib")


class MLIntrusionDetector:
    """Production ML Inference Wrapper for IDS."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or MODEL_PATH
        self.encoders_path = ENCODERS_PATH
        self.pipeline = None
        self.metadata = None
        self._load_model()

    def _load_model(self) -> None:
        """Load trained pipeline bundle or raise clean notification."""
        if os.path.exists(self.model_path) and os.path.exists(self.encoders_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                self.metadata = joblib.load(self.encoders_path)
            except Exception as e:
                print(f"Warning loading model artifacts: {e}")
                self.pipeline = None
        else:
            self.pipeline = None

    def is_ready(self) -> bool:
        """Check if trained model pipeline is loaded and ready."""
        return self.pipeline is not None

    def predict_flow(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Run inference on network flow records.
        Returns augmented DataFrame with predictions/confidence and statistical summary.
        """
        if not self.is_ready():
            raise RuntimeError("Model artifacts not found. Please train or load the model first.")

        df_input = df.copy()

        # Ensure required features exist; fill defaults if absent
        for col in FEATURE_COLUMNS:
            if col not in df_input.columns:
                if col in CATEGORICAL_FEATURES:
                    df_input[col] = "unknown"
                else:
                    df_input[col] = 0.0

        # Run model pipeline predictions
        preds = self.pipeline.predict(df_input[FEATURE_COLUMNS])
        
        # Calculate prediction probabilities if supported
        try:
            probs = self.pipeline.predict_proba(df_input[FEATURE_COLUMNS])
            confidences = np.max(probs, axis=1) * 100.0
        except Exception:
            confidences = [95.0] * len(preds)

        # Build output dataframe
        df_result = df.copy()
        df_result["Predicted_Class"] = preds
        df_result["Confidence_%"] = np.round(confidences, 2)
        df_result["Is_Intrusion"] = df_result["Predicted_Class"].apply(lambda c: c != "Normal")

        # Compute summary metrics
        counts = df_result["Predicted_Class"].value_counts().to_dict()
        for c in CLASSES:
            counts.setdefault(c, 0)

        total = len(df_result)
        intrusions = int(df_result["Is_Intrusion"].sum())
        normal = total - intrusions

        # Determine highest volume threat
        threat_breakdown = {k: v for k, v in counts.items() if k != "Normal" and v > 0}
        top_threat = max(threat_breakdown, key=threat_breakdown.get) if threat_breakdown else "None Detected"

        summary = {
            "total_records": total,
            "normal_count": normal,
            "intrusion_count": intrusions,
            "intrusion_rate_pct": round((intrusions / total) * 100.0, 2) if total > 0 else 0.0,
            "class_distribution": counts,
            "top_threat": top_threat
        }

        return df_result, summary
