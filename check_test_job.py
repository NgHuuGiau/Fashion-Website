# Analyze CI workflow and identify test job configuration
# The test job is failing for 4 Python versions
# We need to check what's happening

import os

os.chdir('D:/Project/Fashion-Website')

# Read the CI workflow
with open('.github/workflows/ci.yml', 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find the test job section
start_idx = None
for i, line in enumerate(lines):
    if 'name: Django Tests (Python' in line:
        start_idx = i
        break

if start_idx:
    print("Test job section:")
    for i in range(start_idx, min(start_idx + 30, len(lines))):
        print(f"{i+1}: {lines[i]}")
else:
    print("Test job not found")
