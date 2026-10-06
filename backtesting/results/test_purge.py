import sys
sys.path.insert(0, "c:/TABELA")
from backtesting.vectorized_backtest import VectorizedBacktestEngine
import config.config as cfg
import pandas as pd

engine = VectorizedBacktestEngine()
engine.load_data()

# Lock in the user's new 90/85 gate for long
cfg.LONG_ENTRY["MIN_RS"] = 90.0
cfg.LONG_ENTRY["MIN_LONG_SCORE"] = 85.0

print(f"{'M_DAYS':^10} | {'P_DAYS':^10} || {'MILD TRADES':^12} | {'MILD WR':^8} || {'BASING TRADES':^14} | {'BASING WR':^10}")
print("-" * 80)

for mild_days in [10, 15, 21, 30, 40]:
    for purge_days in [30, 50, 70]:
        if purge_days <= mild_days:
            continue
            
        cfg.LONG_ENTRY["MILD_DAYS"] = mild_days
        cfg.LONG_ENTRY["PURGE_DAYS"] = purge_days
        
        bt = engine.process(mode="long", silent=True)
        
        m_t = bt["mild_trades"]
        m_wr = bt["mild_win_rate"]
        b_t = bt["basing_trades"]
        b_wr = bt["basing_win_rate"]
        
        print(f"{mild_days:^10} | {purge_days:^10} || {m_t:^12} | {m_wr:>6.1f}% || {b_t:^14} | {b_wr:>8.1f}%")
