with open('docs/SYSTEM_CONTEXT.md', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('#'):
            print(line.strip())
