import os
import shutil

os.makedirs('c:/TABELA/scripts', exist_ok=True)
shutil.move('c:/TABELA/weekly_run.py', 'c:/TABELA/scripts/weekly_run.py')
shutil.move('c:/TABELA/engines/runtime_context.py', 'c:/TABELA/core/runtime_context.py')
shutil.move('c:/TABELA/engines/weekly_intelligence_engine.py', 'c:/TABELA/core/weekly_pipeline.py')
os.rename('c:/TABELA/engines/unknown_classification_engine.py', 'c:/TABELA/engines/unknown_classification_persistence.py')
os.rename('c:/TABELA/docs/SYSTEM_CONTECT.md', 'c:/TABELA/docs/SYSTEM_CONTEXT.md')
os.remove('c:/TABELA/engines/short_engine.py')
