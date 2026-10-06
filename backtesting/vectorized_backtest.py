import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

import config.config as cfg
import scoring.scoring_engine as scoring

class VectorizedBacktestEngine:
    def __init__(self):
        self.master_matrix = None
        self.all_dates = []
        self.raw_etf_matrices = {}

    def load_data(self):
        """Loads all JSONs and CSVs into a master DataFrame ONCE."""
        json_dir = BASE_DIR / "market_data" / "stock_universe"
        csv_dir = BASE_DIR / "market_data" / "input_files"
        
        # 1. Load ETF/Theme data from JSON
        json_data = []
        for f in json_dir.rglob("*_stock_history.json"):
            date_str = f.name[:10]
            with open(f, "r") as json_f:
                try:
                    data = json.load(json_f)
                    for row in data:
                        json_data.append({
                            "date": date_str,
                            "Ticker": row.get("ticker", "").strip(),
                            "theme_class": row.get("theme_class", "Unknown"),
                            "Theme_Score": row.get("theme_strength_score", 0.0),
                            "avg_volume": row.get("avg_volume", 0.0),
                            "sales_growth": row.get("sales_growth", 0.0),
                            "operating_margin": row.get("operating_margin", 0.0)
                        })
                except Exception: pass
                
        df_json = pd.DataFrame(json_data)
        if df_json.empty:
            return False
            
        # 2. Load prices and raw features from CSV
        csv_data = []
        for f in csv_dir.rglob("*stocks.csv"):
            if "_stocks.csv" not in f.name: continue
            date_str = f.name[:8]
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            try:
                df = pd.read_csv(f)
                df["Ticker"] = df["Ticker"].str.strip()
                df["date"] = date_fmt
                csv_data.append(df)
            except Exception: pass
            
        if not csv_data:
            return False
            
        df_csv = pd.concat(csv_data, ignore_index=True)
        
        # 3. Load ETFs from CSV for dynamic Theme Classification
        from pipeline.pipeline import filter_valid_etfs, filter_institutional_etfs, filter_etfs_with_sufficient_history
        from themes.theme_parser import parse_theme
        
        for f in csv_dir.rglob("*_etf.csv"):
            date_str = f.name[:8]
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            try:
                df_etf = pd.read_csv(f)
                df_etf = filter_valid_etfs(df_etf)
                df_etf = filter_institutional_etfs(df_etf)
                df_etf, _ = filter_etfs_with_sufficient_history(df_etf)
                df_etf[["Sector", "Theme", "Subtheme"]] = df_etf["Investment Strategy"].apply(
                    lambda x: pd.Series(parse_theme(x))
                )
                df_etf["Theme"] = df_etf["Theme"].replace({
                    "natural gas": "Natural Gas", "Natural Gas": "Natural Gas",
                    "broad": "Broad", "Broad": "Broad",
                    "mlp": "MLP", "MLP": "MLP",
                    "reits": "REITs", "REITs": "REITs"
                })
                self.raw_etf_matrices[date_fmt] = df_etf
            except Exception: pass
            
        # 4. Merge
        self.master_matrix = pd.merge(df_csv, df_json, on=["date", "Ticker"], how="left")
        self.all_dates = sorted(self.master_matrix["date"].unique())
        return True



    def run_simulation(self, matrix_scored, mode="long"):
        """Run the fast state machine loop over pre-scored matrix."""
        entries = {}
        drop_tracker = {}
        prices = {}
        
        # Pre-build price lookup for speed
        for d in self.all_dates:
            df_d = matrix_scored[matrix_scored["date"] == d]
            prices[d] = dict(zip(df_d["Ticker"], df_d["Last Close"]))

        # Group iterations by date
        for current_date in self.all_dates:
            df_today = matrix_scored[matrix_scored["date"] == current_date]
            if df_today.empty: continue
            
            # Increment all dropped clocks today
            for t in list(drop_tracker.keys()):
                drop_tracker[t]["days_dropped"] += 1

            for _, row in df_today.iterrows():
                ticker = row["Ticker"]
                
                if mode == "long":
                    score = row.get("long_score", 0.0)    
                    rs_rating = row.get("RS_Rating", 0)
                    garage_rs = row.get("Long_Garage_RS_Rating", 0.0)
                else:
                    score = row.get("Short_Score", 0.0)
                    rs_rating = row.get("Short_RS_Rating", 0.0)
                    garage_rs = row.get("Short_Garage_RS_Rating", 0.0)
                    
                theme_class = row.get("theme_class", "Unknown")
                zacks_rank = row.get("Zacks Rank", 3)
                
                entry_price = row.get("Last Close", 0.0)
                
                if mode == "long":
                    allowed_themes = cfg.LONG_ENTRY.get("THEMES", [])
                    min_rs = cfg.LONG_ENTRY.get("MIN_RS", 0.0)
                    min_score = cfg.LONG_ENTRY.get("MIN_LONG_SCORE", 0.0)
                    min_price = cfg.LONG_ENTRY.get("MIN_PRICE", 10.0)
                    mild_floor = cfg.LONG_ENTRY.get("MIN_DROPPED_WATCH_SCORE", 70.0)
                    basing_zacks = cfg.LONG_ENTRY.get("BASING_ZACKS", [1, 2])
                    basing_themes = cfg.LONG_ENTRY.get("BASING_THEMES", ["Leading", "Neutral"])
                    
                    if entry_price < min_price:
                        continue

                    is_strong = (score >= min_score and rs_rating >= min_rs and theme_class in allowed_themes)
                    
                    if ticker not in entries:
                        entries[ticker] = {}

                    if is_strong:
                        if ticker in drop_tracker: del drop_tracker[ticker]
                            
                        if "Strong" not in entries[ticker]:
                            entries[ticker]["Strong"] = {
                                "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                            }
                            # Optional: store full row for attribution
                            entries[ticker]["Strong"].update(row.to_dict())
                    else:
                        if "Strong" in entries[ticker] and ticker not in drop_tracker:
                            drop_tracker[ticker] = {"days_dropped": 1}
                        
                        if ticker in drop_tracker:
                            days = drop_tracker[ticker]["days_dropped"]
                            
                            if days <= 21:
                                if score >= mild_floor and rs_rating >= mild_floor:
                                    if "Mild" not in entries[ticker]:
                                        entries[ticker]["Mild"] = {
                                            "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                                        }
                                        entries[ticker]["Mild"].update(row.to_dict())
                                else:
                                    del drop_tracker[ticker]
                            elif 22 <= days <= cfg.LONG_ENTRY.get("PURGE_DAYS", 50):
                                wake_up_score = cfg.LONG_GARAGE_ENTRY.get("WAKE_UP_SCORE", 85.0)
                                if zacks_rank in basing_zacks and theme_class in basing_themes:
                                    if garage_rs >= wake_up_score:
                                        if "Garage_Wake" not in entries[ticker]:
                                            entries[ticker]["Garage_Wake"] = {
                                                "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                                            }
                                            entries[ticker]["Garage_Wake"].update(row.to_dict())
                                        del drop_tracker[ticker]
                                else:
                                    del drop_tracker[ticker]
                            elif days > cfg.LONG_ENTRY.get("PURGE_DAYS", 50):
                                del drop_tracker[ticker]
                else:
                    # mode == "short"
                    allowed_themes = cfg.SHORT_ENTRY.get("THEMES", [])
                    max_rs = cfg.SHORT_ENTRY.get("MAX_SHORT_RS", 15.0)
                    min_rs_short = cfg.SHORT_ENTRY.get("MIN_SHORT_RS", 8.0)
                    max_score = cfg.SHORT_ENTRY.get("MAX_SHORT_SCORE", 25.0)
                    min_price = cfg.SHORT_ENTRY.get("MIN_PRICE", 10.0)
                    mild_floor = cfg.SHORT_ENTRY.get("MAX_DROPPED_WATCH_SCORE", 30.0)
                    decay_zacks = cfg.SHORT_ENTRY.get("DECAY_ZACKS", [4, 5])
                    decay_themes = cfg.SHORT_ENTRY.get("DECAY_THEMES", ["Lagging"])
                    avg_vol = row.get("avg_volume", 0) or 0
                    
                    passes_liquidity = (entry_price >= min_price) and (avg_vol >= cfg.SHORT_ENTRY.get("MIN_VOLUME", 1000000))
                    if not passes_liquidity:
                        continue
                        
                    is_strong = (score <= max_score and min_rs_short <= rs_rating <= max_rs and theme_class in allowed_themes)
                    
                    if ticker not in entries:
                        entries[ticker] = {}

                    if is_strong:
                        if ticker in drop_tracker: del drop_tracker[ticker]
                        if "Strong" not in entries[ticker]:
                            entries[ticker]["Strong"] = {
                                "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                            }
                            entries[ticker]["Strong"].update(row.to_dict())
                    else:
                        if "Strong" in entries[ticker] and ticker not in drop_tracker:
                            drop_tracker[ticker] = {"days_dropped": 1}
                        
                        if ticker in drop_tracker:
                            days = drop_tracker[ticker]["days_dropped"]
                            if days <= 21:
                                if score <= mild_floor and rs_rating <= mild_floor:
                                    if "Mild" not in entries[ticker]:
                                        entries[ticker]["Mild"] = {
                                            "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                                        }
                                        entries[ticker]["Mild"].update(row.to_dict())
                                else:
                                    del drop_tracker[ticker]
                            elif 22 <= days <= cfg.SHORT_ENTRY.get("PURGE_DAYS", 50):
                                wake_up_score = cfg.SHORT_GARAGE_ENTRY.get("WAKE_UP_SCORE", 85.0)
                                if zacks_rank in decay_zacks and theme_class in decay_themes:
                                    if garage_rs >= wake_up_score:
                                        if "Garage_Wake" not in entries[ticker]:
                                            entries[ticker]["Garage_Wake"] = {
                                                "entry_date": current_date, "entry_price": entry_price, "theme_class": theme_class
                                            }
                                            entries[ticker]["Garage_Wake"].update(row.to_dict())
                                        del drop_tracker[ticker]
                                else:
                                    del drop_tracker[ticker]
                            elif days > cfg.SHORT_ENTRY.get("PURGE_DAYS", 50):
                                del drop_tracker[ticker]

        # Evaluate returns on final day
        final_date = self.all_dates[-1]
        today_prices = prices.get(final_date, {})
        results = []

        for ticker, buckets in entries.items():
            current_price = today_prices.get(ticker, 0)
            if current_price > 0:
                for bucket_type, data in buckets.items():
                    if mode == "long":
                        ret = ((current_price - data["entry_price"]) / data["entry_price"]) * 100.0
                    else:
                        ret = ((data["entry_price"] - current_price) / data["entry_price"]) * 100.0
                        
                    res_row = {
                        "Ticker": ticker,
                        "Bucket": bucket_type,
                        "Entry Date": data["entry_date"],
                        "Entry Px": data["entry_price"],
                        "Current Px": current_price,
                        "Return %": round(ret, 2),
                        "Win": "YES" if ret > 0 else "NO",
                        "Class": data["theme_class"],
                    }
                    # Merge all enriched row data
                    for k, v in data.items():
                        if k not in res_row:
                            res_row[k] = v
                    results.append(res_row)

        res_df = pd.DataFrame(results)
        return res_df

    def process(self, mode="long", silent=False):
        if self.master_matrix is None:
            if not self.load_data():
                return None
                
        # Import pipeline functions for dynamic ETF rescoring
        from pipeline.pipeline import (
            get_theme_strength_settings,
            extract_benchmark_returns,
            build_theme_strength,
            build_theme_classification,
            assign_stock_theme_classification,
            resolve_unclassified_leaders,
            map_stock_themes
        )
        from scoring.etf_engine import calculate_etf_rs, assign_theme_score
        
        # 1. Score the matrix grouped by date
        scored_dfs = []
        for d in self.all_dates:
            df_d = self.master_matrix[self.master_matrix["date"] == d].copy()
            df_etf = self.raw_etf_matrices.get(d)
            
            # --- CALCULATE BASE STOCK METRICS FIRST ---
            if mode == "long":
                cols_to_clean = list(cfg.RS_RAW_WEIGHTS.keys()) + ["Last Close", "avg_volume"]
            else:
                cols_to_clean = list(cfg.RS_RAW_WEIGHTS.keys()) + list(cfg.SHORT_RS_RAW_WEIGHTS.keys()) + ["Last Close", "avg_volume"]
                
            for c in cols_to_clean:
                if c in df_d.columns:
                    df_d[c] = pd.to_numeric(
                        df_d[c].astype(str).str.replace(r'[%$,]', '', regex=True).str.replace(r'^\((.*)\)$', r'-\1', regex=True),
                        errors='coerce'
                    ).fillna(0.0)
                    
            df_d = scoring.calculate_rs_raw(df_d)
            df_d = scoring.calculate_rs_rating(df_d)
            df_d = scoring.calculate_zacks_score(df_d)
            df_d = scoring.calculate_growth_score(df_d)
            
            # Garage specific metrics
            if mode == "long":
                df_d = scoring.calculate_long_garage_rs_raw(df_d)
                df_d = scoring.calculate_long_garage_rs_rating(df_d)
            else:
                df_d = scoring.calculate_short_garage_rs_raw(df_d)
                df_d = scoring.calculate_short_garage_rs_rating(df_d)
            
            # --- DYNAMIC ETF CLASSIFICATION ---
            if df_etf is not None and not df_etf.empty:
                theme_settings = get_theme_strength_settings()
                try: benchmark_returns = extract_benchmark_returns(df_etf, theme_settings)
                except Exception: benchmark_returns = {}
                
                df_etf = calculate_etf_rs(df_etf)
                df_etf = assign_theme_score(df_etf)
                
                theme_strength = build_theme_strength(df_etf, benchmark_returns, theme_settings)
                theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map, avg_leading_score = build_theme_classification(theme_strength)
                
                df_d = map_stock_themes(df_d)
                df_d = resolve_unclassified_leaders(df_d, theme_class_map)
                df_d = assign_stock_theme_classification(
                    df_d,
                    theme_class_map,
                    theme_score_map,
                    theme_raw_score_map,
                    avg_leading_score
                )
                
                # Overwrite obsolete lowercase dictionary mapping with capitalized generated keys
                if "Theme_Class" in df_d.columns:
                    df_d["theme_class"] = df_d["Theme_Class"]
                if "Theme_Score" in df_d.columns:
                    df_d["theme_strength_score"] = df_d["Theme_Score"]
            
            # --- COMPOSITE SCORE ---
            if mode == "long":
                lw = cfg.LONG_WEIGHTS
                rs_w = lw.get("RS_WEIGHT", 0.50)
                theme_w = lw.get("THEME_WEIGHT", 0.25)
                zacks_w = lw.get("ZACKS_WEIGHT", 0.15)
                growth_w = lw.get("GROWTH_WEIGHT", 0.10)
                
                ts = df_d["theme_strength_score"] if "theme_strength_score" in df_d.columns else 50.0
                zs = df_d["Zacks_Score"] if "Zacks_Score" in df_d.columns else 50.0
                gs = df_d["Growth_Score"] if "Growth_Score" in df_d.columns else 50.0
                
                df_d["long_score"] = (
                    df_d["RS_Rating"] * rs_w +
                    ts * theme_w +
                    zs * zacks_w +
                    gs * growth_w
                ).round(2)
            else:
                df_d = scoring.calculate_short_score(df_d)
            
            scored_dfs.append(df_d)
            
        matrix_scored = pd.concat(scored_dfs)
        
        # 2. Run tracker
        res_df = self.run_simulation(matrix_scored, mode=mode)
        
        if res_df.empty:
            if not silent: print("No trades triggered.")
            return {
                "total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                "strong_trades": 0, "strong_win_rate": 0.0, "strong_avg_return": 0.0,
                "mild_trades": 0, "mild_win_rate": 0.0, "mild_avg_return": 0.0,
                "basing_trades": 0, "basing_win_rate": 0.0, "basing_avg_return": 0.0,
                "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0,
                "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
                "_detail_df": res_df
            }
        
        def calc_bucket(df_sub):
            t = len(df_sub)
            wr = (len(df_sub[df_sub['Return %'] > 0]) / t * 100) if t > 0 else 0.0
            ar = df_sub['Return %'].mean() if t > 0 else 0.0
            return t, round(wr, 2), round(ar, 2)
            
        t_all, wr_all, ar_all = calc_bucket(res_df)
        t_str, wr_str, ar_str = calc_bucket(res_df[res_df["Bucket"] == "Strong"])
        t_mil, wr_mil, ar_mil = calc_bucket(res_df[res_df["Bucket"] == "Mild"])
        t_bas, wr_bas, ar_bas = calc_bucket(res_df[res_df["Bucket"].isin(["Basing", "Garage_Wake"])])
        
        lead_df = res_df[res_df['Class'] == 'Leading']
        neut_df = res_df[res_df['Class'] == 'Neutral']
        t_ld, wr_ld, ar_ld = calc_bucket(lead_df)
        t_nt, wr_nt, ar_nt = calc_bucket(neut_df)
        
        if not silent:
            print("\n" + "="*80)
            print(f"          TABELA 3-MONTH {mode.upper()} BACKTEST (VECTORIZED PIPELINE)")
            print("="*80)
            print(f"Total Combined Trades: {t_all} | WR: {wr_all:.1f}% | Avg: {ar_all:.2f}%")
            print(f"  [Strong Tier]  Trades: {t_str} | WR: {wr_str:.1f}% | Avg: {ar_str:.2f}%")
            print(f"  [Mild Tier]    Trades: {t_mil} | WR: {wr_mil:.1f}% | Avg: {ar_mil:.2f}%")
            print(f"  [Basing Tier]  Trades: {t_bas} | WR: {wr_bas:.1f}% | Avg: {ar_bas:.2f}%\n")
            
        return {
            "total_trades": t_all, "win_rate": wr_all, "avg_return": ar_all,
            "strong_trades": t_str, "strong_win_rate": wr_str, "strong_avg_return": ar_str,
            "mild_trades": t_mil, "mild_win_rate": wr_mil, "mild_avg_return": ar_mil,
            "basing_trades": t_bas, "basing_win_rate": wr_bas, "basing_avg_return": ar_bas,
            "leading_trades": t_ld, "leading_win_rate": wr_ld, "leading_avg_return": ar_ld,
            "neutral_trades": t_nt, "neutral_win_rate": wr_nt, "neutral_avg_return": ar_nt,
            "_detail_df": res_df,
        }

# For standalone testing
if __name__ == "__main__":
    import time
    t0 = time.time()
    engine = VectorizedBacktestEngine()
    engine.load_data()
    print(f"Data Loaded in {time.time()-t0:.2f}s")
    t1 = time.time()
    res = engine.process(silent=False)
    print(f"Processed in {time.time()-t1:.2f}s")
