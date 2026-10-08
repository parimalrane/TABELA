import os
import sys

# Ensure root paths
base_dir = "C:/TABELA"
sys.path.append(base_dir)

import pandas as pd
from pipeline.pipeline import build_stock_master
from lifecycle.watchlist_engine import build_long_watchlist
from backtesting.backtest_engine import evaluate_long_trade
import traceback

import config.runtime_context as runtime_context

DATES = [
    "20260710", "20260713", "20260714", "20260715", "20260716", "20260717",
    "20260720", "20260721", "20260722", "20260723", "20260724", "20260727",
    "20260728", "20260729", "20260730", "20260731", "20260803", "20260804",
    "20260805", "20260806", "20260807", "20260810", "20260811", "20260812",
    "20260813", "20260814", "20260817", "20260818", "20260819", "20260820",
    "20260821", "20260824", "20260825", "20260826", "20260827", "20260828",
    "20260901", "20260902", "20260903", "20260904", "20260908", "20260909",
    "20260910", "20260911", "20260914", "20260915", "20260916", "20260917",
    "20260918", "20260921", "20260922", "20260923", "20260924", "20260925",
    "20260928", "20260929", "20260930", "20261001", "20261002", "20261005",
    "20261006", "20261007"
]

WEIGHT_SETS = {
    "LEGACY (PYPL ALLOWED)": {
        "% Price Change (4 Weeks)": 0.60,
        "% Price Change (12 Weeks)": 0.20,
        "% Price Change (1 Week)": 0.20,
        "Relative Price Change (YTD)": 0.00,
        "Price as a % of 52 Wk H-L Range": 0.00
    },
    "PROPOSED (52-WEEK/YTD ENFORCED)": {
        "% Price Change (4 Weeks)": 0.40,
        "% Price Change (12 Weeks)": 0.20,
        "% Price Change (1 Week)": 0.10,
        "Relative Price Change (YTD)": 0.10,
        "Price as a % of 52 Wk H-L Range": 0.20
    }
}

MEMORY_CACHE = {}

def load_data():
    if MEMORY_CACHE:
        return
    print("Loading 62 days of data into memory...")
    for file_date in DATES:
        try:
            stocks_df = pd.read_csv(f"{base_dir}/market_data/input_files/2026-10/{file_date}_stocks.csv", encoding='utf-8')
            etf_df = pd.read_csv(f"{base_dir}/market_data/input_files/2026-10/{file_date}_ETF.csv", encoding='utf-8')
            MEMORY_CACHE[file_date] = {"stocks": stocks_df, "etf": etf_df}
        except Exception as e:
            pass

def run_test_for_weights(name, weights):
    # Patch the config
    import config.config as cfg
    cfg.RS_RAW_WEIGHTS = weights
    
    trades = {}
    
    for file_date in DATES:
        if file_date not in MEMORY_CACHE:
            continue
            
        data = MEMORY_CACHE[file_date]
        runtime_context.ETF_DF = data["etf"]
        
        try:
            master = build_stock_master(data["stocks"], file_date)
            # Recreate strict building conditions
            long_watchlist = build_long_watchlist(master)
            # Limit to [Score: 85, RS: 90]
            valid = long_watchlist[(long_watchlist['Long_Score'] >= 85.0) & (long_watchlist['RS_Rating'] >= 90.0) & (pd.to_numeric(long_watchlist['Avg Volume'], errors='coerce') >= 1500000)]
            
            for ticker in valid['Ticker'].tolist():
                if ticker not in trades:
                    trades[ticker] = file_date
        except Exception as e:
            print(f"Error on {file_date}: {e}")

    # Evaluate all trades
    wins = 0
    losses = 0
    total_returns = []
    
    for ticker, entry_date in trades.items():
        try:
            trade_result = evaluate_long_trade(ticker, entry_date)
            ret = trade_result.get("return", 0.0)
            if ret > 0:
                wins += 1
            else:
                losses += 1
            total_returns.append(ret)
        except Exception as e:
            continue
            
    total_trades = wins + losses
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    avg_return = sum(total_returns) / len(total_returns) if total_returns else 0
    
    print(f"\n=================================")
    print(f"RESULTS: {name}")
    print(f"=================================")
    print(f"Total Unique Trades : {total_trades}")
    print(f"Win Rate            : {win_rate:.2f}%")
    print(f"Avg Return per Trade: {avg_return:.2f}%")
    
if __name__ == "__main__":
    load_data()
    for name, w in WEIGHT_SETS.items():
        run_test_for_weights(name, w)
