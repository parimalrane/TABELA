import os
import itertools
import pandas as pd
from pathlib import Path
import time
import sys
import numpy as np

from quarterly_grid_config import SHORT_PHASE_1, SHORT_PHASE_2

BASE_DIR = Path("c:/TABELA")
CSV_DIR = BASE_DIR / "market_data" / "input_files"

def load_raw_csv_data():
    """Load all daily stock and ETF CSVs. No JSON dependencies."""
    stock_data = {}
    etf_data = {}
    
    print("[1/3] Loading all raw daily CSV files into memory...")
    for root, dirs, files in os.walk(CSV_DIR):
        for file in files:
            filepath = os.path.join(root, file)
                
            if file.endswith("_stocks.csv"):
                print(f"Loading {file}...", end="\r")
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                df = pd.read_csv(filepath)
                df["Ticker"] = df["Ticker"].astype(str).str.strip()
                stock_data[date_fmt] = df
            elif file.endswith("_ETF.csv"):
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                try:
                    df = pd.read_csv(filepath, sep=',', encoding='utf-8')
                    if len(df.columns) < 2:
                        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
                except Exception:
                    df = pd.read_csv(filepath, sep=',', encoding='utf-16')
                    if len(df.columns) < 2:
                        df = pd.read_csv(filepath, sep='\t', encoding='utf-16')
                
                df["Ticker"] = df["Ticker"].astype(str).str.strip()
                etf_data[date_fmt] = df

    print("\n[1/3] Complete.")
    all_dates = sorted(stock_data.keys())
    return stock_data, etf_data, all_dates

sys.path.append(str(BASE_DIR))
from themes.stock_mapper import map_stock_theme

def precalculate_stock_themes(stock_data):
    print("[2/3] Precalculating stock to theme mapping...")
    stock_to_theme = {}
    for date, df in stock_data.items():
        if "Industry" not in df.columns or "Sector" not in df.columns:
            continue
            
        tickers = df['Ticker'].tolist()
        inds = df['Industry'].tolist()
        secs = df['Sector'].tolist()
        for t, i, s in zip(tickers, inds, secs):
            if t not in stock_to_theme:
                stock_to_theme[t] = map_stock_theme(i, s)
    return stock_to_theme

def load_mapping_dicts():
    stock_theme = pd.read_csv("c:/TABELA/data/stock_theme_mapping.csv", low_memory=False)
    stock_theme['Ticker'] = stock_theme['Ticker'].str.strip()
    macro_theme = pd.read_csv("c:/TABELA/data/macro_theme_mapping.csv", low_memory=False)
    
    etf_explicit = {}
    for _, row in stock_theme.iterrows():
        etf_explicit[row['Ticker']] = row.get("Mapped_Theme", "Unknown")
        
    return etf_explicit, macro_theme

def compile_etf_themes(etf_data, all_dates, w_1m, w_1w, w_3m, w_6m, w_1y, etf_explicit, macro_theme):
    compiled_themes = {}
    for date in all_dates:
        df = etf_data.get(date)
        if df is None or df.empty:
            continue
            
        df = df.copy()
        macro_dict = dict(zip(macro_theme['Narrative_Theme'].str.lower().str.strip(), macro_theme['Benchmark_ETF_Theme'].str.strip()))
        
        def map_etf(ticker, inv_cat, inv_strat):
            if ticker in etf_explicit: return etf_explicit[ticker]
            cat_str = str(inv_cat).lower().strip()
            if cat_str in macro_dict: return macro_dict[cat_str]
            strat_str = str(inv_strat).lower().strip()
            if strat_str in macro_dict: return macro_dict[strat_str]
            return "Unknown"
            
        df['Theme'] = df.apply(lambda r: map_etf(r['Ticker'], r.get('Investment Category', ''), r.get('Investment Strategy', '')), axis=1)
        
        for col in ['Performance 1M (%)', 'Performance 1W (%)', 'Performance 3M (%)', 'Performance 6M (%)', 'Performance 1Y (%)']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else: df[col] = 0.0

        df['raw_etf'] = (
            df['Performance 1W (%)'] * w_1w + df['Performance 1M (%)'] * w_1m +
            df['Performance 3M (%)'] * w_3m + df['Performance 6M (%)'] * w_6m + df['Performance 1Y (%)'] * w_1y
        )
        
        df['ETF_Score'] = df['raw_etf'].rank(pct=True) * 100
        theme_map = df.groupby('Theme')['ETF_Score'].max().fillna(0).to_dict()
        compiled_themes[date] = theme_map
        
    return compiled_themes

