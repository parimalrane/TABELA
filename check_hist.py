import json  
with open('market_data/history/theme_intelligence.json') as f:  
    data = json.load(f)  
    print(\"Semiconductors History:\")  
    for p in sorted(data.get('Semiconductors', []), key=lambda x: x['date'])[-5:]:  
        print(p)  
