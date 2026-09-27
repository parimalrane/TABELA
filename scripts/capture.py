import subprocess
import time

with open(r"c:\TABELA\out_test.txt", "w") as f:
    result = subprocess.run(["python", r"c:\TABELA\runners\main.py"], capture_output=True, text=True)
    f.write(result.stdout)
    f.write("\nERRORS:\n")
    f.write(result.stderr)
