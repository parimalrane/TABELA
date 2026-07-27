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

    etf_files = sorted(data_dir.glob("*_ETF.csv"))
    stock_files = sorted(data_dir.glob("*_stocks.csv"))

    if not etf_files:
        raise RuntimeError("No *_ETF.csv file found.")

    if not stock_files:
        raise RuntimeError("No *_stocks.csv file found.")

    etf_file = etf_files[-1]
    stocks_file = stock_files[-1]

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