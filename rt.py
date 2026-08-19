import os  
with open('final_themes.txt', 'r') as f:  
    lines = f.readlines()  
    for i, line in enumerate(lines):  
        if 'Micro Theme' in line:  
            print(\"\".join(lines[i:i+5]))  
            break  
