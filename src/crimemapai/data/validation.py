"""Data validation utilities."""
from __future__ import annotations
import pandas as pd

def key_diagnostics(df: pd.DataFrame, keys: list[str]) -> dict:
    missing = [k for k in keys if k not in df.columns]
    if missing:
        raise KeyError(f"Missing key columns: {missing}")
    key_df = df[keys]
    unique_keys = key_df.drop_duplicates().shape[0]
    return {
        "rows": len(df),
        "keys": keys,
        "unique_keys": int(unique_keys),
        "duplicate_key_rows": int(key_df.duplicated(keep=False).sum()),
        "unique_ratio": unique_keys / len(df) if len(df) else 0.0,
    }
