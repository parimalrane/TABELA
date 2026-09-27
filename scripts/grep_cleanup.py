import os

search_terms = ["MARKET STATISTICS", "print_market_context_summary"]

for root, dirs, files in os.walk(r"c:\TABELA"):
    for file in files:
        if file.endswith(".py") or file.endswith(".bat"):
            path = os.path.join(root, file)
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
                        print(f"{path}:{i+1}: {line.strip()}")
