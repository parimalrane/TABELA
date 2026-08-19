import os  
with open('formatting_test.txt', encoding='utf-8') as f:  
    print(\"\".join(f.readlines()[-40:]))  
