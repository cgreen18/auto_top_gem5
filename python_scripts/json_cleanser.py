
import os

for root, dirs, files, in os.walk('parsec_results'):
    for file_name in files:
        if 'config.json' in file_name:
            f_path = os.path.join(root,file_name)
            print(f'removing {file_name} ({f_path})')
            os.remove(f_path)