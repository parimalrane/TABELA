import os
with open("market_data/daily_reports/2026-08-18.txt", 'r', encoding='utf-8') as f:
    print(''.join(f.readlines()[-40:]))
