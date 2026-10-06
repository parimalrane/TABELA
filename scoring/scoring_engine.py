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
            clean_series = stocks[column].astype(str).str.replace(r'[%$,]', '', regex=True).str.strip()
            clean_series = clean_series.replace(r'^\((.*)\)$', r'-\1', regex=True)
            stocks["RS_Raw"] += pd.to_numeric(clean_series, errors='coerce').fillna(0.0) * weight

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

# ============================================================
# GARAGE ENGINE (Phase 2 Optimization)
# ============================================================

from config.config import LONG_GARAGE_RS_RAW_WEIGHTS, SHORT_GARAGE_RS_RAW_WEIGHTS

def calculate_long_garage_rs_raw(stocks):
    """Computes pure kinetic upside breakout speed."""
    stocks["Long_Garage_RS_Raw"] = 0.0
    for column, weight in LONG_GARAGE_RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            clean_series = stocks[column].astype(str).str.replace(r'[%$,]', '', regex=True).str.strip()
            clean_series = clean_series.replace(r'^\((.*)\)$', r'-\1', regex=True)
            stocks["Long_Garage_RS_Raw"] += pd.to_numeric(clean_series, errors='coerce').fillna(0.0) * weight
    return stocks

def calculate_long_garage_rs_rating(stocks):
    stocks = stocks.sort_values("Long_Garage_RS_Raw", ascending=False).reset_index(drop=True)
    total = len(stocks)
    stocks["Long_Garage_Percentile"] = ((1 - (stocks.index / total)) * 100)
    stocks["Long_Garage_RS_Rating"] = stocks["Long_Garage_Percentile"].clip(lower=1.0, upper=99.0).round().astype(int)
    return stocks

def calculate_short_garage_rs_raw(stocks):
    """Computes pure kinetic downside breakdown speed."""
    stocks["Short_Garage_RS_Raw"] = 0.0
    for column, weight in SHORT_GARAGE_RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            clean_series = stocks[column].astype(str).str.replace(r'[%$,]', '', regex=True).str.strip()
            clean_series = clean_series.replace(r'^\((.*)\)$', r'-\1', regex=True)
            stocks["Short_Garage_RS_Raw"] += pd.to_numeric(clean_series, errors='coerce').fillna(0.0) * weight
    return stocks

def calculate_short_garage_rs_rating(stocks):
    # Sort ascending for downside velocity (weakest gets highest weakness rating)
    stocks = stocks.sort_values("Short_Garage_RS_Raw", ascending=True).reset_index(drop=True)
    total = len(stocks)
    import numpy as np
    stocks["Short_Garage_Percentile"] = (stocks.index.to_numpy() / total) * 100
    stocks["Short_Garage_RS_Rating"] = np.clip(stocks["Short_Garage_Percentile"], 1.0, 99.0).round().astype(int)
    return stocks


# ----------------------------
# ZACKS SCORE
# ----------------------------

from config.config import ZACKS_SCORE_MAP

def zacks_score(rank):
    try:
        rank = int(float(rank))
    except (ValueError, TypeError):
        # Missing Zacks Data: Pro-rate to a neutral 50.0 (7.5 pts out of 15) to prevent math-locking true technical breakouts
        return 50.0
    return ZACKS_SCORE_MAP.get(rank, 0.0)


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

from config.config import (
    SHORT_RS_RAW_WEIGHTS,
    SHORT_COMPOSITE_WEIGHTS,
    SHORT_ZACKS_SCORE_MAP,
    SHORT_GROWTH_SCORE_MAP,
)

def calculate_short_rs_raw(stocks):
    """Computes a dedicated raw RS score using SHORT_RS_RAW_WEIGHTS."""
    stocks["Short_RS_Raw"] = 0.0
    for column, weight in SHORT_RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            clean_series = stocks[column].astype(str).str.replace(r'[%$]', '', regex=True).str.replace(',', '')
            stocks["Short_RS_Raw"] += pd.to_numeric(clean_series, errors='coerce').fillna(0.0) * weight
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
        return SHORT_ZACKS_SCORE_MAP.get(3, 20.0)
    return SHORT_ZACKS_SCORE_MAP.get(rank, 20.0)


def _short_growth_score(grade):
    grade = str(grade).strip().upper()
    return SHORT_GROWTH_SCORE_MAP.get(grade, 50.0)


def calculate_short_score(stocks):
    """
    Computes Short_Score for each stock using SHORT_COMPOSITE_WEIGHTS.
    A higher Short_Score = stronger breakdown conviction.
    Completely separate from Long_Score.
    """
    stocks = calculate_short_rs_raw(stocks)
    stocks = calculate_short_rs_rating(stocks)

    w = SHORT_COMPOSITE_WEIGHTS
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
