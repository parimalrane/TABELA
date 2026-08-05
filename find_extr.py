import os

with open('extr_out.log', 'w', encoding='utf-8') as out:
    for root, _, files in os.walk('market_data/daily_reports'):
        for f in sorted(files):
            if not f.endswith('.txt'): continue
            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                for i, l in enumerate(lines):
                    if 'EXTR' in l:
                        out.write(f'{f}:{i} -> {l}')
