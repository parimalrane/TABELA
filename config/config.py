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

# Zacks Binary: Only Rank 1/2 survive. Rank 3 turnarounds = poison (proven by 61-experiment grid search)
ZACKS_SCORE_MAP = {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}
GROWTH_SCORE_MAP = {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    # Vectorized Optimization Winner: "Tight Gate (90 RS / 85 Long Score) -> 44.2% WR"
    "MIN_RS": 90.0,
    "MIN_LONG_SCORE": 85.0,
    "THEMES": ["Leading", "Neutral", "Unclassified Leader", "Unknown"],
    "BLOCKED_ZACKS": [4, 5],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_500_000,
    "MIN_DROPPED_WATCH_SCORE": 80.0,
    "MILD_DAYS": 21,
    "PURGE_DAYS": 50
}

DIST_ENTRY = {
    # Phase 2 Grid Search Winner (T7): 73.28% WR | +5.16% avg return | ~11 shorts/day
    # "Fall From Grace" zone: former mid-range stocks actively losing momentum
    "MIN_RS": 50.0,            # Floor: stocks must still have some standing to fall from
    "MAX_RS": 75.0,            # Ceiling: catch before they become obvious laggards
    "MAX_LONG_SCORE": 50.0,    # Only short stocks with clear composite deterioration
    "THEMES": ["Neutral", "Unknown"],  # Neutral-only: Lagging adds noise at this RS level
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
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
    "RS_WEIGHT": 0.65,
    "THEME_WEIGHT": 0.20,
    "ZACKS_WEIGHT": 0.10,
    "GROWTH_WEIGHT": 0.05,
}

# Short-specific Zacks scoring (reward confirmed sell ratings, penalise buys)
SHORT_ZACKS_SCORE_MAP = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}

# Short-specific Growth scoring (reward deteriorating earnings quality)
SHORT_GROWTH_SCORE_MAP = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}

# Short entry thresholds — Ultra-Premium Cartesian Winner (Low Volume / High Probability)
SHORT_ENTRY = {
    # 1. STRONG BEARISH (Active Breakdowns)
    "MIN_SHORT_RS": 40.0,
    "MAX_SHORT_RS": 75.0,
    "MAX_SHORT_SCORE": 45.0,
    "THEMES": ["Lagging", "Micro Laggard", "Neutral", "Unknown"],
    "BLOCKED_ZACKS": [1, 2, 3],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 2_500_000,
    
    # 2. MILD BEARISH (Relief Rallies - Days 1 to 21)
    "MAX_DROPPED_WATCH_SCORE": 75.0,
    "MILD_DAYS": 21,
    "PURGE_DAYS": 50
}

# ==========================
# GARAGE ENGINE (Phase 2 Optimization)
# ==========================
LONG_GARAGE_RS_RAW_WEIGHTS = {
    "% Price Change (1 Week)": 0.70,       # Extreme weight on immediate breakout flow
    "% Price Change (4 Weeks)": 0.30,      # Minor stabilization weight
    "% Price Change (12 Weeks)": 0.00,
    "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00
}

LONG_GARAGE_ENTRY = {
    "WAKE_UP_SCORE": 85.0
}

SHORT_GARAGE_RS_RAW_WEIGHTS = {
    "% Price Change (1 Week)": 0.70,       # Extreme weight on immediate downside thrust
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.00,
    "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00
}

SHORT_GARAGE_ENTRY = {
    "WAKE_UP_SCORE": 85.0
}


