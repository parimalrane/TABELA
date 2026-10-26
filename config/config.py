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

# Weights for the sector composite strength score
SECTOR_COMPOSITE_WEIGHTS = {
    "Performance 1W (%)": 0.2,
    "Performance 1M (%)": 0.4,
    "Performance 3M (%)": 0.3,
    "Performance YTD (%)": 0.1,
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

# Zacks Binary: Only Rank 1/2 survive. Rank 3 turnarounds = poison (proven by 61-experiment grid search)
ZACKS_SCORE_MAP = {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}
GROWTH_SCORE_MAP = {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    # Re-tightened to Institutional Elite (Top 10% constraints) for strict watchlist quality over quantity
    "MIN_RS": 90.0,
    "MIN_LONG_SCORE": 85.0,
    "THEMES": ["Leading", "Unclassified Leader"],
    "BLOCKED_ZACKS": [4, 5],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_500_000,
    "MIN_DROPPED_WATCH_SCORE": 70.0,
    "MILD_DAYS": 21
}


# ==========================
# MILD WATCHLIST ENTRY CRITERIA
# Config-driven filtering for mild watchlist candidates
# ==========================

MILD_LONG_ENTRY = {
    # Theme restriction: Long mild stocks must NOT be from lagging themes
    "BLOCKED_THEMES": ["Lagging"],
    
    # Zacks restriction: Long mild stocks must have Zacks rank 1 or 2 only
    "ALLOWED_ZACKS": [1, 2, 3],
    
    # Minimum thresholds (optional - can be more lenient than LONG_ENTRY)
    "MIN_RS": 70.0,
    "MIN_LONG_SCORE": 60.0,
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
    # 1. STRONG BEARISH (Active Breakdowns) - Thematic Exodus Strategy Winner
    "MIN_SHORT_RS": 15.0,
    "MAX_SHORT_RS": 60.0,
    "MAX_SHORT_SCORE": 25.0,
    "THEMES": ["Lagging"],
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 5_000_000,
    
    # 2. MILD BEARISH (Relief Rallies - Days 1 to 14)
    "MAX_DROPPED_WATCH_SCORE": 70.0,
    "MILD_DAYS": 14
}

MILD_SHORT_ENTRY = {
    # Theme restriction: Short mild stocks must NOT be from leading themes
    "BLOCKED_THEMES": ["Leading", "Unclassified Leader"],
    
    # Zacks restriction: Short mild stocks must have Zacks rank 4 or 5 only
    "ALLOWED_ZACKS": [3, 4, 5],
    
    # Maximum thresholds (optional - can be more lenient than SHORT_ENTRY)
    "MAX_SHORT_RS": 70.0,
    "MAX_SHORT_SCORE": 60.0,
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
}

