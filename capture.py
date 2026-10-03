import subprocess

with open('c:\\TABELA\\dump_out.txt', 'w', encoding='utf-8') as f:
    res = subprocess.run(['python', 'runners/main.py'], capture_output=True, text=True)
    f.write(res.stdout)
    f.write("\nSTDERR:\n")
    f.write(res.stderr)
