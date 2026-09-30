import pandas as pd
df25 = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv', encoding='utf-8')
df28 = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260928_stocks.csv', encoding='utf-8')

cols_to_print = ['Ticker', 'Zacks Rank', 'Growth Score', 'Sector', 'Industry']

print("=== 25th ===")
print(df25[df25['Ticker'] == 'OKTA'][cols_to_print].to_dict('records'))

print("=== 28th ===")
print(df28[df28['Ticker'] == 'OKTA'][cols_to_print].to_dict('records'))
