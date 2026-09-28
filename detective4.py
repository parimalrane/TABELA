import re
with open("c:/TABELA/pipeline/pipeline.py") as f:
    lines = f.readlines()
for line in lines:
    if "THEME" in line.upper() and ("PATH" in line.upper() or "CSV" in line.upper()):
        print(line.strip())
