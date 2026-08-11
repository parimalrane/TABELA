lines = open('core/pipeline.py', encoding='utf-8').read().splitlines()
for i, l in enumerate(lines):
    if 'short' in l.lower():
        print(i, l)
