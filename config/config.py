THEME_STRENGTH_CONFIG = {
    # Benchmark ETF used for relative-return subtraction.
    "BENCHMARK_TICKER": "SPY",

    # Relative-return weights by ETF performance period.
    # Fast Sector Rotation (Idea 3): Focus purely on immediate 1W, 1M, and 3M capital flow.
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.40,
        "Performance 1W (%)": 0.35,
        "Performance 3M (%)": 0.25,
        "Performance 6M (%)": 0.00,
        "Performance 1Y (%)": 0.00,
        "Performance 1D (%)": 0.00,
    },

    # Theme aggregation mode: "aum_weighted" or "equal_weight".
    "AGGREGATION_MODE": "aum_weighted",

    # Controls whether the 0-100 normalized diagnostic score is computed.
    "ENABLE_NORMALIZATION": True,

    # Theme breakdown. Leading/Lagging percentages.
    # User Request: 30% Leading / 40% Neutral / 30% Lagging (Expands early-warning drop coverage)
    "CLASSIFICATION_PERCENTAGE_LEADING": 0.30,
    "CLASSIFICATION_PERCENTAGE_LAGGING": 0.30
}

# User Request: 50% RS, 25% Theme, 25% Fundamentals
LONG_WEIGHTS = {
    "RS_WEIGHT": 0.50,
    "THEME_WEIGHT": 0.25,
    "ZACKS_WEIGHT": 0.15,
    "GROWTH_WEIGHT": 0.10
}

RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.50,      # Huge weight on immediate breakout flow
    "% Price Change (12 Weeks)": 0.40,     # Strong weight on intermediate trend
    "% Price Change (1 Week)": 0.10,       # Slight weight on current week
    "Relative Price Change (YTD)": 0.00,   # Nuke YTD to discover Early Turnarounds
    "Price as a % of 52 Wk H-L Range": 0.00 # Removed from raw RS, handled safely in Long Score
}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    "MIN_RS": 90.0,
    "MIN_LONG_SCORE": 85.0,  # Raised to 85.0 (Extreme Exclusivity)
    "THEMES": ["Leading", "Neutral", "Unclassified Leader", "Unknown"],
    "BLOCKED_ZACKS": [4, 5],
    "MIN_PRICE": 10.0,       # Kill penny stock noise
    "MIN_VOLUME": 300000,    # Kill un-tradeable illiquidity traps
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

