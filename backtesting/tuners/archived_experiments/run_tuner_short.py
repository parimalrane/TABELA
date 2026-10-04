"""
TABELA SHORT ENGINE AUTO-TUNER
====================================================
Isolates the DIST_ENTRY parameters while keeping all
Long-side and core scoring config exactly as it is.
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_tuner_short.py"
RESULTS_FILE = BASE_DIR / "backtesting" / "results" / "optimization_results_short.csv"


def make_combo(name, hypothesis, max_rs, max_score, blocked):
    return {
        "name": name,
        "hypothesis": hypothesis,
        "MAX_RS": max_rs,
        "MAX_LONG_SCORE": max_score,
        "BLOCKED_ZACKS": blocked
    }

EXPERIMENTS = [
    # Baseline
    make_combo("Short Phase 0: Baseline (10 RS / 20 Score)",
               "The original short configuration.",
               10.0, 20.0, [1, 2]),

    # Tighter RS
    make_combo("Short Phase 1: Tight RS (5 RS / 20 Score)",
               "Require stricter momentum weakness.",
               5.0, 20.0, [1, 2]),

    # Tighter Score
    make_combo("Short Phase 2: Tight Score (10 RS / 15 Score)",
               "Require stricter composite weakness.",
               10.0, 15.0, [1, 2]),

    # Ultra Tight
    make_combo("Short Phase 3: Ultra Tight (5 RS / 10 Score)",
               "Extreme breakdown filter.",
               5.0, 10.0, [1, 2]),

    # Wide Gate
    make_combo("Short Phase 4: Wide Gate (15 RS / 25 Score)",
               "Does loosening the funnel catch more drops?",
               15.0, 25.0, [1, 2]),

    # Zacks Block 3
    make_combo("Short Phase 5: Block Rank 3 (10 RS / 20 Score)",
               "Force Rank 4/5 only (blocks rank 3 turnarounds).",
               10.0, 20.0, [1, 2, 3]),

    # Zacks Block 3 + Ultra Tight
    make_combo("Short Phase 6: Block 3 + Ultra Tight",
               "Extreme fundamental and momentum strictness.",
               5.0, 10.0, [1, 2, 3])
]


def generate_short_config(exp):
    # This reads the actual config file and ONLY string-replaces the DIST_ENTRY block
    # so we guarantee the Long config is NEVER touched.
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        original = f.read()
    
    import re
    new_dist_entry = f'''DIST_ENTRY = {{
    "MAX_RS": {exp["MAX_RS"]},
    "MAX_LONG_SCORE": {exp["MAX_LONG_SCORE"]},
    "THEMES": ["Lagging", "Micro Laggard"],
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": {exp["BLOCKED_ZACKS"]},
    "MAX_DROPPED_WATCH_SCORE": 30.0
}}'''
    
    # regex replace the entire DIST_ENTRY block
    modified = re.sub(r'DIST_ENTRY\s*=\s*\{.*?\}(?=\n|\Z)', new_dist_entry, original, flags=re.DOTALL)
    return modified


def run_regression_silent():
    result = subprocess.run(
        ["python", str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def run_backtest(mode="short", silent=True):
    sys.path.insert(0, str(BASE_DIR))
    import importlib
    for mod in ["config.config", "scoring.scoring_engine", "scoring.long_scoring_engine", "backtest_short"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    from backtesting.backtest_engine import run_backtest_short
    return run_backtest(silent=True)


def main():
    total = len(EXPERIMENTS)
    print("=" * 80)
    print("     TABELA DISTRIBUTION ENGINE TUNER")
    print(f"     {total} Short Experiments | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py backed up.")

    results = []
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        print(f"\n{'='*80}")
        print(f"  EXPERIMENT {idx}/{total}: {name}")
        print(f"  {exp['hypothesis']}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(generate_short_config(exp))
        print(f"  [1/3] Config rewritten (ONLY DIST_ENTRY mutated).")

        t0 = time.time()
        print(f"  [2/3] Running regression...")
        reg_ok = run_regression_silent()
        reg_time = round(time.time() - t0, 1)

        if not reg_ok:
            print(f"  [ERROR] Regression failed.")
            results.append({"Experiment": idx, "Name": name, "Total Trades": "ERROR",
                            "Win Rate (%)": "ERROR", "Avg Return (%)": "ERROR",
                            "Lagging Trades": "ERROR", "Lagging WR (%)": "ERROR", "Lagging Avg (%)": "ERROR",
                            "Time (s)": reg_time})
            continue

        print(f"  [3/3] Running SHORT backtest...")
        bt = run_backtest(mode="short", silent=True)
        if bt is None:
            bt = {"total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                  "lagging_trades": 0, "lagging_win_rate": 0.0, "lagging_avg_return": 0.0}

        print(f"  >>> Short Trades: {bt['total_trades']} | Short Win Rate: {bt['win_rate']}% | Avg Profit: {bt['avg_return']}%")
        results.append({"Experiment": idx, "Name": name,
                        "Total Trades": bt["total_trades"], "Win Rate (%)": bt["win_rate"],
                        "Avg Return (%)": bt["avg_return"],
                        "Lagging Trades": bt["lagging_trades"], "Lagging WR (%)": bt["lagging_win_rate"],
                        "Lagging Avg (%)": bt["lagging_avg_return"],
                        "Time (s)": reg_time})

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py restored.")

    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\n{'='*80}")
    print(f"     SHORT TUNING COMPLETE | Results: {RESULTS_FILE}")
    print(f"{'='*80}")
    print("\n" + df.sort_values("Win Rate (%)", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
