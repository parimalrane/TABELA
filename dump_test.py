with open('formatting_test.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines()[-40:]:
        print(line.rstrip())
