import re

with open(r'c:\TABELA\pipeline\pipeline.py', 'r', encoding='utf-16') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith('def '):
        print(f"{i}: {line.strip()}")
