with open('final_after_reentry.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for l in lines:
        if "RE-ENTRY" in l or "^" in l:
            print(l.rstrip()[:100])
