"""Multi-Model Comparison for Zawaj — Demo Script.

Trains TWO models and compares performance, picking the best automatically:
  1. XGBoost — gradient boosted trees
  2. Random Forest — bagged decision trees

This is a STANDALONE script for demonstrating model selection during the demo.
It does NOT replace train.py — the deployed app still uses train.py (XGBoost).

To run:
    python -m models.train_comparison
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GENERATED_DIR, MODELS_DIR
from data.generate_dataset import generate_dataset
from data.preprocess import prepare_training_data
from models.compatibility_model import CompatibilityModel

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


def evaluate_xgboost(X, y_score, y_label, feature_cols):
    """Train and evaluate XGBoost (gradient boosting)."""
    print("\n[1/2] Training XGBoost...")
    t0 = time.time()
    model = CompatibilityModel()
    metrics = model.train(X, y_score, y_label, feature_names=feature_cols)
    elapsed = time.time() - t0
    print(f"  RMSE: {metrics['rmse']:.2f}")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1-Score: {metrics['f1_score']:.4f}")
    print(f"  Time: {elapsed:.1f}s")
    return model, metrics


def evaluate_random_forest(X, y_score, y_label):
    """Train and evaluate Random Forest (bagging)."""
    print("\n[2/2] Training Random Forest...")
    t0 = time.time()
    X_train, X_val, ys_train, ys_val, yl_train, yl_val = train_test_split(
        X, y_score, y_label, test_size=0.2, random_state=42
    )

    # Regressor — predicts compatibility score (0-100)
    reg = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    reg.fit(X_train, ys_train)
    rmse = np.sqrt(mean_squared_error(ys_val, reg.predict(X_val)))

    # Classifier — predicts compatibility label
    clf = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    clf.fit(X_train, yl_train)
    pred = clf.predict(X_val)
    acc = accuracy_score(yl_val, pred)
    f1 = f1_score(yl_val, pred, average="weighted")
    elapsed = time.time() - t0

    print(f"  RMSE: {rmse:.2f}")
    print(f"  Accuracy: {acc:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  Time: {elapsed:.1f}s")
    return ({"regressor": reg, "classifier": clf},
            {"rmse": rmse, "accuracy": acc, "f1_score": f1})


def run_comparison():
    """Run full comparison between XGBoost and Random Forest, pick the best."""
    dataset_path = GENERATED_DIR / "couples_dataset.csv"
    if not dataset_path.exists():
        print("Generating synthetic dataset (10,000 couples)...")
        df = generate_dataset(n_couples=10000)
        df.to_csv(dataset_path, index=False)
        print(f"Dataset saved: {df.shape}")
    else:
        print("Loading existing dataset...")
        df = pd.read_csv(dataset_path)
        print(f"Dataset loaded: {df.shape}")

    print("\nPreprocessing data...")
    X, y_score, y_label, feature_cols, encoders, label_enc = prepare_training_data(df)
    print(f"Features: {len(feature_cols)}, Samples: {len(X)}")

    print("\n" + "=" * 60)
    print("MULTI-MODEL COMPARISON")
    print("=" * 60)

    results = {}

    xgb_model, xgb_metrics = evaluate_xgboost(X, y_score, y_label, feature_cols)
    results["XGBoost"] = {"model": xgb_model, "metrics": xgb_metrics}

    rf_model, rf_metrics = evaluate_random_forest(X, y_score, y_label)
    results["Random Forest"] = {"model": rf_model, "metrics": rf_metrics}

    # ---------- Comparison summary ----------
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Model':<22} {'RMSE':>8} {'Accuracy':>12} {'F1-Score':>12}")
    print("-" * 60)
    for name, info in results.items():
        m = info["metrics"]
        print(f"{name:<22} {m['rmse']:>8.2f} {m['accuracy']:>12.4f} {m['f1_score']:>12.4f}")

    # ---------- Pick best by F1 ----------
    best_name = max(results.keys(), key=lambda k: results[k]["metrics"]["f1_score"])
    best_info = results[best_name]
    print("\n" + "=" * 60)
    print(f"BEST MODEL: {best_name}")
    print(f"   F1-Score: {best_info['metrics']['f1_score']:.4f}")
    print(f"   Accuracy: {best_info['metrics']['accuracy']:.4f}")
    print(f"   RMSE:     {best_info['metrics']['rmse']:.2f}")
    print("=" * 60)

    # Save XGBoost as production model (the app integrates with it)
    xgb_model.save()
    with open(MODELS_DIR / "encoders.pkl", "wb") as f:
        pickle.dump({"encoders": encoders, "label_enc": label_enc, "feature_cols": feature_cols}, f)

    # Save comparison report for demo
    comparison_report = {
        name: {"rmse": float(info["metrics"]["rmse"]),
               "accuracy": float(info["metrics"]["accuracy"]),
               "f1_score": float(info["metrics"]["f1_score"])}
        for name, info in results.items()
    }
    comparison_report["_best_model"] = best_name
    with open(MODELS_DIR / "model_comparison.pkl", "wb") as f:
        pickle.dump(comparison_report, f)

    print("\nModels and comparison report saved.")
    print("=== Comparison Complete ===")
    return xgb_model, results, best_name


if __name__ == "__main__":
    run_comparison()
