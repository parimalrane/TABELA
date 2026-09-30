import pandas as pd
from pipeline.pipeline import load_inputs, get_theme_strength_settings, calculate_etf_rs, assign_theme_score, build_theme_strength, build_theme_classification, map_stock_themes, calculate_rs_raw, calculate_rs_rating, calculate_zacks_score, calculate_growth_score, resolve_unclassified_leaders, assign_stock_theme_classification, score_stocks
from config.runtime_context import context
context.market_date = '2026-09-29'
context.stocks_file = 'market_data/input_files/2026-09/20260929_stocks.csv'
context.etf_file = 'market_data/input_files/2026-09/20260929_ETF.csv'
settings = get_theme_strength_settings()
stocks, etf, bench = load_inputs(settings)
etf = calculate_etf_rs(etf)
etf = assign_theme_score(etf)
ts = build_theme_strength(etf, bench, settings)
tc, ts_map, tr_map, trs_map, avg_ld = build_theme_classification(ts)
stocks = map_stock_themes(stocks)
stocks['Theme_Rank'] = stocks['ETF_Theme'].map(tr_map)
stocks = calculate_rs_raw(stocks)
stocks = calculate_rs_rating(stocks)
stocks = calculate_zacks_score(stocks)
stocks = calculate_growth_score(stocks)
stocks = resolve_unclassified_leaders(stocks, tc)
stocks = assign_stock_theme_classification(stocks, tc, ts_map, trs_map, avg_ld)
stocks = score_stocks(stocks)

with open('result_dump.txt', 'w') as f:
    ctva = stocks[stocks['Ticker'].str.strip() == 'CTVA']
    if not ctva.empty:
        ctva = ctva.iloc[0]
        from lifecycle.stock_transition_engine import _meets_criteria
        from config.config import DIST_ENTRY
        f.write(f"CTVA Data: {ctva[['RS_Rating', 'Long_Score', 'Short_RS_Rating', 'Short_Score', 'Theme_Class', 'Last Close', 'Avg Volume']].to_dict()}\n")
        f.write(f"Meets DIST_ENTRY? {_meets_criteria(ctva, DIST_ENTRY)}\n")
        f.write(f"DIST_ENTRY config: {DIST_ENTRY}\n")
    else:
        f.write("CTVA not found!\n")
