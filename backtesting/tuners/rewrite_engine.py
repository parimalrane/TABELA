import sys
import copy

with open("c:/TABELA/backtesting/backtest_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

# I will use multi_replace_file_content natively since the edit fits within 3-4 chunks cleanly. Wait, the Python approach is safer because I don't want cortex step errors.
