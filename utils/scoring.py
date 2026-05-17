"""Scoring utilities for Zawaj."""

import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_OPTIONS, DOMAIN_WEIGHTS


def compute_domain_alignment(person_a, person_b):
    """Compute alignment scores for each life domain.

    Returns dict mapping domain -> alignment percentage (0-100).
    """
    scores = {}
    for domain, options in DOMAIN_OPTIONS.items():
        val_a = person_a.get(domain)
        val_b = person_b.get(domain)
        if val_a is None or val_b is None:
            scores[domain] = 50.0
            continue
        if val_a not in options or val_b not in options:
            scores[domain] = 50.0
            continue
        idx_a = options.index(val_a)
        idx_b = options.index(val_b)
        max_dist = max(len(options) - 1, 1)
        scores[domain] = round((1 - abs(idx_a - idx_b) / max_dist) * 100, 1)
    return scores


def compute_weighted_score(domain_scores):
    """Compute weighted average score from domain alignment scores."""
    total = 0
    for domain, score in domain_scores.items():
        weight = DOMAIN_WEIGHTS.get(domain, 0.1)
        total += weight * score
    return round(total, 1)


def compute_personality_compatibility(person_a, person_b):
    """Compute personality trait compatibility."""
    traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    scores = {}
    for trait in traits:
        a = person_a.get(trait, 0.5)
        b = person_b.get(trait, 0.5)
        if trait == "neuroticism":
            # Lower is better for both
            scores[trait] = round((1 - (a + b) / 2) * 100, 1)
        elif trait == "extraversion":
            # Complementary can work
            scores[trait] = round((0.5 + 0.5 * (1 - abs(a - b))) * 100, 1)
        else:
            # Similar is better
            scores[trait] = round((1 - abs(a - b)) * 100, 1)
    return scores


def get_score_color(score):
    """Get color for a score value (pink wedding theme)."""
    if score >= 70:
        return "#6BAF73"   # soft green
    elif score >= 45:
        return "#E8A846"   # warm amber
    return "#D4577A"       # rose


def get_score_label(score):
    """Get label for a score value."""
    if score >= 70:
        return "Compatible"
    elif score >= 45:
        return "Partially Compatible"
    return "Incompatible"
