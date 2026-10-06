import pandas as pd

from crimemapai.data.compatibility import (
    compatibility_decision,
    geography_overlap,
    normalized_column_candidates,
)


def test_normalized_candidates_detect_renamed_columns():
    left = pd.DataFrame(columns=["credit_card_debit_card_fraud", "year"])
    right = pd.DataFrame(columns=["credit_card_debit", "year"])
    result = normalized_column_candidates(left, right)
    assert "year" in result["normalized_name"].tolist()
    assert result.loc[result["normalized_name"] == "year", "exact_match"].iloc[0]
    assert "credit_card_debit_card_fraud" not in result["normalized_name"].tolist()


def test_geography_overlap():
    left = pd.DataFrame({"state_code": [1, 1, 2], "district_code": [10, 20, 30]})
    right = pd.DataFrame({"state_code": [1, 2, 3], "district_code": [10, 30, 40]})
    result = geography_overlap(left, right)
    assert result["common_geographies"] == 2
    assert result["left_only_geographies"] == 1
    assert result["right_only_geographies"] == 1


def test_conservative_decision():
    assert compatibility_decision(
        has_temporal_gap=False,
        classification_change=False,
        grain_compatible=False,
        geography_compatible=True,
    ) == "DO_NOT_APPEND_YET"
    assert compatibility_decision(
        has_temporal_gap=True,
        classification_change=True,
        grain_compatible=True,
        geography_compatible=True,
    ) == "APPEND_ONLY_WITH_EXPLICIT_HARMONIZATION"
