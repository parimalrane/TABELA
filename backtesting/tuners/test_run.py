import subprocess

print("Running tuner...")
try:
    result = subprocess.run(["python", "-u", "run_quarterly_in_memory_tuner.py"], 
                            capture_output=True, text=True, timeout=120)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
except subprocess.TimeoutExpired as e:
    print("TIMEOUT EXCEEDED!")
    if e.stdout:
        print("PARTIAL STDOUT:")
        if isinstance(e.stdout, bytes):
            print(e.stdout.decode('utf-8'))
        else:
            print(e.stdout)
    if e.stderr:
        print("PARTIAL STDERR:")
        if isinstance(e.stderr, bytes):
            print(e.stderr.decode('utf-8'))
        else:
            print(e.stderr)
