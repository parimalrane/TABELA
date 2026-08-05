import json
try:
    with open('market_data/stock_transition/registry.json', 'r') as f:
        reg = json.load(f)
        for t in ["EXTR", "SNDK", "MU", "ESTA", "HPE", "IQV"]:
            print(f"{t}: {reg.get(t)}")
except Exception as e:
    print(e)
