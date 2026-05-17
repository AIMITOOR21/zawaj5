"""OpenAI LLM client with automatic fallback to mock/template responses."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OPENAI_API_KEY, OPENAI_MODEL


def get_llm_response(prompt, system_prompt=None, temperature=0.7, max_tokens=1000):
    """Get LLM response from OpenAI API or mock fallback.

    Returns:
        tuple: (response_text, used_real_api: bool)
    """
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content, True
        except Exception as e:
            print(f"OpenAI API error: {e}, falling back to mock")

    return _mock_response(prompt), False


def _mock_response(prompt):
    """Generate template-based mock response when no API key is available."""
    prompt_lower = prompt.lower()

    if "conflict" in prompt_lower or "argument" in prompt_lower:
        return _mock_conflict_response(prompt)
    elif "advice" in prompt_lower or "improvement" in prompt_lower:
        return _mock_advice_response(prompt)
    elif "scenario" in prompt_lower:
        return _mock_scenario_response(prompt)
    else:
        return _mock_general_response(prompt)


def _mock_conflict_response(prompt):
    return """Based on the profile differences, here are the predicted conflict scenarios:

**Conflict 1: Career vs Family Expectations (Severity: HIGH)**
Partner A values career growth while Partner B expects a family-focused lifestyle. This creates tension around work hours, travel, and household responsibilities. Resolution will require honest discussion about compromises on both sides.

**Conflict 2: Living Arrangement Disagreement (Severity: HIGH)**
Different expectations about joint vs nuclear family living. One partner's family expects them to live together, while the other values independence. This is one of the most common sources of marital friction in Pakistani families.

**Conflict 3: Financial Management Style (Severity: MEDIUM)**
Different approaches to managing household finances. One prefers pooled income while the other wants financial independence. Establishing a clear financial plan early in marriage is critical.

**Resolution Assessment:**
- Conflict 1: Resolution probability 35% without intervention, 65% with counseling
- Conflict 2: Resolution probability 40% without intervention, 70% with mediation
- Conflict 3: Resolution probability 55% without intervention, 80% with discussion"""


def _mock_advice_response(prompt):
    return """## Compatibility Improvement Plan

Based on the counterfactual analysis, here are actionable steps to improve compatibility:

### High-Impact Changes:
1. **Career Flexibility Discussion** - If both partners agree on a balanced approach to career vs family time, the compatibility score could increase by approximately 15-18%. Consider part-time work options or flexible schedules.

2. **Family Structure Negotiation** - If the families can agree on a modified living arrangement (e.g., nuclear household with regular family visits), this could add 10-12% to the score.

3. **Financial Planning Session** - Establishing a joint financial plan with agreed-upon allocations for family support, savings, and personal spending could improve financial alignment by 8-10%.

### Moderate-Impact Changes:
4. **Religious Practice Alignment** - Finding common ground on religious observance level through mutual understanding and respect.

5. **Role Distribution Agreement** - Creating a written household responsibility plan that both partners find fair.

### Recommendation:
We suggest a facilitated pre-marital discussion covering these topics in order of priority. A trained counselor can help navigate sensitive cultural dynamics."""


def _mock_scenario_response(prompt):
    return """Here is a culturally relevant scenario for assessment:

**Scenario: The Job Transfer**
Your spouse receives a promotion that requires transferring to another city for 2 years. This means leaving behind your joint family setup and your children's current school. Your in-laws strongly oppose the move.

**Choice A:** Support the transfer fully - career growth benefits the whole family
**Choice B:** Negotiate for a shorter assignment of 6 months to test it out
**Choice C:** Ask your spouse to decline - family stability is more important
**Choice D:** Suggest your spouse goes alone while you stay with the family"""


def _mock_general_response(prompt):
    return """Based on the analysis, the couple shows both areas of alignment and significant differences that need attention. The key areas of concern involve differing expectations about family structure and career priorities. With open communication and willingness to compromise, many of these differences can be addressed through structured pre-marital counseling and family discussions."""
