import pandas as pd

from crimemapai.data.profile import build_column_profile, summarize_dataset


def test_summary():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10, None, 30],
            "name": ["a", "b", "b"],
        }
    )

    summary = summarize_dataset(df)

    assert summary.rows == 3
    assert summary.columns == 3
    assert summary.missing_cells == 1
    assert summary.duplicate_rows == 0


def test_column_profile_contains_roles():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
            "state_name": ["A", "A", "B"],
        }
    )

    profile = build_column_profile(df)

    assert set(profile["column"]) == {"id", "value", "state_name"}
    assert profile.loc[profile["column"] == "value", "role"].iloc[0] == "numeric"
