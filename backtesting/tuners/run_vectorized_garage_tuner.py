import os
import sys
import time
import pandas as pd
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

import config.config as cfg
from backtesting.vectorized_backtest import VectorizedBacktestEngine

RESULTS_FILE = BASE_DIR / "backtesting" / "results" / "vectorized_garage_optimization_results.csv"

# Systematic sweeps for Garage Price Velocity Divergence
EXPERIMENTS = [
    {
        "name": "Exp 1: Standard Divergence (Wake Up 80.0)",
        "hypothesis": "70% 1W / 30% 4W with loose 80.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 0.70, "% Price Change (4 Weeks)": 0.30, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 80.0
    },
    {
        "name": "Exp 2: Standard Divergence (Wake Up 85.0)",
        "hypothesis": "70% 1W / 30% 4W with standard 85.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 0.70, "% Price Change (4 Weeks)": 0.30, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 85.0
    },
    {
        "name": "Exp 3: Strict Divergence (Wake Up 90.0)",
        "hypothesis": "70% 1W / 30% 4W with strict 90.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 0.70, "% Price Change (4 Weeks)": 0.30, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 90.0
    },
    {
        "name": "Exp 4: Extreme Divergence (Wake Up 95.0)",
        "hypothesis": "70% 1W / 30% 4W with exclusive 95.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 0.70, "% Price Change (4 Weeks)": 0.30, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 95.0
    },
    {
        "name": "Exp 5: Hyper-Fast Velocity (Wake Up 85.0)",
        "hypothesis": "100% 1W momentum only. Ignore 4W base.",
        "garage_weights": {"% Price Change (1 Week)": 1.00, "% Price Change (4 Weeks)": 0.00, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 85.0
    },
    {
        "name": "Exp 6: Hyper-Fast Velocity (Wake Up 90.0)",
        "hypothesis": "100% 1W momentum only with strict 90.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 1.00, "% Price Change (4 Weeks)": 0.00, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 90.0
    },
    {
        "name": "Exp 7: Balanced Velocity (Wake Up 85.0)",
        "hypothesis": "50% 1W / 50% 4W to ensure slightly more structure.",
        "garage_weights": {"% Price Change (1 Week)": 0.50, "% Price Change (4 Weeks)": 0.50, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 85.0
    },
    {
        "name": "Exp 8: Balanced Velocity (Wake Up 90.0)",
        "hypothesis": "50% 1W / 50% 4W with strict 90.0 trigger.",
        "garage_weights": {"% Price Change (1 Week)": 0.50, "% Price Change (4 Weeks)": 0.50, "% Price Change (12 Weeks)": 0.00, "Relative Price Change (YTD)": 0.00},
        "wake_up_score": 90.0
    }
]

def apply_overrides_to_config(exp):
    backup = {
        "LONG_GARAGE_RS_RAW_WEIGHTS": cfg.LONG_GARAGE_RS_RAW_WEIGHTS.copy(),
        "LONG_GARAGE_ENTRY": cfg.LONG_GARAGE_ENTRY.copy(),
        "PURGE_DAYS": cfg.LONG_ENTRY.get("PURGE_DAYS", 50)
    }
    
    cfg.LONG_GARAGE_RS_RAW_WEIGHTS.clear()
    cfg.LONG_GARAGE_RS_RAW_WEIGHTS.update(exp["garage_weights"])
    
    cfg.LONG_GARAGE_ENTRY["WAKE_UP_SCORE"] = exp["wake_up_score"]
    
    return backup

def restore_config(backup):
    cfg.LONG_GARAGE_RS_RAW_WEIGHTS.clear()
    cfg.LONG_GARAGE_RS_RAW_WEIGHTS.update(backup["LONG_GARAGE_RS_RAW_WEIGHTS"])
    
    cfg.LONG_GARAGE_ENTRY.clear()
    cfg.LONG_GARAGE_ENTRY.update(backup["LONG_GARAGE_ENTRY"])
    
    cfg.LONG_ENTRY["PURGE_DAYS"] = backup["PURGE_DAYS"]


def main():
    print("=" * 80)
    print("    TABELA GARAGE OPTIMIZATION (PRICE VELOCITY DIVERGENCE)")
    print("=" * 80)
    
    t0 = time.time()
    
    print("\n[+] Loading Stock Universe (JSON + CSV) into Pandas Matrix...")
    engine = VectorizedBacktestEngine()
    if not engine.load_data():
        print("[-] Failed to load matrix.")
        return
        
    master_time = time.time() - t0
    print(f"    Matrix built in {master_time:.2f} seconds. Rows: {len(engine.master_matrix)}")
    
    if len(engine.all_dates) == 0:
        print("[-] No dates found.")
        return

    total = len(EXPERIMENTS)
    results = []
    
    print(f"\n[+] Executing {total} Garage permutations testing 'Wake Up' metrics...")
    
    import importlib
    importlib.reload(cfg)

    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        
        bck = apply_overrides_to_config(exp)
        
        exp_start = time.time()
        bt = engine.process(mode="long", silent=True)
        exp_time = time.time() - exp_start
        
        wake_up_trades = bt["basing_trades"]  # Inside the engine, it combines 'Basing' and 'Garage_Wake' metrics 
        wake_up_wr = bt["basing_win_rate"]
        
        print(f"    {idx:02d}/{total} | {name:<45} | Garage Wake Trades: {wake_up_trades:<3} | WR: {wake_up_wr:>5.1f}% | ({exp_time:.2f}s)")
        
        results.append({
            "Experiment": idx,
            "Name": name,
            "Hypothesis": exp["hypothesis"],
            "1W Weight (%)": int(exp["garage_weights"].get("% Price Change (1 Week)", 0) * 100),
            "4W Weight (%)": int(exp["garage_weights"].get("% Price Change (4 Weeks)", 0) * 100),
            "Wake Up Threshold": exp["wake_up_score"],
            "Total Pipeline Trades": bt["total_trades"],
            "Strong Trades": bt["strong_trades"],
            "Mild Trades": bt["mild_trades"],
            "Garage Wake Trades": bt["basing_trades"],
            "Garage Wake WR (%)": bt["basing_win_rate"],
            "Garage Wake Avg (%)": bt["basing_avg_return"],
            "Exec Time (s)": round(exp_time, 2)
        })
        
        restore_config(bck)

    total_time = time.time() - t0
    print(f"\n[+] Garage Grid Search Complete. {total} permutations tested in {total_time:.2f}s.")
    
    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_FILE, index=False)
    print(f"    Results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
