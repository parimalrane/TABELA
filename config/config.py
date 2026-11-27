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
    # Backtest Winner (Theme Tier Optimization): 20% Leading / 60% Neutral / 20% Lagging
    "CLASSIFICATION_PERCENTAGE_LEADING": 0.20,
    "CLASSIFICATION_PERCENTAGE_LAGGING": 0.20
}

# ==========================
# BOTTOM-UP THEME BREADTH CONFIG
# ==========================
BOTTOM_UP_THEME_CONFIG = {
    "ENABLED": True,
    "LEADER_MIN_RS": 75.0,              # Minimum RS for a stock to qualify as a group leader
    "LEADER_MAX_OFF_HIGH_PCT": 15.0,    # Must be within 15% of 52-week high
    "SHRINKAGE_C": 10.0,                # Confidence weighting parameter (smooths small themes)
    "TOP_TIER_PCT": 0.20,               # Top 20% of themes = Leading (Backtest Winner)
    "BOTTOM_TIER_PCT": 0.20,            # Bottom 20% of themes = Lagging (Backtest Winner)
    # Dual-Engine Composite Weights:
    "WEIGHT_TOP_DOWN_ETF": 0.50,        # 50% Macro Top-Down ETF momentum
    "WEIGHT_BOTTOM_UP_BREADTH": 0.50,   # 50% Organic Bottom-Up stock breadth
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
# SECTOR MAPPINGS & GATES
# ==========================
ZACKS_TO_SPDR = {
    "Computer and Technology": "XLK",
    "Business Services": "XLK",
    "Finance": "XLF",
    "Medical": "XLV",
    "Oils-Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Retail-Wholesale": "XLY",
    "Auto-Tires-Trucks": "XLY",
    "Consumer Staples": "XLP",
    "Utilities": "XLU",
    "Basic Materials": "XLB",
    "Construction": "XLI",
    "Industrial Products": "XLI",
    "Aerospace": "XLI",
    "Transportation": "XLI",
    "Conglomerates": "XLI",
    "Multi-Sector Conglomerates": "XLI",
}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    "MIN_RS": 0.0,                     # RS unconstrained in screening (evaluated on chart)
    "BREAKOUT_MIN_RS": 90.0,           # Minimum RS for Breakout classification (top 10%)
    "THEMES": ["Leading", "Unclassified Leader"],
    "BLOCKED_SECTOR_STATUSES": ["LAGGING"], # Never swim upstream against lagging sectors
    "ALLOWED_ZACKS": [1, 2],
    "BLOCKED_ZACKS": [3, 4, 5],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
    "MIN_PCT_OFF_LOW": 0.0,            # 52W distance unconstrained (evaluated on chart)
    "MIN_52W_RANGE": 0.0,              # Preserved for backward-compat / fallback
    "BREAKOUT_MIN_52W_RANGE": 85.0,    # Minimum 52W range for breakout classification (near highs)
    # Zacks 3 Exception:
    "ZACKS_3_EXCEPTION_ENABLED": False,
    "ZACKS_3_ALLOWED_MIN_RS": 95.0,
    "ZACKS_3_ALLOWED_GROWTH": ["A", "B", "C"],
    # Elite Momentum Exception (e.g. KNSA):
    "ELITE_MIN_RS": 95.0,
    "ELITE_ALLOWED_GROWTH": ["A", "B"],
    "ELITE_ALT_MIN_VOLUME": 500_000,
    "ELITE_ALT_MIN_DOLLAR_VOL": 30_000_000,
    # Independent Leader Theme Exemption (Safety Valve against flawed/neutral themes):
    "THEME_EXEMPTION_ENABLED": False,
    "THEME_EXEMPTION_MIN_RS": 95.0,
    "THEME_EXEMPTION_MIN_RANGE": 85.0,
    "THEME_EXEMPTION_ALLOWED_ZACKS": [1, 2],
}

SHORT_ENTRY = {
    "MIN_SHORT_RS": 0.0,
    "MAX_SHORT_RS": 100.0,             # Sh_RS unconstrained in screening (evaluated on chart)
    "THEMES": ["Lagging"],
    "BLOCKED_SECTOR_STATUSES": ["LEADING"], # Never short into a leading sector tide
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
    "MAX_PCT_OFF_HIGH": 0.0,           # 52W distance unconstrained (evaluated on chart)
    "MAX_52W_RANGE": 100.0,            # Preserved for backward-compat
}

# ==========================
# 52W RANGE GATES (LIVE PIPELINE)
# ==========================
PULLBACK_CONFIG = {
    "LONG_MIN_52W_RANGE": 50.0,
    "LONG_BREAKOUT_MIN_52W_RANGE": 85.0,
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


# ==========================
# MILD BULLISH WATCHLIST CONFIGURATION (STATELESS PULLBACKS)
# ==========================
MILD_CONFIG = {
    "LONG_ALLOWED_THEMES": ["Leading"],
    "LONG_ALLOW_MICRO_LEADER": True,
    "LONG_MIN_RS": 50.0,
    "LONG_MIN_52W_RANGE": 40.0,
    "LONG_ALLOWED_ZACKS": [1, 2],
    "LONG_ZACKS_3_MIN_RS": 95.0,
    "LONG_ZACKS_3_ALLOWED_GROWTH": ["A", "B", "C"],
    "LONG_MIN_PRICE": 10.0,
    "LONG_MIN_VOLUME": 1_000_000,
}



