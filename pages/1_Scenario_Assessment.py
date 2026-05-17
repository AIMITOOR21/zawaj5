"""Page 1 — Partner Compatibility Questionnaire.

Gamified scenarios that reveal true values for both partners.
"""

import streamlit as st
import json
import numpy as np
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS, DATA_DIR, DOMAIN_OPTIONS, PERSONALITY_TRAITS


# ---------- Data loading ----------

def load_scenarios():
    with open(DATA_DIR / "scenarios.json", "r", encoding="utf-8") as f:
        return json.load(f)


def extract_profile_from_responses(responses):
    profile = {}
    domain_values = {}
    for _, choice in responses.items():
        domain = choice.get("domain")
        value = choice.get("value")
        if domain and value:
            domain_values.setdefault(domain, []).append(value)

    for domain, values in domain_values.items():
        profile[domain] = Counter(values).most_common(1)[0][0]

    for domain, options in DOMAIN_OPTIONS.items():
        if domain not in profile:
            profile[domain] = options[1]

    vectors = [c.get("vector", {}) for c in responses.values()]
    if vectors:
        profile["openness"] = np.clip(np.mean([v.get("individualism", 0.5) for v in vectors]), 0, 1)
        profile["conscientiousness"] = np.clip(
            np.mean([v.get("tradition", 0.5) for v in vectors]) * 0.7 + 0.15, 0, 1)
        profile["extraversion"] = np.clip(np.random.beta(5, 5), 0, 1)
        profile["agreeableness"] = np.clip(
            1 - np.mean([v.get("confrontation", v.get("individualism", 0.5)) for v in vectors]), 0, 1)
        profile["neuroticism"] = np.clip(np.random.beta(3, 7), 0, 1)
    else:
        for t in PERSONALITY_TRAITS:
            profile[t] = 0.5
    return profile


