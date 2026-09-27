import codecs
import re

with codecs.open(r"C:\TABELA\pipeline\pipeline.py", 'r', encoding='utf-16') as f:
    text = f.read()

print_calls = re.findall(r"print_[a-zA-Z_]+\(", text)
for i, line in enumerate(text.splitlines()):
    if "print_" in line:
        print(f"{i}: {line.strip()}")
