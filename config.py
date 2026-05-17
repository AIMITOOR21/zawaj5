"""Zawaj — Configuration and Constants.

AI-Powered Pre-Marriage Compatibility for Pakistani Families.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------- Paths ----------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
GENERATED_DIR = DATA_DIR / "generated"
MODELS_DIR = BASE_DIR / "models" / "saved"

GENERATED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- OpenAI ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# ---------- Life domains and weights ----------
DOMAIN_WEIGHTS = {
    "career": 0.18,
    "location": 0.15,
    "family_structure": 0.18,
    "children": 0.14,
    "roles": 0.13,
    "finances": 0.10,
    "religion": 0.12,
}

# Ensemble weights: individual partner alignment + in-law alignment + conflict resolution
ENSEMBLE_WEIGHTS = {
    "individual": 0.50,
    "inlaws": 0.30,
    "conflict_resolution": 0.20,
}

DOMAIN_OPTIONS = {
    "career": ["career_focused", "balanced", "family_focused", "no_work"],
    "location": ["stay_local", "same_city", "willing_relocate", "go_abroad"],
    "family_structure": ["joint_family", "joint_nearby", "nuclear_visits", "fully_nuclear"],
    "children": ["no_children", "one_child", "two_children", "three_plus"],
    "roles": ["traditional", "mostly_traditional", "egalitarian", "role_reversal"],
    "finances": ["separate", "partial_pool", "full_pool", "spouse_manages"],
    "religion": ["very_strict", "moderate", "liberal", "secular"],
}

PERSONALITY_TRAITS = [
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
]

# ---------- Compatibility thresholds ----------
THRESHOLDS = {
    "high": 70,
    "moderate": 45,
    "low": 0,
}

# ---------- Pink / White Wedding Theme ----------
COLORS = {
    # Primary palette
    "rose": "#D4577A",         # deep rose (primary)
    "blush": "#F8D7DE",         # blush pink (secondary)
    "soft_pink": "#FDEEF2",     # very light pink
    "gold": "#C9A96E",          # muted gold accent
    "deep": "#5C2A3E",          # deep maroon for text
    "charcoal": "#3E3E3E",      # body text
    "white": "#FFFFFF",
    "mute": "#8A6B7A",          # muted rose-gray
    # Backward-compatible aliases used by older modules
    "berry": "#D4577A",
    "dusty_rose": "#D4577A",
    "cream": "#FDEEF2",
    "dark": "#5C2A3E",
    # Status colors (tuned to pink theme)
    "success": "#6BAF73",
    "warning": "#E8A846",
    "danger": "#D4577A",
}
