"""Cross-dataset merge compatibility audit."""

from __future__ import annotations

import pandas as pd

from .grain import compare_key, estimate_merge_rows


def audit_common_columns(
    left: pd.DataFrame,
    right: pd.DataFrame,
) -> pd.DataFrame:
    """Find exact common columns and compare unique-value overlap."""
    common = sorted(set(left.columns) & set(right.columns))
    rows: list[dict] = []

    for column in common:
        left_values = set(
            left[column]
            .dropna()
            .astype(str)
            .str.strip()
        )
        right_values = set(
            right[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        overlap = left_values & right_values

        rows.append(
            {
                "column": column,
                "left_unique": len(left_values),
                "right_unique": len(right_values),
                "common_values": len(overlap),
                "overlap_pct_left": (
                    len(overlap) / len(left_values) * 100
                    if left_values else 0.0
                ),
                "overlap_pct_right": (
                    len(overlap) / len(right_values) * 100
                    if right_values else 0.0
                ),
            }
        )

    return pd.DataFrame(rows).sort_values(
        "common_values", ascending=False
    ).reset_index(drop=True)


def audit_candidate_keys(
    left: pd.DataFrame,
    right: pd.DataFrame,
    candidates: list[tuple[str, ...]],
) -> pd.DataFrame:
    """Evaluate composite-key candidates and merge cardinality."""
    rows: list[dict] = []

    for keys in candidates:
        try:
            diagnostics = compare_key(left, right, keys)
            merge_stats = estimate_merge_rows(left, right, keys)

            rows.append(
                {
                    "key": " + ".join(keys),
                    **diagnostics,
                    **merge_stats,
                }
            )
        except KeyError:
            # Candidate is invalid for one of the datasets.
            continue

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(
        ["safe_1_to_1", "common_keys"],
        ascending=[False, False],
    ).reset_index(drop=True)


def make_merge_recommendation(audit: pd.DataFrame) -> pd.DataFrame:
    """Assign a conservative diagnostic verdict.

    This function does not claim that a key is semantically valid.
    Semantic validation remains a human/data-documentation decision.
    """
    if audit.empty:
        return audit.copy()

    result = audit.copy()

    def verdict(row: pd.Series) -> str:
        if row["relationship"] == "1:1" and row["common_keys"] > 0:
            return "STRUCTURALLY PROMISING — verify semantics"
        if row["relationship"] in {"1:M", "M:1"}:
            return "ONE-TO-MANY — inspect grain before merge"
        if row["relationship"] == "M:M":
            return "HIGH MERGE-RISK — likely row multiplication"
        return "REJECT / INVESTIGATE"

    result["verdict"] = result.apply(verdict, axis=1)
    return result
