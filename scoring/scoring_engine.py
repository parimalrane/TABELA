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



# ----------------------------
# ZACKS SCORE
# ----------------------------

def zacks_score(rank):
    try:
        rank = int(float(rank))
    except (ValueError, TypeError):
        return 50.0
    return {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}.get(rank, 0.0)


def calculate_zacks_score(stocks):
    stocks["Zacks_Score"] = stocks["Zacks Rank"].apply(zacks_score)
    return stocks

# ----------------------------
# GROWTH SCORE
# ----------------------------

def growth_score(grade):
    grade = str(grade).strip().upper()
    return {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}.get(grade, 20.0)


def calculate_growth_score(stocks):
    if "Growth Score" in stocks.columns:
        stocks["Growth_Score"] = stocks["Growth Score"].fillna('C').apply(growth_score)
    else:
        stocks["Growth_Score"] = growth_score('C')
    return stocks


# ============================================================
# SHORT SCORING ENGINE (FULLY ISOLATED FROM LONG ENGINE)
# Uses SHORT_RS_RAW_WEIGHTS config variable.
# ============================================================

from config.config import SHORT_RS_RAW_WEIGHTS


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
    Computes Short_RS_Rating for breakdown conviction.
    Pure filter architecture: Short_Score maps directly to Short_RS_Rating.
    """
    stocks = calculate_short_rs_raw(stocks)
    stocks = calculate_short_rs_rating(stocks)
    stocks["Short_Score"] = stocks["Short_RS_Rating"]
    return stocks

