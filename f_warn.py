for i, l in enumerate(open('engines/stock_transition_engine.py', encoding='utf-8').read().splitlines()):
    if 'WARNING' in l:
        print(i, l)
