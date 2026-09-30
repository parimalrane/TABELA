"""
TABELA AUTO-TUNER PHASE 2: Combined Multi-Dimensional Grid Search
=================================================================
Tests combinations of the best performers from Phase 1 across
Stock RS + Theme Scoring + Composite Weights + Zacks/Growth simultaneously.

Usage: python run_tuner_phase2.py
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_tuner.py"
RESULTS_FILE = BASE_DIR / "optimization_results_phase2.csv"

# ============================================================
# PHASE 2: COMBINED EXPERIMENTS
# ============================================================
# Phase 1 proved:
#   - Threshold 90/85 is the single biggest lever
#   - Current RS formula (50/40/10) is strong
#   - Current Theme formula (35/40/25) is strong
#   - Steep Zacks + Steep Fibonacci showed marginal gains
#   - Theme Heavy composite showed promise
#
# Phase 2 now COMBINES the top contenders from each dimension
# to find the true global optimum.
# ============================================================

# --- RS FORMULAS ---
RS_CURRENT = {
    "% Price Change (4 Weeks)": 0.50,
    "% Price Change (12 Weeks)": 0.40,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
RS_12W_DOMINANT = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.60,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
RS_YTD_COMEBACK = {
    "% Price Change (4 Weeks)": 0.40,
    "% Price Change (12 Weeks)": 0.35,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.15,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
RS_HYBRID = {
    "% Price Change (4 Weeks)": 0.35,
    "% Price Change (12 Weeks)": 0.35,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.10,
    "Price as a % of 52 Wk H-L Range": 0.10,
}
RS_WEEKLY_PULSE = {
    "% Price Change (4 Weeks)": 0.40,
    "% Price Change (12 Weeks)": 0.30,
    "% Price Change (1 Week)": 0.30,
    "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00,
}

# --- THEME FORMULAS ---
THEME_CURRENT = {
    "Performance 1M (%)": 0.40, "Performance 1W (%)": 0.35,
    "Performance 3M (%)": 0.25, "Performance 6M (%)": 0.00,
    "Performance 1Y (%)": 0.00, "Performance 1D (%)": 0.00,
}
THEME_MONTHLY_DOM = {
    "Performance 1M (%)": 0.60, "Performance 1W (%)": 0.10,
    "Performance 3M (%)": 0.20, "Performance 6M (%)": 0.10,
    "Performance 1Y (%)": 0.00, "Performance 1D (%)": 0.00,
}
THEME_QUARTERLY = {
    "Performance 1M (%)": 0.25, "Performance 1W (%)": 0.10,
    "Performance 3M (%)": 0.45, "Performance 6M (%)": 0.15,
    "Performance 1Y (%)": 0.05, "Performance 1D (%)": 0.00,
}
THEME_6M_ANCHOR = {
    "Performance 1M (%)": 0.20, "Performance 1W (%)": 0.10,
    "Performance 3M (%)": 0.25, "Performance 6M (%)": 0.35,
    "Performance 1Y (%)": 0.10, "Performance 1D (%)": 0.00,
}
THEME_BALANCED = {
    "Performance 1W (%)": 0.15, "Performance 1M (%)": 0.25,
    "Performance 3M (%)": 0.30, "Performance 6M (%)": 0.20,
    "Performance 1Y (%)": 0.10, "Performance 1D (%)": 0.00,
}

# --- COMPOSITE WEIGHT SETS ---
COMP_CURRENT = {"RS_WEIGHT": 0.50, "THEME_WEIGHT": 0.25, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}
COMP_THEME_HEAVY = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.35, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}
COMP_EQUAL = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.30, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.15}
COMP_RS_HEAVY = {"RS_WEIGHT": 0.60, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.12, "GROWTH_WEIGHT": 0.08}

# --- ZACKS CURVES ---
ZACKS_FLAT = {1: 100.0, 2: 95.0, 3: 90.0, 4: 20.0, 5: -50.0}
ZACKS_STEEP = {1: 100.0, 2: 80.0, 3: 60.0, 4: 20.0, 5: -50.0}
ZACKS_BINARY = {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}

# --- GROWTH CURVES ---
GROWTH_FLAT = {"A": 100.0, "B": 95.0, "C": 90.0, "D": 20.0, "F": -50.0}
GROWTH_FIBONACCI = {"A": 100.0, "B": 78.6, "C": 61.8, "D": 38.2, "F": 0.0}


def make_combo(name, hypothesis, rs, theme, comp, zacks, growth, min_rs, min_score, lead_pct=0.30, lag_pct=0.30, blocked=[4,5]):
    return {
        "name": name,
        "hypothesis": hypothesis,
        "RS_RAW_WEIGHTS": rs,
        "PERIOD_WEIGHTS": theme,
        "LONG_WEIGHTS": comp,
        "ZACKS_SCORE_MAP": zacks,
        "GROWTH_SCORE_MAP": growth,
        "MIN_RS": min_rs,
        "MIN_LONG_SCORE": min_score,
        "CLASSIFICATION_PERCENTAGE_LEADING": lead_pct,
        "CLASSIFICATION_PERCENTAGE_LAGGING": lag_pct,
        "BLOCKED_ZACKS": blocked,
    }


EXPERIMENTS = [
    # ============================
    # CONTROL: Phase 1 Winner
    # ============================
    make_combo("Phase1 Winner: 90/85 Baseline",
               "Phase 1 winner. All current settings + RS threshold raised to 90.",
               RS_CURRENT, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    # ============================
    # RS VARIATIONS at 90/85
    # ============================
    make_combo("90/85 + RS: 12W Dominant",
               "Does 12W dominant RS work better at the tighter 90 gate?",
               RS_12W_DOMINANT, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + RS: YTD Comeback",
               "Does YTD drift help at the 90 gate?",
               RS_YTD_COMEBACK, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + RS: Hybrid",
               "Does structural RS (YTD+52W) work at the 90 gate?",
               RS_HYBRID, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + RS: Weekly Pulse",
               "Does amplified weekly catch faster at 90 gate?",
               RS_WEEKLY_PULSE, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    # ============================
    # THEME VARIATIONS at 90/85
    # ============================
    make_combo("90/85 + Theme: Monthly Dominance",
               "Does monthly ETF weight work better at 90 gate?",
               RS_CURRENT, THEME_MONTHLY_DOM, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Theme: Quarterly Anchor",
               "Does quarterly ETF weight work at 90 gate?",
               RS_CURRENT, THEME_QUARTERLY, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Theme: 6-Month Anchor",
               "Does 6M institutional flow work at 90 gate?",
               RS_CURRENT, THEME_6M_ANCHOR, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Theme: Balanced All-Period",
               "Does balanced theme scoring work at 90 gate?",
               RS_CURRENT, THEME_BALANCED, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    # ============================
    # COMPOSITE VARIATIONS at 90/85
    # ============================
    make_combo("90/85 + Composite: Theme Heavy",
               "Does Theme Heavy composite amplify the 90 gate edge?",
               RS_CURRENT, THEME_CURRENT, COMP_THEME_HEAVY, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Composite: Equal Split",
               "Does Equal Split composite balance the 90 gate?",
               RS_CURRENT, THEME_CURRENT, COMP_EQUAL, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Composite: RS Heavy",
               "Does pure RS heavy compound with the 90 gate?",
               RS_CURRENT, THEME_CURRENT, COMP_RS_HEAVY, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    # ============================
    # ZACKS/GROWTH COMBOS at 90/85
    # ============================
    make_combo("90/85 + Zacks Steep + Growth Fibonacci",
               "Do both steep curves compound at the 90 gate?",
               RS_CURRENT, THEME_CURRENT, COMP_CURRENT, ZACKS_STEEP, GROWTH_FIBONACCI, 90.0, 85.0),

    make_combo("90/85 + Zacks Binary",
               "Does binary Zacks work at the 90 gate?",
               RS_CURRENT, THEME_CURRENT, COMP_CURRENT, ZACKS_BINARY, GROWTH_FLAT, 90.0, 85.0),

    make_combo("90/85 + Growth Fibonacci Only",
               "Does steep Growth alone improve at the 90 gate?",
               RS_CURRENT, THEME_CURRENT, COMP_CURRENT, ZACKS_FLAT, GROWTH_FIBONACCI, 90.0, 85.0),

    # ============================
    # FULL COMBO CANDIDATES (Best of Phase 1 stacked)
    # ============================
    make_combo("MEGA COMBO A: 90/85 + Theme Heavy + Steep Zacks + Fib Growth",
               "Stack ALL Phase 1 marginal winners on 90/85.",
               RS_CURRENT, THEME_CURRENT, COMP_THEME_HEAVY, ZACKS_STEEP, GROWTH_FIBONACCI, 90.0, 85.0),

    make_combo("MEGA COMBO B: 90/85 + Equal Split + Steep Zacks + Fib Growth",
               "Equal composite + steep fundamentals on 90/85.",
               RS_CURRENT, THEME_CURRENT, COMP_EQUAL, ZACKS_STEEP, GROWTH_FIBONACCI, 90.0, 85.0),

    make_combo("MEGA COMBO C: 90/85 + Theme Heavy + 6M Anchor + Steep Zacks",
               "Theme Heavy composite + slow theme rotation on 90/85.",
               RS_CURRENT, THEME_6M_ANCHOR, COMP_THEME_HEAVY, ZACKS_STEEP, GROWTH_FLAT, 90.0, 85.0),

    make_combo("MEGA COMBO D: 90/85 + 12W RS + Monthly Theme + Theme Heavy",
               "Slower RS + monthly theme + theme heavy composite.",
               RS_12W_DOMINANT, THEME_MONTHLY_DOM, COMP_THEME_HEAVY, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    make_combo("MEGA COMBO E: 90/85 + Weekly RS + Current Theme + RS Heavy",
               "Fast RS + fast theme + RS heavy composite.",
               RS_WEEKLY_PULSE, THEME_CURRENT, COMP_RS_HEAVY, ZACKS_FLAT, GROWTH_FLAT, 90.0, 85.0),

    # ============================
    # ULTRA TIGHT 90/90 COMBOS
    # ============================
    make_combo("Ultra 90/90 + Theme Heavy + Steep Fundamentals",
               "Does the 90/90 champ get even better with steep curves?",
               RS_CURRENT, THEME_CURRENT, COMP_THEME_HEAVY, ZACKS_STEEP, GROWTH_FIBONACCI, 90.0, 90.0),

    make_combo("Ultra 90/90 + 6M Theme Anchor",
               "Does slow theme rotation help at ultra-tight gate?",
               RS_CURRENT, THEME_6M_ANCHOR, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 90.0),

    make_combo("Ultra 90/90 + 12W RS + Quarterly Theme",
               "Slow RS + slow theme at ultra-tight gate.",
               RS_12W_DOMINANT, THEME_QUARTERLY, COMP_CURRENT, ZACKS_FLAT, GROWTH_FLAT, 90.0, 90.0),

    make_combo("Ultra 90/90 + Weekly RS + Monthly Theme + Equal Split",
               "Fast RS + monthly theme + balanced composite at ultra-tight.",
               RS_WEEKLY_PULSE, THEME_MONTHLY_DOM, COMP_EQUAL, ZACKS_FLAT, GROWTH_FLAT, 90.0, 90.0),

    make_combo("Ultra 90/90 + Zacks Binary + Growth Fibonacci",
               "Maximum fundamental strictness at ultra-tight gate.",
               RS_CURRENT, THEME_CURRENT, COMP_CURRENT, ZACKS_BINARY, GROWTH_FIBONACCI, 90.0, 90.0),
]


def generate_config_content(exp):
    pw = exp["PERIOD_WEIGHTS"]
    lw = exp["LONG_WEIGHTS"]
    rs = exp["RS_RAW_WEIGHTS"]
    zsm = exp["ZACKS_SCORE_MAP"]
    gsm = exp["GROWTH_SCORE_MAP"]
    blocked = exp.get("BLOCKED_ZACKS", [4, 5])

    content = f'''THEME_STRENGTH_CONFIG = {{
    "BENCHMARK_TICKER": "SPY",
    "PERIOD_WEIGHTS": {{
        "Performance 1M (%)": {pw.get("Performance 1M (%)", 0.0)},
        "Performance 1W (%)": {pw.get("Performance 1W (%)", 0.0)},
        "Performance 3M (%)": {pw.get("Performance 3M (%)", 0.0)},
        "Performance 6M (%)": {pw.get("Performance 6M (%)", 0.0)},
        "Performance 1Y (%)": {pw.get("Performance 1Y (%)", 0.0)},
        "Performance 1D (%)": {pw.get("Performance 1D (%)", 0.0)},
    }},
    "AGGREGATION_MODE": "aum_weighted",
    "ENABLE_NORMALIZATION": True,
    "CLASSIFICATION_PERCENTAGE_LEADING": {exp["CLASSIFICATION_PERCENTAGE_LEADING"]},
    "CLASSIFICATION_PERCENTAGE_LAGGING": {exp["CLASSIFICATION_PERCENTAGE_LAGGING"]}
}}

LONG_WEIGHTS = {{
    "RS_WEIGHT": {lw["RS_WEIGHT"]},
    "THEME_WEIGHT": {lw["THEME_WEIGHT"]},
    "ZACKS_WEIGHT": {lw["ZACKS_WEIGHT"]},
    "GROWTH_WEIGHT": {lw["GROWTH_WEIGHT"]}
}}

RS_RAW_WEIGHTS = {{
    "% Price Change (4 Weeks)": {rs.get("% Price Change (4 Weeks)", 0.0)},
    "% Price Change (12 Weeks)": {rs.get("% Price Change (12 Weeks)", 0.0)},
    "% Price Change (1 Week)": {rs.get("% Price Change (1 Week)", 0.0)},
    "Relative Price Change (YTD)": {rs.get("Relative Price Change (YTD)", 0.0)},
    "Price as a % of 52 Wk H-L Range": {rs.get("Price as a % of 52 Wk H-L Range", 0.0)}
}}

ZACKS_SCORE_MAP = {{{", ".join(f"{k}: {v}" for k, v in zsm.items())}}}
GROWTH_SCORE_MAP = {{{", ".join(f"'{k}': {v}" for k, v in gsm.items())}}}

LONG_ENTRY = {{
    "MIN_RS": {exp["MIN_RS"]},
    "MIN_LONG_SCORE": {exp["MIN_LONG_SCORE"]},
    "THEMES": ["Leading", "Neutral", "Unclassified Leader", "Unknown"],
    "BLOCKED_ZACKS": {blocked},
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 300000,
    "MIN_DROPPED_WATCH_SCORE": 70.0
}}

DIST_ENTRY = {{
    "MAX_RS": 10.0,
    "MAX_LONG_SCORE": 20.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
}}
'''
    return content


def run_regression_silent():
    result = subprocess.run(
        ["python", str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def run_backtest_silent():
    sys.path.insert(0, str(BASE_DIR))
    import importlib
    for mod in ["config.config", "scoring.scoring_engine", "scoring.long_scoring_engine", "backtest"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    from backtest import run_backtest
    return run_backtest(silent=True)


def main():
    total = len(EXPERIMENTS)

    print("=" * 80)
    print("     TABELA AUTO-TUNER PHASE 2: Multi-Dimensional Combo Search")
    print(f"     {total} Combined Experiments | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py backed up.")

    results = []

    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        hypothesis = exp["hypothesis"]

        print(f"\n{'='*80}")
        print(f"  EXPERIMENT {idx}/{total}: {name}")
        print(f"  Hypothesis: {hypothesis}")

        # Describe what changed
        rs_label = "Current" if exp["RS_RAW_WEIGHTS"] == RS_CURRENT else "Modified"
        theme_label = "Current" if exp["PERIOD_WEIGHTS"] == THEME_CURRENT else "Modified"
        comp_label = f"{exp['LONG_WEIGHTS']['RS_WEIGHT']}/{exp['LONG_WEIGHTS']['THEME_WEIGHT']}/{exp['LONG_WEIGHTS']['ZACKS_WEIGHT']}/{exp['LONG_WEIGHTS']['GROWTH_WEIGHT']}"
        gate_label = f"{exp['MIN_RS']}/{exp['MIN_LONG_SCORE']}"

        print(f"  RS: {rs_label} | Theme: {theme_label} | Composite: {comp_label} | Gate: {gate_label}")
        print(f"{'='*80}")

        config_content = generate_config_content(exp)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(config_content)
        print(f"  [1/3] Config rewritten.")

        t0 = time.time()
        print(f"  [2/3] Running regression...")
        reg_ok = run_regression_silent()
        reg_time = round(time.time() - t0, 1)

        if not reg_ok:
            print(f"  [ERROR] Regression failed. Skipping.")
            results.append({
                "Experiment": idx, "Name": name, "Hypothesis": hypothesis,
                "RS_Formula": rs_label, "Theme_Formula": theme_label,
                "Composite": comp_label, "Gate": gate_label,
                "Total Trades": "ERROR", "Win Rate (%)": "ERROR",
                "Avg Return (%)": "ERROR",
                "Leading Trades": "ERROR", "Leading WR (%)": "ERROR", "Leading Avg (%)": "ERROR",
                "Neutral Trades": "ERROR", "Neutral WR (%)": "ERROR", "Neutral Avg (%)": "ERROR",
                "Regression Time (s)": reg_time,
            })
            continue

        print(f"  [2/3] Regression complete in {reg_time}s.")
        print(f"  [3/3] Running backtest...")
        bt = run_backtest_silent()

        if bt is None:
            bt = {"total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                  "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
                  "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0}

        print(f"  >>> Trades: {bt['total_trades']} | Win Rate: {bt['win_rate']}% | Avg Return: {bt['avg_return']}%")

        results.append({
            "Experiment": idx, "Name": name, "Hypothesis": hypothesis,
            "RS_Formula": rs_label, "Theme_Formula": theme_label,
            "Composite": comp_label, "Gate": gate_label,
            "Total Trades": bt["total_trades"], "Win Rate (%)": bt["win_rate"],
            "Avg Return (%)": bt["avg_return"],
            "Leading Trades": bt["leading_trades"], "Leading WR (%)": bt["leading_win_rate"],
            "Leading Avg (%)": bt["leading_avg_return"],
            "Neutral Trades": bt["neutral_trades"], "Neutral WR (%)": bt["neutral_win_rate"],
            "Neutral Avg (%)": bt["neutral_avg_return"],
            "Regression Time (s)": reg_time,
        })

    # Restore original config
    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py restored.")

    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)

    print(f"\n{'='*80}")
    print(f"     PHASE 2 OPTIMIZATION COMPLETE")
    print(f"     Results saved to: {RESULTS_FILE}")
    print(f"{'='*80}")

    print("\n" + df.sort_values("Win Rate (%)", ascending=False).to_string(index=False))
    print()


if __name__ == "__main__":
    main()
