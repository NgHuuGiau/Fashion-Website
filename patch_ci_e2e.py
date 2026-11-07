# Frontend E2E Job Fix
# The CI workflow's frontend-e2e job was failing because:
# 1. Django server was not started before running Playwright tests
# 2. The test commands were run without proper environment setup

# This script applies the fix to the CI workflow file

import os
import subprocess

os.chdir('D:/Project/Fashion-Website')

# Read the original CI workflow
with open('.github/workflows/ci.yml', 'r') as f:
    content = f.read()

print("Original CI workflow length:", len(content))

# Find the frontend-e2e job section
start = content.find('  frontend-e2e:')
if start == -1:
    print("ERROR: frontend-e2e job not found")
    exit(1)

end = content.find('  build:', start)
if end == -1:
    print("ERROR: build job not found")
    exit(1)

# The original frontend-e2e job
original = content[start:end]
print("\nOriginal frontend-e2e job:")
print(original)

# Create the fixed frontend-e2e job
fixed_job = '''  frontend-e2e:
    name: Frontend E2E (Playwright)
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci --no-audit --no-fund

      - name: Set up Python and install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y python3 python3-pip unixodbc-dev
          python3 -m venv venv
          source venv/bin/activate
          pip install --upgrade pip
          pip install -r backend/requirements-dev.txt
          pip install "Django==5.2.*"
          python manage.py migrate --noinput

      - name: Run Django server in background
        run: |
          source venv/bin/activate
          cd backend
          nohup python manage.py runserver 127.0.0.1:8000 --noreload > /tmp/django_server.log 2>&1 &
          echo "Django server started with PID $!"

      - name: Wait for Django server
        run: |
          for i in {1..30}; do
            if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
              echo "Django server is ready"
              break
            fi
            sleep 1
          done
          curl -s http://127.0.0.1:8000/ || { echo "::error::Django server not ready"; exit 1; }

      - name: Run Playwright E2E tests
        env:
          BASE_URL: http://127.0.0.1:8000
        run: |
          cd frontend
          npx playwright test --project=chromium --project="Mobile Chrome" --workers=1 --timeout=300000

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: |
            frontend/playwright-report/
            frontend/test-results/
          retention-days: 7

'''

# Replace the frontend-e2e job with the fixed version
new_content = content[:start] + fixed_job + content[end:]

print("\nFixed frontend-e2e job:")
print(new_content[start:start+len(fixed_job)])

# Write the new content back
with open('.github/workflows/ci.yml', 'w') as f:
    f.write(new_content)

print("\nCI workflow updated successfully")
