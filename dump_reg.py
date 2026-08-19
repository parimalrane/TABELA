with open('reg_out.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines()[-40:]:
        print(line.rstrip())
