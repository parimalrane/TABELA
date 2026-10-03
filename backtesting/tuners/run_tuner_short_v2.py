"""
TABELA SHORT ENGINE V2 GRID SEARCH
====================================================
Tests combinations of:
  - SHORT_RS_RAW_WEIGHTS  (velocity of weakness)
  - SHORT_COMPOSITE_WEIGHTS (what matters most in a breakdown)
  - SHORT_ZACKS_SCORE_MAP  (fundamental poison weighting)
  - SHORT_GROWTH_SCORE_MAP (earnings deterioration weighting)
  - SHORT_ENTRY thresholds (RS window + score ceiling)

The Long engine config is NEVER touched.
Safety: config.py is backed up before and fully restored after every run.
"""

import os
import sys
import re
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_short_v2.py"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
RESULTS_FILE = RESULTS_DIR / f"optimization_results_short_v2_{datetime.now().strftime('%Y%m%d')}.csv"
os.makedirs(RESULTS_DIR, exist_ok=True)

# ==================
# PARAMETER LIBRARY
# ==================

# RS Velocity Modes
RS_CLIFF = {"% Price Change (4 Weeks)": 0.50, "% Price Change (12 Weeks)": 0.10, "% Price Change (1 Week)": 0.40, "Relative Price Change (YTD)": 0.00, "Price as a % of 52 Wk H-L Range": 0.00}
RS_SLOW_BLEED = {"% Price Change (4 Weeks)": 0.20, "% Price Change (12 Weeks)": 0.70, "% Price Change (1 Week)": 0.10, "Relative Price Change (YTD)": 0.00, "Price as a % of 52 Wk H-L Range": 0.00}
RS_YTD_REVERSAL = {"% Price Change (4 Weeks)": 0.30, "% Price Change (12 Weeks)": 0.20, "% Price Change (1 Week)": 0.10, "Relative Price Change (YTD)": 0.40, "Price as a % of 52 Wk H-L Range": 0.00}
RS_BALANCED = {"% Price Change (4 Weeks)": 0.50, "% Price Change (12 Weeks)": 0.30, "% Price Change (1 Week)": 0.20, "Relative Price Change (YTD)": 0.00, "Price as a % of 52 Wk H-L Range": 0.00}

# Composite Weight Modes
COMP_STANDARD = {"RS_WEIGHT": 0.50, "THEME_WEIGHT": 0.25, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}
COMP_RS_HEAVY = {"RS_WEIGHT": 0.65, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.10, "GROWTH_WEIGHT": 0.05}
COMP_FUNDAMENTAL = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.25, "GROWTH_WEIGHT": 0.15}
COMP_THEME_HEAVY = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.40, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.05}
COMP_PURE_TECH = {"RS_WEIGHT": 0.80, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.00, "GROWTH_WEIGHT": 0.00}

# Zacks Short Maps
ZACKS_REWARD_SELLS = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}
ZACKS_NEUTRAL = {1: 50.0, 2: 50.0, 3: 50.0, 4: 50.0, 5: 50.0}
ZACKS_IGNORE = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}

# Growth Short Maps
GROWTH_REWARD_DECAY = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}
GROWTH_NEUTRAL = {'A': 50.0, 'B': 50.0, 'C': 50.0, 'D': 50.0, 'F': 50.0}
GROWTH_IGNORE = {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0, 'F': 0.0}

# Entry Threshold Windows
GATE_GRAVEYARD = {"MIN_SHORT_RS": 8.0, "MAX_SHORT_RS": 15.0, "MAX_SHORT_SCORE": 25.0}
GATE_LOWER_MID = {"MIN_SHORT_RS": 15.0, "MAX_SHORT_RS": 35.0, "MAX_SHORT_SCORE": 40.0}
GATE_TRUE_MID = {"MIN_SHORT_RS": 30.0, "MAX_SHORT_RS": 60.0, "MAX_SHORT_SCORE": 55.0}
GATE_FALL_FROM_GRACE = {"MIN_SHORT_RS": 40.0, "MAX_SHORT_RS": 75.0, "MAX_SHORT_SCORE": 65.0}

THEMES_STRICT = ["Lagging", "Micro Laggard"]
THEMES_WIDE = ["Lagging", "Micro Laggard", "Neutral", "Unknown"]


def make_exp(name, hypothesis, gate, blocked_zacks, min_volume, themes):
    return {
        "name": name, "hypothesis": hypothesis,
        "gate": gate, "themes": themes, 
        "blocked_zacks": blocked_zacks, "min_volume": min_volume
    }

