import sys
import traceback

with open("c:/TABELA/execution.log", "w") as f:
    sys.stdout = f
    sys.stderr = f
    try:
        sys.path.append('c:/TABELA')
        import backtesting.tuners.run_vectorized_tuner as rvt
        rvt.main()
    except Exception as e:
        f.write(traceback.format_exc())
