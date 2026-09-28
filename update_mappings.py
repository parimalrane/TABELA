import pandas as pd

updates = {
    'AOUT': 'Leisure and Entertainment',
    'CNK': 'Leisure and Entertainment',
    'IMAX': 'Leisure and Entertainment',
    'NSIT': 'IT Services',
    'CRCT': 'Connected Consumer Devices',
    'MATV': 'Specialty Materials & Paper',
    'VSTS': 'Professional Services',
    'CODI': 'Financial Services',
    'HNST': 'Consumer Staples',
    'SATL': 'Space Infrastructure',
    'AMN': 'Healthcare Services',
    'DDD': 'Industrial Automation',
    'MEOH': 'Chemicals',
    'TITN': 'Industrial Automation',
    'KEYS': 'Semiconductor Testing'
}

with open('c:/TABELA/data/stock_theme_mapping.csv', 'a', encoding='utf-8') as f:
    for ticker, theme in updates.items():
        f.write(f"\n{ticker},{theme}")

print("Added mappings.")
