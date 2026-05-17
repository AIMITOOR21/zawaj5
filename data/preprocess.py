"""Data preprocessing for Zawaj.

Handles encoding, normalization, and feature engineering for the ML pipeline.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DOMAIN_OPTIONS, PERSONALITY_TRAITS, GENERATED_DIR


def encode_categorical(df):
    """Encode categorical domain answers as ordinal integers."""
    encoders = {}
    encoded_df = df.copy()
    categorical_cols = []

    for prefix in ["a_", "b_"]:
        for domain, options in DOMAIN_OPTIONS.items():
            col = f"{prefix}{domain}"
            if col in encoded_df.columns:
                le = LabelEncoder()
                le.fit(options)
                encoded_df[col] = le.transform(encoded_df[col])
                encoders[col] = le
                categorical_cols.append(col)

        # Encode education
        edu_col = f"{prefix}education"
        if edu_col in encoded_df.columns:
            edu_order = ["matric", "intermediate", "bachelors", "masters", "phd"]
            le = LabelEncoder()
            le.fit(edu_order)
            encoded_df[edu_col] = le.transform(encoded_df[edu_col])
            encoders[edu_col] = le
            categorical_cols.append(edu_col)

        # Encode city
        city_col = f"{prefix}city"
        if city_col in encoded_df.columns:
            le = LabelEncoder()
            encoded_df[city_col] = le.fit_transform(encoded_df[city_col])
            encoders[city_col] = le
            categorical_cols.append(city_col)

        # Encode economic status
        econ_col = f"{prefix}economic_status"
        if econ_col in encoded_df.columns:
            econ_order = ["lower", "middle", "upper_middle", "upper"]
            le = LabelEncoder()
            le.fit(econ_order)
            encoded_df[econ_col] = le.transform(encoded_df[econ_col])
            encoders[econ_col] = le
            categorical_cols.append(econ_col)

    return encoded_df, encoders


def add_difference_features(df):
    """Add pairwise difference features between partners."""
    for domain in DOMAIN_OPTIONS:
        col_a = f"a_{domain}"
        col_b = f"b_{domain}"
        if col_a in df.columns and col_b in df.columns:
            df[f"diff_{domain}"] = abs(df[col_a] - df[col_b])

    for trait in PERSONALITY_TRAITS:
        col_a = f"a_{trait}"
        col_b = f"b_{trait}"
        if col_a in df.columns and col_b in df.columns:
            df[f"diff_{trait}"] = abs(df[col_a] - df[col_b])

    # Age difference
    if "a_age" in df.columns and "b_age" in df.columns:
        df["age_diff"] = abs(df["a_age"] - df["b_age"])

    return df


def get_feature_columns(df):
    """Get list of feature columns (everything except targets and IDs)."""
    exclude = {"couple_id", "compatibility_score", "compatibility_label"}
    return [c for c in df.columns if c not in exclude]


def prepare_training_data(df):
    """Full preprocessing pipeline: encode, add features, return X and y."""
    encoded_df, encoders = encode_categorical(df)
    encoded_df = add_difference_features(encoded_df)
    feature_cols = get_feature_columns(encoded_df)
    X = encoded_df[feature_cols].values.astype(np.float32)
    y_score = encoded_df["compatibility_score"].values.astype(np.float32)
    label_enc = LabelEncoder()
    y_label = label_enc.fit_transform(encoded_df["compatibility_label"])
    return X, y_score, y_label, feature_cols, encoders, label_enc


def encode_single_couple(person_a, person_b, encoders):
    """Encode a single couple's answers for prediction."""
    record = {}
    for prefix, person in [("a_", person_a), ("b_", person_b)]:
        for k, v in person.items():
            col = f"{prefix}{k}"
            if col in encoders:
                record[col] = encoders[col].transform([v])[0]
            else:
                record[col] = v

    df = pd.DataFrame([record])
    df = add_difference_features(df)
    return df
