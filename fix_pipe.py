with open('core/pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from engines.short_scoring_engine import calculate_short_score', '')

with open('core/pipeline.py', 'w', encoding='utf-8') as f:
    f.write(text)
