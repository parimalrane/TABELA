import pandas as pd

try:
    df = pd.read_csv('C:/TABELA/backtesting/tuners/quarterly_master_results.csv')
    # Let's just view all columns to ensure we get the right ones
    # print(df.columns)
    
    # Let's filter for parameters close to what they asked
    if 'MIN_LONG_SCORE' in df.columns:
        subset = df[
            (df['MIN_LONG_SCORE'] >= 60.0) & 
            (df['MIN_RS'] >= 75.0) 
        ]
        if 'Trades_Final' in subset.columns:
            print(subset[['MIN_LONG_SCORE', 'MIN_RS', 'MIN_VOLUME', 'Trades_Final', 'WinRate_Final', 'AvgReturn_Final']].head(20).to_string())
        elif 'Trades' in subset.columns:
            print(subset[['MIN_LONG_SCORE', 'MIN_RS', 'MIN_VOLUME', 'Trades', 'WinRate', 'AvgReturn']].head(20).to_string())
        else:
             print("Could not find Trades column, showing head:")
             print(subset.head().to_string())
    else:
        print("MIN_LONG_SCORE column not found. Available columns:")
        print(df.columns.tolist())
except Exception as e:
    print(f"Error accessing file: {e}")
