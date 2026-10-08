"""
TABELA QUARTERLY IN-MEMORY OPTIMIZATION GRID
===========================================

This config defines the parameter boundaries for the Quarterly 
Backtesting System. By testing all variations defined below, the 
engine discovers the most mathematically optimized pipeline configuration.

Long and Short sweeps are logically decoupled. 
Phase 1: Sweep Fundamental Math (RS Weights, Theme calculations)
Phase 2: Sweep Gate Logic (Thresholds, Scores)
"""

# ==============================================================================
# LONG ENGINE GRIDS
# ==============================================================================

# PHASE 1: LONG FUNDAMENTAL MATH
LONG_PHASE_1 = {
    # 1. ETF Momentum Engine (How Themes are Scored)
    "ETF_PERIOD_WEIGHTS": [
        {"1M": 0.40, "1W": 0.35, "3M": 0.25, "6M": 0.0, "1Y": 0.0}, # Current Fast Rotation
        {"1M": 0.33, "1W": 0.33, "3M": 0.34, "6M": 0.0, "1Y": 0.0}, # Equal Balanced
        {"1M": 0.20, "1W": 0.10, "3M": 0.40, "6M": 0.3, "1Y": 0.0}, # Structural Focus
    ],
    "ETF_AGGREGATION_MODE": ["aum_weighted", "equal_weight"],
    "THEME_BUCKETS": [
        {"L": 0.30, "N": 0.40, "D": 0.30}, # Baseline 30/40/30
        {"L": 0.20, "N": 0.60, "D": 0.20}, # Ultra-Strict Leaders
        {"L": 0.40, "N": 0.20, "D": 0.40}, # Polarized
    ],
    
    # 2. Stock Momentum (How RS Rating is Scored)
    "RS_RAW_WEIGHTS": [
        # LEGACY BASELINE (Turnarounds Allowed)
        {"4W": 0.60, "12W": 0.20, "1W": 0.20, "YTD": 0.0, "52W": 0.0},
        # PROPOSED PATCH (Garbage Filtered)
        {"4W": 0.40, "12W": 0.20, "1W": 0.10, "YTD": 0.10, "52W": 0.20},
    ],
    
    # 3. Composite Calculation (How Long_Score is Scored)
    "LONG_WEIGHTS": [
        {"RS": 0.60, "THEME": 0.20, "ZACKS": 0.10, "GROWTH": 0.10}, # Baseline Master
    ],
    
    # 4. Fundamental Curves
    "ZACKS_SCORE_MAP": [
        {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}, # Standard Rank (Blocks 4,5)
        {1: 100.0, 2: 80.0, 3: 50.0, 4: -50.0, 5: -100.0}, # Forgiving Turnaround
    ],
    "GROWTH_SCORE_MAP": [
        {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}, # Standard Growth
    ]
}

# PHASE 2: LONG GATES & THRESHOLDS
LONG_PHASE_2 = {
    "MIN_RS": [85.0, 90.0],
    "MIN_LONG_SCORE": [80.0, 85.0],
    "MIN_DROPPED_WATCH_SCORE": [70.0, 75.0, 80.0], # The Mild Pivot
    "MILD_DAYS": [14, 21, 35],
    "MIN_VOLUME": [1_000_000, 1_500_000],
    "BLOCKED_ZACKS": [[4,5], [3,4,5]],
    "DEEP_RETRACE_ZACKS": [[1,2], [1,2,3]],
}


# ==============================================================================
# SHORT ENGINE GRIDS
# ==============================================================================

# PHASE 1: SHORT FUNDAMENTAL MATH
SHORT_PHASE_1 = {
    # 1. Stock Breakdown Momentum
    "SHORT_RS_RAW_WEIGHTS": [
        # YTD Reversal (Baseline)
        {"4W": 0.30, "12W": 0.20, "1W": 0.10, "YTD": 0.40},
        # Sharp Collapse (Heavy Immediate)
        {"4W": 0.50, "12W": 0.30, "1W": 0.20, "YTD": 0.0},
    ],
    
    # 2. Composite Calculation
    "SHORT_COMPOSITE_WEIGHTS": [
        {"RS": 0.65, "THEME": 0.20, "ZACKS": 0.10, "GROWTH": 0.05}, # Baseline Breakdown
        {"RS": 0.50, "THEME": 0.35, "ZACKS": 0.10, "GROWTH": 0.05}, # Thematic Exodus
    ],
    
    # 3. Fundamental Curves
    "SHORT_ZACKS_SCORE_MAP": [
        {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0},
    ],
    "SHORT_GROWTH_SCORE_MAP": [
        {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0},
    ]
}

# PHASE 2: SHORT GATES & THRESHOLDS
SHORT_PHASE_2 = {
    "MAX_SHORT_RS": [60.0, 75.0],        # Ceiling for RS weakness
    "MIN_SHORT_RS": [8.0, 15.0],         # Floor to avoid graveyard
    "MAX_SHORT_SCORE": [25.0, 35.0, 45.0],
    "MAX_DROPPED_WATCH_SCORE": [65.0, 75.0], # Bounce resistance ceiling
    "MILD_DAYS": [14, 21],
    "MIN_VOLUME": [2_500_000, 5_000_000],
    "BLOCKED_ZACKS": [[1,2], [1,2,3]],
}

# ==============================================================================
# RETRACEMENT ENGINE GRIDS (PHASE 3)
# ==============================================================================

RETRACE_PHASE = {
    # 1. Long Retracement Weights (Testing Basing Logic vs Breakout Momentum)
    "LONG_RETRACE_WEIGHTS": [
        {"RS_WEIGHT": 0.20, "THEME_WEIGHT": 0.40, "ZACKS_WEIGHT": 0.25, "GROWTH_WEIGHT": 0.15}, # Proposed Fundamental Anchor
        {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.40, "ZACKS_WEIGHT": 0.10, "GROWTH_WEIGHT": 0.10}, # Moderate 
        {"RS_WEIGHT": 0.25, "THEME_WEIGHT": 0.50, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}, # Macro Thematic Anchor
    ],
    
    # 2. Long Retracement Thresholds
    "LONG_RETRACE_GATES": [
        {"DEEP_RETRACE_MIN_RS": 70.0, "DEEP_RETRACE_MIN_SCORE": 65.0}, # Institutional Standard
        {"DEEP_RETRACE_MIN_RS": 60.0, "DEEP_RETRACE_MIN_SCORE": 55.0}, # Loose
        {"DEEP_RETRACE_MIN_RS": 40.0, "DEEP_RETRACE_MIN_SCORE": 40.0}, # Ultra Forgiving
    ],

    # 3. Short Retracement Weights (Tracking Relief Rallies waiting for breakdowns)
    "SHORT_RETRACE_WEIGHTS": [
        {"RS_WEIGHT": 0.20, "THEME_WEIGHT": 0.40, "ZACKS_WEIGHT": 0.25, "GROWTH_WEIGHT": 0.15}, # Thematic decay priority
        {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.40, "ZACKS_WEIGHT": 0.10, "GROWTH_WEIGHT": 0.10}, # Balanced
    ],

    # 4. Short Retracement Thresholds
    "SHORT_RETRACE_GATES": [
        {"DEEP_RETRACE_MAX_RS": 25.0, "DEEP_RETRACE_MAX_SCORE": 40.0},
        {"DEEP_RETRACE_MAX_RS": 35.0, "DEEP_RETRACE_MAX_SCORE": 50.0},
        {"DEEP_RETRACE_MAX_RS": 50.0, "DEEP_RETRACE_MAX_SCORE": 60.0},
    ]
}
