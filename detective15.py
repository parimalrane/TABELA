import pandas as pd
df = pd.DataFrame(columns=["Sector"])
if "Sector" in df.columns:
    df["Sector (SPDR)"] = df["Sector"].map({"A": "B"})
    df["Sector Rank"] = df["Sector (SPDR)"].map({"B": 1})
print(df.columns)
df[["Sector (SPDR)", "Sector Rank"]]
