import os
import shutil

target = r"C:\TABELA\backtesting\results"
trash = r"C:\TABELA\trash"
os.makedirs(trash, exist_ok=True)

try:
    for f in os.listdir(target):
        try:
            shutil.move(os.path.join(target, f), os.path.join(trash, f))
            print(f"Moved {f}")
        except Exception as e:
            pass
    shutil.move(target, os.path.join(trash, "results_removed"))
except:
    pass

target2 = r"C:\TABELA\backtesting\tuners"
for f in os.listdir(target2):
    if f in ['debug_load.txt', 'phase1_short_test_output.csv', 'phase1_test_output.csv', 'rewrite_engine.py', 'run.bat', 'run_cartesian_long.py', 'run_cartesian_short.py', 'run_quarterly_tuner.py', 'run_tuner.py', 'run_tuner_short_v2.py', 'run_vectorized_garage_tuner.py', 'run_vectorized_short_tuner.py', 'run_vectorized_tuner.py', 'test_run.py']:
        try:
            shutil.move(os.path.join(target2, f), os.path.join(trash, f))
        except:
            pass
