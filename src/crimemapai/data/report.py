"""Phase-1 report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .loader import load_csv
from .profile import (
    build_categorical_profile,
    build_column_profile,
    build_numeric_profile,
    build_outlier_profile,
    build_temporal_profile,
    summarize_dataset,
)


def analyze_csv(path: str | Path) -> dict[str, object]:
    """Run the complete single-file diagnostic pipeline."""
    result = load_csv(path)
    df = result.dataframe

    return {
        "path": str(result.path),
        "encoding": result.encoding,
        "summary": summarize_dataset(df),
        "column_profile": build_column_profile(df),
        "numeric_profile": build_numeric_profile(df),
        "categorical_profile": build_categorical_profile(df),
        "outlier_profile": build_outlier_profile(df),
        "temporal_profile": build_temporal_profile(df),
    }


def export_csv_report(
    report: dict[str, object],
    output_dir: str | Path,
) -> list[Path]:
    """Export machine-readable CSV tables for one dataset."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    dataset_name = Path(str(report["path"])).stem
    written: list[Path] = []

    table_map = {
        "columns": report["column_profile"],
        "numeric": report["numeric_profile"],
        "categorical": report["categorical_profile"],
        "outliers": report["outlier_profile"],
        "temporal": report["temporal_profile"],
    }

    for suffix, table in table_map.items():
        if isinstance(table, pd.DataFrame) and not table.empty:
            path = output / f"{dataset_name}__{suffix}.csv"
            table.to_csv(path, index=False)
            written.append(path)

    return written
