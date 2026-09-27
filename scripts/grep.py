import re

with open(r'c:\TABELA\reporting\presentation_engine.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "THEME BREADTH" in line:
        print(f"{i}: {line.strip()}")
