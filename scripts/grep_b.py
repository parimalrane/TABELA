import os
for root, dirs, files in os.walk(r"c:\TABELA"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "def build_theme_breadth" in line:
                            print(f"{path}: {line.strip()}")
            except:
                try:
                    with open(path, "r", encoding="utf-16") as f:
                        for line in f:
                            if "def build_theme_breadth" in line:
                                print(f"{path}: {line.strip()}")
                except:
                    pass
