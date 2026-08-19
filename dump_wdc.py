import pandas as pd
for date in ['20260806', '20260807', '20260810', '20260811']:
    df = pd.read_csv(f'market_data/input_files/{date}_stocks.csv')
    row = df[df['Ticker']=='WDC'][['Ticker', 'RS_Rating', 'Long_Score', 'Theme_Class']]
    print(date, "\n", row.to_string())
