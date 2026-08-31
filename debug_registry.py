import json
import traceback

try:
    with open('market_data/stock_transition/registry.json', 'r') as f:
        reg = json.load(f)
        
    d = [k for k,v in reg.items() if v.get('tracking_state') == 'DISTRIBUTION']
    print(f"Num Distribution items in Registry: {len(d)}")
    print("Items:", d)
except Exception as e:
    traceback.print_exc()
