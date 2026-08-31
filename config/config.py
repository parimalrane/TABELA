COMPOSITE_WEIGHTS = {

    "RS_WEIGHT": 0.40,
    "THEME_WEIGHT": 0.25,
    "MARGIN_WEIGHT": 0.05,
    "ZACKS_WEIGHT": 0.10,
    "SALES_WEIGHT": 0.20



}

THEME_STRENGTH_CONFIG = {
    # Benchmark ETF used for relative-return subtraction.
    "BENCHMARK_TICKER": "SPY",

    # Relative-return weights by ETF performance period.
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.45,
        "Performance 1W (%)": 0.30,
        "Performance 3M (%)": 0.20,
        "Performance 1D (%)": 0.05,
    },

    # Theme aggregation mode: "aum_weighted" or "equal_weight".
    "AGGREGATION_MODE": "aum_weighted",

    # Controls whether the 0-100 normalized diagnostic score is computed.
    "ENABLE_NORMALIZATION": True
}

LONG_WEIGHTS = {

    "RS_WEIGHT": 0.55,

    "THEME_WEIGHT": 0.25,

    "SALES_WEIGHT": 0.07,

    "ZACKS_WEIGHT": 0.10,

    "MARGIN_WEIGHT": 0.03

}

# ==========================
# THRESHOLDS (STATE-BASED)
# ==========================

LONG_ENTRY = {
    "MIN_RS": 90.0,
    "MIN_LONG_SCORE": 90.0,
    "THEMES": ["Leading", "Unclassified Leader", "Unknown"],
    "MAX_LIST_SIZE": 21
}

DIST_ENTRY = {
    "MAX_RS": 50.0,
    "MAX_LONG_SCORE": 50.0,
    "THEMES": ["Lagging"],
    "MAX_LIST_SIZE": 21
}

# ==========================================
# STOCK TRANSITION ENGINE
# ==========================================

STOCK_TRANSITION_CONFIG = {
    # Immutable daily registry location
    "REGISTRY_DIR": "market_data/stock_transition"
}
