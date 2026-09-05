import traceback
from pipeline.pipeline import run_tabela_pipeline

try:
    run_tabela_pipeline()
    print("SUCCESS")
except Exception as e:
    with open('error_out.txt', 'w') as f:
        f.write(traceback.format_exc())
