"""
TABELA AUTO-TUNER: Grid Search Optimization Engine
===================================================
One-Click execution. Automatically sweeps through 30 pre-defined experiments,
runs regression + backtest for each, and outputs optimization_results.csv.

Usage: python run_tuner.py
"""

import os
import sys
import json
import shutil
import subprocess
import time
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_tuner.py"
RESULTS_FILE = BASE_DIR / "optimization_results.csv"

# ============================================================
# 30 PRE-FILLED EXPERIMENTS (7 Dimensions)
# ============================================================
# Each experiment is a complete config.py override.
# Keys map directly to config.py variables.
#
# Dimensions:
#   1. RS_RAW_WEIGHTS        (Stock RS formula)
#   2. PERIOD_WEIGHTS         (ETF Theme formula)
#   3. LONG_WEIGHTS           (Composite score weights)
#   4. THRESHOLDS             (MIN_RS, MIN_LONG_SCORE)
#   5. CLASSIFICATION         (Leading/Lagging %)
#   6. ZACKS_SCORE_MAP        (Zacks rank -> score curve)
#   7. GROWTH_SCORE_MAP       (Growth grade -> score curve)
# ============================================================

# --- DEFAULTS (used as base, experiments override specific dimensions) ---
DEFAULT = {
    "RS_RAW_WEIGHTS": {
        "% Price Change (4 Weeks)": 0.50,
        "% Price Change (12 Weeks)": 0.40,
        "% Price Change (1 Week)": 0.10,
        "Relative Price Change (YTD)": 0.00,
        "Price as a % of 52 Wk H-L Range": 0.00,
    },
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.40,
        "Performance 1W (%)": 0.35,
        "Performance 3M (%)": 0.25,
        "Performance 6M (%)": 0.00,
        "Performance 1Y (%)": 0.00,
        "Performance 1D (%)": 0.00,
    },
    "LONG_WEIGHTS": {
        "RS_WEIGHT": 0.50,
        "THEME_WEIGHT": 0.25,
        "ZACKS_WEIGHT": 0.15,
        "GROWTH_WEIGHT": 0.10,
    },
    "MIN_RS": 85.0,
    "MIN_LONG_SCORE": 85.0,
    "CLASSIFICATION_PERCENTAGE_LEADING": 0.30,
    "CLASSIFICATION_PERCENTAGE_LAGGING": 0.30,
    "ZACKS_SCORE_MAP": {1: 100.0, 2: 95.0, 3: 90.0, 4: 20.0, 5: -50.0},
    "GROWTH_SCORE_MAP": {"A": 100.0, "B": 95.0, "C": 90.0, "D": 20.0, "F": -50.0},
    "BLOCKED_ZACKS": [4, 5],
}


def make_experiment(name, hypothesis, overrides):
    """Merge overrides onto the DEFAULT config to produce a complete experiment."""
    exp = {k: (v.copy() if isinstance(v, (dict, list)) else v) for k, v in DEFAULT.items()}
    for k, v in overrides.items():
        if isinstance(v, dict) and k in exp and isinstance(exp[k], dict):
            exp[k] = {**exp[k], **v}
        else:
            exp[k] = v
    exp["name"] = name
    exp["hypothesis"] = hypothesis
    return exp