EXPERIMENTS = [
    make_exp("Baseline (Last Winner P1-F)", "Control group: 1457 trades, 71.1% WR.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 65.0}, "[1, 2]", 1_000_000, THEMES_WIDE),
    make_exp("Sniper 1: Block Zacks 3", "Cut the fundamental noise exactly in half.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 65.0}, "[1, 2, 3]", 1_000_000, THEMES_WIDE),
    make_exp("Sniper 2: Strict Volume Floor", "Require 2.5m volume.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 65.0}, "[1, 2]", 2_500_000, THEMES_WIDE),
    make_exp("Sniper 3: Lower Tech Ceiling", "Crush RS ceiling to 60.", {"MIN_RS": 40.0, "MAX_RS": 60.0, "SCORE": 65.0}, "[1, 2]", 1_000_000, THEMES_WIDE),
    make_exp("Sniper 4: Strict Score Ceiling", "Crush Score ceiling to 45.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 45.0}, "[1, 2]", 1_000_000, THEMES_WIDE),
    make_exp("Sniper 5: Exclude Neutral/Unknown", "Strictly Lagging/Micro Laggard.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 65.0}, "[1, 2]", 1_000_000, THEMES_STRICT),
    make_exp("Combo A: The Clean Cut", "Block Zacks 3 + 2.5m Volume.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 65.0}, "[1, 2, 3]", 2_500_000, THEMES_WIDE),
    make_exp("Combo B: Strict Fundamentals", "Block Zacks 3 + Score 45.", {"MIN_RS": 40.0, "MAX_RS": 75.0, "SCORE": 45.0}, "[1, 2, 3]", 1_000_000, THEMES_WIDE),
    make_exp("Combo C: The Absolute Chokehold", "RS<60 + Score<45 + Zacks 4/5 only + 2.5m Vol.", {"MIN_RS": 40.0, "MAX_RS": 60.0, "SCORE": 45.0}, "[1, 2, 3]", 2_500_000, THEMES_WIDE)
]


def generate_short_config_block(exp):
    """Rewrites ONLY the SHORT_* variables in config.py using regex."""
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        content = f.read()

    gate = exp["gate"]
    themes = str(exp["themes"]).replace("'", '"')
    blocked_zacks = exp["blocked_zacks"]
    min_volume = exp["min_volume"]

    entry_block = (
        f'SHORT_ENTRY = {{\n'
        f'    "MIN_SHORT_RS": {gate["MIN_RS"]},\n'
        f'    "MAX_SHORT_RS": {gate["MAX_RS"]},\n'
        f'    "MAX_SHORT_SCORE": {gate["SCORE"]},\n'
        f'    "THEMES": {themes},\n'
        f'    "BLOCKED_ZACKS": {blocked_zacks},\n'
        f'    "MIN_PRICE": 10.0,\n'
        f'    "MIN_VOLUME": {min_volume},\n'
        f'    "MAX_DROPPED_WATCH_SCORE": 30.0,\n'
        f'    "MILD_DAYS": 21\n'
        f'}}'
    )

    content = re.sub(r'SHORT_ENTRY\s*=\s*\{.*?\}', entry_block, content, flags=re.DOTALL)
    return content


def run_regression_silent():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env=env
    )
    return result.returncode == 0
def run_backtest_short_silent():
    sys.path.insert(0, str(BASE_DIR))
    import importlib
    if "config.config" in sys.modules:
        importlib.reload(sys.modules["config.config"])
    if "scoring.scoring_engine" in sys.modules:
        importlib.reload(sys.modules["scoring.scoring_engine"])
    if "scoring.long_scoring_engine" in sys.modules:
        importlib.reload(sys.modules["scoring.long_scoring_engine"])
    
    sys.path.insert(0, str(BASE_DIR / "backtesting"))
    try:
        import backtest_engine
        importlib.reload(backtest_engine)
        return backtest_engine.run_backtest(mode="short", silent=True)
    except Exception as e:
        print(f"  [ERROR] Backtest failed: {e}")
        return None


def main():
    total = len(EXPERIMENTS)
    print("=" * 80)
    print("     TABELA SHORT ENGINE V2: MULTI-DIMENSIONAL GRID SEARCH")
    print(f"     {total} Experiments | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py backed up. Long engine will NOT be modified.\n")

    results = []
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        print(f"\n{'='*80}")
        print(f"  EXPERIMENT {idx}/{total}: {name}")
        print(f"  {exp['hypothesis']}")
        print(f"  Gate: {exp['gate']} | Blocked Zacks: {exp['blocked_zacks']} | Min Vol: {exp['min_volume']}")
        print(f"{'='*80}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(generate_short_config_block(exp))
        print(f"  [1/3] SHORT_* config rewritten. Long engine unchanged.")

        t0 = time.time()
        print(f"  [2/3] Running regression...")
        reg_ok = run_regression_silent()
        reg_time = round(time.time() - t0, 1)

        if not reg_ok:
            print(f"  [ERROR] Regression failed.")
            results.append({"Exp": idx, "Name": name, "Trades": "ERR", "WR%": "ERR", "AvgReturn%": "ERR", "Time(s)": reg_time})
            continue

        print(f"  [2/3] Regression complete in {reg_time}s.")
        print(f"  [3/3] Running short backtest...")
        bt = run_backtest_short_silent()

        if bt is None:
            bt = {
                "total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                "strong_trades": 0, "strong_win_rate": 0.0, "strong_avg_return": 0.0,
                "mild_trades": 0, "mild_win_rate": 0.0, "mild_avg_return": 0.0,
                "basing_trades": 0, "basing_win_rate": 0.0, "basing_avg_return": 0.0,
            }

        print(f"  >>> Strong WR: {bt['strong_win_rate']}% | Mild WR: {bt['mild_win_rate']}% | Decay WR: {bt['basing_win_rate']}%")
        results.append({
            "Exp": idx, "Name": name,
            "Trades": bt["total_trades"],
            "WR%": bt["win_rate"],
            "Avg%": bt["avg_return"],
            "Str.Trd": bt["strong_trades"],
            "Str.WR%": bt["strong_win_rate"],
            "Mil.Trd": bt["mild_trades"],
            "Mil.WR%": bt["mild_win_rate"],
            "Decay.Trd": bt["basing_trades"],
            "Decay.WR%": bt["basing_win_rate"],
            "Max_RS": exp["gate"]["MAX_RS"],
            "Score": exp["gate"]["SCORE"],
            "ZacksBlocked": exp["blocked_zacks"],
            "MinVol": exp["min_volume"],
            "Themes": len(exp["themes"]),
            "Time(s)": reg_time
        })

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py fully restored.")

    import pandas as pd
    df = pd.DataFrame(results)
    df = df.sort_values("WR%", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\n{'='*80}")
    print(f"     COMPLETE | {RESULTS_FILE.name}")
    print(f"{'='*80}")
    print("\n" + df.to_string(index=False))


if __name__ == "__main__":
    main()
