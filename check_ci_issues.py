# Check CI workflow file and identify issues
import os

os.chdir('D:/Project/Fashion-Website')

# Read the CI workflow
with open('.github/workflows/ci.yml', 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find the frontend-e2e job section
print("Searching for frontend-e2e job...")
for i, line in enumerate(lines):
    if 'frontend-e2e' in line:
        print(f"Found at line {i+1}: {line.strip()}")

# Find the test job section
print("\nSearching for test job...")
for i, line in enumerate(lines):
    if 'Django Tests (Python' in line:
        print(f"Found at line {i+1}: {line.strip()}")
        # Print next 20 lines
        for j in range(i, min(i + 25, len(lines))):
            print(f"{j+1}: {lines[j]}")
        break

# Check if frontend-e2e job has Django server start
print("\nChecking for Django server start in frontend-e2e job...")
for i, line in enumerate(lines):
    if 'no server' in line.lower() or 'webServer' in line or 'runserver' in line.lower():
        print(f"Line {i+1}: {line.strip()}")
