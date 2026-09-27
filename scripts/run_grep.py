import subprocess
with open(r"c:\TABELA\out.txt", "w") as f:
    subprocess.run(["python", r"c:\TABELA\scripts\grep.py"], stdout=f)
