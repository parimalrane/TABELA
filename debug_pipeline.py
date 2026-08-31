import pandas as pd
from config.runtime_context import context
from pipeline.pipeline import score_stocks, build_candidates
import warnings
warnings.filterwarnings('ignore')

from market_data_engine.etf_processor import process_etfs
from themes.company_theme_engine import map_raw_industries_to_themes
from themes.theme_mapping_config import THEME_TRANSLATION, normalize_theme

# Load stocks for Aug 28th
date = "2026-08-28"
# Let's recreate pipeline manually to see where DAL drops out
etf = pd.read_csv(f"market_data/etf_universe/2026-08/{date}.csv")
import json
with open('market_data/stock_transition/registry/2026-08-28_registry.json', 'r') as f:
    reg = json.load(f)

print("DIST IN REGISTRY:", [k for k,v in reg.items() if v['tracking_state'] == 'DISTRIBUTION'])

stocks = pd.read_csv(f"market_data/stock_universe/2026-08/{date}.csv")
from config.config import DIST_ENTRY
dal = stocks[stocks['Ticker'] == 'DAL']
print("DAL in raw:", len(dal))
if len(dal) > 0:
    for c in ['Ticker', 'Industry', 'Sector', 'RS_Rating', 'Long_Score', 'Theme_Class']:
        if c in dal.columns:
            print(f"{c}: {dal[c].iloc[0]}")
