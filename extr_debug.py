import pandas as pd
from core.runtime_context import context
from core.pipeline import load_inputs, get_theme_strength_settings, calculate_etf_rs, assign_theme_score, build_theme_strength, build_theme_classification, map_stock_themes, calculate_rs_raw, calculate_rs_rating, calculate_sales_score, calculate_zacks_score, score_stocks, assign_stock_theme_classification
from engines.institutional_leaders_engine import build_institutional_leaders
from engines.watchlist_engine import build_long_watchlist

theme_strength_settings = get_theme_strength_settings()
stocks, etf_df, benchmark_returns = load_inputs(theme_strength_settings)
etf_df = calculate_etf_rs(etf_df)
etf_df = assign_theme_score(etf_df)
theme_strength = build_theme_strength(etf_df, benchmark_returns, theme_strength_settings)
theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map = build_theme_classification(theme_strength)
stocks = map_stock_themes(stocks)
stocks['Theme_Rank'] = stocks['ETF_Theme'].map(theme_rank_map)
stocks = calculate_rs_raw(stocks)
stocks = calculate_rs_rating(stocks)
stocks = calculate_sales_score(stocks)
stocks = calculate_zacks_score(stocks)
stocks = assign_stock_theme_classification(stocks, theme_class_map, theme_score_map, theme_raw_score_map)
stocks = score_stocks(stocks)

lw = build_long_watchlist(stocks)
il = build_institutional_leaders(stocks)
lc = pd.concat([lw, il]).drop_duplicates(subset='Ticker')

with open("extr_debug.txt", "w") as f:
    f.write(f"EXTR in LW: {'EXTR' in set(lw['Ticker'])}\n")
    f.write(f"EXTR in IL: {'EXTR' in set(il['Ticker'])}\n")
    f.write(f"EXTR in LC: {'EXTR' in set(lc['Ticker'])}\n")
    
    extr_stock = stocks[stocks['Ticker'] == 'EXTR'][['Ticker', 'Theme_Class', 'RS_Rating', 'Long_Score']]
    f.write(extr_stock.to_string())
