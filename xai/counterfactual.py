"""DiCE Counterfactual Explanations for compatibility improvement."""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_OPTIONS, DOMAIN_WEIGHTS


def generate_counterfactuals(person_a, person_b, current_score, n_counterfactuals=5):
    """Generate counterfactual explanations showing what changes would improve compatibility.

    Uses a rule-based approach inspired by DiCE principles:
    finds the minimum changes to maximize score improvement.

    Args:
        person_a: Dict of person A's answers
        person_b: Dict of person B's answers
        current_score: Current compatibility score
        n_counterfactuals: Number of counterfactuals to generate

    Returns:
        List of counterfactual dicts with change descriptions and improved scores
    """
    counterfactuals = []

    for domain, options in DOMAIN_OPTIONS.items():
        val_a = person_a.get(domain)
        val_b = person_b.get(domain)
        if val_a is None or val_b is None:
            continue
        if val_a not in options or val_b not in options:
            continue

        idx_a = options.index(val_a)
        idx_b = options.index(val_b)

        if idx_a == idx_b:
            continue  # Already aligned

        weight = DOMAIN_WEIGHTS.get(domain, 0.1)
        max_dist = len(options) - 1
        current_dist = abs(idx_a - idx_b) / max_dist
        current_contribution = (1 - current_dist) * weight * 100

        # Try moving each person closer to the other
        for direction in ["a_to_b", "b_to_a", "meet_middle"]:
            if direction == "a_to_b":
                new_a_idx = idx_b
                new_a = options[new_a_idx]
                new_b = val_b
                change_desc = f"If Partner A changes {domain.replace('_', ' ')} from '{val_a.replace('_', ' ')}' to '{new_a.replace('_', ' ')}'"
                who_changes = "Partner A"
            elif direction == "b_to_a":
                new_b_idx = idx_a
                new_a = val_a
                new_b = options[new_b_idx]
                change_desc = f"If Partner B changes {domain.replace('_', ' ')} from '{val_b.replace('_', ' ')}' to '{new_b.replace('_', ' ')}'"
                who_changes = "Partner B"
            else:
                mid = (idx_a + idx_b) // 2
                new_a = options[mid]
                new_b = options[mid]
                change_desc = f"If both partners compromise on {domain.replace('_', ' ')} to '{options[mid].replace('_', ' ')}'"
                who_changes = "Both"

            # Calculate improvement
            new_idx_a = options.index(new_a)
            new_idx_b = options.index(new_b)
            new_dist = abs(new_idx_a - new_idx_b) / max_dist
            new_contribution = (1 - new_dist) * weight * 100
            improvement = new_contribution - current_contribution

            if improvement > 1:  # Only meaningful improvements
                counterfactuals.append({
                    "domain": domain,
                    "change": change_desc,
                    "who_changes": who_changes,
                    "improvement": round(improvement, 1),
                    "new_score": round(current_score + improvement, 1),
                    "feasibility": _assess_feasibility(domain, direction),
                })

    # Sort by improvement and return top N
    counterfactuals.sort(key=lambda x: x["improvement"], reverse=True)

    # Remove duplicates by domain (keep best per domain)
    seen_domains = set()
    unique = []
    for cf in counterfactuals:
        if cf["domain"] not in seen_domains:
            seen_domains.add(cf["domain"])
            unique.append(cf)
        if len(unique) >= n_counterfactuals:
            break

    return unique


def _assess_feasibility(domain, direction):
    """Assess cultural feasibility of a change in Pakistani context."""
    # Changes that are harder culturally
    hard_changes = {
        ("family_structure", "a_to_b"): "Moderate - requires family discussion",
        ("family_structure", "b_to_a"): "Moderate - requires family discussion",
        ("religion", "a_to_b"): "Difficult - deeply personal",
        ("religion", "b_to_a"): "Difficult - deeply personal",
        ("roles", "a_to_b"): "Moderate - cultural norms involved",
        ("roles", "b_to_a"): "Moderate - cultural norms involved",
    }

    key = (domain, direction)
    if key in hard_changes:
        return hard_changes[key]

    if direction == "meet_middle":
        return "Feasible - compromise approach"

    return "Feasible - with open discussion"


def compute_max_potential_score(person_a, person_b, current_score, counterfactuals):
    """Calculate the maximum possible score if all counterfactuals are applied."""
    total_improvement = sum(cf["improvement"] for cf in counterfactuals)
    max_score = min(100, current_score + total_improvement)
    return round(max_score, 1)
