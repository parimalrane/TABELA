import subprocess

with open(r'c:\TABELA\cartesian_out.txt', 'w', encoding='utf-8') as out:
    res = subprocess.run(['python', r'c:\TABELA\run_cartesian_short.py'], capture_output=True, text=True)
    out.write(res.stdout)
    out.write('\nSTDERR:\n')
    out.write(res.stderr)
