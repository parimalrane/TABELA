import re

with open(r'c:\TABELA\reporting\presentation_engine.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "display_cols" in line or "df[" in line:
        print(f"{i}: {line.strip()}")
