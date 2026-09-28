import pandas as pd

def check(file):
    try:
        df = pd.read_csv(file)
        pltr = df[df['Ticker'] == 'PLTR']
        if pltr.empty:
            print(f"PLTR not found in {file}")
            return
        
        row = pltr.iloc[0]
        print(f"--- DATA FOR {file} ---")
        print(f"Zacks Rank: {row.get('Zacks Rank')}")
        print(f"Growth Score: {row.get('Growth Score')}")
        print(f"Net Margin %: {row.get('Net Margin %')}")
        print(f"Sales: {row.get('Sales Growth F(0)/F(-1)')}")
        print(f"RS (12W): {row.get('% Price Change (12 Weeks)')}")
        print(f"RS (4W): {row.get('% Price Change (4 Weeks)')}")
        
    except Exception as e:
        print(f"Error: {e}")

check("c:/TABELA/market_data/input_files/2026-09/20260924_stocks.csv")
check("c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv")