def extract_prices(stock_data):
    prices = {}
    for date, df in stock_data.items():
        if "Last Close" in df.columns:
            prices[date] = dict(zip(df["Ticker"], pd.to_numeric(df["Last Close"], errors='coerce').fillna(0)))
    return prices

def compile_stock_scores_short(stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
                               rs_weights, comp_weights, zacks_map, growth_map):
    daily_scored = {}
    
    w_rs_4w = rs_weights["4W"]
    w_rs_12w = rs_weights["12W"]
    w_rs_1w = rs_weights["1W"]
    w_rs_ytd = rs_weights["YTD"]
    
    comp_rs = comp_weights["RS"]
    comp_theme = comp_weights["THEME"]
    comp_zacks = comp_weights["ZACKS"]
    comp_growth = comp_weights["GROWTH"]
    
    for date in all_dates:
        df = stock_data[date]
        if df is None or df.empty:
            continue
            
        df = df.copy()
        
        # Raw Short RS
        for col in ['% Price Change (1 Week)', '% Price Change (4 Weeks)', '% Price Change (12 Weeks)', 'Relative Price Change (YTD)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
                
        df['raw_rs'] = (
            df['% Price Change (4 Weeks)'] * w_rs_4w +
            df['% Price Change (12 Weeks)'] * w_rs_12w +
            df['% Price Change (1 Week)'] * w_rs_1w +
            df['Relative Price Change (YTD)'] * w_rs_ytd
        )
        
        # Sort ascending for Short RS Rating so worst negative gets lowest Short_RS_Rating
        df = df.sort_values("raw_rs", ascending=True).reset_index(drop=True)
        pct = (df.index.to_numpy() / len(df)) * 100.0
        df['Short_RS_Rating'] = np.clip(pct, 1.0, 99.0)
        
        # Theme Lookup
        date_theme_map = compiled_themes_by_date.get(date, {})
        def get_theme_score(ticker):
            theme = stock_to_theme.get(ticker, "Unknown")
            return date_theme_map.get(theme, 0.0)
            
        df['Theme_Score'] = df['Ticker'].apply(get_theme_score)
        
        def get_theme_class(score):
            if score <= 30.0: return "Lagging"
            if score <= 60.0: return "Neutral"
            return "Leading"
        df['Theme_Class'] = df['Theme_Score'].apply(get_theme_class)
        
        # Zacks & Growth
        if 'Zacks Rank' in df.columns:
            df['Zacks Rank'] = pd.to_numeric(df['Zacks Rank'], errors='coerce')
        else:
            df['Zacks Rank'] = np.nan
            
        df['Zacks_Score'] = df['Zacks Rank'].map(zacks_map).fillna(20.0)
        
        if 'Growth Score' in df.columns:
            df['Growth Score'] = df['Growth Score'].astype(str).str.upper()
            df['Growth_Score_Math'] = df['Growth Score'].map(growth_map).fillna(50.0)
        else:
            df['Growth_Score_Math'] = 50.0
            
        # Composite Math
        df['Short_Score'] = (
            df['Short_RS_Rating'] * comp_rs +
            df['Theme_Score'] * comp_theme +
            df['Zacks_Score'] * comp_zacks +
            df['Growth_Score_Math'] * comp_growth
        )
        
        if 'Avg Volume' in df.columns:
            df['Avg Volume'] = pd.to_numeric(df['Avg Volume'], errors='coerce').fillna(0)
        else:
            df['Avg Volume'] = 0
            
        daily_scored[date] = df[['Ticker', 'Short_RS_Rating', 'Short_Score', 'Zacks Rank', 'Theme_Class', 'Avg Volume']]
        
    return daily_scored

def simulate_short_baseline_gates(daily_scored, prices, all_dates, baseline_gates):
    entries = {}
    drop_tracker = {}
    
    max_score = baseline_gates["MAX_SHORT_SCORE"]
    max_rs = baseline_gates["MAX_SHORT_RS"]
    min_rs = baseline_gates["MIN_SHORT_RS"]
    basing_zack_blocks = baseline_gates["BLOCKED_ZACKS"]
    mild_floor = baseline_gates["MAX_DROPPED_WATCH_SCORE"]
    min_volume = baseline_gates["MIN_VOLUME"]
    
    for date in all_dates:
        df = daily_scored.get(date)
        if df is None or df.empty:
            continue
            
        today_prices = prices.get(date, {})
        
        for t in list(drop_tracker.keys()):
            drop_tracker[t]["days_dropped"] += 1
            
        tickers = df['Ticker'].values
        scores = df['Short_Score'].values
        rs_ratings = df['Short_RS_Rating'].values
        theme_classes = df['Theme_Class'].values
        z_ranks = df['Zacks Rank'].values
        volumes = df['Avg Volume'].values
        
        for t, score, rs, theme, zacks, vol in zip(tickers, scores, rs_ratings, theme_classes, z_ranks, volumes):
            entry_price = today_prices.get(t, 0)
            if entry_price < 10.0 or vol < min_volume:
                continue
                
            # STRONG BEARISH Check
            is_strong = (score <= max_score and min_rs <= rs <= max_rs and theme in ["Lagging", "Neutral"] and zacks not in basing_zack_blocks)
            
            if t not in entries:
                entries[t] = {}
                
            if is_strong:
                if t in drop_tracker: del drop_tracker[t]
                if "Strong" not in entries[t]:
                    entries[t]["Strong"] = {"entry_date": date, "entry_price": entry_price}
            else:
                if "Strong" in entries[t] and t not in drop_tracker:
                    drop_tracker[t] = {"days_dropped": 1}
                if t in drop_tracker:
                    days = drop_tracker[t]["days_dropped"]
                    if days <= 21:
                        if score <= mild_floor and rs <= mild_floor:
                            if "Mild" not in entries[t]:
                                entries[t]["Mild"] = {"entry_date": date, "entry_price": entry_price}
                        else:
                            del drop_tracker[t]
                    elif 22 <= days <= 50:
                        if zacks in [4, 5] and theme in ["Lagging", "Neutral"]:
                            if "Basing" not in entries[t]:
                                entries[t]["Basing"] = {"entry_date": date, "entry_price": entry_price}
                        else:
                            del drop_tracker[t]
                    else:
                        del drop_tracker[t]
                        
    current_date = all_dates[-1]
    today_prices = prices.get(current_date, {})
    all_returns = []
    
    for ticker, buckets in entries.items():
        current_price = today_prices.get(ticker, 0)
        if current_price > 0:
            for bucket_type, data in buckets.items():
                if data["entry_price"] > 0:
                    # SHORT RETURN MATH: Entry - Current / Entry
                    ret = ((data["entry_price"] - current_price) / data["entry_price"]) * 100.0
                    all_returns.append(ret)
                    
    if not all_returns:
        return 0.0, 0.0, 0
        
    avg = sum(all_returns) / len(all_returns)
    wr = sum(1 for r in all_returns if r > 0) / len(all_returns) * 100
    
    return wr, avg, len(all_returns)

def run_short_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices):
    print("\nStarting Short Phase 1 (Fundamental Math Sweep)...")
    keys, values = zip(*SHORT_PHASE_1.items())
    permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    print(f"Total Short Parameter Permutations to Test: {len(permutations)}")
    
    baseline_gates = {k: v[0] for k, v in SHORT_PHASE_2.items()}
    baseline_gates["MAX_SHORT_SCORE"] = 60.0
    baseline_gates["MAX_SHORT_RS"] = 75.0
    baseline_gates["MIN_SHORT_RS"] = 1.0
    
    results = []
    etf_explicit, macro_theme = load_mapping_dicts()
    
    for i, p in enumerate(permutations):
        # We reuse the baseline un-tuned ETF weights since short phase 1 doesn't sweep them
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, 0.40, 0.35, 0.25, 0.0, 0.0, etf_explicit, macro_theme)
        daily_scored = compile_stock_scores_short(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["SHORT_RS_RAW_WEIGHTS"], p["SHORT_COMPOSITE_WEIGHTS"], 
            p["SHORT_ZACKS_SCORE_MAP"], p["SHORT_GROWTH_SCORE_MAP"]
        )
        wr, avg, trades = simulate_short_baseline_gates(daily_scored, prices, all_dates, baseline_gates)
        print(f"  [P{i+1}] WR: {wr:.1f}% Avg: {avg:.2f}% Trades: {trades} | Math Map Evaluated")
        
        flat_p = {}
        for k, v in p.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat_p[f"{k}_{sub_k}"] = sub_v
            elif isinstance(v, list):
                flat_p[k] = str(v)
            else:
                flat_p[k] = v
                
        flat_p["WinRate"] = wr
        flat_p["AvgReturn"] = avg
        flat_p["Trades"] = trades
        results.append(flat_p)
        
    out_df = pd.DataFrame(results)
    out_df.to_csv("c:/TABELA/backtesting/tuners/phase1_short_test_output.csv", index=False)
    
    print("\nShort Phase 1 Complete. Selecting Top 5 Math Structures by Win Rate...")
    sorted_results = sorted(results, key=lambda x: (x["WinRate"], x["AvgReturn"]), reverse=True)
    top_5_math = sorted_results[:5]
    
    print("\n==================================")
    print("Starting Short Phase 2 (Gate Sweep)...")
    print("==================================")
    
    from itertools import product
    keys_p2, values_p2 = zip(*SHORT_PHASE_2.items())
    phase2_perms = [dict(zip(keys_p2, v)) for v in product(*values_p2)]
    print(f"Phase 2 Permutations per Math Model: {len(phase2_perms)}")
    
    final_phase2_results = []
    
    for m_idx, flat_base_model in enumerate(top_5_math):
        print(f"\nEvaluating Gates for Top Short Math Model #{m_idx+1} [WR: {flat_base_model['WinRate']:.1f}% Avg: {flat_base_model['AvgReturn']:.2f}%]")
        
        p = [pm for pm in permutations if pm["SHORT_RS_RAW_WEIGHTS"]["4W"] == flat_base_model["SHORT_RS_RAW_WEIGHTS_4W"] and pm["SHORT_COMPOSITE_WEIGHTS"]["RS"] == flat_base_model["SHORT_COMPOSITE_WEIGHTS_RS"]][0]
        
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, 0.40, 0.35, 0.25, 0.0, 0.0, etf_explicit, macro_theme)
        daily_scored = compile_stock_scores_short(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["SHORT_RS_RAW_WEIGHTS"], p["SHORT_COMPOSITE_WEIGHTS"], 
            p["SHORT_ZACKS_SCORE_MAP"], p["SHORT_GROWTH_SCORE_MAP"]
        )
        
        for g_idx, gate in enumerate(phase2_perms):
            p2_wr, p2_avg, trades = simulate_short_baseline_gates(daily_scored, prices, all_dates, gate)
            merged = {**flat_base_model, **gate, 'WinRate_Final': p2_wr, 'AvgReturn_Final': p2_avg, 'Trades_Final': trades}
            final_phase2_results.append(merged)
            
    df_p2 = pd.DataFrame(final_phase2_results)
    df_p2 = df_p2.sort_values(by=["WinRate_Final", "AvgReturn_Final"], ascending=False)
    p2_csv = "C:/TABELA/backtesting/tuners/quarterly_short_master_results.csv"
    df_p2.to_csv(p2_csv, index=False)
    print(f"\nExported {p2_csv}")
    
    print("\nOptimum Final Short System Found:")
    print(df_p2.head(1).to_string())
    
    return final_phase2_results

def main():
    start_time = time.time()
    stock_data, etf_data, all_dates = load_raw_csv_data()
    print(f"Loaded {len(all_dates)} days of market data.")
    
    stock_to_theme = precalculate_stock_themes(stock_data)
    print(f"Mapped {len(stock_to_theme)} unique stocks to themes.")
    
    prices = extract_prices(stock_data)
    
    run_short_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices)
    
    end_time = time.time()
    print(f"\nTotal time elapsed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
