import pandas as pd

df = pd.read_csv('C:/TABELA/backtesting/tuners/quarterly_short_master_results.csv')

print("\n--- HIGH QUALITY (< 150 TRADES) ---")
print(df[df['Trades_Final'] <= 150][['WinRate_Final', 'AvgReturn_Final', 'Trades_Final', 'MAX_SHORT_RS', 'MIN_SHORT_RS', 'MAX_SHORT_SCORE']].head(10).to_string())

print("\n--- ULTRA HIGH QUALITY (< 60 TRADES) ---")
print(df[df['Trades_Final'] <= 60][['WinRate_Final', 'AvgReturn_Final', 'Trades_Final', 'MAX_SHORT_RS', 'MIN_SHORT_RS', 'MAX_SHORT_SCORE']].head(10).to_string())
