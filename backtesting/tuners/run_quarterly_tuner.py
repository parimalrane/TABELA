"""
TABELA QUARTERLY AUTO-TUNER (MASTER EXECUTION)
===================================================
Run this once a quarter to execute the full state-space
grid search across both the Long and Short pipelines.

It executes the 30 Long experiments, restores the config,
then executes the 14 Short V2 experiments, and produces
a unified Quarterly Report in `backtesting/results`.

Usage: python run_quarterly_tuner.py
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
TUNER_DIR = BASE_DIR / "backtesting" / "tuners"

LONG_SCRIPT = TUNER_DIR / "run_tuner.py"
SHORT_SCRIPT = TUNER_DIR / "run_tuner_short_v2.py"

def run_quarterly_master():
    print("=" * 80)
    print("    TABELA QUARTERLY MASTER BACKTEST SUITE")
    print("    Executing all integrated test cases for Long and Short Engines.")
    print("=" * 80)
    
    # 1. Execute Long Tests
    print("\n\n>>> INITIALIZING PHASE 1: LONG ENGINE GRID SEARCH (30 Experiments)")
    try:
        subprocess.run([sys.executable, str(LONG_SCRIPT)], cwd=str(BASE_DIR), check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] Long Engine Tests Failed.")
        sys.exit(1)

    # 2. Execute Short Tests
    print("\n\n>>> INITIALIZING PHASE 2: SHORT ENGINE GRID SEARCH (14 Experiments)")
    try:
        subprocess.run([sys.executable, str(SHORT_SCRIPT)], cwd=str(BASE_DIR), check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] Short Engine Tests Failed.")
        sys.exit(1)

    print("\n\n======================================================================")
    print("   QUARTERLY ENGINE BACKTESTS COMPLETE.")
    print("   Review the output CSVs in `backtesting/results/` for performance metrics.")
    print("   Once a new winner is selected, update `config.py` manually.")
    print("======================================================================")

if __name__ == "__main__":
    run_quarterly_master()
