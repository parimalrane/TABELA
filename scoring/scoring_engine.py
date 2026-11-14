import numpy as np
import pandas as pd
from config.config import RS_RAW_WEIGHTS, SHORT_RS_RAW_WEIGHTS


# ----------------------------
# RS RAW SCORE (LONG)
# ----------------------------

def calculate_rs_raw(stocks):
    stocks["RS_Raw"] = 0.0
    for column, weight in RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            clean_series = stocks[column].astype(str).str.replace(r'[%$,]', '', regex=True).str.strip()
            clean_series = clean_series.replace(r'^\((.*)\)$', r'-\1', regex=True)
            stocks["RS_Raw"] += pd.to_numeric(clean_series, errors='coerce').fillna(0.0) * weight

    return stocks


# ----------------------------
# RS RATING (LONG)
# ----------------------------

def calculate_rs_rating(stocks):
    stocks = stocks.sort_values(
        "RS_Raw",
        ascending=False
    ).reset_index(drop=True)

    total = len(stocks)
    stocks["Percentile"] = (1 - (stocks.index / total)) * 100
    stocks["RS_Rating"] = stocks["Percentile"].clip(lower=1.0, upper=99.0).round().astype(int)
    return stocks


# ============================================================
# SHORT RELATIVE STRENGTH ENGINE (BREAKDOWN CONVICTION)
# Uses SHORT_RS_RAW_WEIGHTS config variable.
# ============================================================

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
    pct = (stocks.index.to_numpy() / total) * 100
    stocks["Short_RS_Rating"] = np.clip(pct, 1.0, 99.0).round().astype(int)
    return stocks
