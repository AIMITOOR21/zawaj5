"""Dynamic scenario generation using LLM.

Generates culturally-relevant interactive scenarios for assessment.
Falls back to pre-built scenarios when LLM is unavailable.
"""

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai.llm_client import get_llm_response
from config import DATA_DIR


def load_scenarios():
    """Load pre-built scenarios from JSON file."""
    path = DATA_DIR / "scenarios.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_dynamic_scenario(domain, existing_scenarios=None):
    """Generate a new scenario using LLM for a given domain."""
    system_prompt = """You are creating interactive assessment scenarios for a Pakistani marriage compatibility system.
Create culturally authentic scenarios that reveal true values about marriage and family life.
Each scenario should have exactly 4 choices, ordered from most traditional to most progressive.
Return ONLY valid JSON."""

    prompt = f"""Create a new interactive scenario for the domain: {domain}

The scenario should:
1. Be set in a realistic Pakistani family context
2. Present a dilemma that reveals values about {domain}
3. Have 4 choices from most traditional to most progressive
4. Each choice should map to a value vector

Return JSON format:
{{
  "domain": "{domain}",
  "title": "Short Title",
  "scenario": "The scenario description...",
  "choices": [
    {{"text": "Choice text", "value": "option_value", "vector": {{"individualism": 0.1, "tradition": 0.9}}}},
    ...
  ]
}}"""

    response, used_api = get_llm_response(prompt, system_prompt, temperature=0.8)

    if used_api:
        try:
            # Try to parse JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback to existing scenarios
    scenarios = load_scenarios()
    domain_scenarios = [s for s in scenarios if s["domain"] == domain]
    if domain_scenarios:
        return domain_scenarios[0]
    return scenarios[0]
