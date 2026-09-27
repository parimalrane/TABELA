import pandas as pd

try:
    df = pd.read_csv("c:\\TABELA\\market_data\\input_files\\2026-09\\20260925_ETF.csv", encoding='utf-8')
    # find unique themes
    print("Columns:", df.columns)
    # The pipeline.py groups by "Theme". But wait, where does 'Theme' come from in the ETF file?
except Exception as e:
    print(e)
