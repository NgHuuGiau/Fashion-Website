import os
os.chdir('D:/Project/Fashion-Website')

ci_content = """name: CI Pipeline

on:
  push:
    branches: [main, develop]
    paths-ignore:
      - '*.md'
      - '.gitignore'
      - 'docs/**'
  pull_request:
    branches: [main, develop]
    paths-ignore:
      - '*.md'
      - '.gitignore'
      - 'docs/**'
  schedule:
    - cron: "0 3 * * 1"  # Weekly Monday 3AM

permissions:
  contents: read
  security-events: write
  pull-requests: write

env:
  PYTHON_VERSION: '3.12'
  DJANGO_SETTINGS_MODULE: 'core.settings'
  DEBUG: 'True'
  SECRET_KEY: 'ci-test-only-not-for-production-7gH4bY9mP2kR8xV6sT1qW3cN5dF0aLZp'
  ALLOWED_HOSTS: 'localhost,127.0.0.1,testserver'
  EMAIL_BACKEND: 'django.core.mail.backends.locmem.EmailBackend'
  EMAIL_HOST: 'localhost'
  DB_ENGINE: 'postgres'
  DB_NAME: 'test_fashion'
  DB_HOST: 'localhost'
  DB_PORT: '5432'
  DB_USER: 'test'
  DB_PASSWORD: 'test'

jobs:
  lint:
    name: Lint (Ruff)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install Ruff
        run: pip install \"ruff>=0.6\"

      - name: Run Ruff check
        run: |
          cd backend && ruff check . --output-format=github
        continue-on-error: false

      - name: Run Ruff format check
        run: |
          cd backend && ruff format --check .
        continue-on-error: false

      - name: Check production readiness script
        run: |
          ruff check scripts/verify_prod.py scripts/test_verify_prod.py
          ruff format --check scripts/verify_prod.py scripts/test_verify_prod.py
          python -m unittest scripts.test_verify_prod

  type-check:
    name: Type Check (mypy)
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y unixodbc-dev

      - name: Install dependencies (from lock file)
        run: |
          python -m pip install --upgrade pip
          pip install uv
          uv pip install -r backend/requirements.lock.txt -r backend/requirements-dev.txt

      - name: Run mypy
        run: |
          cd backend && mypy \\
            core/settings.py core/text_utils.py core/ratelimit.py \\
            products/constants.py products/validators.py \\
            orders/constants.py orders/vnpay.py users/activity.py \\
            orders/momo.py orders/shopeepay.py orders/zalopay.py \\
            orders/services/checkout.py \\
            --config-file=pyproject.toml --ignore-missing-imports --follow-imports=silent
        continue-on-error: false

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    timeout-minutes: 15
    continue-on-error: false
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y unixodbc-dev

      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install bandit==1.7.8 pip-audit==2.7.0

      - name: Run Bandit (SAST)
        run: |
          bandit -r backend -c backend/pyproject.toml -ll
          bandit -r backend -c backend/pyproject.toml -ll -f json -o bandit-results.json

      - name: Run pip-audit (deps vulnerabilities)
        run: |
          pip-audit -r backend/requirements.txt -f json -o pip-audit-results.json

      - name: Upload security artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-results
          path: |
            bandit-results.json
            pip-audit-results.json
          retention-days: 14
"""

with open('.github/workflows/ci.yml', 'w') as f:
    f.write(ci_content)
print('Part 1 written')