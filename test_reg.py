import json
with open('out.txt', 'w') as out:
    with open('market_data/stock_transition/2026-08/2026-08-28_registry.json', 'r') as f:
        reg = json.load(f)

    d = [k for k,v in reg.items() if v['tracking_state'] == 'DISTRIBUTION']
    out.write(f"DIST 28th: {len(d)}\n")
    out.write(f"SAMPLE: {d[:10]}\n")

    try:
        with open('market_data/stock_transition/2026-08/2026-08-27_registry.json', 'r') as f:
            reg27 = json.load(f)
        d_27 = [k for k,v in reg27.items() if v['tracking_state'] == 'DISTRIBUTION']
        out.write(f"DIST 27th: {len(d_27)}\n")
        out.write(f"SAMPLE 27: {d_27[:10]}\n")
    except:
        pass
