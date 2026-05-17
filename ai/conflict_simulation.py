"""Multi-agent conflict simulation using LLM.

Generates realistic future conflict scenarios and simulates how each partner
would argue, then predicts resolution probability.
"""

import random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai.llm_client import get_llm_response
from config import DOMAIN_OPTIONS


CONFLICT_TEMPLATES = {
    "career": {
        "title": "Career vs Family Expectations",
        "description": "Disagreement over career priorities and work-life balance after marriage.",
    },
    "location": {
        "title": "Living Location Dispute",
        "description": "Conflict about where to settle - abroad vs local, or near which family.",
    },
    "family_structure": {
        "title": "Joint vs Nuclear Family Tension",
        "description": "Clash over living with in-laws vs establishing independent household.",
    },
    "children": {
        "title": "Children and Parenting Conflict",
        "description": "Different views on having children, timing, number, and parenting style.",
    },
    "roles": {
        "title": "Gender Roles and Responsibilities",
        "description": "Disagreement about household duties, decision-making power, and equality.",
    },
    "finances": {
        "title": "Financial Management Clash",
        "description": "Conflict over money management, family financial support, and spending.",
    },
    "religion": {
        "title": "Religious Practice Differences",
        "description": "Different levels of religious observance causing daily life friction.",
    },
}


def detect_conflicts(person_a, person_b):
    """Detect conflict areas between two profiles.

    Returns list of conflicts sorted by severity.
    """
    conflicts = []

    for domain, options in DOMAIN_OPTIONS.items():
        val_a = person_a.get(domain)
        val_b = person_b.get(domain)
        if val_a is None or val_b is None:
            continue

        idx_a = options.index(val_a) if val_a in options else 0
        idx_b = options.index(val_b) if val_b in options else 0
        max_dist = len(options) - 1

        if max_dist == 0:
            continue

        distance = abs(idx_a - idx_b) / max_dist

        if distance > 0.3:  # Threshold for flagging as conflict
            severity = "HIGH" if distance > 0.66 else "MEDIUM"
            template = CONFLICT_TEMPLATES.get(domain, {"title": domain, "description": ""})

            # Estimate resolution probability based on distance and personality
            agree_a = person_a.get("agreeableness", 0.5)
            agree_b = person_b.get("agreeableness", 0.5)
            openness_a = person_a.get("openness", 0.5)
            openness_b = person_b.get("openness", 0.5)

            resolution_base = 1 - distance
            resolution_personality = (agree_a + agree_b + openness_a + openness_b) / 4
            resolution_prob = (0.6 * resolution_base + 0.4 * resolution_personality) * 100
            resolution_prob = max(10, min(90, resolution_prob))

            conflicts.append({
                "domain": domain,
                "title": template["title"],
                "description": template["description"],
                "severity": severity,
                "distance": round(distance, 2),
                "resolution_probability": round(resolution_prob, 1),
                "person_a_value": val_a,
                "person_b_value": val_b,
            })

    conflicts.sort(key=lambda x: x["distance"], reverse=True)
    return conflicts


def simulate_conflict(person_a, person_b, conflict, use_llm=True):
    """Simulate a specific conflict using multi-agent LLM.

    Two AI agents role-play each partner's argumentation style.
    """
    if not use_llm:
        return _template_simulation(person_a, person_b, conflict)

    system_prompt = """You are simulating a marriage compatibility conflict analysis for Pakistani couples.
You will role-play both sides of an argument based on their profiles, then assess resolution likelihood.
Be culturally sensitive to Pakistani norms around family, religion, and gender roles.
Format your response with clear sections: Partner A's Perspective, Partner B's Perspective, and Resolution Assessment."""

    prompt = f"""Simulate a conflict between two potential marriage partners:

**Conflict: {conflict['title']}**
{conflict['description']}

**Partner A's stance:** {conflict['person_a_value'].replace('_', ' ')}
- Agreeableness: {person_a.get('agreeableness', 0.5):.1f}/1.0
- Openness: {person_a.get('openness', 0.5):.1f}/1.0

**Partner B's stance:** {conflict['person_b_value'].replace('_', ' ')}
- Agreeableness: {person_b.get('agreeableness', 0.5):.1f}/1.0
- Openness: {person_b.get('openness', 0.5):.1f}/1.0

Severity: {conflict['severity']}

Simulate how each partner would argue their position in a Pakistani cultural context.
Then assess: What is the probability they can resolve this? What compromise might work?"""

    response, used_api = get_llm_response(prompt, system_prompt, temperature=0.7)
    return {
        "conflict": conflict,
        "simulation": response,
        "used_api": used_api,
    }


def _template_simulation(person_a, person_b, conflict):
    """Template-based conflict simulation when LLM is unavailable."""
    domain = conflict["domain"]
    sev = conflict["severity"]
    res_prob = conflict["resolution_probability"]

    simulation = f"""**Conflict Analysis: {conflict['title']}**

**Partner A's Position ({conflict['person_a_value'].replace('_', ' ').title()}):**
Partner A feels strongly about this aspect of their future life. Based on their personality profile (agreeableness: {person_a.get('agreeableness', 0.5):.1f}, openness: {person_a.get('openness', 0.5):.1f}), they are {'likely to be flexible' if person_a.get('agreeableness', 0.5) > 0.6 else 'somewhat rigid'} in negotiations.

**Partner B's Position ({conflict['person_b_value'].replace('_', ' ').title()}):**
Partner B has a different vision for this area. With agreeableness of {person_b.get('agreeableness', 0.5):.1f} and openness of {person_b.get('openness', 0.5):.1f}, they {'may be willing to compromise' if person_b.get('openness', 0.5) > 0.5 else 'may find compromise difficult'}.

**Resolution Assessment:**
- Severity: {sev}
- Resolution Probability: {res_prob:.0f}%
- {'This is a critical conflict that requires professional mediation.' if sev == 'HIGH' else 'This conflict can likely be resolved through honest dialogue.'}
- Suggested approach: {'Pre-marital counseling focused on this specific area' if res_prob < 50 else 'Structured family discussion with both sets of parents'}"""

    return {
        "conflict": conflict,
        "simulation": simulation,
        "used_api": False,
    }


def run_full_simulation(person_a, person_b, use_llm=True):
    """Run complete conflict detection and simulation.

    Returns overall conflict forecast with individual simulations.
    """
    conflicts = detect_conflicts(person_a, person_b)

    if not conflicts:
        return {
            "overall_resolution_score": 85.0,
            "conflicts": [],
            "simulations": [],
            "summary": "No major conflicts detected. The couple shows strong alignment across all life domains.",
        }

    simulations = []
    for conflict in conflicts[:5]:  # Top 5 conflicts
        sim = simulate_conflict(person_a, person_b, conflict, use_llm=use_llm)
        simulations.append(sim)

    # Overall resolution score = average of individual resolution probabilities
    avg_resolution = sum(c["resolution_probability"] for c in conflicts) / len(conflicts)

    return {
        "overall_resolution_score": round(avg_resolution, 1),
        "conflicts": conflicts,
        "simulations": simulations,
        "summary": f"Detected {len(conflicts)} conflict areas. Average resolution probability: {avg_resolution:.0f}%.",
    }
