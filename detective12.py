import pandas as pd
df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv')
from pipeline.pipeline import get_theme_strength_settings, load_inputs, build_theme_strength, build_theme_classification, map_stock_themes, resolve_unclassified_leaders, assign_stock_theme_classification
from scoring.scoring_engine import calculate_rs_raw, calculate_rs_rating, calculate_zacks_score, calculate_growth_score
from scoring.long_scoring_engine import calculate_long_score

settings = get_theme_strength_settings()
stocks, etf, bench = load_inputs(settings)
from scoring.rotation_engine import calculate_etf_rs, assign_theme_score
etf = calculate_etf_rs(etf)
etf = assign_theme_score(etf)
theme_strength = build_theme_strength(etf, bench, settings)
tc, ts, tr, trs = build_theme_classification(theme_strength)
stocks = map_stock_themes(stocks)
stocks = calculate_rs_raw(stocks)
stocks = calculate_rs_rating(stocks)
stocks = calculate_zacks_score(stocks)
stocks = calculate_growth_score(stocks)
stocks = resolve_unclassified_leaders(stocks, tc)
stocks = assign_stock_theme_classification(stocks, tc, ts, trs)
stocks = calculate_long_score(stocks)

print("EQNR Score:", stocks[stocks['Ticker'] == 'EQNR'][['Long_Score', 'Theme_Score']])
print("BE Score:", stocks[stocks['Ticker'] == 'BE'][['Long_Score', 'Theme_Score']])
