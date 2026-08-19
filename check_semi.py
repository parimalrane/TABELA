import sys

def check():
    with open('final_output.txt', 'r') as f:
        for line in f:
            if 'Semiconductors' in line and 'Memory' in line:
                print(line.strip())
                return
check()
