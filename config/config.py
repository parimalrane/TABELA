THEME_STRENGTH_CONFIG = {
    # Benchmark ETF used for relative-return subtraction.
    "BENCHMARK_TICKER": "SPY",

    # Relative-return weights by ETF performance period.
    # Fast Sector Rotation (Idea 3): Focus purely on immediate 1W, 1M, and 3M capital flow.
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.40,
        "Performance 1W (%)": 0.20,
        "Performance 3M (%)": 0.40,
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

# ==========================
# RELATIVE STRENGTH (RS) WEIGHTS
# ==========================
RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.60,      # High velocity near-term
    "% Price Change (12 Weeks)": 0.20,     # Core trend confirmation
    "% Price Change (1 Week)": 0.20,       # Slight weight on immediate term
    "Relative Price Change (YTD)": 0.00,   # Block severe structural downtrends
    "Price as a % of 52 Wk H-L Range": 0.00 # 52W position enforced via PULLBACK_CONFIG gate
}

# Dedicated Short-specific RS raw weights (YTD peak-to-trough reversal)
SHORT_RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.20,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.40,
    "Price as a % of 52 Wk H-L Range": 0.00,
}


# Weights for the sector composite strength score
SECTOR_COMPOSITE_WEIGHTS = {

    "Performance 1W (%)": 0.25,
    "Performance 1M (%)": 0.25,
    "Performance 3M (%)": 0.25,
    "Performance YTD (%)": 0.25,
}

# Configuration for sector classification
SECTOR_CLASSIFICATION_CONFIG = {
    "SPDR_MAP": {
        'XLK': 'Technology', 'XLY': 'Discretionary', 'XLC': 'Communications',
        'XLF': 'Financials', 'XLP': 'Staples', 'XLU': 'Utilities',
        'XLV': 'Health Care', 'XLE': 'Energy', 'XLB': 'Materials',
        'XLI': 'Industrials', 'XLRE': 'Real Estate'
    },
    "TOP_N_LEADERS": 3,  # Number of top sectors to classify as LEADING
    "BOTTOM_N_LAGGARDS": 3, # Number of bottom sectors to classify as LAGGING
    "IMPROVING_RANK_DELTA": 2, # Rank delta for a sector to be classified as IMPROVING
    "DETERIORATING_RANK_DELTA": -2 # Rank delta for a sector to be classified as DETERIORATING
}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    "MIN_RS": 90.0,
    "THEMES": ["Leading", "Unclassified Leader"],
    "BLOCKED_ZACKS": [3, 4, 5],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
}

SHORT_ENTRY = {
    "MIN_SHORT_RS": 8.0,
    "MAX_SHORT_RS": 60.0,
    "THEMES": ["Lagging"],
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 2_000_000,
}

# ==========================
# 52W RANGE GATES (LIVE PIPELINE)
# ==========================
PULLBACK_CONFIG = {
    "LONG_MIN_52W_RANGE": 85.0,
    "SHORT_MAX_52W_RANGE": 30.0,
}

# ==========================
# BACKTEST EXECUTION PARAMS (BACKTEST ONLY - DOES NOT AFFECT LIVE)
# ==========================
BACKTEST_PULLBACK_PARAMS = {
    "BT_LONG_WAIT_DAYS": 42,         # 42 trading days (~8 weeks) to let bases form
    "BT_SHORT_WAIT_DAYS": 21,        # 21 trading days (relief bounces are fast)
    "BT_LONG_PULLBACK_PCT": 0.20,    # 20% healthy pullback entry simulation
    "BT_SHORT_BOUNCE_PCT": 0.15,     # 15% relief rally bounce entry simulation
    "BT_STOP_PCT": 0.07,             # 7% stop loss
    "BT_TARGET_PCT": 0.21,           # 21% profit target (1:3 R:R)
    "BT_MAX_HOLD_DAYS": 50,          # 50 days max hold horizon
}


# TABELA RETENTION STAY-IN THRESHOLDS
LONG_STAY = {
    "MIN_RS": 75.0,
    "THEMES": ["Leading", "Neutral", "Unclassified Leader"],
    "ALLOWED_ZACKS": [1, 2, 3],
}

SHORT_STAY = {
    "MAX_RS": 75.0,
    "THEMES": ["Lagging", "Neutral"],
    "ALLOWED_ZACKS": [2, 3, 4, 5],
}


