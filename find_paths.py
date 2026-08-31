import os
with open("paths.txt", "w") as f:
    for root, dirs, files in os.walk("c:/TABELA/market_data"):
        for file in files:
            if "registry" in file.lower():
                f.write(os.path.join(root, file) + "\n")
