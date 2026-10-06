"""CSV ingestion utilities for CrimeMapAI.

Design goals:
- never modify raw files;
- preserve source filenames;
- make encoding/delimiter handling explicit;
- return deterministic pandas DataFrames.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class CSVLoadResult:
    """Metadata + dataframe returned by the CSV loader."""

    path: Path
    dataframe: pd.DataFrame
    encoding: str


def load_csv(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    low_memory: bool = False,
) -> CSVLoadResult:
    """Load one CSV without changing its values.

    A latin-1 fallback is available only when UTF-8 decoding fails.
    """
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    if csv_path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file: {csv_path}")

    try:
        df = pd.read_csv(csv_path, encoding=encoding, low_memory=low_memory)
        used_encoding = encoding
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="latin-1", low_memory=low_memory)
        used_encoding = "latin-1"

    return CSVLoadResult(
        path=csv_path,
        dataframe=df,
        encoding=used_encoding,
    )


def load_many_csv(paths: Iterable[str | Path]) -> dict[str, CSVLoadResult]:
    """Load multiple CSV files independently.

    Dataset names are derived from filenames. Duplicate stems are rejected
    rather than silently overwriting a dataset.
    """
    results: dict[str, CSVLoadResult] = {}

    for path in paths:
        result = load_csv(path)
        name = result.path.stem

        if name in results:
            raise ValueError(
                f"Duplicate dataset name '{name}'. "
                "Use unique filenames or load files separately."
            )

        results[name] = result

    return results
