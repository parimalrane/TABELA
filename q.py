import pandas as pd  
from core.pipeline import run_tabela_pipeline  
_, _, _, _, _, _, _, _, theme_performance, _ = run_tabela_pipeline()  
print(\"\n\nENGINE OUTPUT:\")  
row = theme_performance[theme_performance['Theme']=='Semiconductors']  
print(row.to_string())  
