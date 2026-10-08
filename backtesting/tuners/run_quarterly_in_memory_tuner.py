import os
import itertools
import pandas as pd
from pathlib import Path
import time
from quarterly_grid_config import LONG_PHASE_1, LONG_PHASE_2

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
            with open("C:/TABELA/backtesting/tuners/debug_load.txt", "w") as f:
                f.write(f"Loading {file}\n")
                
            if file.endswith("_stocks.csv"):
                print(f"Loading {file}...")
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                df = pd.read_csv(filepath)
                df["Ticker"] = df["Ticker"].astype(str).str.strip()
                stock_data[date_fmt] = df
            elif file.endswith("_ETF.csv"):
                print(f"Loading {file}...")
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

    all_dates = sorted(stock_data.keys())
    return stock_data, etf_data, all_dates

import sys
sys.path.append(str(BASE_DIR))
from themes.stock_mapper import map_stock_theme

def precalculate_stock_themes(stock_data):
    """Calculates the theme for every ticker seen across all days."""
    print("[2/3] Precalculating stock to theme mapping (using live stock_mapper rules)...")
    stock_to_theme = {}
    for date, df in stock_data.items():
        if "Industry" not in df.columns or "Sector" not in df.columns:
            continue
            
        tickers = df['Ticker'].tolist()
        inds = df['Industry'].tolist()
        secs = df['Sector'].tolist()
        for t, i, s in zip(tickers, inds, secs):
            if t not in stock_to_theme:
                # Map using the actual pipeline rule engine
                stock_to_theme[t] = map_stock_theme(i, s)
    return stock_to_theme

def load_mapping_dicts():
    # Load explicit ETF -> Theme mappings
    stock_theme = pd.read_csv("c:/TABELA/data/stock_theme_mapping.csv", low_memory=False)
    stock_theme['Ticker'] = stock_theme['Ticker'].str.strip()
    
    macro_theme = pd.read_csv("c:/TABELA/data/macro_theme_mapping.csv", low_memory=False)
    
    etf_explicit = {}
    for _, row in stock_theme.iterrows():
        etf_explicit[row['Ticker']] = row.get("Mapped_Theme", "Unknown")
        
    return etf_explicit, macro_theme

