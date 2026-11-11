import os
import itertools
import pandas as pd
from pathlib import Path
import time
import sys
import numpy as np
from datetime import datetime

from quarterly_grid_config import SHORT_PHASE_1, SHORT_PHASE_2

BASE_DIR = Path("c:/TABELA")
CSV_DIR = BASE_DIR / "market_data" / "input_files"
FWD_SWING_DAYS = 10  # Standard swing trading evaluation window

def load_raw_csv_data():
    """Load all daily stock and ETF CSVs into memory."""
    stock_data = {}
    etf_data = {}
    
    print("[1/3] Loading all raw daily CSV files into memory...", flush=True)
    count = 0
    for root, dirs, files in os.walk(CSV_DIR):
        for file in files:
            filepath = os.path.join(root, file)
                
            if file.endswith("_stocks.csv"):
                count += 1
                if count % 10 == 0:
                    print(f"  Loaded {count} stock CSV files...", flush=True)
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

    all_dates = sorted(stock_data.keys())
    print(f"[1/3] Complete. Total days loaded: {len(all_dates)} ({all_dates[0]} to {all_dates[-1]})", flush=True)
    return stock_data, etf_data, all_dates

sys.path.append(str(BASE_DIR))
from themes.stock_mapper import map_stock_theme

def precalculate_stock_themes(stock_data):
    print("[2/3] Precalculating stock to theme mapping...", flush=True)
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
    print(f"[2/3] Mapped {len(stock_to_theme)} unique stocks to themes.", flush=True)
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
    
    comp_rs = comp_weights.get("RS", comp_weights.get("RS_WEIGHT", 0.65))
    comp_theme = comp_weights.get("THEME", comp_weights.get("THEME_WEIGHT", 0.20))
    comp_zacks = comp_weights.get("ZACKS", comp_weights.get("ZACKS_WEIGHT", 0.10))
    comp_growth = comp_weights.get("GROWTH", comp_weights.get("GROWTH_WEIGHT", 0.05))
    
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

def compute_metrics(rets):
    """Calculates institutional performance metrics from a list of returns."""
    if not rets:
        return {"wr": 0.0, "avg": 0.0, "pf": 0.0, "n": 0, "avg_gain": 0.0, "avg_loss": 0.0}
    gains = [r for r in rets if r > 0]
    losses = [abs(r) for r in rets if r < 0]
    sum_g = sum(gains)
    sum_l = sum(losses)
    pf = round(sum_g / sum_l, 2) if sum_l > 0 else (99.0 if sum_g > 0 else 1.0)
    wr = round((len(gains) / len(rets)) * 100.0, 2)
    avg_ret = round(sum(rets) / len(rets), 2)
    avg_gain = round(sum_g / len(gains), 2) if gains else 0.0
    avg_loss = round(sum_l / len(losses), 2) if losses else 0.0
    return {"wr": wr, "avg": avg_ret, "pf": pf, "n": len(rets), "avg_gain": avg_gain, "avg_loss": avg_loss}

