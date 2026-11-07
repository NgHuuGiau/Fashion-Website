import os
import subprocess

os.chdir('D:/Project/Fashion-Website')

# Add files
subprocess.run(['git', 'add', '.github/workflows/ci.yml', 'backend/requirements.txt', 'backend/requirements-dev.txt'], check=True)

# Commit
result = subprocess.run([
    'git', 'commit', '-m', 'fix: CI pipeline - fix Django tests, frontend-e2e, security scan, type check'
], capture_output=True, text=True)

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)

# Push
if result.returncode == 0:
    push_result = subprocess.run(['git', 'push', 'origin', 'master:main'], capture_output=True, text=True)
    print('Push STDOUT:', push_result.stdout)
    print('Push STDERR:', push_result.stderr)
    print('Push return code:', push_result.returncode)