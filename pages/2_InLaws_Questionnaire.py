"""Page 2 — In-Laws Questionnaire (Extended).

Now collects family data from BOTH sides — girl's family AND boy's family.
Includes optional toggles for brother / sister presence on each side.
Visual theme preserved (Pink Wedding).
"""

import streamlit as st
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS, DATA_DIR
from ai.inlaw_analysis import build_triangle_analysis


# ---------- Quick form questions for additional family members ----------
# These are simple, fast trait-based questions used for girl's family + brothers.
# Boy's parents and sister continue to use the existing scenario file.

QUICK_FAMILY_QUESTIONS = {
    "mother": [
        {"id": "conservatism", "topic": "Cultural outlook",
         "question": "How would you describe her cultural outlook?",
         "choices": [
             {"text": "Very modern — open to all lifestyles", "value": "modern", "score": 1.0},
             {"text": "Balanced — modern but values tradition", "value": "balanced", "score": 0.7},
             {"text": "Mostly traditional", "value": "mostly_traditional", "score": 0.4},
             {"text": "Strictly traditional", "value": "strict", "score": 0.1},
         ]},
        {"id": "career_support", "topic": "Working after marriage",
         "question": "Her stance on the bride continuing her career after marriage?",
         "choices": [
             {"text": "Fully supportive", "value": "fully_supportive", "score": 1.0},
             {"text": "Supportive with conditions", "value": "conditional", "score": 0.65},
             {"text": "Acceptable only before children", "value": "until_children", "score": 0.35},
             {"text": "Prefers homemaker role", "value": "homemaker", "score": 0.1},
         ]},
        {"id": "influence", "topic": "Household influence",
         "question": "How much influence will she have on the couple's daily life?",
         "choices": [
             {"text": "Low — gives them space", "value": "low", "score": 1.0},
             {"text": "Moderate — guidance when asked", "value": "moderate", "score": 0.7},
             {"text": "High — actively involved", "value": "high", "score": 0.4},
             {"text": "Very high — daily involvement", "value": "very_high", "score": 0.1},
         ]},
        {"id": "warmth", "topic": "Warmth toward the spouse",
         "question": "Expected warmth toward the new son/daughter-in-law?",
         "choices": [
             {"text": "Treats like own child", "value": "warm", "score": 1.0},
             {"text": "Friendly and welcoming", "value": "friendly", "score": 0.75},
             {"text": "Polite but reserved", "value": "reserved", "score": 0.4},
             {"text": "Cold or distant", "value": "cold", "score": 0.1},
         ]},
    ],
    "father": [
        {"id": "conservatism", "topic": "Cultural outlook",
         "question": "How would you describe his cultural outlook?",
         "choices": [
             {"text": "Very modern", "value": "modern", "score": 1.0},
             {"text": "Balanced", "value": "balanced", "score": 0.7},
             {"text": "Mostly traditional", "value": "mostly_traditional", "score": 0.4},
             {"text": "Strictly traditional", "value": "strict", "score": 0.1},
         ]},
        {"id": "authority", "topic": "Decision-making style",
         "question": "His approach to family decisions?",
         "choices": [
             {"text": "Lets couple decide independently", "value": "independent", "score": 1.0},
             {"text": "Advises when asked", "value": "advisory", "score": 0.75},
             {"text": "Expects to be consulted", "value": "consulted", "score": 0.45},
             {"text": "Final authority on major matters", "value": "authoritative", "score": 0.15},
         ]},
        {"id": "financial_support", "topic": "Financial outlook",
         "question": "View on the couple's financial independence?",
         "choices": [
             {"text": "Fully independent finances", "value": "independent", "score": 1.0},
             {"text": "Mostly independent, some pooling", "value": "mostly_independent", "score": 0.7},
             {"text": "Shared household finances", "value": "shared", "score": 0.45},
             {"text": "Father manages joint finances", "value": "father_manages", "score": 0.1},
         ]},
        {"id": "religion", "topic": "Religious expectations",
         "question": "His expectation of religious practice in the couple's home?",
         "choices": [
             {"text": "Personal choice", "value": "personal", "score": 1.0},
             {"text": "Encouraged but not enforced", "value": "encouraged", "score": 0.7},
             {"text": "Expected — household-wide", "value": "expected", "score": 0.4},
             {"text": "Strict — non-negotiable", "value": "strict", "score": 0.1},
         ]},
    ],
    "brother": [
        {"id": "support", "topic": "Support for the marriage",
         "question": "His attitude toward the marriage?",
         "choices": [
             {"text": "Fully supportive", "value": "fully_supportive", "score": 1.0},
             {"text": "Cautiously supportive", "value": "cautious", "score": 0.65},
             {"text": "Neutral", "value": "neutral", "score": 0.45},
             {"text": "Skeptical or against", "value": "against", "score": 0.1},
         ]},
        {"id": "involvement", "topic": "Involvement in couple's life",
         "question": "Expected involvement in the couple's daily affairs?",
         "choices": [
             {"text": "Gives them space", "value": "minimal", "score": 1.0},
             {"text": "Occasional check-ins", "value": "occasional", "score": 0.75},
             {"text": "Regular involvement", "value": "regular", "score": 0.45},
             {"text": "Very involved — opinions on everything", "value": "high", "score": 0.15},
         ]},
        {"id": "warmth", "topic": "Warmth toward the spouse",
         "question": "Likely relationship with the new spouse?",
         "choices": [
             {"text": "Warm — like family", "value": "warm", "score": 1.0},
             {"text": "Friendly", "value": "friendly", "score": 0.75},
             {"text": "Polite but distant", "value": "distant", "score": 0.4},
             {"text": "Cold or hostile", "value": "cold", "score": 0.1},
         ]},
    ],
    "sister": [
        {"id": "support", "topic": "Support for the marriage",
         "question": "Her attitude toward the marriage?",
         "choices": [
             {"text": "Fully supportive", "value": "fully_supportive", "score": 1.0},
             {"text": "Cautiously supportive", "value": "cautious", "score": 0.65},
             {"text": "Neutral", "value": "neutral", "score": 0.45},
             {"text": "Skeptical or against", "value": "against", "score": 0.1},
         ]},
        {"id": "involvement", "topic": "Involvement in couple's life",
         "question": "Expected involvement in the couple's daily affairs?",
         "choices": [
             {"text": "Gives them space", "value": "minimal", "score": 1.0},
             {"text": "Occasional check-ins", "value": "occasional", "score": 0.75},
             {"text": "Regular involvement", "value": "regular", "score": 0.45},
             {"text": "Very involved — opinions on everything", "value": "high", "score": 0.15},
         ]},
        {"id": "warmth", "topic": "Warmth toward the spouse",
         "question": "Likely relationship with the new spouse?",
         "choices": [
             {"text": "Warm — like family", "value": "warm", "score": 1.0},
             {"text": "Friendly", "value": "friendly", "score": 0.75},
             {"text": "Polite but distant", "value": "distant", "score": 0.4},
             {"text": "Cold or hostile", "value": "cold", "score": 0.1},
         ]},
    ],
}