def simulate_short_baseline_gates(daily_scored, prices, all_dates, baseline_gates):
    """
    Simulates Short state machine entries and computes both 10-day forward (FWD-10D) 
    and Terminal (To-Date) returns with Profit Factor.
    """
    entries = {}
    drop_tracker = {}
    
    max_score = baseline_gates["MAX_SHORT_SCORE"]
    max_rs = baseline_gates["MAX_SHORT_RS"]
    min_rs = baseline_gates["MIN_SHORT_RS"]
    allowed_themes = baseline_gates.get("THEMES", ["Lagging", "Neutral"])
    basing_zack_blocks = baseline_gates["BLOCKED_ZACKS"]
    mild_floor = baseline_gates.get("MAX_DROPPED_WATCH_SCORE", 70.0)
    min_volume = baseline_gates["MIN_VOLUME"]
    min_price = baseline_gates.get("MIN_PRICE", 10.0)
    
    total_dates = len(all_dates)
    
    for d_idx, date in enumerate(all_dates):
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
            if entry_price < min_price or vol < min_volume:
                continue
                
            # STRONG BEARISH Entry Gate
            is_strong = (score <= max_score and min_rs <= rs <= max_rs and theme in allowed_themes and zacks not in basing_zack_blocks)
            
            if t not in entries:
                entries[t] = {}
                
            if is_strong:
                if t in drop_tracker: del drop_tracker[t]
                if "Strong" not in entries[t]:
                    entries[t]["Strong"] = {"entry_date": date, "entry_idx": d_idx, "entry_price": entry_price}
            else:
                if "Strong" in entries[t] and t not in drop_tracker:
                    drop_tracker[t] = {"days_dropped": 1}
                if t in drop_tracker:
                    days = drop_tracker[t]["days_dropped"]
                    if days <= 14:
                        if score <= mild_floor and rs <= mild_floor:
                            if "Mild" not in entries[t]:
                                entries[t]["Mild"] = {"entry_date": date, "entry_idx": d_idx, "entry_price": entry_price}
                        else:
                            del drop_tracker[t]
                    elif 15 <= days <= 50:
                        if zacks in [4, 5] and theme in allowed_themes:
                            if "Basing" not in entries[t]:
                                entries[t]["Basing"] = {"entry_date": date, "entry_idx": d_idx, "entry_price": entry_price}
                        else:
                            del drop_tracker[t]
                    else:
                        del drop_tracker[t]
                        
    terminal_date = all_dates[-1]
    terminal_prices = prices.get(terminal_date, {})
    
    strong_fwd10_returns = []
    strong_todate_returns = []
    
    all_fwd10_returns = []
    all_todate_returns = []
    
    for ticker, buckets in entries.items():
        for b_name, b_data in buckets.items():
            entry_price = b_data["entry_price"]
            entry_idx = b_data["entry_idx"]
            
            if entry_price <= 0:
                continue
                
            # 1. Forward 10-Day Swing Return (only if 10 days of future data exist)
            if entry_idx + FWD_SWING_DAYS < total_dates:
                exit_date_10 = all_dates[entry_idx + FWD_SWING_DAYS]
                exit_price_10 = prices.get(exit_date_10, {}).get(ticker, 0)
                if exit_price_10 > 0:
                    ret_10 = ((entry_price - exit_price_10) / entry_price) * 100.0
                    all_fwd10_returns.append(ret_10)
                    if b_name == "Strong":
                        strong_fwd10_returns.append(ret_10)
                        
            # 2. To-Date Terminal Return
            last_price = terminal_prices.get(ticker, 0)
            if last_price > 0:
                ret_todate = ((entry_price - last_price) / entry_price) * 100.0
                all_todate_returns.append(ret_todate)
                if b_name == "Strong":
                    strong_todate_returns.append(ret_todate)
                    
    strong_10d_m = compute_metrics(strong_fwd10_returns)
    strong_todate_m = compute_metrics(strong_todate_returns)
    all_10d_m = compute_metrics(all_fwd10_returns)
    
    total_strong_trades = sum(1 for b in entries.values() if "Strong" in b)
    
    return {
        "Strong_WR_10D": strong_10d_m["wr"],
        "Strong_PF_10D": strong_10d_m["pf"],
        "Strong_Avg_10D": strong_10d_m["avg"],
        "Strong_N_10D": strong_10d_m["n"],
        "Strong_WR_ToDate": strong_todate_m["wr"],
        "Strong_Avg_ToDate": strong_todate_m["avg"],
        "Strong_Trades": total_strong_trades,
        "All_WR_10D": all_10d_m["wr"],
        "All_PF_10D": all_10d_m["pf"],
        "All_Trades": len(all_todate_returns)
    }

