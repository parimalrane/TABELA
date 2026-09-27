import re

with open(r'c:\TABELA\pipeline\pipeline.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

for i, line in enumerate(lines[:500]):
    if "aum" in line.lower() or "market cap" in line.lower() or "asset" in line.lower():
        print(f"{i}: {line.strip()}")
