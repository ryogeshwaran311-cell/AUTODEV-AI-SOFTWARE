"""
Safely replace the Authorization header block in deployment_service.py to use
the RENDER_API_KEY environment variable (falling back to the function param api_key).
"""
import re
import os
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
file_path = repo_root / 'backend' / 'services' / 'deployment_service.py'
print(f'Editing: {file_path}')

s = file_path.read_text(encoding='utf-8')

# New headers block: use environment variable RENDER_API_KEY if present, otherwise use api_key parameter
new_headers = (
    'headers = {\n'
    '            "Authorization": "Bearer " + (os.getenv("RENDER_API_KEY") or api_key),\n'
    '            "Accept": "application/json",\n'
    '            "Content-Type": "application/json"\n'
    '        }'
)

# Pattern to match the headers = { ... } block (non-greedy until the closing brace)
pattern = re.compile(r"headers\s*=\s*\{.*?\}", re.DOTALL)

if pattern.search(s):
    s2 = pattern.sub(new_headers, s, count=1)
    if s2 != s:
        file_path.write_text(s2, encoding='utf-8')
        print('Replaced headers block')
    else:
        print('No change made (replacement identical)')
else:
    raise SystemExit('Could not find headers block in file; aborting')

print('Done')
