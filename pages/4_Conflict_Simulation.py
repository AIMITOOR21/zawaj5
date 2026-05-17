"""Page 4 — Conflict Simulation.

LLM-based multi-agent simulation of future conflicts between the couple,
with severity and resolution probability.
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS
from ai.conflict_simulation import run_full_simulation, detect_conflicts
from utils.visualization import create_conflict_chart


def page_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Poppins:wght@300;400;500;600&display=swap');
    .stApp {
        background: linear-gradient(135deg, #FDEEF2 0%, #FFFFFF 50%, #FDEEF2 100%);
        background-attachment: fixed;
    }
    .block-container { padding-top: 1.5rem; max-width: 1100px; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #5C2A3E !important; }
    p, div, span, label, .stMarkdown { font-family: 'Poppins', sans-serif; }

    .page-header { text-align: center; padding: 1.5rem 0 0.5rem; animation: fadeIn 0.7s ease-out; }
    .page-title {
        font-family: 'Playfair Display', serif; font-size: 2.8rem; font-weight: 700;
        font-style: italic;
        background: linear-gradient(135deg, #5C2A3E, #D4577A);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0;
    }
    .page-sub { color: #8A6B7A; font-style: italic; font-size: 1rem; margin-top: 0.3rem; }
    .divider-gold {
        width: 120px; height: 2px;
        background: linear-gradient(90deg, transparent, #C9A96E, transparent);
        margin: 1rem auto;
    }
    .conflict-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin: 0.5rem 0;
        box-shadow: 0 3px 10px rgba(212,87,122,0.08);
        border-left: 4px solid #D4577A;
        animation: fadeIn 0.5s ease-out;
    }
    .stButton > button {
        border-radius: 24px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #D4577A, #5C2A3E) !important;
        color: white !important; border: none !important;
        box-shadow: 0 4px 12px rgba(212, 87, 122, 0.3) !important;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Conflict Simulation · Zawaj", page_icon="⚡", layout="wide")
    page_css()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Conflict Simulation</div>
        <div class='divider-gold'></div>
        <div class='page-sub'>Multi-agent AI stress-tests your match</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("assessment_complete"):
        st.warning("⚠️ Please complete the Partner Assessment first.")
        st.stop()

    person_a = st.session_state.person_a
    person_b = st.session_state.person_b
    name_a = st.session_state.person_a_name
    name_b = st.session_state.person_b_name

    with st.expander("⚙️ Settings"):
        use_llm = st.checkbox("Use LLM (requires OpenAI key)", value=True)
        st.caption("When disabled, uses template-based simulation.")

    conflicts = detect_conflicts(person_a, person_b)

    if not conflicts:
        st.success(f"✨ No significant conflicts between {name_a} and {name_b}. Strong alignment across domains!")
        st.balloons()
        return

    st.markdown("### Overview")
    st.plotly_chart(create_conflict_chart(conflicts), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    high = sum(1 for c in conflicts if c["severity"] == "HIGH")
    medium = sum(1 for c in conflicts if c["severity"] == "MEDIUM")
    avg_res = sum(c["resolution_probability"] for c in conflicts) / len(conflicts)
    with c1: st.metric("High Severity", high)
    with c2: st.metric("Medium Severity", medium)
    with c3: st.metric("Avg Resolution", f"{avg_res:.0f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Run Full Simulation", type="primary"):
        with st.spinner("Running multi-agent simulation..."):
            sim = run_full_simulation(person_a, person_b, use_llm=use_llm)
        st.markdown(f"**Summary:** {sim['summary']}")
        st.markdown(f"**Overall Resolution Score:** {sim['overall_resolution_score']:.1f}%")

        for i, s in enumerate(sim["simulations"]):
            c = s["conflict"]
            icon = "🔴" if c["severity"] == "HIGH" else "🟡"
            with st.expander(
                f"{icon} Conflict {i+1}: {c['title']} (Resolution: {c['resolution_probability']:.0f}%)",
                expanded=(i == 0),
            ):
                col1, col2 = st.columns(2)
                with col1: st.markdown(f"**{name_a}:** {c['person_a_value'].replace('_', ' ')}")
                with col2: st.markdown(f"**{name_b}:** {c['person_b_value'].replace('_', ' ')}")
                st.divider()
                st.markdown(s["simulation"])
    else:
        st.markdown("### Detected Conflicts")
        for c in conflicts:
            icon = "🔴" if c["severity"] == "HIGH" else "🟡"
            st.markdown(f"""
            <div class='conflict-card'>
                <b>{icon} {c["title"]}</b>
                <span style='color:#8A6B7A; float:right;'>{c["severity"]}</span>
                <div style='margin-top:0.4rem; font-size:0.9rem; color:#3E3E3E;'>
                    <b style='color:#D4577A;'>{name_a}:</b> {c["person_a_value"].replace("_", " ")} &nbsp;·&nbsp;
                    <b style='color:#8A6B7A;'>{name_b}:</b> {c["person_b_value"].replace("_", " ")}
                </div>
                <div style='color:#8A6B7A; font-size:0.85rem; margin-top:0.3rem; font-style:italic;'>
                    {c["description"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.info("Click **Run Full Simulation** for AI-powered conflict dialogue simulations.")


main()