# ---------- Styling ----------

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

    .page-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        animation: fadeInDown 0.7s ease-out;
    }
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
    .page-sub {
        color: #8A6B7A;
        font-style: italic;
        font-size: 1rem;
        margin-top: 0.3rem;
    }
    .divider-gold {
        width: 120px; height: 2px;
        background: linear-gradient(90deg, transparent, #C9A96E, transparent);
        margin: 1rem auto;
    }

    /* Partner name cards */
    .partner-card {
        background: white;
        padding: 1.2rem 1.3rem;
        border-radius: 16px;
        border: 1px solid #F8D7DE;
        box-shadow: 0 4px 14px rgba(212, 87, 122, 0.10);
        animation: fadeInUp 0.6s ease-out;
        text-align: center;
    }
    .partner-label {
        color: #D4577A;
        font-size: 0.78rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }

    /* Progress pill */
    .progress-pill {
        background: white;
        border-radius: 30px;
        padding: 0.6rem 1.3rem;
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        box-shadow: 0 3px 10px rgba(212, 87, 122, 0.1);
        border: 1px solid #F8D7DE;
        color: #5C2A3E;
        font-weight: 500;
    }

    /* Scenario tile */
    .scenario-tile {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin: 0.5rem 0;
        border: 1px solid #F8D7DE;
        box-shadow: 0 2px 8px rgba(212, 87, 122, 0.06);
        transition: all 0.3s ease;
    }
    .scenario-tile:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 14px rgba(212, 87, 122, 0.14);
    }
    .scenario-badge-done {
        background: linear-gradient(135deg, #6BAF73, #4A8C51);
        color: white;
        padding: 0.15rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .scenario-badge-pending {
        background: #F8D7DE;
        color: #D4577A;
        padding: 0.15rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
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
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(212, 87, 122, 0.4) !important;
    }
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #D4577A !important;
        border: 1.5px solid #F8D7DE !important;
    }

    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #F8D7DE !important;
        padding: 0.6rem 0.9rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #D4577A !important;
        box-shadow: 0 0 0 2px rgba(212, 87, 122, 0.15) !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 1.5rem;
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

    .completion-card {
        background: linear-gradient(135deg, #FDEEF2, #FFFFFF);
        border: 2px solid #D4577A;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        animation: fadeInUp 0.6s ease-out;
        box-shadow: 0 8px 28px rgba(212, 87, 122, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)


# ---------- Main ----------

def main():
    st.set_page_config(page_title="Partner Assessment · Zawaj", page_icon="💕", layout="wide")
    page_css()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Partner Compatibility</div>
        <div class="divider-gold"></div>
        <div class="page-sub">Interactive scenarios that reveal your true values</div>
    </div>
    """, unsafe_allow_html=True)

    scenarios = load_scenarios()

    # Partner names
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="partner-label">👰 Partner A (Bride)</div>', unsafe_allow_html=True)
        name_a = st.text_input("", value=st.session_state.get("person_a_name", "") or "Sara",
                               key="name_a_input", placeholder="Enter her name", label_visibility="collapsed")
        st.session_state.person_a_name = name_a or "Partner A"
    with col2:
        st.markdown('<div class="partner-label">🤵 Partner B (Groom)</div>', unsafe_allow_html=True)
        name_b = st.text_input("", value=st.session_state.get("person_b_name", "") or "Ahmed",
                               key="name_b_input", placeholder="Enter his name", label_visibility="collapsed")
        st.session_state.person_b_name = name_b or "Partner B"

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress snapshot
    responses_a = st.session_state.get("scenario_responses_a", {})
    responses_b = st.session_state.get("scenario_responses_b", {})
    total = len(scenarios)

    pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
    with pcol2:
        st.markdown(f"""
        <div style='text-align: center;'>
            <span class='progress-pill'>
                💕 {name_a}: <b>{len(responses_a)}/{total}</b> &nbsp;·&nbsp;
                {name_b}: <b>{len(responses_b)}/{total}</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for both partners
    tab_a, tab_b = st.tabs([f"📋 {name_a}'s Scenarios", f"📋 {name_b}'s Scenarios"])

    for tab, partner_key, partner_name in [(tab_a, "a", name_a), (tab_b, "b", name_b)]:
        with tab:
            response_key = f"scenario_responses_{partner_key}"
            responses = st.session_state.get(response_key, {})

            completed = len(responses)
            st.progress(completed / total, text=f"{completed} of {total} completed")
            st.markdown("<br>", unsafe_allow_html=True)

            for i, scenario in enumerate(scenarios):
                is_done = str(scenario['id']) in responses
                badge_html = ('<span class="scenario-badge-done">✓ Done</span>'
                              if is_done
                              else '<span class="scenario-badge-pending">Pending</span>')
                with st.expander(
                    f"Scenario {scenario['id']} — {scenario['title']}",
                    expanded=(not is_done and completed == i),
                ):
                    st.markdown(
                        f"<div style='color:#D4577A; font-size:0.78rem; letter-spacing:2px; "
                        f"text-transform:uppercase; font-weight:600; margin-bottom:0.4rem;'>"
                        f"{scenario['domain'].replace('_', ' ').title()} · {badge_html}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='background: #FDEEF2; padding: 1rem 1.2rem; border-radius: 12px; "
                        f"border-left: 4px solid #D4577A; color: #5C2A3E; font-style: italic;'>"
                        f"{scenario['scenario']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    current_value = responses.get(str(scenario['id']), {}).get("text", "")

                    for j, choice in enumerate(scenario["choices"]):
                        is_selected = current_value == choice["text"]
                        col_btn, col_text = st.columns([0.08, 0.92])
                        with col_btn:
                            if st.button(
                                "✓" if is_selected else chr(65 + j),
                                key=f"{partner_key}_s{scenario['id']}_c{j}",
                                type="primary" if is_selected else "secondary",
                            ):
                                responses[str(scenario['id'])] = {
                                    "domain": scenario["domain"],
                                    "value": choice["value"],
                                    "vector": choice["vector"],
                                    "text": choice["text"],
                                }
                                st.session_state[response_key] = responses
                                st.rerun()
                        with col_text:
                            weight = "600" if is_selected else "400"
                            color = "#5C2A3E" if is_selected else "#3E3E3E"
                            st.markdown(
                                f"<div style='padding-top:0.35rem; color:{color}; font-weight:{weight};'>"
                                f"{choice['text']}</div>",
                                unsafe_allow_html=True,
                            )

            if completed == total:
                st.markdown(
                    f"<div style='text-align:center; color:#6BAF73; font-weight:600; margin-top:1rem;'>"
                    f"✨ All scenarios completed for {partner_name}!</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # Summary
    a_done = len(responses_a) >= total
    b_done = len(responses_b) >= total

    if a_done and b_done:
        st.markdown("""
        <div class='completion-card'>
            <div style='font-size:2rem; margin-bottom:0.3rem;'>🎉</div>
            <div style='font-family:"Playfair Display",serif; font-size:1.5rem; color:#5C2A3E; font-weight:700;'>
                Both Partners Done!
            </div>
            <div style='color:#8A6B7A; margin:0.5rem 0 1rem;'>
                Now move to the In-Laws Questionnaire.
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Extract Profiles & Continue →", type="primary", use_container_width=True):
                st.session_state.person_a = extract_profile_from_responses(responses_a)
                st.session_state.person_b = extract_profile_from_responses(responses_b)
                st.session_state.assessment_complete = True
                st.success("Profiles extracted. Navigate to the In-Laws Questionnaire.")
    else:
        st.info(f"📝 {name_a}: {len(responses_a)}/{total}  ·  {name_b}: {len(responses_b)}/{total}")

    # Demo mode
    with st.expander("🎬 Demo Mode · Quick-fill sample data"):
        st.caption("Auto-fill responses so you can explore the full system quickly.")
        if st.button("Load Sara & Ahmed demo", type="secondary"):
            sara_responses, ahmed_responses = {}, {}
            for s in scenarios:
                sid = str(s["id"])
                sara_idx = 0 if s["domain"] in ["career", "location"] else 2
                ahmed_idx = 3 if s["domain"] in ["career", "location"] else 0
                sara_idx = min(sara_idx, len(s["choices"]) - 1)
                ahmed_idx = min(ahmed_idx, len(s["choices"]) - 1)
                sara_responses[sid] = {
                    "domain": s["domain"],
                    "value": s["choices"][sara_idx]["value"],
                    "vector": s["choices"][sara_idx]["vector"],
                    "text": s["choices"][sara_idx]["text"],
                }
                ahmed_responses[sid] = {
                    "domain": s["domain"],
                    "value": s["choices"][ahmed_idx]["value"],
                    "vector": s["choices"][ahmed_idx]["vector"],
                    "text": s["choices"][ahmed_idx]["text"],
                }
            st.session_state.scenario_responses_a = sara_responses
            st.session_state.scenario_responses_b = ahmed_responses
            st.session_state.person_a_name = "Sara"
            st.session_state.person_b_name = "Ahmed"
            st.session_state.person_a = extract_profile_from_responses(sara_responses)
            st.session_state.person_b = extract_profile_from_responses(ahmed_responses)
            st.session_state.assessment_complete = True
            st.success("Demo data loaded! Continue to the In-Laws Questionnaire.")
            st.rerun()


main()
