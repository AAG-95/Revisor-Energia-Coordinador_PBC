import os
import re

def find_imports_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
    return imports

def find_imports_in_workspace(workspace_path):
    all_imports = set()
    for root, _, files in os.walk(workspace_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                imports = find_imports_in_file(file_path)
                all_imports.update(imports)
    return sorted(all_imports)

workspace_path = 'C:\\Github Revisor Energía'  # Update this path to your workspace path
libraries_used = find_imports_in_workspace(workspace_path)

print("Libraries used in the workspace:")
for lib in libraries_used:
    print(lib)