import os
import glob

output = []
for file in glob.glob(r"c:\TABELA\**\*.py", recursive=True):
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except:
        try:
            with open(file, "r", encoding="utf-16") as f:
                lines = f.readlines()
        except:
            continue
            
    for i, line in enumerate(lines):
        if "def build_theme_classification" in line or "def calculate_etf_rs" in line or "def assign_theme_score" in line:
            output.append(f"{file}:{i+1}: {line.strip()}")

with open(r"c:\TABELA\found_theme.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
