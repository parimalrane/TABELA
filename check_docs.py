import sys
with open('c:/TABELA/docs/SYSTEM_CONTEXT.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines[7990:8010], start=7990):
    print(f"{i}: {line.strip().encode('ascii', 'ignore').decode()}")
