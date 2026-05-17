"""Page 3 — Results Dashboard.

Comprehensive compatibility view combining partner alignment, in-law triangle
analysis, and conflict resolution — with XAI (SHAP, LIME) explanations.
"""

import streamlit as st
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS, MODELS_DIR
from utils.scoring import (
    compute_domain_alignment, compute_weighted_score,
    compute_personality_compatibility, get_score_color,
)
from utils.visualization import (
    create_gauge_chart, create_domain_radar, create_domain_bar_chart,
    create_ensemble_breakdown, create_personality_chart,
)
from models.ensemble import compute_ensemble_score
from ai.conflict_simulation import detect_conflicts


def page_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Poppins:wght@300;400;500;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #FDEEF2 0%, #FFFFFF 50%, #FDEEF2 100%);
        background-attachment: fixed;
    }
    .block-container { padding-top: 1.5rem; max-width: 1150px; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #5C2A3E !important; }
    p, div, span, label, .stMarkdown { font-family: 'Poppins', sans-serif; }

    .page-header { text-align: center; padding: 1.5rem 0 0.5rem; animation: fadeInDown 0.7s ease-out; }
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        font-style: italic;
        background: linear-gradient(135deg, #5C2A3E, #D4577A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    .page-sub { color: #8A6B7A; font-style: italic; font-size: 1rem; margin-top: 0.3rem; }
    .divider-gold {
        width: 120px; height: 2px;
        background: linear-gradient(90deg, transparent, #C9A96E, transparent);
        margin: 1rem auto;
    }

    .score-card {
        background: white;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        box-shadow: 0 8px 28px rgba(212, 87, 122, 0.15);
        text-align: center;
        animation: fadeInUp 0.7s ease-out;
    }
    .score-huge {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #5C2A3E, #D4577A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .score-label {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: -0.5rem;
    }
    .couple-names {
        color: #8A6B7A;
        font-style: italic;
        font-size: 1.05rem;
    }

    .metric-tile {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border-top: 3px solid #D4577A;
        box-shadow: 0 3px 12px rgba(212, 87, 122, 0.08);
        animation: fadeInUp 0.6s ease-out both;
    }
    .metric-tile .label {
        color: #8A6B7A; font-size: 0.8rem;
        text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;
    }
    .metric-tile .value {
        font-family: 'Playfair Display', serif;
        font-size: 2rem; color: #5C2A3E; font-weight: 700; margin-top: 0.2rem;
    }

    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #5C2A3E;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #F8D7DE;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 0.55rem 1.3rem;
        color: #8A6B7A;
        border: 1px solid #F8D7DE;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4577A, #5C2A3E) !important;
        color: white !important;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .domain-row {
        background: white;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin: 0.4rem 0;
        box-shadow: 0 2px 6px rgba(212, 87, 122, 0.06);
        display: grid;
        grid-template-columns: 2fr 2fr 2fr 1fr;
        gap: 1rem;
        align-items: center;
    }
    .conflict-pill {
        background: white;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 8px rgba(212, 87, 122, 0.08);
        border-left: 3px solid #D4577A;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Results · Zawaj", page_icon="💖", layout="wide")
    page_css()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Results Dashboard</div>
        <div class='divider-gold'></div>
        <div class='page-sub'>Your complete compatibility story — powered by AI</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("assessment_complete"):
        st.warning("⚠️ Please complete the Partner Assessment first.")
        st.stop()

    person_a = st.session_state.person_a
    person_b = st.session_state.person_b
    name_a = st.session_state.person_a_name
    name_b = st.session_state.person_b_name

    # Scores
    domain_scores = compute_domain_alignment(person_a, person_b)
    individual_score = compute_weighted_score(domain_scores)
    personality_scores = compute_personality_compatibility(person_a, person_b)

    inlaw_score = st.session_state.get("inlaw_score")
    if inlaw_score is None:
        inlaw_score = 55.0  # neutral default if in-laws not filled
        inlaw_pending = True
    else:
        inlaw_pending = False

    conflicts = detect_conflicts(person_a, person_b)
    resolution_score = (np.mean([c["resolution_probability"] for c in conflicts])
                        if conflicts else 85.0)

    results = compute_ensemble_score(individual_score, inlaw_score, resolution_score)

    st.session_state.results = results
    st.session_state.conflicts = conflicts
    st.session_state.domain_scores = domain_scores
    st.session_state.results_computed = True

    # ---------- Top: score + breakdown ----------
    color = get_score_color(results["final_score"])

    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.markdown(f"""
        <div class='score-card'>
            <div style='color:#8A6B7A; font-size:0.78rem; letter-spacing:3px;
                        text-transform:uppercase; font-weight:600;'>
                Overall Compatibility
            </div>
            <div class='score-huge'>{results["final_score"]:.1f}%</div>
            <div class='score-label' style='color:{color};'>{results["label"]}</div>
            <div class='couple-names'>{name_a} &nbsp;·&nbsp; {name_b}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        fig_gauge = create_gauge_chart(results["final_score"])
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        fig_ens = create_ensemble_breakdown(results["breakdown"])
        st.plotly_chart(fig_ens, use_container_width=True)

        # Metric tiles
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='metric-tile'>
                <div class='label'>Partner Alignment</div>
                <div class='value'>{individual_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            extra = " ⓘ" if inlaw_pending else ""
            st.markdown(f"""
            <div class='metric-tile'>
                <div class='label'>In-Law Alignment{extra}</div>
                <div class='value'>{inlaw_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='metric-tile'>
                <div class='label'>Conflict Resolution</div>
                <div class='value'>{resolution_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        if inlaw_pending:
            st.caption("⚠️ In-Law Alignment is a placeholder (55%). Complete the In-Laws Questionnaire for your real score.")

    st.markdown("<div class='section-title'>Domain Compatibility</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🕸️ Radar", "📊 Bar"])
    with tab1:
        st.plotly_chart(create_domain_radar(domain_scores), use_container_width=True)
    with tab2:
        st.plotly_chart(create_domain_bar_chart(domain_scores), use_container_width=True)

    # Detailed table
    st.markdown("<div class='section-title'>Detailed Breakdown</div>", unsafe_allow_html=True)
    for domain, score in domain_scores.items():
        val_a = str(person_a.get(domain, "N/A")).replace("_", " ").title()
        val_b = str(person_b.get(domain, "N/A")).replace("_", " ").title()
        c = get_score_color(score)
        st.markdown(f"""
        <div class='domain-row'>
            <div style='font-weight:600; color:#5C2A3E;'>{domain.replace("_", " ").title()}</div>
            <div style='color:#3E3E3E;'><b style='color:#D4577A;'>{name_a}:</b> {val_a}</div>
            <div style='color:#3E3E3E;'><b style='color:#8A6B7A;'>{name_b}:</b> {val_b}</div>
            <div style='color:{c}; font-weight:700; font-family:"Playfair Display", serif;
                        font-size:1.2rem; text-align:right;'>{score:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------- Personality ----------
    st.markdown("<div class='section-title'>Personality Compatibility</div>", unsafe_allow_html=True)
    st.plotly_chart(create_personality_chart(personality_scores), use_container_width=True)

    # ---------- XAI ----------
    st.markdown("<div class='section-title'>Explainable AI (SHAP · LIME)</div>", unsafe_allow_html=True)

    if (MODELS_DIR / "compatibility_model.pkl").exists():
        try:
            from models.compatibility_model import CompatibilityModel
            from data.preprocess import prepare_training_data
            import pandas as pd
            from config import GENERATED_DIR

            model = CompatibilityModel.load()
            df = pd.read_csv(GENERATED_DIR / "couples_dataset.csv")
            X, y_score, y_label, feature_cols, encoders, label_enc = prepare_training_data(df)

            tab_shap, tab_lime = st.tabs(["SHAP (Global)", "LIME (Local)"])

            with tab_shap:
                with st.spinner("Computing SHAP values..."):
                    from xai.shap_explainer import get_shap_explanations, plot_global_shap, plot_local_shap
                    shap_data = get_shap_explanations(model, X, feature_cols)
                    st.plotly_chart(plot_global_shap(shap_data), use_container_width=True)
                    st.caption("Which features matter most across all predictions.")
                    st.plotly_chart(plot_local_shap(shap_data), use_container_width=True)
                    st.caption("How features affect this specific prediction.")

            with tab_lime:
                with st.spinner("Computing LIME..."):
                    from xai.lime_explainer import get_lime_explanation, plot_lime_explanation
                    sample = X[0]
                    lime_data = get_lime_explanation(model, X[:200], sample, feature_cols)
                    st.plotly_chart(plot_lime_explanation(lime_data), use_container_width=True)
                    st.caption("Which features most influenced this prediction.")
        except Exception as e:
            st.error(f"Could not load XAI explanations: {e}")
    else:
        st.info("Models not yet trained. Reload the app to auto-train.")

    # ---------- Conflicts ----------
    if conflicts:
        st.markdown("<div class='section-title'>Detected Conflicts</div>", unsafe_allow_html=True)
        for c in conflicts:
            icon = "🔴" if c["severity"] == "HIGH" else "🟡"
            st.markdown(f"""
            <div class='conflict-pill'>
                <b>{icon} {c["title"]}</b> &nbsp;·&nbsp;
                <span style='color:#8A6B7A;'>Severity: {c["severity"]} · Resolution: {c["resolution_probability"]:.0f}%</span>
                <br>
                <span style='color:#3E3E3E; font-size:0.9rem;'>
                    <b style='color:#D4577A;'>{name_a}:</b> {c["person_a_value"].replace("_", " ")}
                    &nbsp;·&nbsp;
                    <b style='color:#8A6B7A;'>{name_b}:</b> {c["person_b_value"].replace("_", " ")}
                </span>
            </div>
            """, unsafe_allow_html=True)


main()
