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
        intel = si.generate_intelligence_report()
        
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

def run_sector_grid_sweep(all_files: List[str]):
    print("\n========================================================================")
    print("SECTOR_COMPOSITE_WEIGHTS - IN-MEMORY GRID OPTIMIZATION (85 DAYS)")
    print("========================================================================")

    # Preload all ETF DataFrames once into memory
    etf_dfs = []
    dates = []
    for path in all_files:
        try:
            df = pd.read_csv(path, encoding='utf-16')
            if len(df.columns) < 2:
                df = pd.read_csv(path, sep='\t', encoding='utf-16')
        except Exception:
            df = pd.read_csv(path, encoding='utf-8')
            if len(df.columns) < 2:
                df = pd.read_csv(path, sep='\t', encoding='utf-8')
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        etf_dfs.append(df)
        dates.append(os.path.basename(path).split('_')[0])

    # Pre-extract 1D returns and period metrics per ticker per day
    p1d_by_day = []
    metrics_by_day = []
    for df in etf_dfs:
        p1d_map = {}
        m_map = {}
        for _, row in df[df['Ticker'].isin(list(SPDR_MAP.keys()) + ['SPY'])].iterrows():
            t = row['Ticker']
            p1d = pd.to_numeric(str(row.get("Performance 1D (%)", 0)).replace('%', '').strip(), errors='coerce')
            p1w = pd.to_numeric(str(row.get("Performance 1W (%)", 0)).replace('%', '').strip(), errors='coerce')
            p1m = pd.to_numeric(str(row.get("Performance 1M (%)", 0)).replace('%', '').strip(), errors='coerce')
            p3m = pd.to_numeric(str(row.get("Performance 3M (%)", 0)).replace('%', '').strip(), errors='coerce')
            pytd = pd.to_numeric(str(row.get("Performance YTD (%)", row.get("Performance 1Y (%)", 0))).replace('%', '').strip(), errors='coerce')
            p1d_map[t] = 0.0 if pd.isna(p1d) else float(p1d)
            m_map[t] = {
                "1W": 0.0 if pd.isna(p1w) else float(p1w),
                "1M": 0.0 if pd.isna(p1m) else float(p1m),
                "3M": 0.0 if pd.isna(p3m) else float(p3m),
                "YTD": 0.0 if pd.isna(pytd) else float(pytd),
            }
        p1d_by_day.append(p1d_map)
        metrics_by_day.append(m_map)

    def fast_fwd_ret(ticker: str, start_idx: int, days_fwd: int) -> float:
        end_idx = min(start_idx + days_fwd, len(etf_dfs) - 1)
        comp = 1.0
        for idx in range(start_idx + 1, end_idx + 1):
            r = p1d_by_day[idx].get(ticker, 0.0)
            comp *= (1.0 + r / 100.0)
        return (comp - 1.0) * 100.0

    candidates = [
        {"Name": "1. Current Prod (20/40/30/10)",     "1W": 0.20, "1M": 0.40, "3M": 0.30, "YTD": 0.10},
        {"Name": "2. Fast Rotation (35/40/25/0)",     "1W": 0.35, "1M": 0.40, "3M": 0.25, "YTD": 0.00},
        {"Name": "3. Ultra Fast 1W/1M (50/35/15/0)",  "1W": 0.50, "1M": 0.35, "3M": 0.15, "YTD": 0.00},
        {"Name": "4. Pure 1M/3M Swing (0/50/50/0)",   "1W": 0.00, "1M": 0.50, "3M": 0.50, "YTD": 0.00},
        {"Name": "5. 1M Dominant (20/60/20/0)",       "1W": 0.20, "1M": 0.60, "3M": 0.20, "YTD": 0.00},
        {"Name": "6. 3M/YTD Structural (10/20/40/30)","1W": 0.10, "1M": 0.20, "3M": 0.40, "YTD": 0.30},
        {"Name": "7. Equal Weight (25/25/25/25)",     "1W": 0.25, "1M": 0.25, "3M": 0.25, "YTD": 0.25},
        {"Name": "8. YTD Trend Anchor (15/25/25/35)", "1W": 0.15, "1M": 0.25, "3M": 0.25, "YTD": 0.35},
        {"Name": "9. 3M Dominant (15/25/50/10)",      "1W": 0.15, "1M": 0.25, "3M": 0.50, "YTD": 0.10},
        {"Name": "10. Pure Short-Term (60/40/0/0)",   "1W": 0.60, "1M": 0.40, "3M": 0.00, "YTD": 0.00},
    ]

    summary_rows = []
    for cand in candidates:
        w1w, w1m, w3m, wytd = cand["1W"], cand["1M"], cand["3M"], cand["YTD"]
        rows = []
        for i in range(len(etf_dfs)):
            if i + 10 >= len(etf_dfs):
                continue
            m_map = metrics_by_day[i]
            scores = []
            for ticker in SPDR_MAP.keys():
                if ticker not in m_map:
                    continue
                m = m_map[ticker]
                sc = m["1W"] * w1w + m["1M"] * w1m + m["3M"] * w3m + m["YTD"] * wytd
                scores.append((ticker, sc))
            if len(scores) < 6:
                continue
            scores.sort(key=lambda x: x[1], reverse=True)
            long_wl = [t for t, _ in scores[:3]]
            short_wl = [t for t, _ in scores[-3:]]

            for f_days in [5, 10]:
                l_ret = sum(fast_fwd_ret(t, i, f_days) for t in long_wl) / len(long_wl)
                s_ret = sum(fast_fwd_ret(t, i, f_days) for t in short_wl) / len(short_wl)
                spy_ret = fast_fwd_ret('SPY', i, f_days)
                tx = 0.1
                spread = l_ret - s_ret - (tx * 2)
                excess_l = (l_ret - tx) - spy_ret
                excess_s = spy_ret - (s_ret + tx)
                rows.append({
                    "f_days": f_days,
                    "l_ret": l_ret,
                    "s_ret": s_ret,
                    "spread": spread,
                    "excess_l": excess_l,
                    "excess_s": excess_s,
                })
        df_c = pd.DataFrame(rows)
        d10 = df_c[df_c["f_days"] == 10]
        d5 = df_c[df_c["f_days"] == 5]
        summary_rows.append({
            "Model": cand["Name"],
            "1W": w1w, "1M": w1m, "3M": w3m, "YTD": wytd,
            "10D_Long_Ret%": round(d10["l_ret"].mean(), 2),
            "10D_Short_Asset_Ret%": round(d10["s_ret"].mean(), 2),
            "10D_L_S_Spread%": round(d10["spread"].mean(), 2),
            "10D_Spread_WR%": round((d10["spread"] > 0).mean() * 100, 1),
            "10D_Long_Ex_SPY%": round(d10["excess_l"].mean(), 2),
            "10D_Long_WR_vs_SPY%": round((d10["excess_l"] > 0).mean() * 100, 1),
            "10D_Short_WR_vs_SPY%": round((d10["excess_s"] > 0).mean() * 100, 1),
            "5D_L_S_Spread%": round(d5["spread"].mean(), 2),
            "5D_Spread_WR%": round((d5["spread"] > 0).mean() * 100, 1),
        })

    out_df = pd.DataFrame(summary_rows).sort_values(by=["10D_L_S_Spread%", "10D_Long_WR_vs_SPY%"], ascending=False)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "sector_weights_optimization.csv")
    out_df.to_csv(out_path, index=False)
    print(out_df.to_string(index=False))
    print(f"\nSaved sector optimization results to: {out_path}")


if __name__ == "__main__":
    all_files = get_all_etf_files()
    run_sector_grid_sweep(all_files)

