"""SHAP explainability for compatibility predictions."""

import numpy as np
import shap
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_shap_explanations(model, X, feature_names=None, sample_idx=0):
    """Compute SHAP values for the compatibility model.

    Args:
        model: Trained CompatibilityModel
        X: Feature matrix
        feature_names: List of feature names
        sample_idx: Index of sample to explain locally

    Returns:
        dict with global and local SHAP data
    """
    # Use TreeExplainer for XGBoost
    explainer = shap.TreeExplainer(model.regressor)

    # Sample background data for efficiency
    n_background = min(100, len(X))
    bg_indices = np.random.choice(len(X), n_background, replace=False)

    shap_values = explainer.shap_values(X[bg_indices])

    # Global feature importance
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    if feature_names is None:
        feature_names = [f"Feature {i}" for i in range(X.shape[1])]

    # Sort by importance
    sorted_idx = np.argsort(mean_abs_shap)[::-1]
    top_n = min(15, len(sorted_idx))

    global_importance = {
        "features": [feature_names[i] for i in sorted_idx[:top_n]],
        "importance": [float(mean_abs_shap[i]) for i in sorted_idx[:top_n]],
    }

    # Local explanation for specific sample
    local_idx = min(sample_idx, len(bg_indices) - 1)
    local_shap = shap_values[local_idx]
    local_sorted = np.argsort(np.abs(local_shap))[::-1][:10]

    local_explanation = {
        "features": [feature_names[i] for i in local_sorted],
        "shap_values": [float(local_shap[i]) for i in local_sorted],
        "feature_values": [float(X[bg_indices[local_idx], i]) for i in local_sorted],
    }

    return {
        "global": global_importance,
        "local": local_explanation,
        "base_value": float(explainer.expected_value),
    }


def plot_global_shap(shap_data):
    """Create Plotly bar chart for global SHAP feature importance."""
    features = shap_data["global"]["features"][::-1]
    importance = shap_data["global"]["importance"][::-1]

    fig = go.Figure(go.Bar(
        x=importance,
        y=features,
        orientation="h",
        marker_color="#6D2E46",
    ))
    fig.update_layout(
        title="Global Feature Importance (SHAP)",
        xaxis_title="Mean |SHAP Value|",
        yaxis_title="",
        height=400,
        margin=dict(l=200, r=20, t=40, b=40),
        template="plotly_white",
    )
    return fig


def plot_local_shap(shap_data):
    """Create Plotly waterfall chart for local SHAP explanation."""
    features = shap_data["local"]["features"]
    values = shap_data["local"]["shap_values"]

    colors = ["#4CAF50" if v > 0 else "#F44336" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"Local Explanation (Base: {shap_data['base_value']:.1f})",
        xaxis_title="SHAP Value (Impact on Score)",
        yaxis_title="",
        height=350,
        margin=dict(l=200, r=20, t=40, b=40),
        template="plotly_white",
    )
    return fig
