import pandas as pd

from crimemapai.data.grain import compare_key, estimate_merge_rows, key_profile


def test_composite_key_unique():
    df = pd.DataFrame(
        {
            "state_code": [1, 1, 2],
            "district_code": [10, 11, 20],
            "year": [2020, 2020, 2020],
        }
    )

    result = key_profile(df, ["state_code", "district_code", "year"])

    assert result["is_unique"] is True
    assert result["duplicate_key_rows"] == 0


def test_many_to_one_relationship():
    left = pd.DataFrame(
        {
            "state_code": [1, 1, 1],
            "district_code": [10, 10, 11],
            "year": [2020, 2020, 2020],
        }
    )

    right = pd.DataFrame(
        {
            "state_code": [1, 1],
            "district_code": [10, 11],
            "year": [2020, 2020],
        }
    )

    result = compare_key(
        left,
        right,
        ["state_code", "district_code", "year"],
    )

    assert result["relationship"] == "M:1"
    assert result["common_keys"] == 2


def test_merge_row_multiplier_detected():
    left = pd.DataFrame(
        {
            "district_code": [10],
            "year": [2020],
        }
    )

    right = pd.DataFrame(
        {
            "district_code": [10, 10],
            "year": [2020, 2020],
        }
    )

    result = estimate_merge_rows(
        left,
        right,
        ["district_code", "year"],
    )

    assert result["inner_merge_rows"] == 2
    assert result["row_multiplier_vs_left"] == 2.0
