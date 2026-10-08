import pandas as pd
from config.runtime_context import context
from config.config import THEME_STRENGTH_CONFIG
from pipeline.pipeline import get_theme_strength_settings, load_inputs, build_theme_strength, build_theme_classification

context.market_date = '2026-10-07'
context.etf_file = r'C:\TABELA\market_data\input_files\2026-10\20261007_ETF.csv'
context.stocks_file = r'C:\TABELA\market_data\input_files\2026-10\20261007_stocks.csv'

ts = get_theme_strength_settings()
stocks, etf_df, bench = load_inputs(ts)
res = build_theme_strength(etf_df, bench, ts)
t_class, t_score, t_rank, t_raw, avg_l = build_theme_classification(res)

cc = res[res['Theme'] == 'Cloud Computing']
print("=== CLOUD COMPUTING STATS ===")
print(cc[['Theme', 'Theme_Relative_Score', 'Theme_Strength_Normalized', 'ETF_RS_Raw']].to_string())
print("Class:", t_class.get('Cloud Computing'))
print("Score:", t_score.get('Cloud Computing'))
print("Avg Leading:", avg_l)
