import os  
with open('final_regression.txt') as f:  
    lines = f.readlines()  
    try:  
        idx = lines.index(\"DISTRIBUTION WATCHLIST\n\")  
        print(\"FOUND IT!\")  
    except ValueError:  
        print(\"Title not found\")  
