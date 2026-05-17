"""Page 5 — Improvement Plan.

Counterfactual XAI (DiCE) + LLM-generated advice showing what small changes
would raise the compatibility score, plus conversation starters.
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS
from xai.counterfactual import generate_counterfactuals, compute_max_potential_score
from ai.advice_generator import generate_compatibility_advice, generate_quick_summary


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
        font-family: 'Playfair Display', serif; font-size: 2.8rem; font-weight: 700; font-style: italic;
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

    .cf-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin: 0.5rem 0;
        box-shadow: 0 3px 10px rgba(212, 87, 122, 0.08);
        border-left: 4px solid #C9A96E;
        animation: fadeIn 0.5s ease-out;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1rem;
        align-items: center;
    }
    .cf-delta {
        background: linear-gradient(135deg, #6BAF73, #4A8C51);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
    }
    .summary-box {
        background: linear-gradient(135deg, #FDEEF2, #FFFFFF);
        border: 1px solid #F8D7DE;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin: 0.6rem 0 1.2rem;
        box-shadow: 0 4px 14px rgba(212, 87, 122, 0.08);
        animation: fadeIn 0.6s ease-out;
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
    st.set_page_config(page_title="Improvement Plan · Zawaj", page_icon="✨", layout="wide")
    page_css()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Improvement Plan</div>
        <div class='divider-gold'></div>
        <div class='page-sub'>Counterfactual AI · What small changes would raise your score?</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("results_computed"):
        st.warning("⚠️ View the Results Dashboard first to compute scores.")
        st.stop()

    person_a = st.session_state.person_a
    person_b = st.session_state.person_b
    name_a = st.session_state.person_a_name
    name_b = st.session_state.person_b_name
    results = st.session_state.results
    conflicts = st.session_state.get("conflicts", [])
    current_score = results["final_score"]

    # Quick summary
    summary = generate_quick_summary(current_score, results["label"], conflicts)
    st.markdown(f"<div class='summary-box'>💫 {summary}</div>", unsafe_allow_html=True)

    # Counterfactuals
    st.markdown("### Counterfactual Suggestions (DiCE)")
    counterfactuals = generate_counterfactuals(person_a, person_b, current_score)

    if not counterfactuals:
        st.success("✨ The couple is highly compatible — no major changes needed!")
    else:
        max_potential = compute_max_potential_score(person_a, person_b, current_score, counterfactuals)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Current Score", f"{current_score:.1f}%")
        with c2: st.metric("Potential Score", f"{max_potential:.1f}%", delta=f"+{max_potential - current_score:.1f}%")
        with c3: st.metric("Changes Suggested", len(counterfactuals))

        st.markdown("<br>", unsafe_allow_html=True)

        for i, cf in enumerate(counterfactuals):
            st.markdown(f"""
            <div class='cf-card'>
                <div>
                    <div style='color:#5C2A3E; font-weight:600; font-size:1rem; margin-bottom:0.3rem;'>
                        {i+1}. {cf["change"]}
                    </div>
                    <div style='color:#8A6B7A; font-size:0.82rem;'>
                        Changes: <b>{cf["who_changes"]}</b> &nbsp;·&nbsp; Feasibility: <b>{cf["feasibility"]}</b>
                    </div>
                </div>
                <div class='cf-delta'>+{cf["improvement"]:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    # LLM Advice
    st.markdown("### AI-Generated Improvement Plan")

    if st.button("✨ Generate Detailed Advice", type="primary"):
        with st.spinner("Generating personalized guidance..."):
            advice = generate_compatibility_advice(results, conflicts, counterfactuals)
        st.markdown("---")
        st.markdown(advice)
        from config import OPENAI_API_KEY
        if OPENAI_API_KEY:
            st.caption("✨ Powered by OpenAI GPT")
        else:
            st.caption("✨ Template-based advice — add OPENAI_API_KEY for personalized AI")
    else:
        st.info("Click above to generate a detailed, AI-powered improvement plan with specific action items.")

    # Conversation starters
    st.markdown("### Suggested Conversation Starters")
    if conflicts:
        for c in conflicts[:5]:
            with st.expander(f"💬 Discuss: {c['title']}"):
                for starter in _get_starters(c, name_a, name_b):
                    st.markdown(f"- {starter}")
    else:
        st.success("No major conflicts — couple is well-aligned!")


def _get_starters(conflict, name_a, name_b):
    domain = conflict["domain"]
    starters = {
        "career": [
            f"'{name_a}, how do you see your career in 5 years? {name_b}, how do you see yours?'",
            "'If one of us gets a great job opportunity that requires sacrifice from the other, how would we handle it?'",
        ],
        "location": [
            "'Where do we both see ourselves living in 5-10 years?'",
            "'How important is living near our families to each of us?'",
        ],
        "family_structure": [
            "'How do we feel about joint family living after marriage?'",
            "'What boundaries are important to us in terms of family involvement?'",
        ],
        "children": [
            "'Do we both want children? If so, when and how many?'",
            "'How would we share parenting responsibilities?'",
        ],
        "roles": [
            "'How do we divide household responsibilities fairly?'",
            "'Who makes the big decisions — together or individually?'",
        ],
        "finances": [
            "'Joint or separate bank accounts?'",
            "'What are our savings goals and spending priorities?'",
        ],
        "religion": [
            "'How important is shared religious practice to each of us?'",
            "'What role should religion play in our children's upbringing?'",
        ],
    }
    return starters.get(domain, [
        "'Let us discuss expectations openly without judgment.'",
        "'What compromise would make both of us comfortable?'",
    ])


main()
