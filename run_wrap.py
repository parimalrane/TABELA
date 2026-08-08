import os
import subprocess
with open('verify_output.txt', 'w') as f:
    subprocess.run(['.venv\\Scripts\\python.exe', 'run_historical.py'], stdout=f, stderr=subprocess.STDOUT)
