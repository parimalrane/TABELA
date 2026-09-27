import re

with open(r'c:\TABELA\pipeline\pipeline.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "print_" in line or "print(" in line:
        print(f"{i}: {line.strip()}")
