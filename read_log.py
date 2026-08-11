with open('market_data/daily_reports/2026-08-06.txt', encoding='utf-8') as f:
    lines = f.read().splitlines()

with open('out.txt', 'w', encoding='utf-8') as f:
    for i, l in enumerate(lines):
        if 'Software' in l or '↳' in l:
            f.write(l + '\n')
