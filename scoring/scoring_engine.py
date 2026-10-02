import pandas as pd


# ----------------------------
# RS RAW SCORE
# ----------------------------

# ----------------------------
# RS RAW SCORE V2
# ----------------------------

from config.config import RS_RAW_WEIGHTS

def calculate_rs_raw(stocks):

    # Start with a series of zeros
    stocks["RS_Raw"] = 0.0
    for column, weight in RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            stocks["RS_Raw"] += stocks[column].fillna(0) * weight

    return stocks


# ----------------------------
# RS RATING
# ----------------------------

def calculate_rs_rating(stocks):

    stocks = stocks.sort_values(
        "RS_Raw",
        ascending=False
    ).reset_index(drop=True)

    total = len(stocks)

    stocks["Percentile"] = (

        (1 - (stocks.index / total)) * 100
    )

    stocks["RS_Rating"] = (

        stocks["Percentile"].clip(lower=1.0, upper=99.0).round().astype(int)

    )

    # NEW FIELD FOR SHORT ENGINE ONLY

    stocks["Weakness_Score"] = (

        100 - stocks["Percentile"]

    )

    return stocks






# ----------------------------
# ZACKS SCORE
# ----------------------------

from config.config import ZACKS_SCORE_MAP

def zacks_score(rank):
    try:
        rank = int(float(rank))
    except (ValueError, TypeError):
        return ZACKS_SCORE_MAP.get(3, 20.0)
    return ZACKS_SCORE_MAP.get(rank, 20.0)


def calculate_zacks_score(stocks):
    stocks["Zacks_Score"] = stocks["Zacks Rank"].apply(zacks_score)
    return stocks

# ----------------------------
# GROWTH SCORE
# ----------------------------

from config.config import GROWTH_SCORE_MAP

def growth_score(grade):
    grade = str(grade).strip().upper()
    return GROWTH_SCORE_MAP.get(grade, 20.0)

def calculate_growth_score(stocks):
    if "Growth Score" in stocks.columns:
        stocks["Growth_Score"] = stocks["Growth Score"].fillna('C').apply(growth_score)
    else:
        stocks["Growth_Score"] = growth_score('C')
    return stocks


# ============================================================
# SHORT SCORING ENGINE (FULLY ISOLATED FROM LONG ENGINE)
# Uses SHORT_* config variables exclusively.
# Does NOT touch RS_Rating, Long_Score, Zacks_Score, Growth_Score.
# ============================================================

import config.config as cfg

def calculate_short_rs_raw(stocks):
    """Computes a dedicated raw RS score using SHORT_RS_RAW_WEIGHTS."""
    stocks["Short_RS_Raw"] = 0.0
    for column, weight in cfg.SHORT_RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            stocks["Short_RS_Raw"] += stocks[column].fillna(0) * weight
    return stocks


def calculate_short_rs_rating(stocks):
    """Ranks stocks by Short_RS_Raw weakness and assigns Short_RS_Rating (1=weakest, 99=strongest)."""
    # Sort ascending so the weakest stock gets the lowest percentile
    stocks = stocks.sort_values("Short_RS_Raw", ascending=True).reset_index(drop=True)
    total = len(stocks)
    import numpy as np
    pct = (stocks.index.to_numpy() / total) * 100
    stocks["Short_RS_Rating"] = np.clip(pct, 1.0, 99.0).round().astype(int)
    return stocks


def _short_zacks_score(rank):
    try:
        rank = int(float(rank))
    except (ValueError, TypeError):
        return cfg.SHORT_ZACKS_SCORE_MAP.get(3, 20.0)
    return cfg.SHORT_ZACKS_SCORE_MAP.get(rank, 20.0)


def _short_growth_score(grade):
    grade = str(grade).strip().upper()
    return cfg.SHORT_GROWTH_SCORE_MAP.get(grade, 50.0)


def calculate_short_score(stocks):
    """
    Computes Short_Score for each stock using SHORT_COMPOSITE_WEIGHTS.
    A higher Short_Score = stronger breakdown conviction.
    Completely separate from Long_Score.
    """
    stocks = calculate_short_rs_raw(stocks)
    stocks = calculate_short_rs_rating(stocks)

    w = cfg.SHORT_COMPOSITE_WEIGHTS
    rs_w = w.get("RS_WEIGHT", 0.50)
    theme_w = w.get("THEME_WEIGHT", 0.25)
    zacks_w = w.get("ZACKS_WEIGHT", 0.15)
    growth_w = w.get("GROWTH_WEIGHT", 0.10)

    short_zacks = stocks["Zacks Rank"].apply(_short_zacks_score) if "Zacks Rank" in stocks.columns else pd.Series(20.0, index=stocks.index)
    short_growth = stocks["Growth Score"].fillna('C').apply(_short_growth_score) if "Growth Score" in stocks.columns else pd.Series(50.0, index=stocks.index)

    theme_score = stocks["Theme_Score"] if "Theme_Score" in stocks.columns else pd.Series(50.0, index=stocks.index)

    stocks["Short_Score"] = (
        stocks["Short_RS_Rating"] * rs_w
        + theme_score * theme_w
        + short_zacks * zacks_w
        + short_growth * growth_w
    ).round(2)

    return stocks
