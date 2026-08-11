import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "stock_theme_mapping.csv"

mapping_df = pd.read_csv(CSV_PATH)

# Duplicate protection
duplicates = mapping_df[mapping_df["Ticker"].duplicated()]

if not duplicates.empty:
    duplicate_list = duplicates["Ticker"].tolist()
    raise ValueError(
        f"Duplicate tickers found in stock_theme_mapping.csv: {duplicate_list}"
    )

COMPANY_THEME = dict(
    zip(
        mapping_df["Ticker"].str.strip(),
        mapping_df["Theme"].str.strip()
    )
)