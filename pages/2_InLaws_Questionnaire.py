"""Page 2 — In-Laws Questionnaire.

The novel core of Zawaj. Instead of inferring family traits from a graph,
real family members (mother-in-law, father-in-law, sister-in-law) answer
scenarios directly. The boy also shares his claims about his family, and the
girl shares her expectations — the system then performs triangle analysis to
surface contradictions and alignment gaps.
"""

import streamlit as st
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS, DATA_DIR
from ai.inlaw_analysis import build_triangle_analysis


# ---------- CSS ----------

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

    /* Role intro card */
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

    /* Question tile */
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
        margin-bottom: 0.6rem;
    }

    /* Verdict card */
    .verdict-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 8px 26px rgba(212, 87, 122, 0.15);
        animation: fadeInUp 0.6s ease-out;
        text-align: center;
    }
    .verdict-score {
        font-family: 'Playfair Display', serif;
        font-size: 3.8rem;
        font-weight: 700;
        margin: 0;
    }

    /* Contradiction card */
    .contra-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin: 0.6rem 0;
        box-shadow: 0 3px 10px rgba(212, 87, 122, 0.08);
        animation: fadeInUp 0.5s ease-out;
    }
    .contra-high    { border-left: 4px solid #D4577A; }
    .contra-medium  { border-left: 4px solid #E8A846; }
    .contra-low     { border-left: 4px solid #6BAF73; }
    .contra-severity-high    {
        background: #FFE8EE; color: #D4577A; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.72rem; font-weight: 700;
    }
    .contra-severity-medium  {
        background: #FFF2D6; color: #B87914; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.72rem; font-weight: 700;
    }
    .contra-severity-low     {
        background: #E4F3E7; color: #4A8C51; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.72rem; font-weight: 700;
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

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #D4577A, #C9A96E) !important;
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


# ---------- Helpers ----------

def load_inlaw_scenarios():
    with open(DATA_DIR / "inlaw_scenarios.json", "r", encoding="utf-8") as f:
        return json.load(f)


def render_questions(questions, storage_dict, key_prefix):
    """Render a list of multiple-choice questions that persist into storage_dict."""
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


# ---------- Main ----------

def main():
    st.set_page_config(page_title="In-Laws · Zawaj", page_icon="👨‍👩‍👧", layout="wide")
    page_css()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>In-Laws Questionnaire</div>
        <div class='divider-gold'></div>
        <div class='page-sub'>Real family voices · Triangle analysis · Contradiction detection</div>
    </div>
    """, unsafe_allow_html=True)

    scenarios = load_inlaw_scenarios()

    # Init storage dicts in session state
    inlaw_responses = st.session_state.setdefault("inlaw_responses", {})
    boy_claims = st.session_state.setdefault("boy_claims", {})
    girl_expectations = st.session_state.setdefault("girl_expectations", {})

    name_a = st.session_state.get("person_a_name", "Partner A")
    name_b = st.session_state.get("person_b_name", "Partner B")

    # Progress summary
    total_inlaw = (len(scenarios["mother_in_law"]) + len(scenarios["father_in_law"])
                   + len(scenarios["sister_in_law"]))
    total_bc = len(scenarios["boy_claims"])
    total_ge = len(scenarios["girl_expectations"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("In-Laws answered", f"{len(inlaw_responses)}/{total_inlaw}")
    with c2:
        st.metric(f"{name_b}'s claims", f"{len(boy_claims)}/{total_bc}")
    with c3:
        st.metric(f"{name_a}'s expectations", f"{len(girl_expectations)}/{total_ge}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_mil, tab_fil, tab_sil, tab_boy, tab_girl, tab_result = st.tabs([
        "👩 Mother-in-Law", "👨 Father-in-Law", "👧 Sister-in-Law",
        f"🤵 {name_b}'s Claims", f"👰 {name_a}'s Hopes", "🔺 Triangle",
    ])

    with tab_mil:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>Mother-in-Law</div>
            <div class='role-sub'>Your future ammi answers about career, visits, living, and household life.</div>
        </div>
        """, unsafe_allow_html=True)
        render_questions(scenarios["mother_in_law"], inlaw_responses, "mil")
        st.session_state.inlaw_responses = inlaw_responses

    with tab_fil:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>Father-in-Law</div>
            <div class='role-sub'>Your future abbu answers on finances, religion, and decision-making.</div>
        </div>
        """, unsafe_allow_html=True)
        render_questions(scenarios["father_in_law"], inlaw_responses, "fil")
        st.session_state.inlaw_responses = inlaw_responses

    with tab_sil:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>Sister-in-Law</div>
            <div class='role-sub'>Your future nand on closeness, visits, and brother's loyalty.</div>
        </div>
        """, unsafe_allow_html=True)
        render_questions(scenarios["sister_in_law"], inlaw_responses, "sil")
        st.session_state.inlaw_responses = inlaw_responses

    with tab_boy:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>{name_b}'s Predictions</div>
            <div class='role-sub'>What does {name_b} claim his family believes? We'll compare this to their real answers.</div>
        </div>
        """, unsafe_allow_html=True)
        render_questions(scenarios["boy_claims"], boy_claims, "bc")
        st.session_state.boy_claims = boy_claims

    with tab_girl:
        st.markdown(f"""
        <div class='role-intro'>
            <div class='role-title'>{name_a}'s Hopes</div>
            <div class='role-sub'>What is {name_a} hoping for from her future in-laws?</div>
        </div>
        """, unsafe_allow_html=True)
        render_questions(scenarios["girl_expectations"], girl_expectations, "ge")
        st.session_state.girl_expectations = girl_expectations

    with tab_result:
        render_triangle_tab(inlaw_responses, boy_claims, girl_expectations,
                            total_inlaw, total_bc, total_ge, name_a, name_b, scenarios)


def render_triangle_tab(inlaw_responses, boy_claims, girl_expectations,
                        total_inlaw, total_bc, total_ge, name_a, name_b, scenarios):
    """Render the triangle analysis tab."""
    if (len(inlaw_responses) < total_inlaw or len(boy_claims) < total_bc
            or len(girl_expectations) < total_ge):
        missing = []
        if len(inlaw_responses) < total_inlaw:
            missing.append(f"In-Laws ({total_inlaw - len(inlaw_responses)} left)")
        if len(boy_claims) < total_bc:
            missing.append(f"{name_b}'s claims ({total_bc - len(boy_claims)} left)")
        if len(girl_expectations) < total_ge:
            missing.append(f"{name_a}'s hopes ({total_ge - len(girl_expectations)} left)")
        st.info(f"Complete remaining to see triangle analysis: {', '.join(missing)}")

        # Demo mode
        with st.expander("🎬 Demo Mode · Auto-fill in-law data"):
            if st.button("Load demo in-law responses", type="secondary"):
                load_demo_inlaw(scenarios)
                st.rerun()
        return

    # Compute triangle
    result = build_triangle_analysis(inlaw_responses, boy_claims, girl_expectations)
    st.session_state.inlaw_score = result["inlaw_score"]
    st.session_state.triangle_analysis = result

    # Verdict card
    st.markdown(f"""
    <div class='verdict-card'>
        <div style='color:#8A6B7A; font-size:0.8rem; letter-spacing:3px; text-transform:uppercase; font-weight:600;'>
            Family Alignment Score
        </div>
        <div class='verdict-score' style='color:{result["verdict_color"]};'>{result["inlaw_score"]:.1f}%</div>
        <div style='color:{result["verdict_color"]}; font-family:"Playfair Display",serif;
                    font-size:1.25rem; font-weight:600; margin-top:0.3rem;'>
            {result["verdict"]}
        </div>
        <div style='color:#8A6B7A; margin-top:0.5rem; font-size:0.9rem;'>
            Based on how well in-law answers align with {name_a}'s hopes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gauge chart via visualization util
    try:
        from utils.visualization import create_triangle_chart
        fig = create_triangle_chart(result["inlaw_score"], len(result["contradictions"]))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass

    # Contradictions
    st.markdown("### Contradiction Analysis")
    st.markdown(
        f"<div style='color:#8A6B7A; font-size:0.95rem;'>"
        f"Gaps between what <b>{name_b}</b> claims about his family, and what the family <i>actually</i> said.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if not result["contradictions"]:
        st.success(f"✨ No contradictions detected. {name_b}'s understanding of his family is accurate.")
    else:
        for c in result["contradictions"]:
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
    c1, c2 = st.columns(2)
    with c1:
        st.metric("High-severity contradictions", result["high_contradictions"])
    with c2:
        st.metric("Medium-severity contradictions", result["medium_contradictions"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("✅ Triangle analysis complete. Go to the Results Dashboard to see your full compatibility.")


def load_demo_inlaw(scenarios):
    """Load demo in-law responses showing clear friction with supportive girl."""
    # Mother-in-law: traditional
    mil_demo = {"mil_1": "until_children", "mil_2": "biweekly", "mil_3": "joint_separate",
                "mil_4": "family_consensus", "mil_5": "mostly_wife", "mil_6": "active_help",
                "mil_7": "matching", "mil_8": "uncomfortable"}
    # Father-in-law: mixed traditional
    fil_demo = {"fil_1": "husband_lead", "fil_2": "optional", "fil_3": "conditional",
                "fil_4": "consensus", "fil_5": "respectful", "fil_6": "conditional"}
    # Sister-in-law: wants involvement
    sil_demo = {"sil_1": "close_friends", "sil_2": "regular", "sil_3": "balanced",
                "sil_4": "neutral", "sil_5": "consulted"}
    # Boy claims: he thinks his family is modern
    bc_demo = {"bc_1": "fully_supportive", "bc_2": "whenever", "bc_3": "nuclear",
               "bc_4": "couple_only", "bc_5": "equal", "bc_6": "personal",
               "bc_7": "cordial"}
    # Girl expectations: fully modern
    ge_demo = {"ge_1": "fully_supportive", "ge_2": "weekly", "ge_3": "nearby",
               "ge_4": "couple_only", "ge_5": "equal", "ge_6": "personal",
               "ge_7": "cordial"}

    st.session_state.inlaw_responses = {**mil_demo, **fil_demo, **sil_demo}
    st.session_state.boy_claims = bc_demo
    st.session_state.girl_expectations = ge_demo
    st.session_state.inlaws_complete = True


main()
