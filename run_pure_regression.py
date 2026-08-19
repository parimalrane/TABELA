import os
import glob
from pathlib import Path
from core.pipeline import run_tabela_pipeline
import core.runtime_context as rc
from unittest.mock import patch

input_dir = Path("market_data/input_files")
etf_files = sorted(input_dir.glob("*_ETF.csv"))

print("Running pure regression...")

for etf_file in etf_files:
    date_str = etf_file.stem.split("_")[0]
    stocks_file = input_dir / f"{date_str}_stocks.csv"
    market_file = input_dir / f"{date_str}_Market.csv"
    
    if not stocks_file.exists() or not market_file.exists():
        continue
        
    date_obj = __import__('datetime').datetime.strptime(date_str, "%Y%m%d").date()
    
    ctx = rc.RuntimeContext(
        market_date=date_obj,
        etf_file=etf_file,
        stocks_file=stocks_file,
        market_file=market_file
    )
    
    with patch('core.runtime_context.context', ctx):
        # We also need to patch load_runtime_context if it's called
        with patch('core.runtime_context.load_runtime_context', return_value=ctx):
            with patch('core.pipeline.context', ctx):
                with patch('engines.stock_transition_engine.context', ctx):
                    try:
                        run_tabela_pipeline()
                    except Exception as e:
                        pass

print("Regression done.")
