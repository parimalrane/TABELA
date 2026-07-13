from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


@dataclass(frozen=True)
class RuntimeContext:
    market_date: str
    etf_file: Path
    stocks_file: Path


def load_runtime_context() -> RuntimeContext:

    data_dir = Path("market_data") / "zacks_input_data"

    etf_files = list(data_dir.glob("*_ETF.csv"))
    stock_files = list(data_dir.glob("*_stocks.csv"))

    if len(etf_files) != 1:
        raise RuntimeError("Expected exactly one *_ETF.csv file.")

    if len(stock_files) != 1:
        raise RuntimeError("Expected exactly one *_stocks.csv file.")

    etf_file = etf_files[0]
    stocks_file = stock_files[0]

    etf_date = re.match(r"(\d{8})_ETF\.csv$", etf_file.name).group(1)
    stock_date = re.match(r"(\d{8})_stocks\.csv$", stocks_file.name).group(1)

    if etf_date != stock_date:
        raise RuntimeError("ETF and Stocks file dates do not match.")

    market_date = datetime.strptime(etf_date, "%Y%m%d").date()

    return RuntimeContext(
        market_date=market_date,
        etf_file=etf_file,
        stocks_file=stocks_file,
    )


context = load_runtime_context()