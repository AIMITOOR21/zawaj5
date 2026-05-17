"""Natural language advice generation using LLM.

Translates counterfactual XAI outputs and compatibility results
into human-readable improvement plans in English.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai.llm_client import get_llm_response


def generate_compatibility_advice(results, conflicts, counterfactuals=None):
    """Generate comprehensive compatibility advice using LLM.

    Args:
        results: Ensemble scoring results dict
        conflicts: List of detected conflicts
        counterfactuals: Optional DiCE counterfactual explanations

    Returns:
        str: Natural language advice
    """
    score = results["final_score"]
    label = results["label"]
    breakdown = results["breakdown"]

    system_prompt = """You are a culturally sensitive marriage counselor AI for Pakistani couples.
Provide constructive, balanced advice that respects Pakistani cultural norms while encouraging
healthy communication. Be specific and actionable. Never be judgmental."""

    cf_section = ""
    if counterfactuals:
        cf_section = f"\n\nCounterfactual Analysis (what could improve compatibility):\n"
        for cf in counterfactuals:
            cf_section += f"- If {cf['change']}: score improves by +{cf['improvement']}%\n"

    conflict_section = ""
    if conflicts:
        conflict_section = "\n\nDetected Conflicts:\n"
        for c in conflicts[:5]:
            conflict_section += f"- {c['title']} (Severity: {c['severity']}, Resolution: {c['resolution_probability']:.0f}%)\n"
            conflict_section += f"  Partner A: {c['person_a_value']}, Partner B: {c['person_b_value']}\n"

    prompt = f"""Generate a comprehensive compatibility improvement plan for this Pakistani couple:

**Compatibility Score: {score}% ({label})**

Score Breakdown:
- Individual Compatibility: {breakdown['Individual Compatibility']['score']}%
- Family Network: {breakdown['Family Network']['score']}%
- Conflict Resolution: {breakdown['Conflict Resolution']['score']}%
{conflict_section}{cf_section}

Please provide:
1. Overall assessment (2-3 sentences)
2. Top 3 priority areas to address (with specific, actionable steps)
3. Conversation starters for the couple to discuss difficult topics
4. Recommendation for next steps (counseling, family discussion, etc.)

Be culturally appropriate for Pakistani families."""

    response, used_api = get_llm_response(prompt, system_prompt, temperature=0.6, max_tokens=1500)
    return response


def generate_quick_summary(score, label, top_conflicts):
    """Generate a brief one-paragraph summary."""
    if score >= 70:
        tone = "strong alignment"
        outlook = "encouraging"
    elif score >= 45:
        tone = "moderate compatibility with some differences"
        outlook = "workable with discussion"
    else:
        tone = "significant differences"
        outlook = "requiring careful consideration"

    conflict_names = [c["title"] for c in top_conflicts[:3]] if top_conflicts else ["None detected"]

    return (
        f"This couple shows {tone} with an overall compatibility score of {score}%. "
        f"The outlook is {outlook}. "
        f"Key areas of concern: {', '.join(conflict_names)}. "
        f"{'A structured pre-marital discussion is recommended.' if score < 70 else 'The couple appears well-aligned for a successful partnership.'}"
    )
