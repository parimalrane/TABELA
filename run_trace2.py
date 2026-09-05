import io
from contextlib import redirect_stdout
from pipeline.pipeline import run_tabela_pipeline

buffer = io.StringIO()
with redirect_stdout(buffer):
    run_tabela_pipeline()

with open('c:/TABELA/MY_REPORT.txt', 'w') as f:
    f.write(buffer.getvalue())
print("DONE")
