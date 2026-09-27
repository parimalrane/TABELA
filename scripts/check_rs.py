import os
import glob

output = []
for file in glob.glob(r"c:\TABELA\**\*.py", recursive=True):
    path = file
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
        if "RS_Rating ==" in line or "RS_Rating.isin" in line:
            output.append(f"{path}:{i+1}: {line.strip()}")

with open(r"c:\TABELA\scripts\check_rs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
