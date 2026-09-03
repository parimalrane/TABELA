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
    "MIN_RS": 85.0,
    "MIN_LONG_SCORE": 85.0,
    "THEMES": ["Leading", "Micro Leader", "Unclassified Leader", "Unknown"],
    "MAX_PER_THEME": 3,
    "MICRO_BREAKAWAY_PERCENTILE": 0.05
}

DIST_ENTRY = {
    "MAX_RS": 50.0,
    "MAX_LONG_SCORE": 50.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "MAX_PER_THEME": 3,
    "MICRO_BREAKAWAY_PERCENTILE": 0.05
}

