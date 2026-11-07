import os
import subprocess

os.chdir('D:/Project/Fashion-Website')

# Stage the requirements.txt file
subprocess.run(['git', 'add', 'backend/requirements.txt'], check=True)

# Commit the changes
result = subprocess.run([
    'git', 'commit', '-m', 'fix: requirements.txt - use UTF-8 encoding for Vietnamese comments'
], capture_output=True, text=True)

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)
