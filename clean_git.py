import os

def clean_git_markers():
    directory = 'c:/TABELA/market_data/stock_universe'
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '<<<<<<< HEAD' in content:
                    lines = content.split('\n')
                    cleaned_lines = []
                    skip = False
                    for line in lines:
                        if line.startswith('<<<<<<< HEAD'):
                            skip = True
                        elif line.startswith('======='):
                            pass # Still skipping until >>>>
                        elif line.startswith('>>>>>>>'):
                            skip = False
                        elif not skip:
                            cleaned_lines.append(line)
                            
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(cleaned_lines))
                    print(f"Cleaned git markers from {file}")

if __name__ == '__main__':
    clean_git_markers()
