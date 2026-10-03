import os
import sys

# overwrite print
class Logger:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'w') as f:
            f.write('')
    def write(self, msg):
        with open(self.filename, 'a') as f:
            f.write(msg)
    def flush(self):
        pass

sys.stdout = Logger(r'c:\TABELA\cart_live.txt')

import run_cartesian_short
run_cartesian_short.main()
