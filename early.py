import os  
with open('final.txt', encoding='utf-8') as f:  
    lines = f.readlines()  
    try: idx = lines.index(\"THEME BREADTH ANALYSIS\n\")  
    except ValueError: idx=0  
    for l in lines[idx:idx+25]: print(l.rstrip())  
