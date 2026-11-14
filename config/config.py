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

# User Request: 50% RS, 25% Theme, 25% Fundamentals
LONG_WEIGHTS = {
    "RS_WEIGHT": 0.60,
    "THEME_WEIGHT": 0.20,
    "ZACKS_WEIGHT": 0.10,
    "GROWTH_WEIGHT": 0.10
}

RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.60,      # High velocity near-term
    "% Price Change (12 Weeks)": 0.20,     # Core trend confirmation
    "% Price Change (1 Week)": 0.20,       # Slight weight on immediate term
    "Relative Price Change (YTD)": 0.00,   # Block severe structural downtrends
    "Price as a % of 52 Wk H-L Range": 0.00 # Force true breakouts near high ranges
}

# Zacks Binary: Only Rank 1/2 survive. Rank 3 turnarounds = poison (proven by Cartesian backtests)
ZACKS_SCORE_MAP = {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}
GROWTH_SCORE_MAP = {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}

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




# ==========================
# SHORT ENGINE (ISOLATED)
# These variables are EXCLUSIVELY used by the Short backtesting tuner.
# They do NOT affect the live Long pipeline in any way.
# Tune these freely without risk of breaking the Long engine.
# ==========================

# Short-specific RS raw weights — P3-C Winner: YTD Reversal (YTD 40%, 4W 30%, 12W 20%, 1W 10%)
SHORT_RS_RAW_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.20,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.40,   # Peak-to-trough reversal is the key short signal
    "Price as a % of 52 Wk H-L Range": 0.00,
}

# Short-specific composite weights — P3-C Winner: RS Heavy (RS 65%, Theme 20%)
SHORT_COMPOSITE_WEIGHTS = {
    "RS_WEIGHT": 0.50,
    "THEME_WEIGHT": 0.35,
    "ZACKS_WEIGHT": 0.10,
    "GROWTH_WEIGHT": 0.05,
}

# Short-specific Zacks scoring (reward confirmed sell ratings, penalise buys)
SHORT_ZACKS_SCORE_MAP = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}

# Short-specific Growth scoring (reward deteriorating earnings quality)
SHORT_GROWTH_SCORE_MAP = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}

# Short entry thresholds — Proven by 2026-10-31 Cartesian Backtest (197 Trades, 60.7% 10D WR, PF: 8.47, +20.5% Avg Return)
SHORT_ENTRY = {
    # 1. STRONG BEARISH (Active Breakdowns)
    "MIN_SHORT_RS": 8.0,
    "MAX_SHORT_RS": 60.0,
    "THEMES": ["Lagging"],
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 2_000_000,
}



# ==========================
# RE-ENTERED / INFLECTION ENGINE
# Scans recent dropped history for stocks whose fundamentals,
# theme flow, and price have confirmed a quantitative turnaround.
# ==========================
REENTERED_LONG = {
    "LOOKBACK_DAYS": 50,
    "ALLOWED_ZACKS": [1, 2],
    "ZACKS_3_MIN_SCORE": 70.0,
    "THEMES": ["Leading", "Neutral", "Unclassified Leader"],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
    "MIN_RS": 60.0,
    "MIN_LONG_SCORE": 60.0,
    "EXCLUDE_STRONG": True,
}

REENTERED_SHORT = {
    "LOOKBACK_DAYS": 50,
    "ALLOWED_ZACKS": [3, 4, 5],
    "THEMES": ["Lagging", "Neutral"],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
    "MAX_SHORT_RS": 50.0,
    "EXCLUDE_STRONG": True,
}

# ==========================
# PULLBACK & 52W RANGE GATE CONFIG (CLUB RULE)
# ==========================
PULLBACK_CONFIG = {
    "LONG_MIN_52W_RANGE": 85.0,
    "SHORT_MAX_52W_RANGE": 30.0,
    "WAIT_DAYS": 21,
    "LONG_PULLBACK_PCT": 0.08,    # 8% dip from pick date
    "SHORT_BOUNCE_PCT": 0.10,     # 10% bounce from pick date
    "MAX_HOLD_DAYS": 50,
}

# CLUB RULE STAY-IN THRESHOLDS
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

