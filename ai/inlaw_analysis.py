"""Zawaj — In-Laws Triangle Analysis.

Analyzes responses from three sources:
  - The girl's (partner A's) expectations of in-laws
  - The boy's (partner B's) claims about his family
  - The in-laws' actual answers (mother-in-law, father-in-law, sister-in-law)

Detects contradictions between boy claims and in-law actual answers,
computes alignment between girl expectations and in-law actual answers,
and produces a structured triangle analysis.
"""

import json
from pathlib import Path
from config import DATA_DIR


def load_inlaw_scenarios():
    with open(DATA_DIR / "inlaw_scenarios.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_score_for_answer(role_scenarios, scenario_id, value):
    """Return the score attached to a chosen value for a given scenario."""
    for s in role_scenarios:
        if s["id"] == scenario_id:
            for c in s["choices"]:
                if c["value"] == value:
                    return c["score"]
    return None


def compute_inlaw_alignment(inlaw_responses, girl_expectations):
    """Compute alignment between what in-laws said and what the girl hopes for.

    Returns an alignment score in 0-100 where 100 means perfect alignment.
    """
    scenarios = load_inlaw_scenarios()
    role_data = {
        "mil": ("mother_in_law", scenarios["mother_in_law"]),
        "fil": ("father_in_law", scenarios["father_in_law"]),
        "sil": ("sister_in_law", scenarios["sister_in_law"]),
    }
    girl_scenarios = scenarios["girl_expectations"]

    diffs = []
    for ge in girl_scenarios:
        mapped_id = ge["maps_to"]
        # find role
        role_key = mapped_id.split("_")[0]  # "mil" / "fil" / "sil"
        if role_key not in role_data:
            continue
        role_name, role_list = role_data[role_key]

        girl_resp = girl_expectations.get(ge["id"])
        inlaw_resp = inlaw_responses.get(mapped_id)
        if not girl_resp or not inlaw_resp:
            continue

        girl_score = get_score_for_answer(girl_scenarios, ge["id"], girl_resp)
        inlaw_score = get_score_for_answer(role_list, mapped_id, inlaw_resp)

        if girl_score is None or inlaw_score is None:
            continue
        diffs.append(abs(girl_score - inlaw_score))

    if not diffs:
        return 50.0
    avg_diff = sum(diffs) / len(diffs)
    # Convert diff -> alignment score (diff of 0 = 100, diff of 1 = 0)
    alignment = max(0.0, min(100.0, (1.0 - avg_diff) * 100))
    return round(alignment, 1)


def detect_contradictions(inlaw_responses, boy_claims):
    """Detect contradictions between what the boy claims about his family
    and what the family (in-laws) actually said.

    Returns list of dicts with:
        - topic, boy_said, family_said, severity (HIGH/MEDIUM/LOW), gap (0-1)
    """
    scenarios = load_inlaw_scenarios()
    boy_scenarios = scenarios["boy_claims"]
    role_map = {
        "mil": scenarios["mother_in_law"],
        "fil": scenarios["father_in_law"],
        "sil": scenarios["sister_in_law"],
    }

    contradictions = []
    for bc in boy_scenarios:
        mapped_id = bc["maps_to"]
        role_key = mapped_id.split("_")[0]
        role_list = role_map.get(role_key, [])

        boy_resp = boy_claims.get(bc["id"])
        inlaw_resp = inlaw_responses.get(mapped_id)
        if not boy_resp or not inlaw_resp:
            continue

        boy_score = get_score_for_answer(boy_scenarios, bc["id"], boy_resp)
        inlaw_score = get_score_for_answer(role_list, mapped_id, inlaw_resp)
        if boy_score is None or inlaw_score is None:
            continue

        gap = abs(boy_score - inlaw_score)
        if gap < 0.15:
            continue  # negligible

        severity = "HIGH" if gap >= 0.5 else ("MEDIUM" if gap >= 0.3 else "LOW")

        # Readable labels
        boy_text = next((c["text"] for c in bc["choices"] if c["value"] == boy_resp), boy_resp)
        inlaw_text = next(
            (c["text"] for s in role_list if s["id"] == mapped_id
             for c in s["choices"] if c["value"] == inlaw_resp),
            inlaw_resp,
        )
        role_nice = {"mil": "Mother-in-law", "fil": "Father-in-law", "sil": "Sister-in-law"}[role_key]

        contradictions.append({
            "topic": bc["topic"],
            "role": role_nice,
            "boy_said": boy_text,
            "family_said": inlaw_text,
            "gap": round(gap, 2),
            "severity": severity,
        })

    # Sort by severity (HIGH first), then gap
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    contradictions.sort(key=lambda c: (severity_order[c["severity"]], -c["gap"]))
    return contradictions


def build_triangle_analysis(inlaw_responses, boy_claims, girl_expectations):
    """Produce the full triangle analysis result dict."""
    alignment_score = compute_inlaw_alignment(inlaw_responses, girl_expectations)
    contradictions = detect_contradictions(inlaw_responses, boy_claims)

    # Summary stats
    high = sum(1 for c in contradictions if c["severity"] == "HIGH")
    medium = sum(1 for c in contradictions if c["severity"] == "MEDIUM")

    if alignment_score >= 75 and high == 0:
        verdict = "Strong Family Alignment"
        verdict_color = "#6BAF73"
    elif alignment_score >= 55 and high <= 1:
        verdict = "Moderate Family Alignment"
        verdict_color = "#E8A846"
    else:
        verdict = "Significant Friction Risk"
        verdict_color = "#D4577A"

    return {
        "inlaw_score": alignment_score,
        "contradictions": contradictions,
        "high_contradictions": high,
        "medium_contradictions": medium,
        "verdict": verdict,
        "verdict_color": verdict_color,
    }
