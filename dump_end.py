with open('final_regression.txt') as f:
    lines = f.readlines()
    for l in lines[-40:]:
        print(l.rstrip('\n'))
