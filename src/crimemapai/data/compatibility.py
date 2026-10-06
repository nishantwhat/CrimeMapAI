"""Cross-dataset compatibility diagnostics for longitudinal crime data."""

from __future__ import annotations

import re
from typing import Sequence

import pandas as pd

from .grain import compare_key, key_profile


def normalize_column_name(name: str) -> str:
    """Normalize a column name for candidate semantic matching."""
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")


def common_columns(left: pd.DataFrame, right: pd.DataFrame) -> list[str]:
    """Return exact common column names in left-column order."""
    right_columns = set(right.columns)
    return [c for c in left.columns if c in right_columns]


def normalized_column_candidates(
    left: pd.DataFrame, right: pd.DataFrame
) -> pd.DataFrame:
    """Find columns sharing a normalized name while retaining exact names."""
    left_map: dict[str, list[str]] = {}
    right_map: dict[str, list[str]] = {}

    for column in left.columns:
        left_map.setdefault(normalize_column_name(column), []).append(column)
    for column in right.columns:
        right_map.setdefault(normalize_column_name(column), []).append(column)

    rows = []
    for normalized in sorted(set(left_map) & set(right_map)):
        for left_name in left_map[normalized]:
            for right_name in right_map[normalized]:
                rows.append(
                    {
                        "normalized_name": normalized,
                        "left_column": left_name,
                        "right_column": right_name,
                        "exact_match": left_name == right_name,
                    }
                )
    return pd.DataFrame(rows)


def grain_audit(
    df: pd.DataFrame,
    candidate_keys: Sequence[Sequence[str]],
) -> pd.DataFrame:
    """Profile several candidate keys for one dataset."""
    rows = []
    for keys in candidate_keys:
        try:
            result = key_profile(df, keys)
        except KeyError as exc:
            rows.append({"keys": " + ".join(keys), "error": str(exc)})
            continue
        result["keys"] = " + ".join(keys)
        rows.append(result)
    return pd.DataFrame(rows)


def cross_dataset_key_audit(
    left: pd.DataFrame,
    right: pd.DataFrame,
    candidate_keys: Sequence[Sequence[str]],
) -> pd.DataFrame:
    """Compare candidate keys across two datasets."""
    rows = []
    for keys in candidate_keys:
        if not all(key in left.columns and key in right.columns for key in keys):
            continue
        result = compare_key(left, right, keys)
        result["keys"] = " + ".join(keys)
        rows.append(result)
    return pd.DataFrame(rows)


def geography_overlap(
    left: pd.DataFrame,
    right: pd.DataFrame,
    columns: Sequence[str] = ("state_code", "district_code"),
) -> dict:
    """Compare distinct geographic keys without modifying either dataframe."""
    columns = list(columns)
    if not all(column in left.columns and column in right.columns for column in columns):
        missing = [c for c in columns if c not in left.columns or c not in right.columns]
        raise KeyError(f"Missing geography columns: {missing}")

    left_keys = set(map(tuple, left[columns].drop_duplicates().to_numpy()))
    right_keys = set(map(tuple, right[columns].drop_duplicates().to_numpy()))
    return {
        "left_unique_geographies": len(left_keys),
        "right_unique_geographies": len(right_keys),
        "common_geographies": len(left_keys & right_keys),
        "left_only_geographies": len(left_keys - right_keys),
        "right_only_geographies": len(right_keys - left_keys),
    }


def compatibility_decision(
    *,
    has_temporal_gap: bool,
    classification_change: bool,
    grain_compatible: bool,
    geography_compatible: bool,
) -> str:
    """Return a conservative longitudinal-use decision."""
    if not grain_compatible or not geography_compatible:
        return "DO_NOT_APPEND_YET"
    if classification_change or has_temporal_gap:
        return "APPEND_ONLY_WITH_EXPLICIT_HARMONIZATION"
    return "APPEND_PLAUSIBLE_AFTER_VALIDATION"
