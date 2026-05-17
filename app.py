"""Zawaj — Main Streamlit Application.

AI-Powered Pre-Marriage Compatibility for Pakistani Families.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import COLORS, MODELS_DIR


# ── SESSION STATE ──────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "person_a": {}, "person_b": {},
        "person_a_name": "", "person_b_name": "",
        "scenario_responses_a": {}, "scenario_responses_b": {},
        "inlaw_responses": {}, "boy_claims": {}, "girl_expectations": {},
        "assessment_complete": False, "inlaws_complete": False,
        "results_computed": False, "results": None, "conflicts": None,
        "domain_scores": None, "inlaw_score": None,
        "triangle_analysis": None, "model_trained": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def check_model_trained():
    return (MODELS_DIR / "compatibility_model.pkl").exists()


@st.cache_resource
def auto_train_models():
    if not check_model_trained():
        from models.train import train_all
        train_all()
    return True


# ── JOURNEY STEP LOGIC ────────────────────────────────────────────────────────

def get_journey_step():
    if st.session_state.get("results_computed"):
        return 5
    if st.session_state.get("inlaws_complete"):
        return 4
    if st.session_state.get("assessment_complete"):
        return 3
    if st.session_state.get("model_trained"):
        return 2
    return 1


def pill_class(step_num, active_step):
    if step_num < active_step:
        return "done"
    if step_num == active_step:
        return "active"
    return ""


# ── GLOBAL CSS (applies to all pages) ─────────────────────────────────────────

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,300;1,400;1,700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp {
        background: linear-gradient(160deg, #fbd8e6 0%, #f5bece 45%, #faccd8 75%, #f0b8c8 100%) !important;
        background-attachment: fixed !important;
    }
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    #MainMenu, footer, header { visibility: hidden; height: 0; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }

    [data-testid="stSidebar"] {
        background: rgba(251,216,230,0.96) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(180,50,80,0.1) !important;
    }
    .stButton > button {
        background: #b83050 !important;
        color: white !important; border: none !important;
        border-radius: 50px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        box-shadow: 0 6px 20px rgba(184,48,80,0.25) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        background: #a02844 !important;
        transform: translateY(-2px) !important;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #b83050, #c47060) !important;
    }
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.75) !important;
        border-radius: 14px !important;
        border-top: 2px solid rgba(184,48,80,0.28) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif !important;
        color: #5a0c1e !important; font-style: italic !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.65) !important;
        border-radius: 10px 10px 0 0 !important;
        color: rgba(100,20,40,0.6) !important;
        border: 1px solid rgba(180,50,80,0.1) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTabs [aria-selected="true"] {
        background: #b83050 !important;
        color: white !important;
    }
    .stAlert { border-radius: 14px !important; border: none !important; }
    h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #5a0c1e !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.2rem 0 0.8rem;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;
                      font-style:italic;font-weight:700;color:#5a0c1e;">Zawaj</div>
          <div style="font-size:1rem;color:rgba(180,50,80,0.5);letter-spacing:6px;margin-top:2px;">زواج</div>
          <div style="height:1px;background:rgba(180,50,80,0.12);margin:0.8rem 0;"></div>
        </div>
        """, unsafe_allow_html=True)

        a_done  = st.session_state.get("assessment_complete", False)
        il_done = st.session_state.get("inlaws_complete", False)
        r_done  = st.session_state.get("results_computed", False)

        def row(label, done):
            c = "rgba(40,160,90,0.85)" if done else "rgba(180,50,80,0.35)"
            s = "✓" if done else "○"
            return f'<div style="display:flex;align-items:center;gap:8px;padding:0.3rem 0;font-size:0.8rem;color:rgba(80,10,30,0.65);"><span style="color:{c};font-weight:600;">{s}</span>{label}</div>'

        st.markdown(row("Partner Assessment", a_done) +
                    row("In-Laws Questionnaire", il_done) +
                    row("Results Computed", r_done),
                    unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(180,50,80,0.1);margin:0.8rem 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.72rem;color:rgba(100,20,40,0.4);line-height:1.8;">
          Aiman Fatima · Sania Saeed · Khadija<br>
          AI-201 · BSSE<br>Dr. Umara Zahid
        </div>
        """, unsafe_allow_html=True)


# ── LANDING PAGE HTML ──────────────────────────────────────────────────────────

def build_landing_html(active_step):
    def pc(n):
        return pill_class(n, active_step)

    h = '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,300;1,400;1,700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{min-height:100%;font-family:'Inter',sans-serif;
  background:linear-gradient(160deg,#fbd8e6 0%,#f5bece 45%,#faccd8 75%,#f0b8c8 100%);
  position:relative;}}
body::before{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:radial-gradient(circle,rgba(180,50,80,0.05) 1px,transparent 1px);
  background-size:26px 26px;}}
body::after{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(ellipse 80% 50% at 50% 22%,rgba(255,245,248,0.6) 0%,transparent 65%),
             radial-gradient(ellipse 100% 35% at 50% 100%,rgba(140,20,50,0.09) 0%,transparent 55%);}}
canvas{{position:fixed;inset:0;z-index:1;pointer-events:none;}}
.page{{position:relative;z-index:2;}}
nav{{padding:18px 36px;display:flex;align-items:center;justify-content:space-between;
  background:rgba(255,240,246,0.52);backdrop-filter:blur(24px);
  border-bottom:1px solid rgba(180,50,80,0.07);position:sticky;top:0;z-index:100;}}
.logo{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:700;font-size:24px;color:#6a0c24;}}
.logo em{{font-style:normal;font-size:11px;font-weight:400;color:rgba(120,30,60,0.55);letter-spacing:5px;margin-left:10px;font-family:'Inter',sans-serif;}}
.nav-r{{font-size:10px;color:rgba(100,20,40,0.35);letter-spacing:2.5px;text-transform:uppercase;}}
.hero{{text-align:center;padding:70px 36px 56px;position:relative;opacity:0;animation:up 1.2s 0.1s cubic-bezier(0.16,1,0.3,1) forwards;}}
.ghost-ar{{position:absolute;top:18px;left:50%;transform:translateX(-50%);
  font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:700;
  font-size:190px;color:rgba(180,50,80,0.072);white-space:nowrap;pointer-events:none;
  line-height:1;user-select:none;letter-spacing:-6px;}}
.eyebrow{{font-size:10px;font-weight:500;letter-spacing:5px;text-transform:uppercase;color:rgba(130,30,60,0.48);margin-bottom:18px;}}
.title{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:700;font-size:84px;
  line-height:0.88;color:#3a0814;letter-spacing:-2px;white-space:nowrap;
  text-shadow:0 4px 28px rgba(90,12,30,0.12);}}
.divider{{display:flex;align-items:center;justify-content:center;gap:16px;margin:24px 0 20px;}}
.dline{{width:50px;height:1px;background:rgba(160,40,70,0.18);}}
.ddiamond{{width:8px;height:8px;transform:rotate(45deg);border:1px solid rgba(160,40,70,0.35);position:relative;}}
.ddiamond::after{{content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:3px;height:3px;border-radius:50%;background:rgba(160,40,70,0.4);}}
.taglines{{display:flex;flex-direction:column;gap:2px;align-items:center;}}
.tline{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:400;
  font-size:17px;color:rgba(80,10,30,0.6);letter-spacing:0.3px;line-height:1.7;opacity:0;}}
.tline:nth-child(1){{animation:fadeSlide 0.7s 0.9s ease-out forwards;}}
.tline:nth-child(2){{animation:fadeSlide 0.7s 1.05s ease-out forwards;}}
.tline:nth-child(3){{animation:fadeSlide 0.7s 1.2s ease-out forwards;}}
.tline span{{color:rgba(160,40,70,0.55);margin:0 4px;}}
.cred-row{{display:flex;align-items:center;justify-content:center;gap:10px;
  margin-top:24px;opacity:0;animation:up 0.8s 1.35s ease-out forwards;}}
.cred-pill{{display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;
  background:rgba(255,255,255,0.55);border:1px solid rgba(180,50,80,0.14);
  font-size:10px;font-weight:500;color:rgba(90,12,30,0.6);}}
.cred-pill svg{{width:12px;height:12px;stroke:#b83050;fill:rgba(184,48,80,0.15);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;}}
.cred-sep{{width:3px;height:3px;border-radius:50%;background:rgba(180,50,80,0.25);}}
.sbreak{{margin:0 36px 24px;height:1px;background:linear-gradient(90deg,transparent,rgba(180,50,80,0.1),transparent);}}
.journey{{margin:0 36px 24px;opacity:0;animation:up 1s 0.38s cubic-bezier(0.16,1,0.3,1) forwards;}}
.j-head{{display:flex;align-items:center;gap:10px;margin-bottom:14px;}}
.j-accent{{width:3px;height:20px;background:linear-gradient(180deg,#b83050,rgba(184,48,80,0.3));border-radius:2px;}}
.j-label{{font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:rgba(130,30,60,0.65);}}
.j-label-heart svg{{width:13px;height:13px;stroke:#b83050;fill:rgba(184,48,80,0.15);stroke-width:1.8;stroke-linecap:round;margin-left:6px;vertical-align:middle;}}
.j-pills{{display:flex;gap:8px;align-items:stretch;}}
.jpill{{flex:1;padding:13px 8px;border-radius:14px;border:1px solid rgba(180,50,80,0.13);
  background:rgba(255,255,255,0.42);cursor:pointer;
  transition:all 0.35s cubic-bezier(0.16,1,0.3,1);text-align:center;position:relative;}}
.jpill:hover{{background:rgba(255,255,255,0.68);transform:translateY(-2px);}}
.jpill.done{{background:rgba(255,255,255,0.6);border-color:rgba(180,50,80,0.22);}}
.jpill.done .jnum{{color:rgba(100,20,40,0.65);}}
.jpill.done .jtxt{{color:rgba(100,20,40,0.52);}}
.jpill.active{{flex:1.5;background:#fff;border-color:rgba(180,50,80,0.3);
  box-shadow:0 10px 32px rgba(160,30,60,0.14);transform:translateY(-3px);}}
.jpill.active .jnum{{color:#b83050;font-size:23px;}}
.jpill.active .jtxt{{color:#b83050;font-weight:600;}}
.jnum{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:20px;font-weight:700;
  color:rgba(120,30,60,0.3);line-height:1;margin-bottom:5px;}}
.jtxt{{font-size:9px;color:rgba(120,30,60,0.42);letter-spacing:0.5px;}}
.tip{{position:absolute;bottom:calc(100% + 10px);left:50%;
  transform:translateX(-50%) translateY(6px);background:#3a0818;
  color:rgba(255,255,255,0.88);font-size:10px;padding:7px 13px;border-radius:8px;
  white-space:nowrap;opacity:0;pointer-events:none;transition:opacity 0.2s,transform 0.2s;z-index:20;}}
.tip::after{{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);
  border:5px solid transparent;border-top-color:#3a0818;}}
.jpill:hover .tip{{opacity:1;transform:translateX(-50%) translateY(0);}}
.features{{margin:0 36px 22px;}}
.feat-hero{{background:rgba(255,255,255,0.74);border:1px solid rgba(180,50,80,0.1);
  border-radius:22px;padding:24px 26px;margin-bottom:10px;
  display:flex;align-items:center;gap:24px;cursor:pointer;position:relative;overflow:hidden;
  transition:all 0.4s cubic-bezier(0.16,1,0.3,1);opacity:0;animation:up 0.9s 0.68s ease-out forwards;}}
.feat-hero::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(184,48,80,0.45),transparent);
  transform:scaleX(0);transition:transform 0.45s;}}
.feat-hero:hover{{background:rgba(255,255,255,0.92);transform:translateY(-4px);
  box-shadow:0 22px 55px rgba(160,30,60,0.12);}}
.feat-hero:hover::before{{transform:scaleX(1);}}
.fh-icon{{flex:0 0 66px;height:66px;position:relative;display:flex;align-items:center;justify-content:center;}}
.ring-a{{position:absolute;width:66px;height:66px;border-radius:50%;
  border:1px solid rgba(184,48,80,0.14);animation:sp 10s linear infinite;}}
.ring-b{{position:absolute;width:48px;height:48px;border-radius:50%;
  border:1px dashed rgba(184,48,80,0.1);animation:sp 6s linear infinite reverse;}}
.fh-core{{width:42px;height:42px;border-radius:50%;
  background:linear-gradient(135deg,rgba(184,48,80,0.1),rgba(200,80,110,0.05));
  border:1px solid rgba(184,48,80,0.14);display:flex;align-items:center;
  justify-content:center;position:relative;z-index:1;}}
.fh-core svg{{width:20px;height:20px;stroke:#b83050;fill:rgba(184,48,80,0.1);
  stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;}}
.fh-body{{flex:1;}}
.fh-tag{{font-size:9px;font-weight:500;letter-spacing:3px;text-transform:uppercase;
  color:rgba(184,48,80,0.52);margin-bottom:6px;}}
.fh-title{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:22px;
  font-weight:700;color:#5a0c1e;margin-bottom:4px;}}
.fh-desc{{font-size:12px;font-weight:300;color:rgba(100,20,40,0.5);line-height:1.55;}}
.fh-num{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:58px;
  font-weight:700;color:rgba(184,48,80,0.055);line-height:1;flex:0 0 auto;align-self:flex-end;}}
.feat-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}}
.feat{{background:rgba(255,255,255,0.64);border:1px solid rgba(180,50,80,0.09);
  border-left:3px solid transparent;border-radius:18px;padding:22px 18px;cursor:pointer;
  position:relative;overflow:hidden;transition:all 0.35s cubic-bezier(0.16,1,0.3,1);opacity:0;}}
.feat:hover{{background:rgba(255,255,255,0.95);border-left-color:#b83050;
  border-color:rgba(180,50,80,0.18);transform:translateY(-5px);
  box-shadow:0 20px 48px rgba(160,30,60,0.13);}}
.fa{{animation:up 0.8s 0.82s ease-out forwards;}}
.fb{{animation:up 0.8s 0.96s ease-out forwards;}}
.fc{{animation:up 0.8s 1.1s ease-out forwards;}}
.fn{{position:absolute;top:14px;right:16px;font-family:'Cormorant Garamond',serif;
  font-style:italic;font-size:42px;font-weight:700;color:rgba(184,48,80,0.055);line-height:1;}}
.fheart{{margin-bottom:13px;}}
.fheart svg{{width:20px;height:20px;stroke:#c03858;fill:rgba(192,56,88,0.09);
  stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;}}
.ftitle{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:19px;
  font-weight:700;color:#5a0c1e;margin-bottom:4px;}}
.fdesc{{font-size:11px;font-weight:300;color:rgba(100,20,40,0.48);line-height:1.55;}}
.cta{{display:flex;flex-direction:column;align-items:center;gap:12px;
  padding:6px 36px 0;opacity:0;animation:up 0.9s 1.14s ease-out forwards;}}
.cta-btns{{display:flex;align-items:center;gap:12px;}}
.btn{{padding:15px 46px;border-radius:50px;border:none;cursor:pointer;
  background:#b83050;color:#fff;font-family:'Inter',sans-serif;
  font-size:13px;font-weight:600;letter-spacing:0.4px;
  display:flex;align-items:center;gap:9px;
  box-shadow:0 8px 28px rgba(184,48,80,0.3);
  transition:transform 0.3s,box-shadow 0.3s,background 0.3s;}}
.btn:hover{{background:#a02844;transform:translateY(-3px);
  box-shadow:0 14px 36px rgba(184,48,80,0.42);}}
.btn svg{{width:14px;height:14px;stroke:#fff;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;}}
.btn2{{padding:15px 28px;border-radius:50px;cursor:pointer;background:transparent;
  border:1px solid rgba(160,40,70,0.22);color:rgba(80,10,30,0.58);
  font-family:'Inter',sans-serif;font-size:13px;font-weight:400;transition:all 0.3s;}}
.btn2:hover{{background:rgba(255,255,255,0.5);}}
.trust{{font-size:10px;font-weight:300;color:rgba(100,20,40,0.4);
  letter-spacing:1px;display:flex;align-items:center;gap:8px;padding-bottom:4px;}}
.trust-dot{{width:2px;height:2px;border-radius:50%;background:rgba(180,50,80,0.3);}}
footer{{padding:16px 36px;border-top:1px solid rgba(180,50,80,0.09);
  display:flex;align-items:center;justify-content:space-between;
  opacity:0;animation:up 0.8s 1.2s ease-out forwards;margin-top:24px;}}
.fl{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:15px;color:rgba(100,20,40,0.42);}}
.fr{{display:flex;align-items:center;gap:8px;}}
.heartbeat{{display:flex;align-items:center;gap:1px;height:16px;}}
.heartbeat span{{display:inline-block;width:2px;border-radius:1px;
  background:rgba(184,48,80,0.35);animation:beat 1.4s ease-in-out infinite;}}
.heartbeat span:nth-child(1){{height:4px;animation-delay:0s;}}
.heartbeat span:nth-child(2){{height:8px;animation-delay:0.1s;}}
.heartbeat span:nth-child(3){{height:14px;animation-delay:0.2s;}}
.heartbeat span:nth-child(4){{height:8px;animation-delay:0.3s;}}
.heartbeat span:nth-child(5){{height:4px;animation-delay:0.4s;}}
.heartbeat span:nth-child(6){{height:10px;animation-delay:0.5s;}}
.heartbeat span:nth-child(7){{height:5px;animation-delay:0.6s;}}
.fr-text{{font-size:10px;color:rgba(100,20,40,0.3);letter-spacing:2px;text-transform:uppercase;}}
@keyframes up{{from{{opacity:0;transform:translateY(18px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeSlide{{from{{opacity:0;transform:translateY(8px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes sp{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}
@keyframes beat{{0%,100%{{opacity:0.35;}}50%{{opacity:0.9;}}}}
</style></head><body>
<canvas id="c"></canvas>
<div class="page">
  <nav>
    <div class="logo">Zawaj <em>زواج</em></div>
    <div class="nav-r">AI-201 · BSSE</div>
  </nav>
  <div class="hero">
    <div class="ghost-ar">زواج</div>
    <div class="eyebrow">Pre-Marriage Compatibility</div>
    <div class="title-wrap"><div class="title">Zawaj</div></div>
    <div class="divider"><div class="dline"></div><div class="ddiamond"></div><div class="dline"></div></div>
    <div class="taglines">
      <div class="tline">Know your person<span>·</span></div>
      <div class="tline">Know their family<span>·</span></div>
      <div class="tline">Know yourself.</div>
    </div>
    <div class="cred-row">
      <div class="cred-pill">{h} 5 compatibility dimensions</div>
      <div class="cred-sep"></div>
      <div class="cred-pill">{h} Results in 15 minutes</div>
      <div class="cred-sep"></div>
      <div class="cred-pill">{h} Urdu &amp; English</div>
    </div>
  </div>
  <div class="sbreak"></div>
  <div class="journey">
    <div class="j-head">
      <div class="j-accent"></div>
      <div class="j-label">Your Journey <span class="j-label-heart">{h}</span></div>
    </div>
    <div class="j-pills">
      <div class="jpill {pc(1)}"><div class="tip">Partners enter basic details</div><div class="jnum">1</div><div class="jtxt">Setup</div></div>
      <div class="jpill {pc(2)}"><div class="tip">20 scenario-based questions</div><div class="jnum">2</div><div class="jtxt">Assessment</div></div>
      <div class="jpill {pc(3)}"><div class="tip">Family answers independently</div><div class="jnum">3</div><div class="jtxt">In-Laws</div></div>
      <div class="jpill {pc(4)}"><div class="tip">AI detects contradictions</div><div class="jnum">4</div><div class="jtxt">Analysis</div></div>
      <div class="jpill {pc(5)}"><div class="tip">Full compatibility report</div><div class="jnum">5</div><div class="jtxt">Results</div></div>
    </div>
  </div>
  <div class="sbreak"></div>
  <div class="features">
    <div class="feat-hero">
      <div class="fh-icon"><div class="ring-a"></div><div class="ring-b"></div>
        <div class="fh-core">{h}</div>
      </div>
      <div class="fh-body">
        <div class="fh-tag">Core Feature</div>
        <div class="fh-title">Compatibility Assessment</div>
        <div class="fh-desc">Scenario-based questions that reveal true values — not just stated ones</div>
      </div>
      <div class="fh-num">01</div>
    </div>
    <div class="feat-row">
      <div class="feat fa"><div class="fn">02</div><div class="fheart">{h}</div><div class="ftitle">Family Voices</div><div class="fdesc">Real answers from in-laws</div></div>
      <div class="feat fb"><div class="fn">03</div><div class="fheart">{h}</div><div class="ftitle">Truth Analysis</div><div class="fdesc">Surface contradictions early</div></div>
      <div class="feat fc"><div class="fn">04</div><div class="fheart">{h}</div><div class="ftitle">Growth Plan</div><div class="fdesc">AI guidance, Urdu &amp; English</div></div>
    </div>
  </div>
  <div class="cta">
    <div class="cta-btns">
      <button class="btn">Begin Assessment <svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></button>
      <button class="btn2">How It Works</button>
    </div>
    <div class="trust">Free<div class="trust-dot"></div>No account required<div class="trust-dot"></div>Results in 15 minutes</div>
  </div>
  <footer>
    <div class="fl">Zawaj — زواج</div>
    <div class="fr">
      <div class="heartbeat"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
      <div class="fr-text">AI-201 · BSSE · Dr. Umara Zahid</div>
    </div>
  </footer>
</div>
<script>
const cv=document.getElementById('c'),ct=cv.getContext('2d');
function resize(){{cv.width=window.innerWidth;cv.height=window.innerHeight;}}
resize();window.addEventListener('resize',resize);
function H(){{
  this.reset=function(){{
    this.x=Math.random()*cv.width;this.y=cv.height+16;
    this.s=Math.random()*8+3;this.vy=Math.random()*0.42+0.16;
    this.vx=(Math.random()-0.5)*0.32;this.op=Math.random()*0.11+0.04;
    this.rot=Math.random()*Math.PI*2;this.rv=(Math.random()-0.5)*0.008;
    this.wb=Math.random()*Math.PI*2;this.ws=Math.random()*0.013+0.005;
    this.col=Math.random()<0.65?'175,45,75':'215,95,125';
  }};
  this.reset();this.y=Math.random()*cv.height;
}}
H.prototype.draw=function(){{
  ct.save();ct.translate(this.x,this.y);ct.rotate(this.rot);
  ct.globalAlpha=this.op;ct.fillStyle=`rgba(${{this.col}},1)`;
  const s=this.s;
  ct.beginPath();ct.moveTo(0,-s*.4);
  ct.bezierCurveTo(s*.45,-s,s*1.05,-s*.4,s,s*.3);
  ct.bezierCurveTo(s,s*.8,s*.45,s*1.2,0,s*1.5);
  ct.bezierCurveTo(-s*.45,s*1.2,-s,s*.8,-s,s*.3);
  ct.bezierCurveTo(-s*1.05,-s*.4,-s*.45,-s,0,-s*.4);
  ct.closePath();ct.fill();ct.restore();
}};
H.prototype.tick=function(){{
  this.wb+=this.ws;this.x+=this.vx+Math.sin(this.wb)*0.32;
  this.y-=this.vy;this.rot+=this.rv;if(this.y<-20)this.reset();
}};
const hs=[];for(let i=0;i<40;i++)hs.push(new H());
(function loop(){{ct.clearRect(0,0,cv.width,cv.height);hs.forEach(h=>{{h.draw();h.tick();}});requestAnimationFrame(loop);}})();
document.querySelectorAll('.feat,.feat-hero').forEach(el=>{{
  el.addEventListener('mousemove',e=>{{
    const r=el.getBoundingClientRect();
    const x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
    el.style.transform=`translateY(-4px) rotateX(${{-y*3.5}}deg) rotateY(${{x*3.5}}deg)`;
  }});
  el.addEventListener('mouseleave',()=>el.style.transform='');
}});
</script>
</body></html>"""


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Zawaj — Marriage Compatibility",
        page_icon="💖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_global_css()
    init_session_state()

    with st.spinner(""):
        auto_train_models()
    st.session_state.model_trained = True

    render_sidebar()

    active_step = get_journey_step()
    components.html(build_landing_html(active_step), height=960, scrolling=True)


if __name__ == "__main__":
    main()
