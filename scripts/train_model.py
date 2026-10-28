"""
NetGuard-IDS ML Training & Model Evaluation Pipeline.
Trains and compares Random Forest and XGBoost classifiers on network intrusion flows,
evaluates Accuracy, Precision, Recall, F1, Confusion Matrix, and saves best pipeline with Joblib.
Also generates a sample flow CSV for instant dashboard testing.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from core.ml_detector import (
    FEATURE_COLUMNS, CATEGORICAL_FEATURES, NUMERIC_FEATURES,
    ATTACK_MAPPING, CLASSES, MODEL_DIR, MODEL_PATH, ENCODERS_PATH
)

def train_and_evaluate(dataset_csv: str = "data/nsl_kdd_train.csv") -> None:
    """Train Random Forest and XGBoost, compare metrics, and serialize top model."""
    print("=== NetGuard-IDS Machine Learning Training & Benchmark ===")
    print(f"Loading dataset from: {dataset_csv}")
    df = pd.read_csv(dataset_csv)
    print(f"Dataset shape: {df.shape}")

    # Map attack_type to 5 standard classes: Normal, DoS, Probe, R2L, U2R
    if "attack_type" in df.columns:
        df["target_class"] = df["attack_type"].astype(str).str.lower().map(
            lambda x: ATTACK_MAPPING.get(x, "Normal" if "normal" in x else "DoS")
        )
    else:
        raise ValueError("Missing 'attack_type' column in training dataset.")

    print("Class distribution:")
    print(df["target_class"].value_counts())

    X = df[FEATURE_COLUMNS]
    y = df["target_class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"Training split: {len(X_train)} rows | Testing split: {len(X_test)} rows")

    # Define preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )

    # 1. Random Forest Classifier
    rf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1))
    ])

    print("\n[1/2] Training Random Forest Classifier...")
    rf_pipeline.fit(X_train, y_train)
    rf_preds = rf_pipeline.predict(X_test)

    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds, average="weighted", zero_division=0)
    rf_precision = precision_score(y_test, rf_preds, average="weighted", zero_division=0)
    rf_recall = recall_score(y_test, rf_preds, average="weighted", zero_division=0)

    print(f"Random Forest Results -> Accuracy: {rf_acc:.4f} | F1-Score: {rf_f1:.4f} | Precision: {rf_precision:.4f} | Recall: {rf_recall:.4f}")

    # 2. XGBoost Classifier
    # Map target strings to integer codes for XGBoost
    label_to_id = {cls_name: i for i, cls_name in enumerate(CLASSES)}
    id_to_label = {i: cls_name for i, cls_name in enumerate(CLASSES)}
    y_train_xgb = y_train.map(label_to_id).fillna(0).astype(int)
    y_test_xgb = y_test.map(label_to_id).fillna(0).astype(int)

    xgb_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="mlogloss", n_jobs=-1))
    ])

    print("\n[2/2] Training XGBoost Classifier...")
    xgb_pipeline.fit(X_train, y_train_xgb)
    xgb_raw_preds = xgb_pipeline.predict(X_test)
    xgb_preds = [id_to_label[i] for i in xgb_raw_preds]

    xgb_acc = accuracy_score(y_test, xgb_preds)
    xgb_f1 = f1_score(y_test, xgb_preds, average="weighted", zero_division=0)
    xgb_precision = precision_score(y_test, xgb_preds, average="weighted", zero_division=0)
    xgb_recall = recall_score(y_test, xgb_preds, average="weighted", zero_division=0)

    print(f"XGBoost Results       -> Accuracy: {xgb_acc:.4f} | F1-Score: {xgb_f1:.4f} | Precision: {xgb_precision:.4f} | Recall: {xgb_recall:.4f}")

    # Compare and select winning model
    os.makedirs(MODEL_DIR, exist_ok=True)
    if rf_f1 >= xgb_f1:
        best_name = "Random Forest"
        best_pipeline = rf_pipeline
        best_acc, best_f1, best_prec, best_rec = rf_acc, rf_f1, rf_precision, rf_recall
        cm = confusion_matrix(y_test, rf_preds, labels=CLASSES)
        report_str = classification_report(y_test, rf_preds, zero_division=0)
    else:
        best_name = "XGBoost"
        best_pipeline = xgb_pipeline
        best_acc, best_f1, best_prec, best_rec = xgb_acc, xgb_f1, xgb_precision, xgb_recall
        cm = confusion_matrix(y_test, xgb_preds, labels=CLASSES)
        report_str = classification_report(y_test, xgb_preds, zero_division=0)

    print(f"\nWinner: {best_name} with Weighted F1 {best_f1:.4f}!")
    print("\nDetailed Classification Report:")
    print(report_str)

    # Serialize best model and metadata
    joblib.dump(best_pipeline, MODEL_PATH)
    metadata = {
        "best_model": best_name,
        "classes": CLASSES,
        "features": FEATURE_COLUMNS,
        "rf_metrics": {"accuracy": rf_acc, "f1": rf_f1, "precision": rf_precision, "recall": rf_recall},
        "xgb_metrics": {"accuracy": xgb_acc, "f1": xgb_f1, "precision": xgb_precision, "recall": xgb_recall},
        "confusion_matrix": cm.tolist(),
        "report_summary": report_str
    }
    joblib.dump(metadata, ENCODERS_PATH)
    print(f"Saved best model pipeline to: {MODEL_PATH}")
    print(f"Saved model metadata to: {ENCODERS_PATH}")

    # Create bundled sample flow CSV for instant dashboard demo
    sample_df = X_test.copy().head(50)
    sample_df["true_attack_type"] = y_test.head(50).values
    sample_csv_path = "data/sample_network_flows.csv"
    sample_df.to_csv(sample_csv_path, index=False)
    print(f"Created instant demo flow dataset ({len(sample_df)} records) at: {sample_csv_path}")

if __name__ == "__main__":
    train_and_evaluate()
