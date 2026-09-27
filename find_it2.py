import os
import glob

search_terms = ["MARKET STATISTICS", "print_market_context_summary"]

output = []
for file in glob.glob(r"c:\TABELA\**\*.py", recursive=True):
    path = file
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except:
        try:
            with open(path, "r", encoding="utf-16") as f:
                lines = f.readlines()
        except:
            continue
            
    for i, line in enumerate(lines):
        for term in search_terms:
            if term in line:
                output.append(f"{path}:{i+1}: {line.strip()}")

with open(r"c:\TABELA\found2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
