import pandas as pd

def profile_monsters():
    try:
        # Load July 10th and Sept 25th data
        july_df = pd.read_csv('c:/TABELA/market_data/input_files/2026-07/20260710_stocks.csv')
        sept_df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv')
        
        july_df["Ticker"] = july_df["Ticker"].str.strip()
        sept_df["Ticker"] = sept_df["Ticker"].str.strip()
        
        # Merge on Ticker
        merged = pd.merge(
            july_df, 
            sept_df[['Ticker', 'Last Close']], 
            on='Ticker', 
            suffixes=('_jul', '_sep')
        )
        
        # Filter out thin/penny stocks in July
        merged = merged[merged['Last Close_jul'] >= 8.0]
        
        # Calculate return
        merged['Return'] = ((merged['Last Close_sep'] - merged['Last Close_jul']) / merged['Last Close_jul']) * 100
        
        # Isolate TOP 30 Monsters
        monsters = merged.sort_values('Return', ascending=False).head(30)
        
        res = {
            "Total Sample": len(monsters),
            "Avg_Return": monsters['Return'].mean(),
            "Avg_Price_Jul": monsters['Last Close_jul'].mean(),
            "1_Wk_Momentum": monsters.get('% Price Change (1 Week)', pd.Series()).mean(),
            "4_Wk_Momentum": monsters.get('% Price Change (4 Weeks)', pd.Series()).mean(),
            "12_Wk_Momentum": monsters.get('% Price Change (12 Weeks)', pd.Series()).mean(),
            "YTD_Momentum": monsters.get('Relative Price Change (YTD)', pd.Series()).mean(),
            "52_Wk_Range_Pos": monsters.get('Price as a % of 52 Wk H-L Range', pd.Series()).mean(),
        }
        
        print("\nTHE MONSTER PROFILE (July 10 -> Sept 25)")
        print("="*50)
        print(f"Sample Size: {res['Total Sample']} Stocks")
        print(f"Average Return: {res['Avg_Return']:.1f}%\n")
        
        print("CHARACTERISTICS ON THE DAY THEY STARTED RUNNING (July 10):")
        print(f"1-Week Relative Strength:  {res['1_Wk_Momentum']:.2f}%")
        print(f"4-Week Relative Strength:  {res['4_Wk_Momentum']:.2f}%")
        print(f"12-Week Relative Strength: {res['12_Wk_Momentum']:.2f}%")
        print(f"YTD Relative Strength:     {res['YTD_Momentum']:.2f}%")
        print(f"Distance to 52w High:      {res['52_Wk_Range_Pos']:.1f}%\n")
        
        print("ZACKS RANK DISTRIBUTION:")
        if 'Zacks Rank' in monsters:
            print(monsters['Zacks Rank'].value_counts().sort_index().to_string())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    profile_monsters()
