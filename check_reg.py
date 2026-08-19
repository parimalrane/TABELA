import os, glob  
for f in glob.glob('market_data/stock_transition/*.json'): os.remove(f)  
