import subprocess
import traceback

with open("c:/TABELA/final_log.txt", "w") as f:
    try:
        result = subprocess.run(
            ["python", "c:/TABELA/backtesting/tuners/run_vectorized_tuner.py"],
            cwd="c:/TABELA",
            capture_output=True,
            text=True
        )
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
        f.write("\nRETURN CODE:\n")
        f.write(str(result.returncode))
    except Exception as e:
        f.write(traceback.format_exc())
