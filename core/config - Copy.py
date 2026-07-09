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



SHORT_FILTERS = {

   "MIN_SHORT_SCORE": 70,

   "USE_LEGACY_WEAKNESS_FILTER": True

}


DISTRIBUTION_ENGINE_CONFIG = {
    "DEFAULT_TOP_N": 50,
    "MAX_HISTORY_DAYS": 21,
    "SNAPSHOT_MAX_DAYS": 21,
    "ROTATION_MAX_FILES": 3,
    "RECENT_BASELINE_LOOKBACK_DAYS": 5,
    "DOWNTREND_WINDOW_DAYS": 5,
    "MIN_RS_DROP_1D": 0.0,
    "MIN_RS_DROP_RECENT": 0.0,
    "MIN_COMPOSITE_DROP_1D": 0.0,
    "MIN_COMPOSITE_DROP_RECENT": 0.0,
    "MIN_RS_PERSISTENCE_DAYS": 2,
    "MIN_COMPOSITE_PERSISTENCE_DAYS": 2,
    "MIN_RS_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_RS_DROP_RECENT_FOR_DOWN_DAYS": 0.0,
    "MIN_COMPOSITE_DROP_RECENT_FOR_DOWN_DAYS": 0.0,
    "USE_COMPOSITE_MEDIAN_CONFIRMATION_WHEN_HISTORY_SPARSE": True,
    "MIN_COMPOSITE_MEDIAN_CONFIRMATION_GAP": 0.0,
    "LEADERSHIP_RS_THRESHOLD": 80.0,
    "USE_LEADERSHIP_AS_HISTORY_CONFIRMATION": True,
    "MIN_RS_DROP_RECENT_FOR_LEADERSHIP_CONFIRMATION": 0.0,
    "MIN_THEME_LAGGING_STREAK_DAYS": 3,
    "MIN_THEME_WEAKENING_TRANSITIONS": 2,
    "MAX_REASON_TOKENS": 6,
    "SORT_LEADERSHIP_MISSING_SENTINEL": 9999,
}


ETF_FILTERS = {

    "MIN_MARKET_VALUE": 200

}


THEME_STRENGTH_CONFIG = {
    # Benchmark ETF used for relative-return subtraction.
    "BENCHMARK_TICKER": "QQQ",

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

    "SALES_WEIGHT": 0.12,

    "ZACKS_WEIGHT": 0.05,

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
# FILE PATHS
# ==========================================

DATA_FOLDER = "market_data"

# ==========================================
# LONG SCORING WEIGHTS
# ==========================================

RS_WEIGHT = 40

THEME_WEIGHT = 25

MARGIN_WEIGHT = 15

SALES_WEIGHT = 10

ZACKS_WEIGHT = 10





# ==========================================
# UNKNOWN EMERGING LEADERS
# ==========================================

UNKNOWN_RS_THRESHOLD = 85

UNKNOWN_LONG_SCORE_THRESHOLD = 80

UNKNOWN_PRICE_POSITION_THRESHOLD = 80

UNKNOWN_MARKET_CAP_THRESHOLD = 500



# ==========================================
# WEEKLY REVIEW PARAMETERS
# ==========================================

MIN_MARKET_CAP = 300

MIN_PRICE_FILTER = 5

MIN_VOLUME_FILTER = 300000



