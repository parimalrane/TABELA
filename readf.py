import os  
with open('final.txt','r') as f:  
    for line in f:  
        if 'QQQ' in line or 'IWM' in line or 'SPY' in line or 'DIA' in line: print(line.strip('\n'))  
