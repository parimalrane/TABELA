import sys
sys.path.append("C:/TABELA/backtesting/tuners")
sys.path.append("C:/TABELA")

from run_quarterly_in_memory_tuner import load_raw_csv_data, precalculate_stock_themes, extract_prices, compile_etf_themes, compile_stock_scores, simulate_long_baseline_gates, load_mapping_dicts

print("Loading data...")
stock_data, etf_data, all_dates = load_raw_csv_data()
stock_to_theme = precalculate_stock_themes(stock_data)
prices = extract_prices(stock_data)
etf_explicit, macro_theme = load_mapping_dicts()

p = {
    "ETF_PERIOD_WEIGHTS": {"1M": 0.4, "1W": 0.35, "3M": 0.25, "6M": 0.0, "1Y": 0.0},
    "RS_RAW_WEIGHTS": {"4W": 0.6, "12W": 0.2, "1W": 0.2, "YTD": 0.0},
    "LONG_WEIGHTS": {"RS": 0.6, "THEME": 0.2, "ZACKS": 0.1, "GROWTH": 0.1},
    "ZACKS_SCORE_MAP": {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0},
    "GROWTH_SCORE_MAP": {'A': 100.0, 'B': 95.0, 'C': 90.0, 'D': 20.0, 'F': -50.0}
}
g = {
    "MIN_RS": 75.0,
    "MIN_LONG_SCORE": 65.0,
    "MIN_DROPPED_WATCH_SCORE": 70.0,
    "MILD_DAYS": 14,
    "MIN_VOLUME": 1500000,
    "BLOCKED_ZACKS": [4, 5],
    "DEEP_RETRACE_ZACKS": [1, 2]
}

compiled_themes_by_date = compile_etf_themes(etf_data, all_dates, p["ETF_PERIOD_WEIGHTS"], "aum", etf_explicit, macro_theme)
daily_scored = compile_stock_scores(
    stock_data, all_dates, stock_to_theme, compiled_themes_by_date, 
    p["RS_RAW_WEIGHTS"], p["LONG_WEIGHTS"], p["ZACKS_SCORE_MAP"], p["GROWTH_SCORE_MAP"]
)

# the patched method returns 3 values now
wr, avg, trc = simulate_long_baseline_gates(daily_scored, prices, all_dates, g)

print("============ RESULTS ============")
print(f"Win Rate: {wr:.2f}%")
print(f"Avg Return: {avg:.2f}%")
print(f"Total Trades over 62 Days: {trc}")
print(f"Average Trades per Day: {trc / 62:.2f}")
