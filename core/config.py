COMPOSITE_WEIGHTS = {

    "RS_WEIGHT": 0.40,
    "THEME_WEIGHT": 0.25,
    "MARGIN_WEIGHT": 0.05,
    "ZACKS_WEIGHT": 0.10

}


LONG_FILTERS = {

   "MIN_RS": 90,

   "MIN_LONG_SCORE": 85

}




MIN_HISTORY_DAYS = 20


DISTRIBUTION_ENGINE_CONFIG = {
    # Universe and file windows.
    "DEFAULT_TOP_N": 50,
    "MAX_HISTORY_DAYS": 21,
    "SNAPSHOT_MAX_DAYS": 21,
    "ROTATION_MAX_FILES": 3,

    # Trend/baseline lookbacks.
    "RECENT_BASELINE_LOOKBACK_DAYS": 5,
    "DOWNTREND_WINDOW_DAYS": 5,

    # RS deterioration thresholds.
    "MIN_RS_DROP_1D": 0.0,
    "MIN_RS_DROP_RECENT": 0.0,

    # Composite deterioration thresholds.
    "MIN_COMPOSITE_DROP_1D": -0.001,
    "MIN_COMPOSITE_DROP_RECENT": -0.001,

    # Persistence and down-day confirmation.
    "MIN_RS_PERSISTENCE_DAYS": 2,
    "MIN_COMPOSITE_PERSISTENCE_DAYS": 2,
    "MIN_RS_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_RS_DROP_RECENT_FOR_DOWN_DAYS": 25.0,
    "MIN_COMPOSITE_DROP_RECENT_FOR_DOWN_DAYS": 0.0,

    # Sparse-history handling.
    "SPARSE_COMPOSITE_HISTORY_MAX_POINTS": 1,
    "USE_COMPOSITE_MEDIAN_CONFIRMATION_WHEN_HISTORY_SPARSE": True,
    "MIN_COMPOSITE_MEDIAN_CONFIRMATION_GAP": 0.0,

    # Leadership-based historical confirmation.
    "LEADERSHIP_RS_THRESHOLD": 80.0,
    "USE_LEADERSHIP_AS_HISTORY_CONFIRMATION": True,
    "MIN_RS_DROP_RECENT_FOR_LEADERSHIP_CONFIRMATION": 25.0,

    # Theme context thresholds (context only, not classifier).
    "MIN_THEME_LAGGING_STREAK_DAYS": 3,
    "MIN_THEME_WEAKENING_TRANSITIONS": 2,

    # Output/readability controls.
    "MAX_REASON_TOKENS": 6,
    "EVIDENCE_MIN_ABS_DELTA": 0.05,

    # Ranking defaults.
    "SORT_LEADERSHIP_MISSING_SENTINEL": 9999,
}


ETF_FILTERS = {

    "MIN_MARKET_VALUE": 200

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
    "ENABLE_NORMALIZATION": True,

    # Enables temporary terminal diagnostics for Theme Strength.
    "DEBUG_THEME_STRENGTH": True,
}




LONG_WEIGHTS = {

    "RS_WEIGHT": 0.55,

    "THEME_WEIGHT": 0.25,

    "SALES_WEIGHT": 0.07,

    "ZACKS_WEIGHT": 0.10,

    "MARGIN_WEIGHT": 0.03

}


SHORT_WEIGHTS = {

    "RS_WEIGHT": 0.45,

    "THEME_WEIGHT": 0.42,

    "SALES_WEIGHT": 0.00,

    "ZACKS_WEIGHT": 0.10,

    "MARGIN_WEIGHT": 0.03

}





# ==========================================
# STOCK TRANSITION ENGINE
# ==========================================

STOCK_TRANSITION_CONFIG = {
    # Immutable daily registry location
    "REGISTRY_DIR": "market_data/stock_transition",

    # Observation lifecycle (measured in successful TABELA runs)
    "OBSERVATION_MIN_RUNS": 7,
    "OBSERVATION_MAX_RUNS": 7,
}

OBSERVATION_FALLBACK_SCORE_THRESHOLD = 80.0
OBSERVATION_FALLBACK_RS_THRESHOLD = 80.0

