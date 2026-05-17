"""XGBoost-based individual compatibility scoring model."""

import numpy as np
import pickle
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR


class CompatibilityModel:
    """XGBoost model for predicting individual compatibility scores."""

    def __init__(self):
        self.regressor = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        self.classifier = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="mlogloss",
        )
        self.feature_names = None
        self.is_trained = False

    def train(self, X, y_score, y_label, feature_names=None):
        """Train both regressor and classifier."""
        self.feature_names = feature_names
        X_train, X_val, ys_train, ys_val, yl_train, yl_val = train_test_split(
            X, y_score, y_label, test_size=0.2, random_state=42
        )

        # Train regressor
        self.regressor.fit(X_train, ys_train)
        score_pred = self.regressor.predict(X_val)
        rmse = np.sqrt(mean_squared_error(ys_val, score_pred))

        # Train classifier
        self.classifier.fit(X_train, yl_train)
        label_pred = self.classifier.predict(X_val)
        acc = accuracy_score(yl_val, label_pred)
        f1 = f1_score(yl_val, label_pred, average="weighted")

        self.is_trained = True
        return {"rmse": rmse, "accuracy": acc, "f1_score": f1}

    def predict_score(self, X):
        """Predict compatibility score (0-100)."""
        score = self.regressor.predict(X)
        return np.clip(score, 0, 100)

    def predict_label(self, X):
        """Predict compatibility label."""
        return self.classifier.predict(X)

    def predict_proba(self, X):
        """Predict class probabilities."""
        return self.classifier.predict_proba(X)

    def save(self, path=None):
        """Save model to disk."""
        path = path or MODELS_DIR / "compatibility_model.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path=None):
        """Load model from disk."""
        path = path or MODELS_DIR / "compatibility_model.pkl"
        with open(path, "rb") as f:
            return pickle.load(f)
