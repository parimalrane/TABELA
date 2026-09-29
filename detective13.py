import pandas as pd

def analyze_top_movers():
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
    
    # Filter out penny stocks in July
    merged = merged[merged['Last Close_jul'] >= 5.0]
    
    # Calculate return
    merged['3_Month_Return'] = ((merged['Last Close_sep'] - merged['Last Close_jul']) / merged['Last Close_jul']) * 100
    
    # Get Top 50 Movers
    top_movers = merged.sort_values('3_Month_Return', ascending=False).head(50)
    
    print("\n" + "="*80)
    print("      ATTRIBUTION ANALYSIS: TOP 50 FASTEST MOVERS (JULY 10 -> SEPT 25)")
    print("="*80)
    
    print("\n--- BASELINE CHARACTERISTICS ON JULY 10th BEFORE THEY MOVED ---")
    
    # Analyze Momentum Characteristics
    print(f"Average 1-Week RS natively: {top_movers['% Price Change (1 Week)'].mean():.2f}%")
    print(f"Average 4-Week RS natively: {top_movers['% Price Change (4 Weeks)'].mean():.2f}%")
    print(f"Average 12-Week RS natively: {top_movers['% Price Change (12 Weeks)'].mean():.2f}%")
    print(f"Average YTD RS natively: {top_movers['Relative Price Change (YTD)'].mean():.2f}%")
    
    # Analyze Fundamental Characteristics
    zacks_counts = top_movers['Zacks Rank'].value_counts().sort_index()
    print("\nZacks Rank Distribution on July 10:")
    for rank, count in zacks_counts.items():
        print(f"Rank {rank}: {count}/50")
        
    growth_counts = top_movers['Growth Score'].value_counts().sort_index()
    print("\nGrowth Score Distribution on July 10:")
    for score, count in growth_counts.items():
        print(f"Score {score}: {count}/50")
        
    # Provide the raw dump for top 20
    print("\n--- RAW DATA FOR TOP 20 MONSTER STOCKS ON JULY 10 ---")
    cols = ['Ticker', '3_Month_Return', '% Price Change (12 Weeks)', '% Price Change (4 Weeks)', 'Zacks Rank', 'Growth Score']
    print(top_movers.head(20)[cols].to_string(index=False))

if __name__ == "__main__":
    analyze_top_movers()
