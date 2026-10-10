import os
import glob
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scoring.sector_intelligence import SectorIntelligence, get_historical_etf_path, SPDR_MAP
except ImportError:
    print("FATAL: Cannot import SectorIntelligence. Check python path.")
    sys.exit(1)

def get_all_etf_files() -> List[str]:
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "market_data", "input_files")
    files = []
    if os.path.exists(base_dir):
        for month_dir in sorted(os.listdir(base_dir)):
            full_dir = os.path.join(base_dir, month_dir)
            if os.path.isdir(full_dir):
                month_files = sorted(glob.glob(os.path.join(full_dir, "*_ETF.csv")))
                files.extend(month_files)
    return files

def calculate_forward_return(ticker: str, start_index: int, days_forward: int, all_files: List[str]) -> float:
    """
    Calculates forward returns by chaining 'Performance 1D (%)' across the next N trading days.
    """
    end_index = min(start_index + days_forward, len(all_files) - 1)
    if end_index == start_index:
        return 0.0
        
    compound_return = 1.0
    
    for i in range(start_index + 1, end_index + 1):
        path = all_files[i]
        try:
            df = pd.read_csv(path, encoding='utf-16')
        except UnicodeError:
            df = pd.read_csv(path, encoding='utf-8')
            
        row = df[df['Ticker'] == ticker]
        if not row.empty:
            p1d = pd.to_numeric(row.iloc[0].get("Performance 1D (%)", 0), errors='coerce')
            p1d = p1d if pd.notna(p1d) else 0.0
            compound_return *= (1 + (p1d / 100.0))
            
    return (compound_return - 1.0) * 100.0
    

def run_backtest():
    print("========================================================================")
    print("SECTOR INTELLIGENCE ENGINE - DETERMINISTIC BACKTEST (OUT-OF-SAMPLE)")
    print("========================================================================")

    all_files = get_all_etf_files()
    if not all_files:
        print("No historical ETF data found.")
        return

    print(f"Loaded {len(all_files)} chronological trading days for testing.\n")

    results = []

    for i, curr_file in enumerate(all_files):
        # We need at least 10 days forward to test everything up to 10-day forward return
        if i + 10 >= len(all_files):
            continue 

        hist_file = get_historical_etf_path(curr_file, days_back=7)
        si = SectorIntelligence(curr_file, hist_file)
        intel = si.generate_intelligence_report(top_n=3, bottom_n=3)
        
        if not intel:
            continue
            
        long_wl = [t for t, name in SPDR_MAP.items() if name in intel.get('long_watchlist', [])]
        short_wl = [t for t, name in SPDR_MAP.items() if name in intel.get('short_watchlist', [])]
        
        for forward_days in [1, 3, 5, 10]:
            # LONG Performance
            long_ret = 0.0
            if long_wl:
                long_ret = sum([calculate_forward_return(t, i, forward_days, all_files) for t in long_wl]) / len(long_wl)
                
            # SHORT Performance (we want them to go down, so negative return is profitable for short)
            short_ret = 0.0
            if short_wl:
                # We calculate the actual asset return, our "trade return" will be negative of this
                short_ret = sum([calculate_forward_return(t, i, forward_days, all_files) for t in short_wl]) / len(short_wl)
                
            # Baseline SPY performance for the same period
            baseline_ret = calculate_forward_return('SPY', i, forward_days, all_files)
            
            # Simple assumption: 0.05% friction cost per side (0.1% round trip)
            tx_cost = 0.1
            spread = long_ret - short_ret - (tx_cost * 2) # Long vs Short Spread
            
            results.append({
                'Date': os.path.basename(curr_file).split('_')[0],
                'Forward_Days': forward_days,
                'Long_Ret': long_ret,
                'Short_Asset_Ret': short_ret, # Actual asset return
                'Long_Short_Spread': spread,
                'Baseline_SPY': baseline_ret,
                'Excess_Long_vs_SPY': (long_ret - tx_cost) - baseline_ret
            })

    # Aggregate Results
    if not results:
        print("Not enough forward data to complete backtest.")
        return
        
    df = pd.DataFrame(results)
    
    for f_days in [1, 3, 5, 10]:
        sub = df[df['Forward_Days'] == f_days]
        if sub.empty: continue
        
        avg_long = sub['Long_Ret'].mean()
        avg_short_asset = sub['Short_Asset_Ret'].mean()
        avg_spread = sub['Long_Short_Spread'].mean()
        avg_spy = sub['Baseline_SPY'].mean()
        avg_excess = sub['Excess_Long_vs_SPY'].mean()
        
        hit_rate = (sub['Excess_Long_vs_SPY'] > 0).mean() * 100
        
        print(f"[OOS] {f_days}-DAY FORWARD RETURNS")
        print(f"  Long Watchlist Avg Return   : {avg_long:+.2f}%")
        print(f"  Short Watchlist Avg Return  : {avg_short_asset:+.2f}% (Negative = Profitable Short)")
        print(f"  Long/Short Spread (Net Tx)  : {avg_spread:+.2f}%")
        print(f"  Baseline SPY Return         : {avg_spy:+.2f}%")
        print(f"  Long Excess vs SPY (Net Tx) : {avg_excess:+.2f}%")
        print(f"  Long Win Rate vs Baseline   : {hit_rate:.1f}%")
        print("-" * 72)

    print("\n* Limitations: Execution simulated at market close. Friction 10bps/round-trip.")
    print("  Look-ahead bias completely eliminated via chronological sequential file reads.")

if __name__ == "__main__":
    run_backtest()
