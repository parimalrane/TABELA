import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import config.config as cfg
import time

BASE_DIR = Path("c:/TABELA")
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
os.makedirs(RESULTS_DIR, exist_ok=True)
RESULTS_FILE = RESULTS_DIR / f"optimization_results_basing_{datetime.now().strftime('%Y%m%d')}.csv"

EXPERIMENTS = [
    {
        "name": "1. Baseline (No Traps)",
        "hypothesis": "Track EVERYTHING > Day 22 for baseline conversion rate.",
        "rs_floor": 0.0, "zacks": [1,2,3,4,5], "themes": ["Leading", "Neutral", "Lagging", "Unknown", "Micro Laggard", "Unclassified Leader"]
    },
    {
        "name": "2. Original Setup (Fundamental Forgiveness)",
        "hypothesis": "Wait for 1/2, ignore price completely.",
        "rs_floor": 0.0, "zacks": [1, 2], "themes": ["Leading", "Neutral"]
    },
    {
        "name": "3. Loose Structural Support (RS > 50)",
        "hypothesis": "Ignore fundamentals, but drop falling knives.",
        "rs_floor": 50.0, "zacks": [1,2,3,4,5], "themes": ["Leading", "Neutral", "Lagging", "Unknown", "Micro Laggard", "Unclassified Leader"]
    },
    {
        "name": "4. Tight Structural Support (RS > 65)",
        "hypothesis": "Stock must maintain upper relative strength while resting.",
        "rs_floor": 65.0, "zacks": [1,2,3,4,5], "themes": ["Leading", "Neutral", "Lagging", "Unknown", "Micro Laggard", "Unclassified Leader"]
    },
    {
        "name": "5. Structural + Fundamental (RS > 65 + Zacks 1/2)",
        "hypothesis": "Best of both: good earnings + good structural support.",
        "rs_floor": 65.0, "zacks": [1, 2], "themes": ["Leading", "Neutral", "Lagging", "Unknown", "Micro Laggard", "Unclassified Leader"]
    },
    {
        "name": "6. Structural + Fundamental + Macro",
        "hypothesis": "RS > 65 + Zacks 1/2 + Restricted to Non-Lagging themes.",
        "rs_floor": 65.0, "zacks": [1, 2], "themes": ["Leading", "Neutral", "Unclassified Leader"]
    },
    {
        "name": "7. Ultra Coiled Spring (RS > 75)",
        "hypothesis": "Maximum possible strictness.",
        "rs_floor": 75.0, "zacks": [1, 2], "themes": ["Leading"]
    }
]

def run_basing_simulator(exp):
    input_dir = BASE_DIR / "market_data" / "input_files"
    json_dir = BASE_DIR / "market_data" / "stock_universe"
    
    json_files = sorted([os.path.join(r, f) for r, d, files in os.walk(json_dir) for f in files if f.endswith("_stock_history.json")])
    if not json_files: return None

    # Tracker: {ticker: {"days": int, "in_base": bool, "converted": bool, "killed": bool}}
    state = {}
    
    total_entered_base = 0
    total_conversions = 0
    
    min_rs_floor = exp["rs_floor"]
    allowed_zacks = exp["zacks"]
    allowed_themes = exp["themes"]

    # Golden Config entry strings for the 90/90 gate check
    min_rs_breakout = cfg.LONG_ENTRY.get("MIN_RS", 90.0)
    min_score_breakout = cfg.LONG_ENTRY.get("MIN_LONG_SCORE", 90.0)
    allowed_themes_breakout = cfg.LONG_ENTRY.get("THEMES", ["Leading", "Neutral", "Unclassified Leader", "Unknown"])
    
    for file in json_files:
        with open(file, "r") as f:
            try: data = json.load(f)
            except: continue
        
        # Increment internal clocks for known dropped stocks
        for t in list(state.keys()):
            if not state[t].get("killed", False):
                state[t]["days"] += 1
            
        for row in data:
            ticker = row["ticker"]
            score = row.get("long_score", 0.0)
            rs_rating = row.get("rs_rating", 0)
            theme_class = row.get("theme_class", "Unknown")
            zacks_rank = row.get("zacks_rank", 3)
            
            is_strong = (score >= min_score_breakout and rs_rating >= min_rs_breakout and theme_class in allowed_themes_breakout)
            
            if ticker not in state:
                if is_strong:
                    state[ticker] = {"days": 0, "in_base": False, "converted": False, "killed": False}
                continue
                
            if is_strong:
                # 90/90 Breakout Detected!
                # If it was actively waiting in the base bucket:
                if state[ticker].get("in_base", False) and not state[ticker].get("converted", False):
                    total_conversions += 1
                    state[ticker]["converted"] = True
                
                # Reset state completely since it survived and hit strong
                state[ticker]["days"] = 0
                state[ticker]["in_base"] = False
                state[ticker]["killed"] = False
            else:
                # Dropped state
                days = state[ticker]["days"]
                killed = state[ticker].get("killed", False)
                if not killed and days >= 22:
                    # Stock is entering the basing window. Does it survive the floor check?
                    passes = (rs_rating >= min_rs_floor and zacks_rank in allowed_zacks and theme_class in allowed_themes)
                    
                    if passes:
                        # Survives another day in the base!
                        if not state[ticker].get("in_base", False):
                            state[ticker]["in_base"] = True
                            state[ticker]["converted"] = False
                            total_entered_base += 1
                    else:
                        # Broke support level. Kill it immediately.
                        state[ticker]["killed"] = True
                        state[ticker]["in_base"] = False

    return total_entered_base, total_conversions

def main():
    print("=" * 80)
    print("     TABELA BASING CONVERSION ENGINE V1")
    print(f"     Testing {len(EXPERIMENTS)} Base Configurations...")
    print("=" * 80)

    results = []
    
    for idx, exp in enumerate(EXPERIMENTS, 1):
        t0 = time.time()
        print(f"  [{idx}/{len(EXPERIMENTS)}] Running: {exp['name']}")
        entered, converted = run_basing_simulator(exp)
        t_time = round(time.time() - t0, 2)
        
        rate = round((converted / entered) * 100, 2) if entered > 0 else 0.0
        
        print(f"     -> Coiled Springs Found: {entered}")
        print(f"     -> Breakouts Triggered: {converted}")
        print(f"     -> Conversion Rate: {rate}% | {t_time}s\n")
        
        results.append({
            "Exp": idx,
            "Name": exp["name"],
            "Hypothesis": exp["hypothesis"],
            "Springs Found": entered,
            "Breakouts": converted,
            "Conversion Rate (%)": rate,
            "RS Floor": exp["rs_floor"],
            "Allowed Zacks": str(exp["zacks"]),
        })

    df = pd.DataFrame(results).sort_values("Conversion Rate (%)", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)
    
    print("\n" + df.to_string(index=False))
    print(f"\n[BASING TUNER COMPLETE] Results saved to {RESULTS_FILE.name}")


if __name__ == "__main__":
    main()
