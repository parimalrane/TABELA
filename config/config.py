THEME_STRENGTH_CONFIG = {
    "BENCHMARK_TICKER": "SPY",
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.4,
        "Performance 1W (%)": 0.35,
        "Performance 3M (%)": 0.25,
        "Performance 6M (%)": 0.0,
        "Performance 1Y (%)": 0.0,
        "Performance 1D (%)": 0.0,
    },
    "AGGREGATION_MODE": "aum_weighted",
    "ENABLE_NORMALIZATION": True,
    "CLASSIFICATION_PERCENTAGE_LEADING": 0.3,
    "CLASSIFICATION_PERCENTAGE_LAGGING": 0.3
}

LONG_WEIGHTS = {
    "RS_WEIGHT": 0.5,
    "THEME_WEIGHT": 0.25,
    "ZACKS_WEIGHT": 0.15,
    "GROWTH_WEIGHT": 0.1
}

RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.5,
    "% Price Change (12 Weeks)": 0.4,
    "% Price Change (1 Week)": 0.1,
    "Relative Price Change (YTD)": 0.0,
    "Price as a % of 52 Wk H-L Range": 0.0
}

ZACKS_SCORE_MAP = {1: 100.0, 2: 95.0, 3: 90.0, 4: 20.0, 5: -50.0}
GROWTH_SCORE_MAP = {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}

LONG_ENTRY = {
    "MIN_RS": 90.0,
    "MIN_LONG_SCORE": 90.0,
    "THEMES": ["Leading", "Neutral", "Unclassified Leader", "Unknown"],
    "BLOCKED_ZACKS": [4, 5],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 300000,
    "MIN_DROPPED_WATCH_SCORE": 70.0
}

DIST_ENTRY = {
    "MAX_RS": 10.0,
    "MAX_LONG_SCORE": 20.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
}

# ==========================================================
# SHORT ENGINE CONFIGURATION (LOCKED: P1-C)
# ==========================================================

SHORT_RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.20,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.40,
    "Price as a % of 52 Wk H-L Range": 0.00
}

SHORT_COMPOSITE_WEIGHTS = {
    "RS_WEIGHT": 0.50,
    "THEME_WEIGHT": 0.25,
    "ZACKS_WEIGHT": 0.15,
    "GROWTH_WEIGHT": 0.10
}

SHORT_ZACKS_SCORE_MAP = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}
SHORT_GROWTH_SCORE_MAP = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}

SHORT_ENTRY = {
    "MIN_SHORT_RS": 15.0,
    "MAX_SHORT_RS": 35.0,
    "MAX_SHORT_SCORE": 40.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1000000
}
