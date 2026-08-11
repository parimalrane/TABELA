for i, l in enumerate(open('core/pipeline.py', encoding='utf-8').read().splitlines()):
    if 'breadth' in l.lower():
        print(i, l)
