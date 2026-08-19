with open("final.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, l in enumerate(lines):
        if "THEME BREADTH ANALYSIS" in l:
            for x in lines[i:i+40]:
                print(x.rstrip())
            break
