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
        {"1M": 0.40, "1W": 0.20, "3M": 0.40, "6M": 0.0, "1Y": 0.0}, # Production Baseline (Balanced 1M/3M)
    ],
    "ETF_AGGREGATION_MODE": ["aum_weighted"],
    "THEME_BUCKETS": [
        {"L": 0.30, "N": 0.40, "D": 0.30}, # Baseline 30/40/30
    ],
    
    # 2. Stock Momentum (How RS Rating is Scored)
    "RS_RAW_WEIGHTS": [
        # 1. Production Baseline (High Near-Term Velocity)
        {"4W": 0.60, "12W": 0.20, "1W": 0.20, "YTD": 0.0, "52W": 0.0},
        # 2. Balanced 4W/12W Trend Confirmation
        {"4W": 0.40, "12W": 0.40, "1W": 0.20, "YTD": 0.0, "52W": 0.0},
        # 3. Structural 52W Patch
        {"4W": 0.40, "12W": 0.20, "1W": 0.10, "YTD": 0.10, "52W": 0.20},
        # 4. Multi-Timeframe Trend (YTD + 12W + 4W)
        {"4W": 0.35, "12W": 0.35, "1W": 0.10, "YTD": 0.20, "52W": 0.0},
        # 5. Ultra Short-Term Burst (1W/4W Heavy)
        {"4W": 0.50, "12W": 0.10, "1W": 0.40, "YTD": 0.0, "52W": 0.0},
    ],
    
    # 3. Composite Calculation (How Long_Score is Scored)
    "LONG_WEIGHTS": [
        {"RS": 0.60, "THEME": 0.20, "ZACKS": 0.10, "GROWTH": 0.10}, # 1. Production Baseline (60/20/10/10)
        {"RS": 0.50, "THEME": 0.25, "ZACKS": 0.15, "GROWTH": 0.10}, # 2. Config Comment Split (50% RS, 25% Theme, 25% Fund)
        {"RS": 0.70, "THEME": 0.15, "ZACKS": 0.10, "GROWTH": 0.05}, # 3. Pure RS Momentum (70/15/10/5)
        {"RS": 0.45, "THEME": 0.35, "ZACKS": 0.10, "GROWTH": 0.10}, # 4. Theme-Driven Leader (45/35/10/10)
        {"RS": 0.50, "THEME": 0.15, "ZACKS": 0.20, "GROWTH": 0.15}, # 5. Fundamental + Momentum Anchor (50/15/20/15)
    ],
    
    # 4. Fundamental Curves
    "ZACKS_SCORE_MAP": [
        {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}, # Standard Rank (Blocks 4,5)
    ],
    "GROWTH_SCORE_MAP": [
        {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}, # Standard Growth
    ]
}

# PHASE 2: LONG GATES & THRESHOLDS
LONG_PHASE_2 = {
    "MIN_RS": [80.0, 85.0, 90.0],
    "MIN_LONG_SCORE": [75.0, 80.0, 85.0],
    "THEMES": [["Leading"], ["Leading", "Neutral"], ["Leading", "Unclassified Leader"], ["Leading", "Neutral", "Unclassified Leader"]],
    "MIN_VOLUME": [500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000],
    "BLOCKED_ZACKS": [[4, 5], [3, 4, 5]],
    "MIN_DROPPED_WATCH_SCORE": [70.0],
    "MILD_DAYS": [14],
}


# ==============================================================================
# SHORT ENGINE GRIDS
# ==============================================================================

# PHASE 1: SHORT FUNDAMENTAL MATH
SHORT_PHASE_1 = {
    # 1. Stock Breakdown Momentum
    "SHORT_RS_RAW_WEIGHTS": [
        # 1. YTD Reversal (Production Baseline)
        {"4W": 0.30, "12W": 0.20, "1W": 0.10, "YTD": 0.40},
        # 2. Sharp Collapse (Heavy Immediate)
        {"4W": 0.50, "12W": 0.30, "1W": 0.20, "YTD": 0.0},
        # 3. Balanced Intermediate Breakdown
        {"4W": 0.40, "12W": 0.30, "1W": 0.10, "YTD": 0.20},
        # 4. 12W Structural Roll-Over
        {"4W": 0.25, "12W": 0.45, "1W": 0.10, "YTD": 0.20},
        # 5. Heavy YTD Structural Decay
        {"4W": 0.20, "12W": 0.20, "1W": 0.05, "YTD": 0.55},
    ],
    
    # 2. Composite Calculation
    "SHORT_COMPOSITE_WEIGHTS": [
        {"RS": 0.50, "THEME": 0.35, "ZACKS": 0.10, "GROWTH": 0.05}, # 1. Production Baseline: Thematic Exodus (50/35/10/5)
        {"RS": 0.65, "THEME": 0.20, "ZACKS": 0.10, "GROWTH": 0.05}, # 2. Legacy Breakdown (65/20/10/5)
        {"RS": 0.75, "THEME": 0.15, "ZACKS": 0.05, "GROWTH": 0.05}, # 3. Pure Breakdown Momentum (75/15/5/5)
        {"RS": 0.55, "THEME": 0.25, "ZACKS": 0.10, "GROWTH": 0.10}, # 4. Balanced Bearish (55/25/10/10)
        {"RS": 0.50, "THEME": 0.20, "ZACKS": 0.20, "GROWTH": 0.10}, # 5. Fundamental Deterioration Heavy (50/20/20/10)
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
    "MAX_SHORT_SCORE": [25.0, 30.0, 35.0, 40.0],
    "THEMES": [["Lagging"], ["Lagging", "Neutral"], ["Lagging", "Neutral", "Unknown"]],
    "MIN_VOLUME": [500_000, 1_000_000, 2_000_000, 3_000_000, 5_000_000],
    "BLOCKED_ZACKS": [[1,2], [1,2,3]],
    "MAX_DROPPED_WATCH_SCORE": [70.0], # Bounce resistance ceiling
    "MILD_DAYS": [14],
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
