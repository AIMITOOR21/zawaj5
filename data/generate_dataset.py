"""Synthetic dataset generator for Zawaj — Restructured (Individuals + Couples).

Generates TWO datasets:
  1. individuals.csv — 5,000 unique Pakistani individuals (each with a unique person_id)
  2. couples_dataset.csv — 10,000 pairings between those individuals with compatibility labels

Same individual can appear in multiple pairings, reflecting how real matchmaking works:
one user can be a candidate for many potential matches, not just one fixed partner.

The couples_dataset.csv structure stays identical to before (so training works unchanged).
The individuals.csv is NEW — it proves the dataset supports many-to-many matching.
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

    # Personality compatibility
    personality_sim = 0.0
    personality_sim += 1 - abs(profile_a["openness"] - profile_b["openness"])
    personality_sim += 1 - abs(profile_a["conscientiousness"] - profile_b["conscientiousness"])
    personality_sim += 0.5 + 0.5 * (1 - abs(profile_a["extraversion"] - profile_b["extraversion"]))
    personality_sim += min(profile_a["agreeableness"], profile_b["agreeableness"])
    personality_sim += 1 - (profile_a["neuroticism"] + profile_b["neuroticism"]) / 2
    personality_sim /= 5

    raw_score = 0.85 * score + 0.15 * personality_sim
    return raw_score * 100


def generate_family_features(rng, profile):
    """Generate family-level features for a person."""
    family = {}
    family["family_size"] = int(rng.choice([3, 4, 5, 6, 7, 8], p=[0.05, 0.15, 0.25, 0.25, 0.20, 0.10]))
    family["father_authority"] = rng.beta(6, 4)
    family["mother_influence"] = rng.beta(5, 5)
    family["sibling_support"] = rng.beta(5, 5)
    family["family_conservatism"] = rng.beta(5, 5)
    family["economic_status"] = rng.choice(
        ["lower", "middle", "upper_middle", "upper"],
        p=[0.15, 0.40, 0.30, 0.15],
    )

    if profile["religion"] in ["very_strict"]:
        family["family_conservatism"] = min(1.0, family["family_conservatism"] + 0.2)
    if profile["family_structure"] in ["joint_family"]:
        family["father_authority"] = min(1.0, family["father_authority"] + 0.15)

    return family


def generate_individuals(n_individuals=5000, seed=42):
    """Generate a pool of unique individual profiles.

    Each individual gets a unique person_id. They can later be paired up
    into couples — the same individual may appear in multiple pairings.
    """
    rng = np.random.default_rng(seed)
    records = []

    # Assign gender so we can build heterosexual pairings
    for i in range(n_individuals):
        profile = generate_individual_profile(rng)
        family = generate_family_features(rng, profile)

        # Roughly equal split of genders
        gender = "female" if i % 2 == 0 else "male"

        record = {
            "person_id": f"P{i:05d}",
            "gender": gender,
        }
        record.update(profile)
        record.update(family)
        records.append(record)

    df = pd.DataFrame(records)
    return df


def generate_couples_from_individuals(individuals_df, n_couples=10000, seed=42):
    """Generate couple pairings by sampling from the individuals pool.

    Each couple = one female + one male, sampled independently.
    Same individual can appear in multiple couples — reflecting real-world
    where one user is a candidate for many potential matches.
    """
    rng = np.random.default_rng(seed)
    records = []

    females = individuals_df[individuals_df["gender"] == "female"].reset_index(drop=True)
    males = individuals_df[individuals_df["gender"] == "male"].reset_index(drop=True)

    for i in range(n_couples):
        # Sample one female and one male from the pool
        f_idx = rng.integers(0, len(females))
        m_idx = rng.integers(0, len(males))
        person_a = females.iloc[f_idx]
        person_b = males.iloc[m_idx]

        # Extract profile dicts (excluding person_id and gender)
        skip_cols = {"person_id", "gender"}
        pa = {k: v for k, v in person_a.items() if k not in skip_cols}
        pb = {k: v for k, v in person_b.items() if k not in skip_cols}

        # Compute compatibility (same logic as before)
        score = compute_compatibility(pa, pb)
        score += rng.normal(0, 5)
        score = max(0, min(100, score))

        if score >= 70:
            label = "compatible"
        elif score >= 45:
            label = "partially_compatible"
        else:
            label = "incompatible"

        # Build couple record — IDENTICAL structure to before (no new columns)
        # so training pipeline works unchanged. IDs are tracked in print stats only.
        record = {"couple_id": i}
        for k, v in pa.items():
            record[f"a_{k}"] = v
        for k, v in pb.items():
            record[f"b_{k}"] = v

        record["compatibility_score"] = round(score, 2)
        record["compatibility_label"] = label

        # Track IDs separately for the many-to-many statistics
        record["_a_id_internal"] = person_a["person_id"]
        record["_b_id_internal"] = person_b["person_id"]
        records.append(record)

    df = pd.DataFrame(records)
    # Stash the ID columns as an attribute for stats, then drop them from the final CSV
    df.attrs["a_ids"] = df["_a_id_internal"].tolist()
    df.attrs["b_ids"] = df["_b_id_internal"].tolist()
    df = df.drop(columns=["_a_id_internal", "_b_id_internal"])
    return df


def generate_dataset(n_couples=10000, n_individuals=5000, seed=42):
    """Generate the full dataset — both individuals and couples.

    Backward-compatible: returns the couples dataframe (same as before)
    so existing train.py works unchanged. Also writes individuals.csv to disk.
    """
    # Step 1: Generate the pool of unique individuals
    individuals_df = generate_individuals(n_individuals=n_individuals, seed=seed)

    # Save individuals.csv alongside couples_dataset.csv
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    individuals_path = GENERATED_DIR / "individuals.csv"
    individuals_df.to_csv(individuals_path, index=False)
    print(f"Individuals saved to {individuals_path} — {individuals_df.shape}")

    # Step 2: Generate couple pairings from the pool
    couples_df = generate_couples_from_individuals(
        individuals_df, n_couples=n_couples, seed=seed + 1
    )

    # Show how many times the same person appears across couples (proof of many-to-many)
    import collections
    a_counts = collections.Counter(couples_df.attrs["a_ids"])
    b_counts = collections.Counter(couples_df.attrs["b_ids"])
    print(f"Most-paired female appears in {max(a_counts.values())} couples")
    print(f"Most-paired male appears in {max(b_counts.values())} couples")
    print(f"Average pairings per individual: {couples_df.shape[0] * 2 / n_individuals:.1f}")

    return couples_df


if __name__ == "__main__":
    print("Generating synthetic dataset...")
    print(f"  - 5,000 unique individuals")
    print(f"  - 10,000 couple pairings sampled from those individuals")
    print()

    df = generate_dataset(n_couples=10000, n_individuals=5000)
    output_path = GENERATED_DIR / "couples_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"\nCouples dataset saved to {output_path}")
    print(f"Shape: {df.shape}")
    print(f"\nLabel distribution:")
    print(df["compatibility_label"].value_counts())
    print(f"\nScore statistics:")
    print(df["compatibility_score"].describe())