def run_short_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices):
    print("\n=======================================================", flush=True)
    print("Starting Short Phase 1 (Fundamental Math Sweep)...", flush=True)
    print("=======================================================", flush=True)
    keys, values = zip(*SHORT_PHASE_1.items())
    permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    print(f"Total Short Parameter Permutations to Test: {len(permutations)}", flush=True)
    
    baseline_gates = {k: v[0] for k, v in SHORT_PHASE_2.items()}
    baseline_gates["MAX_SHORT_SCORE"] = 30.0
    baseline_gates["MAX_SHORT_RS"] = 60.0
    baseline_gates["MIN_SHORT_RS"] = 8.0
    baseline_gates["THEMES"] = ["Lagging"]
    baseline_gates["BLOCKED_ZACKS"] = [1, 2]
    baseline_gates["MIN_VOLUME"] = 1_000_000
    
    results = []
    etf_explicit, macro_theme = load_mapping_dicts()
    
    for i, p in enumerate(permutations):
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, 0.40, 0.20, 0.40, 0.0, 0.0, etf_explicit, macro_theme)
        daily_scored = compile_stock_scores_short(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["SHORT_RS_RAW_WEIGHTS"], p["SHORT_COMPOSITE_WEIGHTS"], 
            p["SHORT_ZACKS_SCORE_MAP"], p["SHORT_GROWTH_SCORE_MAP"]
        )
        metrics = simulate_short_baseline_gates(daily_scored, prices, all_dates, baseline_gates)
        print(f"  [Model {i+1:02d}] RS_W={p['SHORT_RS_RAW_WEIGHTS']} | COMP_W={p['SHORT_COMPOSITE_WEIGHTS']} -> 10D WR: {metrics['Strong_WR_10D']}% | PF: {metrics['Strong_PF_10D']} | Avg: {metrics['Strong_Avg_10D']}% | Trades: {metrics['Strong_Trades']}", flush=True)
        
        flat_p = {"Model_ID": i + 1}
        for k, v in p.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat_p[f"{k}_{sub_k}"] = sub_v
            elif isinstance(v, list):
                flat_p[k] = str(v)
            else:
                flat_p[k] = v
                
        flat_p.update(metrics)
        results.append(flat_p)
        
    sorted_results = sorted(results, key=lambda x: (x["Strong_PF_10D"], x["Strong_WR_10D"], x["Strong_Avg_10D"]), reverse=True)
    out_df = pd.DataFrame(sorted_results)
    out_df.to_csv("c:/TABELA/backtesting/tuners/phase1_short_test_output.csv", index=False)
    
    print("\nShort Phase 1 Complete. Selecting Top 3 Math Structures by 10D Profit Factor & Win Rate...", flush=True)
    top_models = sorted_results[:3]  # Top 3 best math models
    
    print("\n=======================================================", flush=True)
    print("Starting Short Phase 2 (Gate & Threshold Sweep)...", flush=True)
    print("=======================================================", flush=True)
    
    keys_p2, values_p2 = zip(*SHORT_PHASE_2.items())
    phase2_perms = [dict(zip(keys_p2, v)) for v in itertools.product(*values_p2)]
    print(f"Phase 2 Permutations per Math Model: {len(phase2_perms)} (Total runs: {len(phase2_perms) * len(top_models)})", flush=True)
    
    final_phase2_results = []
    
    for m_idx, flat_base_model in enumerate(top_models):
        print(f"\nEvaluating Gates for Model #{m_idx+1} (Model_ID={flat_base_model['Model_ID']}) [Base 10D WR: {flat_base_model['Strong_WR_10D']}% PF: {flat_base_model['Strong_PF_10D']}]...", flush=True)
        
        p = permutations[flat_base_model["Model_ID"] - 1]
        
        compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, 0.40, 0.20, 0.40, 0.0, 0.0, etf_explicit, macro_theme)
        daily_scored = compile_stock_scores_short(
            stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
            p["SHORT_RS_RAW_WEIGHTS"], p["SHORT_COMPOSITE_WEIGHTS"], 
            p["SHORT_ZACKS_SCORE_MAP"], p["SHORT_GROWTH_SCORE_MAP"]
        )
        
        for g_idx, gate in enumerate(phase2_perms):
            if (g_idx + 1) % 100 == 0 or g_idx == len(phase2_perms) - 1:
                print(f"  Progress: {g_idx+1}/{len(phase2_perms)} gate permutations evaluated...", flush=True)
            metrics = simulate_short_baseline_gates(daily_scored, prices, all_dates, gate)
            
            gate_flat = {}
            for gk, gv in gate.items():
                gate_flat[gk] = str(gv) if isinstance(gv, list) else gv
                
            merged = {**flat_base_model, **gate_flat, **metrics}
            final_phase2_results.append(merged)
            
    date_str = datetime.now().strftime("%Y%m%d")
    df_p2 = pd.DataFrame(final_phase2_results)
    
    # Sort primarily by 10-day forward Profit Factor and Win Rate (minimum 30 trades for statistical significance)
    df_p2 = df_p2.sort_values(by=["Strong_PF_10D", "Strong_WR_10D", "Strong_Avg_10D"], ascending=False)
    p2_csv = f"C:/TABELA/backtesting/tuners/{date_str}_quarterly_short_master_results.csv"
    df_p2.to_csv(p2_csv, index=False)
    print(f"\n=======================================================", flush=True)
    print(f"Master Optimization Results Exported to:\n{p2_csv}", flush=True)
    print(f"=======================================================", flush=True)
    
    # Filter for statistically meaningful sample (trades >= 30)
    sig_df = df_p2[df_p2["Strong_Trades"] >= 30]
    if sig_df.empty:
        sig_df = df_p2
        
    print("\n--- TOP 5 SHORT GATE CONFIGURATIONS (Minimum 30 Trades) ---")
    cols_display = [
        "Model_ID", "SHORT_RS_RAW_WEIGHTS_4W", "SHORT_RS_RAW_WEIGHTS_12W", "SHORT_RS_RAW_WEIGHTS_YTD",
        "SHORT_COMPOSITE_WEIGHTS_RS", "SHORT_COMPOSITE_WEIGHTS_THEME", "SHORT_COMPOSITE_WEIGHTS_ZACKS",
        "MIN_VOLUME", "MAX_SHORT_SCORE", "MIN_SHORT_RS", "MAX_SHORT_RS", "THEMES", "BLOCKED_ZACKS",
        "Strong_WR_10D", "Strong_PF_10D", "Strong_Avg_10D", "Strong_Trades", "Strong_WR_ToDate", "Strong_Avg_ToDate"
    ]
    avail_cols = [c for c in cols_display if c in sig_df.columns]
    print(sig_df[avail_cols].head(5).to_string(index=False), flush=True)
    
    return final_phase2_results

def main():
    start_time = time.time()
    stock_data, etf_data, all_dates = load_raw_csv_data()
    stock_to_theme = precalculate_stock_themes(stock_data)
    prices = extract_prices(stock_data)
    
    run_short_phase_1(stock_data, etf_data, all_dates, stock_to_theme, prices)
    
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds", flush=True)

if __name__ == "__main__":
    main()
