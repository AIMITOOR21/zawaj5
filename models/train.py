"""Training pipeline for Zawaj.

Trains the XGBoost compatibility model from the synthetic dataset.
For multi-model comparison (XGBoost vs Random Forest vs Logistic Regression),
run models/train_comparison.py instead — that script is for demo purposes.
"""

import pandas as pd
import pickle
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GENERATED_DIR, MODELS_DIR
from data.generate_dataset import generate_dataset
from data.preprocess import prepare_training_data
from models.compatibility_model import CompatibilityModel


def train_all():
    """Generate dataset (if missing) and train the compatibility model."""
    dataset_path = GENERATED_DIR / "couples_dataset.csv"
    if not dataset_path.exists():
        print("Generating synthetic dataset...")
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

    print("\nTraining XGBoost compatibility model...")
    model = CompatibilityModel()
    metrics = model.train(X, y_score, y_label, feature_names=feature_cols)
    print(f"  RMSE: {metrics['rmse']:.2f}")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1-Score: {metrics['f1_score']:.4f}")
    model.save()

    # Save encoders
    with open(MODELS_DIR / "encoders.pkl", "wb") as f:
        pickle.dump({"encoders": encoders, "label_enc": label_enc, "feature_cols": feature_cols}, f)
    print("Encoders saved.")

    print("\n=== Training Complete ===")
    return model, metrics


if __name__ == "__main__":
    train_all()
