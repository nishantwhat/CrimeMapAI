"""Dataset profiling for CrimeMapAI Phase 1."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd


_ID_PATTERN = re.compile(
    r"(^id$|_id$|^id_|code$|_code$|key$|_key$)",
    flags=re.IGNORECASE,
)
_DATE_PATTERN = re.compile(
    r"date|time|year|month|day|timestamp",
    flags=re.IGNORECASE,
)


def normalize_name(name: object) -> str:
    """Normalize a column name for comparison only.

    This does not modify the source dataframe.
    """
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")


def looks_like_id(series: pd.Series) -> bool:
    """Heuristically identify likely identifier/key columns."""
    if len(series) == 0:
        return False

    name = normalize_name(series.name)
    unique_ratio = series.nunique(dropna=True) / len(series)

    name_hint = bool(_ID_PATTERN.search(name))
    high_cardinality_text = (
        unique_ratio >= 0.95
        and (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        )
    )

    return name_hint or high_cardinality_text


def looks_like_datetime(series: pd.Series) -> bool:
    """Heuristically identify date/time columns without mutating them."""
    name = normalize_name(series.name)
    name_hint = bool(_DATE_PATTERN.search(name))

    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    if pd.api.types.is_numeric_dtype(series) and not name_hint:
        return False

    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        sample = series.dropna().astype(str).head(300)

        if sample.empty:
            return name_hint

        parsed = pd.to_datetime(sample, errors="coerce")
        return name_hint or parsed.notna().mean() >= 0.85

    return name_hint


def infer_role(series: pd.Series) -> str:
    """Return a human-readable heuristic role."""
    if looks_like_datetime(series):
        return "datetime / temporal"

    if looks_like_id(series):
        return "likely ID / key"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    return "categorical / text"


@dataclass(frozen=True)
class DatasetSummary:
    """High-level dataset statistics."""

    rows: int
    columns: int
    duplicate_rows: int
    memory_mb: float
    missing_cells: int
    missing_cells_pct: float


def summarize_dataset(df: pd.DataFrame) -> DatasetSummary:
    """Return high-level structural statistics."""
    cells = df.shape[0] * df.shape[1]
    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    return DatasetSummary(
        rows=len(df),
        columns=df.shape[1],
        duplicate_rows=duplicates,
        memory_mb=float(df.memory_usage(deep=True).sum() / 1024**2),
        missing_cells=missing,
        missing_cells_pct=(missing / cells * 100) if cells else 0.0,
    )


def build_column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Create a machine-readable schema/data-quality profile."""
    rows: list[dict] = []

    for column in df.columns:
        series = df[column]
        non_null = int(series.notna().sum())
        unique = int(series.nunique(dropna=True))

        rows.append(
            {
                "column": column,
                "dtype": str(series.dtype),
                "role": infer_role(series),
                "rows": len(series),
                "non_null": non_null,
                "missing": int(series.isna().sum()),
                "missing_pct": round(series.isna().mean() * 100, 4),
                "unique": unique,
                "unique_pct": round(
                    unique / len(series) * 100, 4
                ) if len(series) else 0.0,
                "duplicated_values": non_null - unique,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["missing_pct", "column"],
        ascending=[False, True],
    ).reset_index(drop=True)


def build_numeric_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric fields."""
    numeric = df.select_dtypes(include=np.number)

    if numeric.empty:
        return pd.DataFrame()

    return numeric.describe(
        percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
    ).T.reset_index(names="column")


def build_categorical_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize categorical/text cardinality and dominant values."""
    categorical = df.select_dtypes(
        include=["object", "string", "category", "bool"]
    )

    rows: list[dict] = []

    for column in categorical.columns:
        series = categorical[column]
        counts = series.value_counts(dropna=False)

        top_value = counts.index[0] if not counts.empty else None
        top_count = int(counts.iloc[0]) if not counts.empty else 0

        rows.append(
            {
                "column": column,
                "unique": int(series.nunique(dropna=True)),
                "missing_pct": round(series.isna().mean() * 100, 4),
                "top_value": str(top_value)[:200],
                "top_frequency": top_count,
                "top_frequency_pct": round(
                    top_count / len(series) * 100, 4
                ) if len(series) else 0.0,
            }
        )

    return pd.DataFrame(rows).sort_values(
        "unique", ascending=False
    ).reset_index(drop=True)


def build_outlier_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Screen numeric columns with the IQR rule.

    This is diagnostic only. No values are removed or transformed.
    """
    numeric = df.select_dtypes(include=np.number)
    rows: list[dict] = []

    for column in numeric.columns:
        series = numeric[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            count = 0
        else:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())

        rows.append(
            {
                "column": column,
                "outliers": count,
                "outlier_pct": round(count / len(series) * 100, 4),
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
            }
        )

    return pd.DataFrame(rows).sort_values(
        "outlier_pct", ascending=False
    ).reset_index(drop=True)


def build_temporal_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Identify likely temporal fields and report parse coverage."""
    rows: list[dict] = []

    for column in df.columns:
        if not looks_like_datetime(df[column]):
            continue

        parsed = pd.to_datetime(df[column], errors="coerce")
        valid = parsed.dropna()

        rows.append(
            {
                "column": column,
                "parse_success_pct": round(
                    valid.size / len(df) * 100, 4
                ) if len(df) else 0.0,
                "min_value": valid.min() if not valid.empty else pd.NaT,
                "max_value": valid.max() if not valid.empty else pd.NaT,
            }
        )

    return pd.DataFrame(rows)