def compile_etf_themes(etf_data, all_dates, phase_1_etf_weights, mode, etf_explicit, macro_theme):
    """
    Computes ETF scores based on permutation weights.
    Returns nested dictionary: compiled_themes[date][theme] = score
    """
    w_1m = phase_1_etf_weights["1M"]
    w_1w = phase_1_etf_weights["1W"]
    w_3m = phase_1_etf_weights["3M"]
    w_6m = phase_1_etf_weights["6M"]
    w_1y = phase_1_etf_weights["1Y"]
    
    compiled_themes = {}
    for date in all_dates:
        df = etf_data.get(date)
        if df is None or df.empty:
            continue
            
        df = df.copy()
        
        # 1. Evaluate explicit mappings
        macro_dict = dict(zip(macro_theme['Narrative_Theme'].str.lower().str.strip(), macro_theme['Benchmark_ETF_Theme'].str.strip()))
        
        def map_etf(ticker, inv_cat, inv_strat):
            if ticker in etf_explicit:
                return etf_explicit[ticker]
                
            # Check Investment Category
            cat_str = str(inv_cat).lower().strip()
            if cat_str in macro_dict:
                return macro_dict[cat_str]
                
            # Check Investment Strategy
            strat_str = str(inv_strat).lower().strip()
            if strat_str in macro_dict:
                return macro_dict[strat_str]
                
            return "Unknown"
            
        df['Theme'] = df.apply(lambda r: map_etf(r['Ticker'], r.get('Investment Category', ''), r.get('Investment Strategy', '')), axis=1)
        
        # Convert performance columns to numerics safely
        for col in ['Performance 1M (%)', 'Performance 1W (%)', 'Performance 3M (%)', 'Performance 6M (%)', 'Performance 1Y (%)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0

        # Calculate raw ETF Score
        df['raw_etf'] = (
            df['Performance 1W (%)'] * w_1w +
            df['Performance 1M (%)'] * w_1m +
            df['Performance 3M (%)'] * w_3m +
            df['Performance 6M (%)'] * w_6m +
            df['Performance 1Y (%)'] * w_1y
        )
        
        # The ETF Percentile Score
        df['ETF_Score'] = df['raw_etf'].rank(pct=True) * 100
        
        # Map back to highest score per theme
        theme_map = df.groupby('Theme')['ETF_Score'].max().fillna(0).to_dict()
        compiled_themes[date] = theme_map
        
    return compiled_themes

def extract_prices(stock_data):
    prices = {}
    for date, df in stock_data.items():
        if "Last Close" in df.columns:
            prices[date] = dict(zip(df["Ticker"], pd.to_numeric(df["Last Close"], errors='coerce').fillna(0)))
    return prices

def compile_stock_scores(stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
                         rs_weights, long_weights, zacks_map, growth_map):
    """
    Simulates Phase 1 Math logic across all 90 days.
    Returns: daily_scored[date] = DataFrame[['Ticker', 'RS_Rating', 'Long_Score', 'Zacks Rank', 'Theme_Class']]
    """
    daily_scored = {}
    
    w_rs_4w = rs_weights["4W"]
    w_rs_12w = rs_weights["12W"]
    w_rs_1w = rs_weights["1W"]
    w_rs_ytd = rs_weights["YTD"]
    w_rs_52w = rs_weights.get("52W", 0.0)
    
    comp_rs = long_weights["RS"]
    comp_theme = long_weights["THEME"]
    comp_zacks = long_weights["ZACKS"]
    comp_growth = long_weights["GROWTH"]
    
    for date in all_dates:
        df = stock_data[date]
        if df is None or df.empty:
            continue
            
        df = df.copy()
        
        # 1. Raw RS
        for col in ['% Price Change (1 Week)', '% Price Change (4 Weeks)', '% Price Change (12 Weeks)', 'Relative Price Change (YTD)', 'Price as a % of 52 Wk H-L Range']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
                
        df['raw_rs'] = (
            df['% Price Change (4 Weeks)'] * w_rs_4w +
            df['% Price Change (12 Weeks)'] * w_rs_12w +
            df['% Price Change (1 Week)'] * w_rs_1w +
            df['Relative Price Change (YTD)'] * w_rs_ytd + 
            df['Price as a % of 52 Wk H-L Range'] * w_rs_52w
        )
        
        # RS Rating ignores 0 values properly usually, but standard rank is sufficient 
        df['RS_Rating'] = df['raw_rs'].rank(pct=True) * 100
        
        # 2. Theme Lookup
        date_theme_map = compiled_themes_by_date.get(date, {})
        def get_theme_score(ticker):
            theme = stock_to_theme.get(ticker, "Unknown")
            return date_theme_map.get(theme, 0.0)
            
        df['Theme_Score'] = df['Ticker'].apply(get_theme_score)
        
        # For simplicity in this demo, let's assign theme class based on score arbitrarily
        # Real pipeline calculates percentiles across active themes.
        # Quick proxy:
        def get_theme_class(score):
            if score >= 60.0: return "Leading"
            if score >= 30.0: return "Neutral"
            return "Lagging"
        df['Theme_Class'] = df['Theme_Score'].apply(get_theme_class)
        
        # 3. Zacks & Growth
        if 'Zacks Rank' in df.columns:
            df['Zacks Rank'] = pd.to_numeric(df['Zacks Rank'], errors='coerce')
        else:
            df['Zacks Rank'] = np.nan
            
        df['Zacks_Score'] = df['Zacks Rank'].map(zacks_map).fillna(0.0)
        
        if 'Growth Score' in df.columns:
            df['Growth Score'] = df['Growth Score'].astype(str).str.upper()
            df['Growth_Score_Math'] = df['Growth Score'].map(growth_map).fillna(-50.0)
        else:
            df['Growth_Score_Math'] = -50.0
            
        # 4. Composite Math
        df['Long_Score'] = (
            df['RS_Rating'] * comp_rs +
            df['Theme_Score'] * comp_theme +
            df['Zacks_Score'] * comp_zacks +
            df['Growth_Score_Math'] * comp_growth
        )
        
        if 'Avg Volume' in df.columns:
            df['Avg Volume'] = pd.to_numeric(df['Avg Volume'], errors='coerce').fillna(0)
        else:
            df['Avg Volume'] = 0
            
        daily_scored[date] = df[['Ticker', 'RS_Rating', 'Long_Score', 'Zacks Rank', 'Theme_Class', 'Avg Volume']]
        
    return daily_scored

def simulate_long_baseline_gates(daily_scored, prices, all_dates, baseline_gates):
    """
    Executes the 4-tier Cartesian structural state machine against the dynamically calculated array.
    """
    entries = {}
    drop_tracker = {}
    
    min_rs = baseline_gates["MIN_RS"]
    min_score = baseline_gates["MIN_LONG_SCORE"]
    mild_floor = baseline_gates["MIN_DROPPED_WATCH_SCORE"]
    basing_zacks = baseline_gates["DEEP_RETRACE_ZACKS"]
    min_volume = baseline_gates["MIN_VOLUME"]
    
    max_score_seen = -999.0
    max_rs_seen = -999.0
    
    for date in all_dates:
        df = daily_scored.get(date)
        if df is None or df.empty:
            continue
            
        today_prices = prices.get(date, {})
        
        # Increment all dropped clocks today
        for t in list(drop_tracker.keys()):
            drop_tracker[t]["days_dropped"] += 1
            
        tickers = df['Ticker'].values
        scores = df['Long_Score'].values
        rs_ratings = df['RS_Rating'].values
        theme_classes = df['Theme_Class'].values
        z_ranks = df['Zacks Rank'].values
        volumes = df['Avg Volume'].values
        
        for t, score, rs, theme, zacks, vol in zip(tickers, scores, rs_ratings, theme_classes, z_ranks, volumes):
            if score > max_score_seen:
                max_score_seen = score
            if rs > max_rs_seen:
                max_rs_seen = rs
                
            entry_price = today_prices.get(t, 0)
            if entry_price < 10.0 or vol < min_volume:
                continue
                
            is_strong = (score >= min_score and rs >= min_rs and theme in ["Leading", "Neutral"])
            
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
                        if score >= mild_floor and rs >= mild_floor:
                            if "Mild" not in entries[t]:
                                entries[t]["Mild"] = {"entry_date": date, "entry_price": entry_price}
                        else:
                            del drop_tracker[t]
                    elif 22 <= days <= 50:
                        if zacks in basing_zacks and theme in ["Leading", "Neutral"]:
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
                    ret = ((current_price - data["entry_price"]) / data["entry_price"]) * 100.0
                    all_returns.append(ret)
                    
    if not all_returns:
        return 0.0, 0.0, 0
        
    avg = sum(all_returns) / len(all_returns)
    wr = sum(1 for r in all_returns if r > 0) / len(all_returns) * 100
    
    return wr, avg, len(all_returns)

def run_long_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices):
    print("\nStarting Long Phase 1 (Fundamental Math Sweep)...")
    keys, values = zip(*LONG_PHASE_1.items())
    permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    print(f"Total Parameter Permutations to Test: {len(permutations)}")
    
    baseline_gates = {k: v[0] for k, v in LONG_PHASE_2.items()}
    baseline_gates["MIN_LONG_SCORE"] = 65.0
    baseline_gates["MIN_RS"] = 80.0
    
    results = []
    
    etf_explicit, macro_theme = load_mapping_dicts()
    
    for i, p in enumerate(permutations):
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, p["ETF_PERIOD_WEIGHTS"], "aum", etf_explicit, macro_theme)
        daily_scored = compile_stock_scores(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["RS_RAW_WEIGHTS"], p["LONG_WEIGHTS"], p["ZACKS_SCORE_MAP"], p["GROWTH_SCORE_MAP"]
        )
        wr, avg, trc = simulate_long_baseline_gates(daily_scored, prices, all_dates, baseline_gates)
        print(f"  [P{i+1}] WR: {wr:.1f}% Avg: {avg:.2f}% | Math Map Evaluated")
        
        # Flatten dict for readable csv columns
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
        results.append(flat_p)
        
    out_df = pd.DataFrame(results)
    out_df.to_csv("c:/TABELA/backtesting/tuners/phase1_test_output.csv", index=False)
    print("Exported phase1_test_output.csv")
    
    print("\nPhase 1 Complete. Selecting Top 5 Math Structures by Win Rate...")
    from operator import itemgetter
    
    # Sort Phase 1 results by Win Rate, then Avg Return
    sorted_results = sorted(results, key=lambda x: (x["WinRate"], x["AvgReturn"]), reverse=True)
    top_5_math = sorted_results[:5]
    
    print("\n==================================")
    print("Starting Long Phase 2 (Gate Sweep)...")
    print("==================================")
    
    # Generate Phase 2 permutations
    from itertools import product
    keys_p2, values_p2 = zip(*LONG_PHASE_2.items())
    phase2_perms = [dict(zip(keys_p2, v)) for v in product(*values_p2)]
    print(f"Phase 2 Permutations per Math Model: {len(phase2_perms)}")
    
    final_phase2_results = []
    
    for m_idx, flat_base_model in enumerate(top_5_math):
        print(f"\nEvaluating Gates for Top Math Model #{m_idx+1} [WR: {flat_base_model['WinRate']:.1f}% Avg: {flat_base_model['AvgReturn']:.2f}%]")
        
        # We must re-extract the actual unflattened math formula
        p = [pm for pm in permutations if pm["RS_RAW_WEIGHTS"]["4W"] == flat_base_model["RS_RAW_WEIGHTS_4W"] and pm["ZACKS_SCORE_MAP"][1] == flat_base_model["ZACKS_SCORE_MAP_1"] and pm["ETF_PERIOD_WEIGHTS"]["1M"] == flat_base_model["ETF_PERIOD_WEIGHTS_1M"] and pm["LONG_WEIGHTS"]["RS"] == flat_base_model["LONG_WEIGHTS_RS"]][0]
        
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, p["ETF_PERIOD_WEIGHTS"], "aum", etf_explicit, macro_theme)
        daily_scored = compile_stock_scores(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["RS_RAW_WEIGHTS"], p["LONG_WEIGHTS"], p["ZACKS_SCORE_MAP"], p["GROWTH_SCORE_MAP"]
        )
        
        for g_idx, gate in enumerate(phase2_perms):
            p2_wr, p2_avg, p2_trades = simulate_long_baseline_gates(daily_scored, prices, all_dates, gate)
            merged = {**flat_base_model, **gate, 'WinRate_Final': p2_wr, 'AvgReturn_Final': p2_avg, 'Trades_Final': p2_trades}
            final_phase2_results.append(merged)
            
    # Export Phase 2 results
    df_p2 = pd.DataFrame(final_phase2_results)
    df_p2 = df_p2.sort_values(by=["WinRate_Final", "AvgReturn_Final"], ascending=False)
    p2_csv = "C:/TABELA/backtesting/tuners/quarterly_master_results.csv"
    df_p2.to_csv(p2_csv, index=False)
    print(f"\nExported {p2_csv}")
    
    print("\nOptimum Final System Found:")
    print(df_p2.head(1).to_string())
    
    return final_phase2_results

def main():
    start_time = time.time()
    stock_data, etf_data, all_dates = load_raw_csv_data()
    print(f"Loaded {len(all_dates)} days of market data.")
    
    stock_to_theme = precalculate_stock_themes(stock_data)
    print(f"Mapped {len(stock_to_theme)} unique stocks to themes.")
    
    prices = extract_prices(stock_data)
    
    # Run Phase 1
    import numpy as np
    sys.path.append(str(BASE_DIR)) # ensuring numpy is imported safely if needed
    run_long_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices)
    
    end_time = time.time()
    print(f"\nTotal time elapsed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()

