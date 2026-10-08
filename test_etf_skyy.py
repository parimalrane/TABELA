import pandas as pd
df = pd.read_csv(r'C:\TABELA\market_data\input_files\2026-10\20261007_ETF.csv', encoding='utf-16')
res = ""
res += "---SPY---\n"
res += df[df['Ticker']=='SPY'].to_csv()
res += "\n---CLOUD ETHS---\n"
res += df[df['Investment Strategy'].str.contains('Cloud', na=False, case=False)].to_csv()

with open('C:\\TABELA\\etf_dump.txt', 'w') as f:
    f.write(res)