EXPERIMENTS = [
    # ============================
    # EXPERIMENT 1: BASELINE (Control Group)
    # ============================
    make_experiment(
        "Baseline (Current Config)",
        "Control group. Current production settings.",
        {}
    ),

    # ============================
    # RS FORMULA VARIATIONS (Exps 2-7)
    # ============================
    make_experiment(
        "RS: 12W Dominant",
        "Does longer-term intermediate trend beat short-term breakout?",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (4 Weeks)": 0.30,
            "% Price Change (12 Weeks)": 0.60,
            "% Price Change (1 Week)": 0.10,
            "Relative Price Change (YTD)": 0.00,
            "Price as a % of 52 Wk H-L Range": 0.00,
        }}
    ),
    make_experiment(
        "RS: YTD Comeback (15%)",
        "Does adding back YTD drift catch better long-term winners?",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (4 Weeks)": 0.40,
            "% Price Change (12 Weeks)": 0.35,
            "% Price Change (1 Week)": 0.10,
            "Relative Price Change (YTD)": 0.15,
            "Price as a % of 52 Wk H-L Range": 0.00,
        }}
    ),
    make_experiment(
        "RS: 52W High Proximity (15%)",
        "Does nearness to 52-week high improve breakout quality?",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (4 Weeks)": 0.40,
            "% Price Change (12 Weeks)": 0.35,
            "% Price Change (1 Week)": 0.10,
            "Relative Price Change (YTD)": 0.00,
            "Price as a % of 52 Wk H-L Range": 0.15,
        }}
    ),
    make_experiment(
        "RS: Weekly Pulse (30%)",
        "Does amplifying weekly momentum catch fresher breakouts?",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (4 Weeks)": 0.40,
            "% Price Change (12 Weeks)": 0.30,
            "% Price Change (1 Week)": 0.30,
            "Relative Price Change (YTD)": 0.00,
            "Price as a % of 52 Wk H-L Range": 0.00,
        }}
    ),
    make_experiment(
        "RS: Legacy Formula",
        "Does the original pre-optimization formula actually perform better?",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (12 Weeks)": 0.40,
            "Relative Price Change (YTD)": 0.25,
            "Price as a % of 52 Wk H-L Range": 0.15,
            "% Price Change (4 Weeks)": 0.15,
            "% Price Change (1 Week)": 0.05,
        }}
    ),
    make_experiment(
        "RS: Hybrid (YTD + 52W)",
        "Best of both: immediate breakout + structural strength.",
        {"RS_RAW_WEIGHTS": {
            "% Price Change (4 Weeks)": 0.35,
            "% Price Change (12 Weeks)": 0.35,
            "% Price Change (1 Week)": 0.10,
            "Relative Price Change (YTD)": 0.10,
            "Price as a % of 52 Wk H-L Range": 0.10,
        }}
    ),

    # ============================
    # ETF THEME FORMULA VARIATIONS (Exps 8-13)
    # ============================
    make_experiment(
        "Theme: Monthly Dominance (60%)",
        "Does monthly ETF flow outperform weekly rotation detection?",
        {"PERIOD_WEIGHTS": {
            "Performance 1M (%)": 0.60,
            "Performance 1W (%)": 0.10,
            "Performance 3M (%)": 0.20,
            "Performance 6M (%)": 0.10,
            "Performance 1Y (%)": 0.00,
            "Performance 1D (%)": 0.00,
        }}
    ),
    make_experiment(
        "Theme: Quarterly Anchor (45%)",
        "Does longer-term capital flow produce more stable Leading sectors?",
        {"PERIOD_WEIGHTS": {
            "Performance 1M (%)": 0.25,
            "Performance 1W (%)": 0.10,
            "Performance 3M (%)": 0.45,
            "Performance 6M (%)": 0.15,
            "Performance 1Y (%)": 0.05,
            "Performance 1D (%)": 0.00,
        }}
    ),
    make_experiment(
        "Theme: Pure Weekly Pulse (50%)",
        "Does ultra-fast weekly rotation catch sector shifts earlier?",
        {"PERIOD_WEIGHTS": {
            "Performance 1M (%)": 0.30,
            "Performance 1W (%)": 0.50,
            "Performance 3M (%)": 0.20,
            "Performance 6M (%)": 0.00,
            "Performance 1Y (%)": 0.00,
            "Performance 1D (%)": 0.00,
        }}
    ),
    make_experiment(
        "Theme: Legacy Drift Formula",
        "Does the original slow-moving theme formula actually outperform?",
        {"PERIOD_WEIGHTS": {
            "Performance 3M (%)": 0.40,
            "Performance 6M (%)": 0.25,
            "Performance 1Y (%)": 0.15,
            "Performance 1M (%)": 0.15,
            "Performance 1W (%)": 0.03,
            "Performance 1D (%)": 0.02,
        }}
    ),
    make_experiment(
        "Theme: Balanced All-Period",
        "Does a balanced blend across all timeframes reduce whipsaw?",
        {"PERIOD_WEIGHTS": {
            "Performance 1W (%)": 0.15,
            "Performance 1M (%)": 0.25,
            "Performance 3M (%)": 0.30,
            "Performance 6M (%)": 0.20,
            "Performance 1Y (%)": 0.10,
            "Performance 1D (%)": 0.00,
        }}
    ),
    make_experiment(
        "Theme: 6-Month Anchor",
        "Does 6-month institutional flow reveal true secular trends?",
        {"PERIOD_WEIGHTS": {
            "Performance 1W (%)": 0.10,
            "Performance 1M (%)": 0.20,
            "Performance 3M (%)": 0.25,
            "Performance 6M (%)": 0.35,
            "Performance 1Y (%)": 0.10,
            "Performance 1D (%)": 0.00,
        }}
    ),

    # ============================
    # COMPOSITE WEIGHT VARIATIONS (Exps 14-18)
    # ============================
    make_experiment(
        "Composite: RS Heavy (60/20/12/8)",
        "Does pure momentum domination maximize win rate?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.60, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.12, "GROWTH_WEIGHT": 0.08}}
    ),
    make_experiment(
        "Composite: Theme Heavy (40/35/15/10)",
        "Does macro flow conviction beat individual stock momentum?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.35, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}}
    ),
    make_experiment(
        "Composite: Fundamentals Heavy (40/20/25/15)",
        "Does weighting Zacks/Growth heavily filter garbage breakouts?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.25, "GROWTH_WEIGHT": 0.15}}
    ),
    make_experiment(
        "Composite: Equal Split (40/30/15/15)",
        "Does balanced weighting reduce concentration risk?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.30, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.15}}
    ),
    make_experiment(
        "Composite: Pure Momentum (70/15/10/5)",
        "Does extreme RS dominance crush everything else?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.70, "THEME_WEIGHT": 0.15, "ZACKS_WEIGHT": 0.10, "GROWTH_WEIGHT": 0.05}}
    ),

    # ============================
    # THRESHOLD VARIATIONS (Exps 19-22)
    # ============================
    make_experiment(
        "Threshold: Loose Gate (80/80)",
        "Does a wider funnel catch more winners despite more noise?",
        {"MIN_RS": 80.0, "MIN_LONG_SCORE": 80.0}
    ),
    make_experiment(
        "Threshold: Medium Gate (85/80)",
        "Does RS strictness with score flexibility find the sweet spot?",
        {"MIN_RS": 85.0, "MIN_LONG_SCORE": 80.0}
    ),
    make_experiment(
        "Threshold: Tight Gate (90/85)",
        "Does extreme RS filtration maximize precision?",
        {"MIN_RS": 90.0, "MIN_LONG_SCORE": 85.0}
    ),
    make_experiment(
        "Threshold: Ultra Tight (90/90)",
        "Does maximum exclusivity produce the highest win rate?",
        {"MIN_RS": 90.0, "MIN_LONG_SCORE": 90.0}
    ),

    # ============================
    # SECTOR CLASSIFICATION VARIATIONS (Exps 23-25)
    # ============================
    make_experiment(
        "Sector: Narrow Leading (20/20)",
        "Does a narrow Leading bucket concentrate on truly elite sectors?",
        {"CLASSIFICATION_PERCENTAGE_LEADING": 0.20, "CLASSIFICATION_PERCENTAGE_LAGGING": 0.20}
    ),
    make_experiment(
        "Sector: Wide Leading (40/40)",
        "Does a wide Leading bucket catch more rotational opportunities?",
        {"CLASSIFICATION_PERCENTAGE_LEADING": 0.40, "CLASSIFICATION_PERCENTAGE_LAGGING": 0.40}
    ),
    make_experiment(
        "Sector: Asymmetric (25/35)",
        "Does a tight Leading + wide Lagging create earlier warnings?",
        {"CLASSIFICATION_PERCENTAGE_LEADING": 0.25, "CLASSIFICATION_PERCENTAGE_LAGGING": 0.35}
    ),

    # ============================
    # ZACKS CURVE VARIATIONS (Exps 26-28)
    # ============================
    make_experiment(
        "Zacks: Steep Penalty",
        "Does harshly punishing Rank 3 turnarounds improve quality?",
        {"ZACKS_SCORE_MAP": {1: 100.0, 2: 80.0, 3: 60.0, 4: 20.0, 5: -50.0}}
    ),
    make_experiment(
        "Zacks: Pure Binary",
        "Does treating Rank 1-2 as pass and everything else as fail work?",
        {"ZACKS_SCORE_MAP": {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}}
    ),
    make_experiment(
        "Zacks: Block Rank 3",
        "Does completely blocking Rank 3 turnarounds improve win rate?",
        {"BLOCKED_ZACKS": [3, 4, 5]}
    ),

    # ============================
    # GROWTH CURVE VARIATIONS (Exps 29-30)
    # ============================
    make_experiment(
        "Growth: Steep Fibonacci",
        "Does the classic Fibonacci penalty curve beat the flattened one?",
        {"GROWTH_SCORE_MAP": {"A": 100.0, "B": 78.6, "C": 61.8, "D": 38.2, "F": 0.0}}
    ),
    make_experiment(
        "Growth: Irrelevant (Weight = 0)",
        "Does Growth Score add any value at all, or is it pure noise?",
        {"LONG_WEIGHTS": {"RS_WEIGHT": 0.55, "THEME_WEIGHT": 0.30, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.00}}
    ),
]


