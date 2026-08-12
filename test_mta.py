import pandas as pd
from core.pipeline import map_stock_themes
from core.stock_mapper import map_stock_theme

print("Raw mapping:", map_stock_theme("Mining - Miscellaneous", "Basic Materials"))

df = pd.DataFrame([{
    "Ticker": "MTA",
    "Industry": "Mining - Miscellaneous",
    "Sector": "Basic Materials"
}])

out = map_stock_themes(df)
print(out[["Ticker", "Mapped_Theme", "ETF_Theme"]])
