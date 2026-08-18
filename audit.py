import pandas as pd  
df = pd.read_csv('market_data/input_files/20260814_Market.csv')  
print(f\"{'ETF':<5} | {'1D %':<7} | {'Vol':<10} | {'Avg 20D vol':<12} | {'State'}\")  
print(\"-\" * 55)  
for _, r in df.iterrows():  
    r1d = r['1D Perf %']; vol = r['Volume']; avg = r['20D Avg Vol']  
    if r1d > 1.0 and vol > avg: state = \"Accumulation\"  
    elif -0.5 <= r1d <= 0.5 and vol < avg * 0.70: state = \"Consolidation\"  
    elif r1d < -1.0 and vol < avg: state = \"Distribution\"  
    else: state = \"Neutral\"  
    print(f\"{r['ETF']:<5} | {r1d:<7} | {vol:<10} | {avg:<12} | {state}\")  