def generate_config_content(exp):
    """Generate a complete config.py file string from an experiment dictionary."""
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
    """Run regression.bat silently (suppress pipeline output)."""
    result = subprocess.run(
        ["python", str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def run_backtest_silent():
    """Run backtest.py and return results dict."""
    sys.path.insert(0, str(BASE_DIR))
    
    # Force reload config and scoring modules to pick up new config
    import importlib
    if "config.config" in sys.modules:
        importlib.reload(sys.modules["config.config"])
    if "scoring.scoring_engine" in sys.modules:
        importlib.reload(sys.modules["scoring.scoring_engine"])
    if "scoring.long_scoring_engine" in sys.modules:
        importlib.reload(sys.modules["scoring.long_scoring_engine"])
    if "backtest" in sys.modules:
        importlib.reload(sys.modules["backtest"])
    
    from backtest import run_backtest
    return run_backtest(silent=True)


def main():
    total = len(EXPERIMENTS)
    
    print("=" * 80)
    print("     TABELA AUTO-TUNER: Grid Search Optimization Engine")
    print(f"     {total} Experiments Queued | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Step 1: Backup original config
    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py backed up to: {CONFIG_BACKUP}")
    
    results = []
    
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        hypothesis = exp["hypothesis"]
        
        print(f"\n{'='*80}")
        print(f"  EXPERIMENT {idx}/{total}: {name}")
        print(f"  Hypothesis: {hypothesis}")
        print(f"{'='*80}")
        
        # Step 2: Rewrite config.py
        config_content = generate_config_content(exp)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(config_content)
        print(f"  [1/3] Config rewritten.")
        
        # Step 3: Run regression
        t0 = time.time()
        print(f"  [2/3] Running regression (rebuilding 3-month history)...")
        reg_ok = run_regression_silent()
        reg_time = round(time.time() - t0, 1)
        
        if not reg_ok:
            print(f"  [ERROR] Regression failed for experiment {idx}. Skipping.")
            results.append({
                "Experiment": idx,
                "Name": name,
                "Hypothesis": hypothesis,
                "Total Trades": "ERROR",
                "Win Rate (%)": "ERROR",
                "Avg Return (%)": "ERROR",
                "Leading Trades": "ERROR",
                "Leading WR (%)": "ERROR",
                "Leading Avg (%)": "ERROR",
                "Neutral Trades": "ERROR",
                "Neutral WR (%)": "ERROR",
                "Neutral Avg (%)": "ERROR",
                "Regression Time (s)": reg_time,
            })
            continue
        
        print(f"  [2/3] Regression complete in {reg_time}s.")
        
        # Step 4: Run backtest
        print(f"  [3/3] Running backtest...")
        bt = run_backtest_silent()
        
        if bt is None:
            bt = {
                "total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
                "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0,
            }
        
        print(f"  >>> Trades: {bt['total_trades']} | Win Rate: {bt['win_rate']}% | Avg Return: {bt['avg_return']}%")
        
        results.append({
            "Experiment": idx,
            "Name": name,
            "Hypothesis": hypothesis,
            "Total Trades": bt["total_trades"],
            "Win Rate (%)": bt["win_rate"],
            "Avg Return (%)": bt["avg_return"],
            "Leading Trades": bt["leading_trades"],
            "Leading WR (%)": bt["leading_win_rate"],
            "Leading Avg (%)": bt["leading_avg_return"],
            "Neutral Trades": bt["neutral_trades"],
            "Neutral WR (%)": bt["neutral_win_rate"],
            "Neutral Avg (%)": bt["neutral_avg_return"],
            "Regression Time (s)": reg_time,
        })
    
    # Step 5: Restore original config
    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py restored from backup.")
    
    # Step 6: Save results
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    
    print(f"\n{'='*80}")
    print(f"     OPTIMIZATION COMPLETE")
    print(f"     Results saved to: {RESULTS_FILE}")
    print(f"{'='*80}")
    
    # Print summary table
    print("\n" + df.sort_values("Win Rate (%)", ascending=False).to_string(index=False))
    print()


if __name__ == "__main__":
    main()
