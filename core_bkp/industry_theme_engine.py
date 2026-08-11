import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "industry_theme_mapping.csv"
REQUIRED_COLUMNS = ["Industry", "Theme", "Confidence", "Last_Reviewed"]

mapping_df = pd.read_csv(CSV_PATH)

missing_columns = [c for c in REQUIRED_COLUMNS if c not in mapping_df.columns]
if missing_columns:
    raise ValueError(
        f"Missing required columns in industry_theme_mapping.csv: {missing_columns}"
    )

mapping_df["Industry_Key"] = mapping_df["Industry"].astype(str).str.strip().str.lower()

duplicates = mapping_df[mapping_df["Industry_Key"].duplicated()]
if not duplicates.empty:
    duplicate_list = duplicates["Industry"].tolist()
    raise ValueError(
        f"Duplicate industries found in industry_theme_mapping.csv: {duplicate_list}"
    )

INDUSTRY_THEME = dict(
    zip(
        mapping_df["Industry_Key"],
        mapping_df["Theme"].astype(str).str.strip(),
    )
)
