import pytest
import sys

with open("pytest_output.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    pytest.main(["tests/test_ticker_disappearance.py", "-v"])
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

with open("pytest_output.txt", "r") as f:
    r = f.read()

with open("pytest_success.txt", "w") as f:
    f.write(r)
