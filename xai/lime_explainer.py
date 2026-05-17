"""LIME explainability for local compatibility predictions."""

import numpy as np
import lime.lime_tabular
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_lime_explanation(model, X_train, X_instance, feature_names=None, num_features=10):
    """Generate LIME explanation for a single prediction.

    Args:
        model: Trained CompatibilityModel
        X_train: Training data for background
        X_instance: Single instance to explain (1D array)
        feature_names: List of feature names
        num_features: Number of features to show

    Returns:
        dict with LIME explanation data
    """
    if feature_names is None:
        feature_names = [f"Feature {i}" for i in range(X_train.shape[1])]

    explainer = lime.lime_tabular.LimeTabularExplainer(
        X_train,
        feature_names=feature_names,
        mode="regression",
        random_state=42,
    )

    explanation = explainer.explain_instance(
        X_instance,
        model.regressor.predict,
        num_features=num_features,
    )

    # Extract feature contributions
    feature_weights = explanation.as_list()
    predicted_value = model.predict_score(X_instance.reshape(1, -1))[0]

    return {
        "features": [fw[0] for fw in feature_weights],
        "weights": [fw[1] for fw in feature_weights],
        "predicted_value": float(predicted_value),
        "intercept": float(explanation.intercept[0]) if hasattr(explanation, "intercept") else 0,
    }


def plot_lime_explanation(lime_data):
    """Create Plotly bar chart for LIME explanation."""
    features = lime_data["features"][::-1]
    weights = lime_data["weights"][::-1]

    colors = ["#4CAF50" if w > 0 else "#F44336" for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=features,
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"LIME Explanation (Predicted: {lime_data['predicted_value']:.1f}%)",
        xaxis_title="Feature Contribution",
        yaxis_title="",
        height=400,
        margin=dict(l=250, r=20, t=40, b=40),
        template="plotly_white",
    )
    return fig
