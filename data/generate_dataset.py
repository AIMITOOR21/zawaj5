"""Synthetic dataset generator for Zawaj.

Generates realistic Pakistani couple profiles with compatibility labels.
Uses rule-based generation with controlled noise for training ML models.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_OPTIONS, GENERATED_DIR


def generate_individual_profile(rng):
    """Generate a single person's life-goal profile."""
    profile = {}
    for domain, options in DOMAIN_OPTIONS.items():
        profile[domain] = rng.choice(options)

    # Personality traits (Big Five, 0-1 scale)
    profile["openness"] = rng.beta(5, 5)
    profile["conscientiousness"] = rng.beta(5, 5)
    profile["extraversion"] = rng.beta(5, 5)
    profile["agreeableness"] = rng.beta(5, 5)
    profile["neuroticism"] = rng.beta(3, 7)

    # Demographics
    profile["age"] = int(rng.normal(26, 4))
    profile["age"] = max(18, min(45, profile["age"]))
    profile["education"] = rng.choice(
        ["matric", "intermediate", "bachelors", "masters", "phd"],
        p=[0.05, 0.15, 0.40, 0.30, 0.10],
    )
    profile["city"] = rng.choice(
        ["Lahore", "Karachi", "Islamabad", "Peshawar", "Faisalabad", "Multan", "Quetta"],
        p=[0.25, 0.25, 0.15, 0.10, 0.10, 0.10, 0.05],
    )
    return profile


def compute_domain_similarity(val_a, val_b, options):
    """Compute similarity between two domain values (0-1)."""
    idx_a = options.index(val_a)
    idx_b = options.index(val_b)
    max_dist = len(options) - 1
    if max_dist == 0:
        return 1.0
    return 1.0 - abs(idx_a - idx_b) / max_dist


def compute_compatibility(profile_a, profile_b):
    """Compute ground-truth compatibility score between two profiles."""
    score = 0.0
    weights = {
        "career": 0.18, "location": 0.15, "family_structure": 0.18,
        "children": 0.14, "roles": 0.13, "finances": 0.10, "religion": 0.12,
    }

    for domain, weight in weights.items():
        options = DOMAIN_OPTIONS[domain]
        sim = compute_domain_similarity(profile_a[domain], profile_b[domain], options)
        score += weight * sim

    # Personality compatibility (complementary on some, similar on others)
    personality_sim = 0.0
    # Similar: conscientiousness, openness
    personality_sim += 1 - abs(profile_a["openness"] - profile_b["openness"])
    personality_sim += 1 - abs(profile_a["conscientiousness"] - profile_b["conscientiousness"])
    # Complementary: extraversion (one intro + one extro can work)
    personality_sim += 0.5 + 0.5 * (1 - abs(profile_a["extraversion"] - profile_b["extraversion"]))
    # Similar: agreeableness (both agreeable = good)
    personality_sim += min(profile_a["agreeableness"], profile_b["agreeableness"])
    # Low neuroticism is better
    personality_sim += 1 - (profile_a["neuroticism"] + profile_b["neuroticism"]) / 2
    personality_sim /= 5  # normalize to 0-1

    # Final score: 85% life goals + 15% personality
    raw_score = 0.85 * score + 0.15 * personality_sim
    return raw_score * 100


def generate_family_features(rng, profile):
    """Generate family-level features for a person."""
    family = {}
    family["family_size"] = int(rng.choice([3, 4, 5, 6, 7, 8], p=[0.05, 0.15, 0.25, 0.25, 0.20, 0.10]))
    family["father_authority"] = rng.beta(6, 4)  # 0-1, higher = more authoritative
    family["mother_influence"] = rng.beta(5, 5)
    family["sibling_support"] = rng.beta(5, 5)
    family["family_conservatism"] = rng.beta(5, 5)
    family["economic_status"] = rng.choice(
        ["lower", "middle", "upper_middle", "upper"],
        p=[0.15, 0.40, 0.30, 0.15],
    )

    # Correlate family conservatism with individual preferences
    if profile["religion"] in ["very_strict"]:
        family["family_conservatism"] = min(1.0, family["family_conservatism"] + 0.2)
    if profile["family_structure"] in ["joint_family"]:
        family["father_authority"] = min(1.0, family["father_authority"] + 0.15)

    return family


def generate_dataset(n_couples=10000, seed=42):
    """Generate the full synthetic couples dataset."""
    rng = np.random.default_rng(seed)
    records = []

    for i in range(n_couples):
        pa = generate_individual_profile(rng)
        pb = generate_individual_profile(rng)
        fa = generate_family_features(rng, pa)
        fb = generate_family_features(rng, pb)

        score = compute_compatibility(pa, pb)
        # Add noise
        score += rng.normal(0, 5)
        score = max(0, min(100, score))

        # Classification label
        if score >= 70:
            label = "compatible"
        elif score >= 45:
            label = "partially_compatible"
        else:
            label = "incompatible"

        record = {"couple_id": i}
        # Person A features
        for k, v in pa.items():
            record[f"a_{k}"] = v
        for k, v in fa.items():
            record[f"a_{k}"] = v
        # Person B features
        for k, v in pb.items():
            record[f"b_{k}"] = v
        for k, v in fb.items():
            record[f"b_{k}"] = v
        # Target
        record["compatibility_score"] = round(score, 2)
        record["compatibility_label"] = label

        records.append(record)

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    print("Generating synthetic dataset (10,000 couples)...")
    df = generate_dataset(n_couples=10000)
    output_path = GENERATED_DIR / "couples_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")
    print(f"Shape: {df.shape}")
    print(f"\nLabel distribution:")
    print(df["compatibility_label"].value_counts())
    print(f"\nScore statistics:")
    print(df["compatibility_score"].describe())