def load_inlaw_scenarios():
    with open(DATA_DIR / "inlaw_scenarios.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- CSS (unchanged — same pink wedding theme) ----------

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

    .role-intro {
        background: linear-gradient(135deg, #FDEEF2, #FFFFFF);
        padding: 1.2rem 1.4rem;
        border-radius: 16px;
        border: 1px solid #F8D7DE;
        margin-bottom: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }
    .role-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        color: #5C2A3E;
        font-weight: 600;
        margin: 0;
    }
    .role-sub {
        color: #8A6B7A;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: 0.2rem;
    }

    .q-tile {
        background: white;
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin: 0.7rem 0;
        border: 1px solid #F8D7DE;
        box-shadow: 0 2px 8px rgba(212, 87, 122, 0.06);
        transition: all 0.3s ease;
        animation: fadeInUp 0.4s ease-out;
    }
    .q-tile:hover { box-shadow: 0 4px 14px rgba(212, 87, 122, 0.12); }
    .q-topic {
        color: #D4577A;
        font-size: 0.72rem;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .q-text {
        color: #5C2A3E;
        font-size: 1.02rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }

    .setup-card {
        background: linear-gradient(135deg, #FDEEF2, #FFFFFF);
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        border: 1.5px solid #F8D7DE;
        margin: 1rem 0;
        box-shadow: 0 4px 14px rgba(212, 87, 122, 0.1);
    }

    .verdict-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 2px solid #F8D7DE;
        box-shadow: 0 8px 28px rgba(212, 87, 122, 0.15);
        animation: fadeInUp 0.6s ease-out;
        margin: 1rem 0;
    }
    .verdict-score {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }

    .contra-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin: 0.6rem 0;
        border-left: 4px solid #D4577A;
        box-shadow: 0 2px 8px rgba(212, 87, 122, 0.08);
    }
    .contra-high { border-left-color: #D4577A; }
    .contra-medium { border-left-color: #E8A846; }
    .contra-low { border-left-color: #6BAF73; }
    .contra-severity-high {
        background: #D4577A; color: white;
        padding: 0.15rem 0.7rem; border-radius: 20px;
        font-size: 0.72rem; font-weight: 600;
    }
    .contra-severity-medium {
        background: #E8A846; color: white;
        padding: 0.15rem 0.7rem; border-radius: 20px;
        font-size: 0.72rem; font-weight: 600;
    }
    .contra-severity-low {
        background: #6BAF73; color: white;
        padding: 0.15rem 0.7rem; border-radius: 20px;
        font-size: 0.72rem; font-weight: 600;
    }

    .stButton > button {
        border-radius: 24px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #D4577A, #5C2A3E) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(212, 87, 122, 0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #D4577A !important;
        border: 1.5px solid #F8D7DE !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 1.2rem;
        color: #8A6B7A;
        border: 1px solid #F8D7DE;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4577A, #5C2A3E) !important;
        color: white !important;
    }

    /* Fix expander text visibility */
    [data-testid="stExpander"] details summary,
    [data-testid="stExpander"] details summary p,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    .streamlit-expanderHeader,
    .streamlit-expanderHeader p {
        color: #5C2A3E !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }
    [data-testid="stExpander"] {
        background: white !important;
        border: 1px solid #F8D7DE !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
    }
    [data-testid="stExpander"] details summary:hover {
        background: #FDEEF2 !important;
    }

    /* Fix checkbox label visibility */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label p,
    [data-testid="stCheckbox"] label span,
    .stCheckbox label,
    .stCheckbox label p {
        color: #3E3E3E !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }

    /* Fix markdown text inside expanders */
    [data-testid="stExpander"] .stMarkdown,
    [data-testid="stExpander"] .stMarkdown p,
    [data-testid="stExpander"] .stMarkdown strong,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #3E3E3E !important;
        opacity: 1 !important;
    }
    [data-testid="stExpander"] strong,
    [data-testid="stExpander"] b {
        color: #5C2A3E !important;
        font-weight: 600 !important;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)


# ---------- Generic question renderer ----------

def render_questions(questions, storage_dict, key_prefix):
    """Render multiple-choice questions that persist into storage_dict."""
    for q in questions:
        qid = q["id"]
        current = storage_dict.get(qid)
        with st.container():
            st.markdown(f"""
            <div class='q-tile'>
                <div class='q-topic'>{q['topic']}</div>
                <div class='q-text'>{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            for i, choice in enumerate(q["choices"]):
                is_selected = current == choice["value"]
                col_btn, col_txt = st.columns([0.08, 0.92])
                with col_btn:
                    if st.button(
                        "✓" if is_selected else chr(65 + i),
                        key=f"{key_prefix}_{qid}_{i}",
                        type="primary" if is_selected else "secondary",
                    ):
                        storage_dict[qid] = choice["value"]
                        st.rerun()
                with col_txt:
                    color = "#5C2A3E" if is_selected else "#3E3E3E"
                    weight = "600" if is_selected else "400"
                    st.markdown(
                        f"<div style='padding-top:0.35rem; color:{color}; font-weight:{weight};'>{choice['text']}</div>",
                        unsafe_allow_html=True,
                    )


def compute_family_score(responses, questions):
    """Average the scores of answered questions."""
    if not responses:
        return None
    scores = []
    for q in questions:
        v = responses.get(q["id"])
        if v is None:
            continue
        for c in q["choices"]:
            if c["value"] == v:
                scores.append(c["score"])
                break
    if not scores:
        return None
    return round(sum(scores) / len(scores) * 100, 1)


# ---------- Main ----------

def main():
    st.set_page_config(page_title="Family Profile · Zawaj", page_icon="👨‍👩‍👧", layout="wide")
    page_css()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Family Profile</div>
        <div class='divider-gold'></div>
        <div class='page-sub'>Both families · Member-by-member · Optional siblings</div>
    </div>
    """, unsafe_allow_html=True)

    name_a = st.session_state.get("person_a_name", "Sara")
    name_b = st.session_state.get("person_b_name", "Ahmed")

    # ---------- Family setup ----------
    setup = st.session_state.setdefault("family_setup", {
        "girl_has_brother": True, "girl_has_sister": True,
        "boy_has_brother": True, "boy_has_sister": True,
    })

    with st.expander("⚙️ Family Setup — toggle which siblings exist", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{name_a}'s family**")
            setup["girl_has_brother"] = st.checkbox(
                f"{name_a} has a brother", value=setup["girl_has_brother"], key="gb")
            setup["girl_has_sister"] = st.checkbox(
                f"{name_a} has a sister", value=setup["girl_has_sister"], key="gs")
        with col2:
            st.markdown(f"**{name_b}'s family**")
            setup["boy_has_brother"] = st.checkbox(
                f"{name_b} has a brother", value=setup["boy_has_brother"], key="bb")
            setup["boy_has_sister"] = st.checkbox(
                f"{name_b} has a sister", value=setup["boy_has_sister"], key="bs")
        st.session_state.family_setup = setup

    # ---------- Storage ----------
    girl_family = st.session_state.setdefault("girl_family", {
        "mother": {}, "father": {}, "brother": {}, "sister": {}
    })
    boy_family = st.session_state.setdefault("boy_family", {
        "brother": {}  # boy's mother/father/sister still use scenario-based existing storage
    })
    # legacy storage (kept for triangle analysis)
    inlaw_responses = st.session_state.setdefault("inlaw_responses", {})
    boy_claims = st.session_state.setdefault("boy_claims", {})
    girl_expectations = st.session_state.setdefault("girl_expectations", {})

    scenarios = load_inlaw_scenarios()

    # ---------- Tabs ----------
    tab_labels = [f"👰 {name_a}'s Family", f"🤵 {name_b}'s Family",
                  "💬 Claims vs Hopes", "🔺 Final Analysis"]
    tab_girl, tab_boy, tab_claims, tab_result = st.tabs(tab_labels)

    # ---------- GIRL'S FAMILY ----------
    with tab_girl:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>{name_a}'s Family</div>
            <div class='role-sub'>Profile each member individually. Sibling sections appear if enabled above.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"👩 {name_a}'s Mother", expanded=True):
            render_questions(QUICK_FAMILY_QUESTIONS["mother"],
                             girl_family["mother"], "gmom")
            score = compute_family_score(girl_family["mother"], QUICK_FAMILY_QUESTIONS["mother"])
            if score is not None:
                st.markdown(f"<div style='color:#6BAF73; font-weight:600;'>Profile score: {score}%</div>",
                            unsafe_allow_html=True)

        with st.expander(f"👨 {name_a}'s Father", expanded=False):
            render_questions(QUICK_FAMILY_QUESTIONS["father"],
                             girl_family["father"], "gdad")
            score = compute_family_score(girl_family["father"], QUICK_FAMILY_QUESTIONS["father"])
            if score is not None:
                st.markdown(f"<div style='color:#6BAF73; font-weight:600;'>Profile score: {score}%</div>",
                            unsafe_allow_html=True)

        if setup["girl_has_brother"]:
            with st.expander(f"🧑 {name_a}'s Brother", expanded=False):
                render_questions(QUICK_FAMILY_QUESTIONS["brother"],
                                 girl_family["brother"], "gbro")
                score = compute_family_score(girl_family["brother"], QUICK_FAMILY_QUESTIONS["brother"])
                if score is not None:
                    st.markdown(f"<div style='color:#6BAF73; font-weight:600;'>Profile score: {score}%</div>",
                                unsafe_allow_html=True)

        if setup["girl_has_sister"]:
            with st.expander(f"👧 {name_a}'s Sister", expanded=False):
                render_questions(QUICK_FAMILY_QUESTIONS["sister"],
                                 girl_family["sister"], "gsis")
                score = compute_family_score(girl_family["sister"], QUICK_FAMILY_QUESTIONS["sister"])
                if score is not None:
                    st.markdown(f"<div style='color:#6BAF73; font-weight:600;'>Profile score: {score}%</div>",
                                unsafe_allow_html=True)

        st.session_state.girl_family = girl_family

    # ---------- BOY'S FAMILY ----------
    with tab_boy:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>{name_b}'s Family</div>
            <div class='role-sub'>Mother, father, sister use full scenarios. Brother is optional.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"👩 {name_b}'s Mother (Mother-in-Law)", expanded=True):
            render_questions(scenarios["mother_in_law"], inlaw_responses, "mil")
            st.session_state.inlaw_responses = inlaw_responses

        with st.expander(f"👨 {name_b}'s Father (Father-in-Law)", expanded=False):
            render_questions(scenarios["father_in_law"], inlaw_responses, "fil")
            st.session_state.inlaw_responses = inlaw_responses

        if setup["boy_has_brother"]:
            with st.expander(f"🧑 {name_b}'s Brother (Brother-in-Law)", expanded=False):
                render_questions(QUICK_FAMILY_QUESTIONS["brother"],
                                 boy_family["brother"], "bbro")
                score = compute_family_score(boy_family["brother"], QUICK_FAMILY_QUESTIONS["brother"])
                if score is not None:
                    st.markdown(f"<div style='color:#6BAF73; font-weight:600;'>Profile score: {score}%</div>",
                                unsafe_allow_html=True)
                st.session_state.boy_family = boy_family

        if setup["boy_has_sister"]:
            with st.expander(f"👧 {name_b}'s Sister (Sister-in-Law)", expanded=False):
                render_questions(scenarios["sister_in_law"], inlaw_responses, "sil")
                st.session_state.inlaw_responses = inlaw_responses

    # ---------- CLAIMS vs HOPES ----------
    with tab_claims:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>Claims vs Hopes</div>
            <div class='role-sub'>What {name_b} thinks his family believes — and what {name_a} hopes for.</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🤵 {name_b}'s Claims")
            render_questions(scenarios["boy_claims"], boy_claims, "bc")
            st.session_state.boy_claims = boy_claims
        with col2:
            st.markdown(f"### 👰 {name_a}'s Hopes")
            render_questions(scenarios["girl_expectations"], girl_expectations, "ge")
            st.session_state.girl_expectations = girl_expectations

    # ---------- FINAL ANALYSIS ----------
    with tab_result:
        render_final_analysis(
            inlaw_responses, boy_claims, girl_expectations,
            girl_family, boy_family, setup, name_a, name_b, scenarios
        )


def render_final_analysis(inlaw_responses, boy_claims, girl_expectations,
                          girl_family, boy_family, setup, name_a, name_b, scenarios):
    """Combined analysis: girl family + boy family + triangle."""

    # --- Girl-family score ---
    girl_scores = []
    if girl_family["mother"]:
        s = compute_family_score(girl_family["mother"], QUICK_FAMILY_QUESTIONS["mother"])
        if s is not None: girl_scores.append(s)
    if girl_family["father"]:
        s = compute_family_score(girl_family["father"], QUICK_FAMILY_QUESTIONS["father"])
        if s is not None: girl_scores.append(s)
    if setup["girl_has_brother"] and girl_family["brother"]:
        s = compute_family_score(girl_family["brother"], QUICK_FAMILY_QUESTIONS["brother"])
        if s is not None: girl_scores.append(s)
    if setup["girl_has_sister"] and girl_family["sister"]:
        s = compute_family_score(girl_family["sister"], QUICK_FAMILY_QUESTIONS["sister"])
        if s is not None: girl_scores.append(s)
    girl_family_score = round(sum(girl_scores) / len(girl_scores), 1) if girl_scores else None

    # --- Boy-family score: existing triangle analysis handles MIL/FIL/SIL, plus optional brother ---
    boy_extras = []
    if setup["boy_has_brother"] and boy_family.get("brother"):
        s = compute_family_score(boy_family["brother"], QUICK_FAMILY_QUESTIONS["brother"])
        if s is not None: boy_extras.append(s)

    total_inlaw_needed = (len(scenarios["mother_in_law"]) + len(scenarios["father_in_law"]))
    if setup["boy_has_sister"]:
        total_inlaw_needed += len(scenarios["sister_in_law"])

    if len(inlaw_responses) < total_inlaw_needed or not boy_claims or not girl_expectations:
        st.info(
            f"Complete the questionnaires to see analysis. "
            f"Boy's family answers: {len(inlaw_responses)}/{total_inlaw_needed} · "
            f"Claims: {len(boy_claims)}/{len(scenarios['boy_claims'])} · "
            f"Hopes: {len(girl_expectations)}/{len(scenarios['girl_expectations'])}"
        )
        with st.expander("🎬 Demo Mode — auto-fill all family data"):
            if st.button("Load Sara & Ahmed family demo", type="secondary"):
                load_demo(scenarios)
                st.rerun()
        return

    # Run triangle analysis on boy's family side
    triangle = build_triangle_analysis(inlaw_responses, boy_claims, girl_expectations)
    boy_family_score = triangle["inlaw_score"]
    if boy_extras:
        boy_family_score = round((boy_family_score + sum(boy_extras) / len(boy_extras)) / 2, 1)

    # Combined family score
    if girl_family_score is not None:
        combined = round((girl_family_score + boy_family_score) / 2, 1)
    else:
        combined = boy_family_score

    st.session_state.inlaw_score = combined
    st.session_state.triangle_analysis = triangle
    st.session_state.girl_family_score = girl_family_score
    st.session_state.boy_family_score = boy_family_score

    # Verdict
    color = "#6BAF73" if combined >= 70 else ("#E8A846" if combined >= 45 else "#D4577A")
    verdict = "Strong Family Alignment" if combined >= 70 else ("Moderate Alignment" if combined >= 45 else "Friction Risk")

    st.markdown(f"""
    <div class='verdict-card'>
        <div style='color:#8A6B7A; font-size:0.8rem; letter-spacing:3px; text-transform:uppercase; font-weight:600;'>
            Combined Family Score
        </div>
        <div class='verdict-score' style='color:{color};'>{combined}%</div>
        <div style='color:{color}; font-family:"Playfair Display",serif; font-size:1.25rem; font-weight:600; margin-top:0.3rem;'>
            {verdict}
        </div>
        <div style='color:#8A6B7A; margin-top:0.5rem; font-size:0.9rem;'>
            Averaged across {name_a}'s family and {name_b}'s family.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Side-by-side breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background:white; padding:1.2rem; border-radius:14px; border:1px solid #F8D7DE; text-align:center;'>
            <div style='color:#8A6B7A; font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; font-weight:600;'>{name_a}'s Family</div>
            <div style='font-family:"Playfair Display",serif; font-size:2.2rem; color:#5C2A3E; font-weight:700;'>
                {girl_family_score if girl_family_score is not None else '—'}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background:white; padding:1.2rem; border-radius:14px; border:1px solid #F8D7DE; text-align:center;'>
            <div style='color:#8A6B7A; font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; font-weight:600;'>{name_b}'s Family</div>
            <div style='font-family:"Playfair Display",serif; font-size:2.2rem; color:#5C2A3E; font-weight:700;'>
                {boy_family_score}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Contradictions from triangle
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Contradiction Analysis")
    st.markdown(
        f"<div style='color:#8A6B7A; font-size:0.95rem;'>"
        f"Gaps between what <b>{name_b}</b> claims about his family, and what they actually said.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if not triangle["contradictions"]:
        st.success(f"✨ No contradictions detected. {name_b}'s view of his family is consistent.")
    else:
        for c in triangle["contradictions"]:
            sev_cls = c["severity"].lower()
            st.markdown(f"""
            <div class='contra-card contra-{sev_cls}'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;'>
                    <div style='font-family:"Playfair Display",serif; font-size:1.05rem; color:#5C2A3E; font-weight:600;'>
                        {c["topic"]} · <span style='color:#8A6B7A; font-size:0.85rem;'>{c["role"]}</span>
                    </div>
                    <span class='contra-severity-{sev_cls}'>{c["severity"]}</span>
                </div>
                <div style='background:#FDEEF2; padding:0.6rem 0.9rem; border-radius:10px; margin-bottom:0.4rem;'>
                    <b style='color:#D4577A;'>{name_b} said:</b>
                    <span style='color:#3E3E3E;'> {c["boy_said"]}</span>
                </div>
                <div style='background:#F4F0EC; padding:0.6rem 0.9rem; border-radius:10px;'>
                    <b style='color:#8A6B7A;'>Family actually said:</b>
                    <span style='color:#3E3E3E;'> {c["family_said"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("✅ Family analysis complete. Go to the Results Dashboard to see full compatibility.")


def load_demo(scenarios):
    """Auto-fill demo data for both families."""
    # Boy's family scenarios (existing) — all valid scenario values
    mil_demo = {"mil_1": "fully_supportive", "mil_2": "whenever", "mil_3": "nuclear",
                "mil_4": "couple_only", "mil_5": "shared", "mil_6": "supportive",
                "mil_7": "personal", "mil_8": "supportive"}
    fil_demo = {"fil_1": "equal", "fil_2": "optional", "fil_3": "supportive",
                "fil_4": "couple", "fil_5": "personal", "fil_6": "supportive"}
    sil_demo = {"sil_1": "close_friends", "sil_2": "periodic", "sil_3": "wife_first",
                "sil_4": "supportive", "sil_5": "hands_off"}
    bc_demo = {"bc_1": "fully_supportive", "bc_2": "whenever", "bc_3": "nuclear",
               "bc_4": "couple_only", "bc_5": "equal", "bc_6": "personal", "bc_7": "close_friends"}
    ge_demo = {"ge_1": "fully_supportive", "ge_2": "whenever", "ge_3": "nuclear",
               "ge_4": "couple_only", "ge_5": "equal", "ge_6": "personal", "ge_7": "close_friends"}

    st.session_state.inlaw_responses = {**mil_demo, **fil_demo, **sil_demo}
    st.session_state.boy_claims = bc_demo
    st.session_state.girl_expectations = ge_demo

    # Girl's family + boy's brother quick answers
    st.session_state.girl_family = {
        "mother": {"conservatism": "balanced", "career_support": "fully_supportive",
                   "influence": "moderate", "warmth": "warm"},
        "father": {"conservatism": "balanced", "authority": "advisory",
                   "financial_support": "independent", "religion": "encouraged"},
        "brother": {"support": "fully_supportive", "involvement": "occasional", "warmth": "warm"},
        "sister": {"support": "fully_supportive", "involvement": "occasional", "warmth": "friendly"},
    }
    st.session_state.boy_family = {
        "brother": {"support": "cautious", "involvement": "regular", "warmth": "friendly"}
    }
    st.session_state.family_setup = {
        "girl_has_brother": True, "girl_has_sister": True,
        "boy_has_brother": True, "boy_has_sister": True,
    }
    st.session_state.inlaws_complete = True


main()
