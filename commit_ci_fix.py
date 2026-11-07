import os
import subprocess

os.chdir('D:/Project/Fashion-Website')

# Stage changes
subprocess.run(['git', 'add', '.github/workflows/ci.yml'], check=True)

# Commit changes
result = subprocess.run([
    'git', 'commit', '-m', 'fix: CI pipeline frontend-e2e job - start Django server before running Playwright tests'
], capture_output=True, text=True)

print('Commit result:')
print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)
