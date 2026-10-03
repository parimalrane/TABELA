import csv

with open(r'c:\TABELA\read_fsly_out.txt', 'w', encoding='utf-8') as out:
    with open(r'c:\TABELA\market_data\input_files\2026-10\20261002_stocks.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            if 'FSLY' in row:
                for i, h in enumerate(headers):
                    out.write(f"{h}: {row[i]}\n")
