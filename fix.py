content = open('engines/presentation_engine.py', encoding='utf-8').read()  
new_lines = []  
for i, line in enumerate(content.split('\n')):  
    if 429 <= i <= 474:   
        if line.startswith('    ') and not line.startswith('        '):  
            new_lines.append(line)  
        elif line.startswith('        '):  
            new_lines.append(line[4:])  
        else:  
            new_lines.append(line)  
    else:  
        new_lines.append(line)  
open('engines/presentation_engine.py', 'w', encoding='utf-8').write('\n'.join(new_lines))  
