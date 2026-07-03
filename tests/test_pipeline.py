import pandas as pd

from core.pipeline import (
    assign_stock_theme_classification,
    build_theme_classification,
)


def test_build_theme_classification_assigns_expected_classes():
    theme_strength = pd.DataFrame(
        {
            "Theme": ["Alpha", "Beta", "Gamma", "Delta"],
            "ETF_RS_Raw": [100.0, 80.0, 60.0, 40.0],
        }
    )

    theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map = (
        build_theme_classification(theme_strength)
    )

    assert theme_class_map["Alpha"] == "Leading"
    assert theme_score_map["Alpha"] == 100
    assert theme_rank_map["Alpha"] == 1
    assert theme_raw_score_map["Alpha"] == 100.0

    assert theme_class_map["Beta"] == "Neutral"
    assert theme_class_map["Gamma"] == "Neutral"
    assert theme_score_map["Beta"] == 73.33
    assert theme_score_map["Gamma"] == 46.67

    assert theme_class_map["Delta"] == "Lagging"
    assert theme_score_map["Delta"] == 20
    assert theme_rank_map["Delta"] == 4
    assert theme_raw_score_map["Delta"] == 40.0


def test_build_theme_classification_single_theme_scores_100():
    theme_strength = pd.DataFrame(
        {
            "Theme": ["Solo"],
            "ETF_RS_Raw": [12.34],
        }
    )

    theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map = (
        build_theme_classification(theme_strength)
    )

    assert theme_class_map["Solo"] == "Leading"
    assert theme_score_map["Solo"] == 100
    assert theme_rank_map["Solo"] == 1
    assert theme_raw_score_map["Solo"] == 12.34


def test_build_theme_classification_assigns_three_state_distribution():
    theme_strength = pd.DataFrame(
        {
            "Theme": [f"Theme{i}" for i in range(1, 11)],
            "ETF_RS_Raw": [float(i) for i in range(10, 0, -1)],
        }
    )

    theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map = (
        build_theme_classification(theme_strength)
    )

    assert theme_class_map["Theme1"] == "Leading"
    assert theme_class_map["Theme2"] == "Leading"
    assert theme_class_map["Theme3"] == "Neutral"
    assert theme_class_map["Theme8"] == "Neutral"
    assert theme_class_map["Theme9"] == "Lagging"
    assert theme_class_map["Theme10"] == "Lagging"

    assert theme_rank_map["Theme1"] == 1
    assert theme_rank_map["Theme10"] == 10
    assert theme_raw_score_map["Theme1"] == 10.0
    assert theme_raw_score_map["Theme10"] == 1.0


def test_assign_stock_theme_classification_handles_unclassified_leader_fallback():
    stocks = pd.DataFrame(
        [
            {
                "Ticker": "ABC",
                "ETF_Theme": "Other",
                "Mapped_Theme": "Unknown",
                "RS_Rating": 95,
                "Sales_Score": 85,
                "Zacks_Score": 90,
            }
        ]
    )

    result = assign_stock_theme_classification(
        stocks,
        {"Known": "Leading"},
        {"Known": 100},
        {"Known": 55.5},
    )

    assert result.loc[0, "Theme_Class"] == "Unclassified Leader"
    assert result.loc[0, "Theme_Score"] == 80
    assert result.loc[0, "Theme_State"] is None
    assert result.loc[0, "ETF_Raw_Score"] is None
