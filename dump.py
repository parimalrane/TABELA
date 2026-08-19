with open('temp_market.txt') as f: print(\"\".join([l for l in f.readlines() if \"SPY\" in l or \"QQQ\" in l or \"IWM\" in l or \"DIA\" in l][:4]))  
