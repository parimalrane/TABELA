import os
import time

d = r'c:\TABELA\backtesting\results'
with open(r'c:\TABELA\mtime_out.txt', 'w') as out:
    for f in os.listdir(d):
        path = os.path.join(d, f)
        mtime = os.path.getmtime(path)
        out.write(f"{f} - {time.ctime(mtime)}\n")
