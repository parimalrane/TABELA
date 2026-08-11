import pandas as pd
from core.theme_translation_engine import THEME_TRANSLATION

df = pd.DataFrame(list(THEME_TRANSLATION.items()), columns=['Narrative_Theme', 'Benchmark_ETF_Theme'])
df.to_csv('data/macro_theme_mapping.csv', index=False)
print("CSV DUMPED")
