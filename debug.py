import pandas as pd
from core.runtime_context import context
from core.pipeline import load_inputs, get_theme_strength_settings, calculate_etf_rs, assign_theme_score, build_theme_strength, build_theme_classification, map_stock_themes, calculate_rs_raw, calculate_rs_rating, calculate_sales_score, calculate_zacks_score, score_stocks, assign_stock_theme_classification

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

from engines.institutional_leaders_engine import build_institutional_leaders
il = build_institutional_leaders(stocks)

with open('debug_out.txt', 'w') as f:
    f.write('IL Size: ' + str(len(il)) + '\n')
    f.write(str(il['Theme_Class'].value_counts().to_dict()) + '\n')
    f.write('EXTR in IL: ' + str('EXTR' in il['Ticker'].values) + '\n')
