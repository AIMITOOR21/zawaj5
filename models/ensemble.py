"""Ensemble model combining individual, in-laws, and conflict resolution scores."""

import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ENSEMBLE_WEIGHTS, THRESHOLDS


def compute_ensemble_score(individual_score, inlaw_score, conflict_score):
    """Compute final compatibility using weighted ensemble.

    Args:
        individual_score: Individual compatibility between partners (0-100)
        inlaw_score:      In-law alignment score from triangle analysis (0-100)
        conflict_score:   Conflict resolution probability average (0-100)
    """
    w = ENSEMBLE_WEIGHTS
    final = (
        w["individual"] * individual_score
        + w["inlaws"] * inlaw_score
        + w["conflict_resolution"] * conflict_score
    )
    final = np.clip(final, 0, 100)

    if final >= THRESHOLDS["high"]:
        label = "Compatible"
    elif final >= THRESHOLDS["moderate"]:
        label = "Partially Compatible"
    else:
        label = "Incompatible"

    return {
        "final_score": round(float(final), 1),
        "label": label,
        "breakdown": {
            "Partner Compatibility": {
                "score": round(float(individual_score), 1),
                "weight": w["individual"],
                "contribution": round(float(w["individual"] * individual_score), 1),
            },
            "In-Law Alignment": {
                "score": round(float(inlaw_score), 1),
                "weight": w["inlaws"],
                "contribution": round(float(w["inlaws"] * inlaw_score), 1),
            },
            "Conflict Resolution": {
                "score": round(float(conflict_score), 1),
                "weight": w["conflict_resolution"],
                "contribution": round(float(w["conflict_resolution"] * conflict_score), 1),
            },
        },
    }


def get_domain_scores(person_a, person_b, domain_options):
    """Compute per-domain alignment scores."""
    domain_scores = {}
    for domain, options in domain_options.items():
        val_a = person_a.get(domain)
        val_b = person_b.get(domain)
        if val_a is None or val_b is None:
            domain_scores[domain] = 50.0
            continue
        if val_a not in options or val_b not in options:
            domain_scores[domain] = 50.0
            continue
        idx_a = options.index(val_a)
        idx_b = options.index(val_b)
        max_dist = len(options) - 1
        sim = 1.0 if max_dist == 0 else 1 - abs(idx_a - idx_b) / max_dist
        domain_scores[domain] = round(sim * 100, 1)
    return domain_scores
