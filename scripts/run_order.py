import subprocess
with open(r"c:\TABELA\out_order.txt", "w") as f:
    subprocess.run(["python", r"c:\TABELA\scripts\order.py"], stdout=f)
