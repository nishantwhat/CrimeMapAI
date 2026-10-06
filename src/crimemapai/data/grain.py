"""Dataset grain and candidate-key diagnostics."""

from __future__ import annotations

from itertools import combinations
from typing import Sequence

import pandas as pd


def key_profile(
    df: pd.DataFrame,
    keys: Sequence[str],
) -> dict:
    """Profile a candidate composite key inside one dataset."""
    keys = list(keys)

    missing_columns = [key for key in keys if key not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing key columns: {missing_columns}")

    key_frame = df[keys]
    unique_keys = int(key_frame.drop_duplicates().shape[0])
    duplicate_rows = int(key_frame.duplicated(keep=False).sum())
    null_key_rows = int(key_frame.isna().any(axis=1).sum())

    return {
        "keys": keys,
        "rows": len(df),
        "unique_keys": unique_keys,
        "unique_ratio": unique_keys / len(df) if len(df) else 0.0,
        "duplicate_key_rows": duplicate_rows,
        "null_key_rows": null_key_rows,
        "is_unique": duplicate_rows == 0 and null_key_rows == 0,
    }


def compare_key(
    left: pd.DataFrame,
    right: pd.DataFrame,
    keys: Sequence[str],
) -> dict:
    """Compare a candidate key across two datasets.

    Value comparison is performed on string-normalized copies only.
    The source dataframes are never modified.
    """
    keys = list(keys)

    left_profile = key_profile(left, keys)
    right_profile = key_profile(right, keys)

    left_keys = (
        left[list(keys)]
        .dropna()
        .astype(str)
        .drop_duplicates()
    )
    right_keys = (
        right[list(keys)]
        .dropna()
        .astype(str)
        .drop_duplicates()
    )

    left_set = set(map(tuple, left_keys.to_numpy()))
    right_set = set(map(tuple, right_keys.to_numpy()))

    common = left_set & right_set

    if left_profile["is_unique"] and right_profile["is_unique"]:
        relationship = "1:1"
    elif left_profile["is_unique"] and not right_profile["is_unique"]:
        relationship = "1:M"
    elif not left_profile["is_unique"] and right_profile["is_unique"]:
        relationship = "M:1"
    else:
        relationship = "M:M"

    return {
        "keys": keys,
        "left_rows": len(left),
        "right_rows": len(right),
        "left_unique_ratio": left_profile["unique_ratio"],
        "right_unique_ratio": right_profile["unique_ratio"],
        "left_duplicate_key_rows": left_profile["duplicate_key_rows"],
        "right_duplicate_key_rows": right_profile["duplicate_key_rows"],
        "left_null_key_rows": left_profile["null_key_rows"],
        "right_null_key_rows": right_profile["null_key_rows"],
        "common_keys": len(common),
        "left_only_keys": len(left_set - right_set),
        "right_only_keys": len(right_set - left_set),
        "relationship": relationship,
        "safe_1_to_1": relationship == "1:1",
    }


def estimate_merge_rows(
    left: pd.DataFrame,
    right: pd.DataFrame,
    keys: Sequence[str],
) -> dict:
    """Estimate actual pandas inner-merge cardinality.

    This is diagnostic only; the returned merged dataframe is not retained.
    """
    keys = list(keys)

    left_tmp = left[keys].copy()
    right_tmp = right[keys].copy()

    left_tmp["_left_row"] = range(len(left_tmp))
    right_tmp["_right_row"] = range(len(right_tmp))

    merged = left_tmp.merge(
        right_tmp,
        on=keys,
        how="inner",
    )

    return {
        "left_rows": len(left),
        "right_rows": len(right),
        "inner_merge_rows": len(merged),
        "row_multiplier_vs_left": (
            len(merged) / len(left) if len(left) else 0.0
        ),
        "row_multiplier_vs_right": (
            len(merged) / len(right) if len(right) else 0.0
        ),
    }


def candidate_composite_keys(
    df: pd.DataFrame,
    preferred_columns: Sequence[str],
    max_key_size: int = 3,
) -> list[tuple[str, ...]]:
    """Generate conservative composite-key candidates.

    Only existing preferred columns are considered. This avoids creating
    hundreds of meaningless combinations from every feature column.
    """
    available = [c for c in preferred_columns if c in df.columns]

    candidates: list[tuple[str, ...]] = []

    for size in range(1, min(max_key_size, len(available)) + 1):
        candidates.extend(combinations(available, size))

    return candidates
