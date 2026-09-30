import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_breakdown.py"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
RESULTS_FILE = RESULTS_DIR / f"optimization_results_short_breakdown_{datetime.now().strftime('%Y%m%d')}.csv"

os.makedirs(RESULTS_DIR, exist_ok=True)

def make_exp(name, min_rs, max_rs, max_score, themes):
    return {
        "name": name,
        "min_rs": min_rs,
        "max_rs": max_rs,
        "max_score": max_score,
        "themes": themes
    }

T_LAG = ["Lagging", "Micro Laggard", "Unknown"]
T_NEUT = ["Neutral", "Lagging", "Micro Laggard", "Unknown"]

EXPERIMENTS = [
    # Baseline (Our original winning floor)
    make_exp("Baseline Graveyard (8-15 RS / 25 Score)", 8.0, 15.0, 25.0, T_LAG),
    
    # Lower Mid-Tier (Starting to look higher)
    make_exp("Lower-Mid Lagging (20-40 RS / 35 Score)", 20.0, 40.0, 35.0, T_LAG),
    make_exp("Lower-Mid Neutral+Lag (20-40 RS / 35 Score)", 20.0, 40.0, 35.0, T_NEUT),
    
    # True Mid-Tier (Fresh Breakdowns)
    make_exp("True Mid-Tier Lagging (30-60 RS / 45 Score)", 30.0, 60.0, 45.0, T_LAG),
    make_exp("True Mid-Tier Neutral+Lag (30-60 RS / 45 Score)", 30.0, 60.0, 45.0, T_NEUT),
    
    # Upper Mid-Tier (Former Leaders falling)
    make_exp("Upper-Mid Lagging (40-70 RS / 55 Score)", 40.0, 70.0, 55.0, T_LAG),
    make_exp("Upper-Mid Neutral+Lag (40-70 RS / 55 Score)", 40.0, 70.0, 55.0, T_NEUT),
    
    # Wide Funnels
    make_exp("Wide Mid Funnel Lagging (20-60 RS / 50 Score)", 20.0, 60.0, 50.0, T_LAG),
    make_exp("Wide Mid Funnel Neutral+Lag (20-60 RS / 50 Score)", 20.0, 60.0, 50.0, T_NEUT),
    
    # Very High Quality Breakdowns (Earnings disasters)
    make_exp("High-Quality Breakdown Lagging (50-80 RS / 65 Score)", 50.0, 80.0, 65.0, T_LAG),
    make_exp("High-Quality Breakdown Neutral+Lag (50-80 RS / 65 Score)", 50.0, 80.0, 65.0, T_NEUT)
]

def generate_short_config(exp):
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        original = f.read()
    
    import re
    themes_str = str(exp["themes"]).replace("'", '"')
    new_dist_entry = f'''DIST_ENTRY = {{
    "MIN_RS": {exp["min_rs"]},
    "MAX_RS": {exp["max_rs"]},
    "MAX_LONG_SCORE": {exp["max_score"]},
    "THEMES": {themes_str},
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
}}'''
    
    modified = re.sub(r'DIST_ENTRY\s*=\s*\{.*?\}(?=\n|\Z)', new_dist_entry, original, flags=re.DOTALL)
    return modified

def run_regression_silent():
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0

def run_backtest_short_silent():
    # Update backtest_engine dynamically instead of using old short engine
    sys.path.insert(0, str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR / "backtesting"))
    import importlib
    for mod in ["config.config", "scoring.scoring_engine", "scoring.long_scoring_engine", "backtest_engine"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
            
    try:
        from backtesting.backtest_engine import run_backtest
        return run_backtest(mode="short", silent=True)
    except Exception as e:
        print(f"Error running backtest: {e}")
        return None

def main():
    print("=" * 80)
    print("     SHORT ENGINE: FRESH BREAKDOWN GRID SEARCH")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)

    results = []
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        print(f"\n  Running {idx}/{len(EXPERIMENTS)}: {name}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(generate_short_config(exp))

        reg_ok = run_regression_silent()
        if not reg_ok:
            print("  >>> Regression Failed.")
            continue
            
        bt = run_backtest_short_silent()

        if bt:
            print(f"  >>> Trades: {bt['total_trades']} | Win Rate: {bt['win_rate']}% | Avg Profit: {bt['avg_return']}%")
            results.append({
                "Experiment": name,
                "Win Rate (%)": bt["win_rate"],
                "Avg Return (%)": bt["avg_return"],
                "Trades": bt["total_trades"]
            })

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    
    import pandas as pd
    df = pd.DataFrame(results)
    df = df.sort_values("Win Rate (%)", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)
    
    print(f"\n{'=' * 80}")
    print(f"Grid Search Complete. Results saved to {RESULTS_FILE.name}")
    print("\n" + df.to_string(index=False))

if __name__ == "__main__":
    main()
