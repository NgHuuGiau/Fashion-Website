# GitHub Actions CI/CD Pipeline

## Overview
Complete CI/CD pipeline for HUUGIAU Fashion Website (Django + Vanilla JS/CSS).

## Workflows

### `ci.yml` - Main CI Pipeline
Runs on: push, PR, schedule (weekly)

**Jobs:**
| Job | Description | Timeout |
|-----|-------------|---------|
| `lint` | Ruff (lint + format check) | 10min |
| `type-check` | MyPy static analysis | 15min |
| `security` | Bandit, pip-audit, Safety | 15min |
| `codeql` | GitHub CodeQL SAST | 30min |
| `test` | Django tests (3.10/3.11/3.12 × Django 4.2/5.0) | 30min |
| `frontend-lint` | Stylelint + ESLint | 10min |
| `build` | Django system check + collectstatic | 20min |
| `dependency-review` | PR dependency scanning | 5min |
| `summary` | Aggregated status badge | 1min |

## Required Secrets
Configure in GitHub repo Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `CODECOV_TOKEN` | Codecov upload token (optional) |

## Local Development

### Install pre-commit hooks
```bash
pip install pre-commit
pre-commit install
```

### Run all hooks manually
```bash
pre-commit run --all-files
```

### Run specific checks
```bash
# Lint
ruff check backend frontend
ruff format --check backend frontend

# Type check
cd backend && mypy . --config-file=pyproject.toml

# Security
bandit -r backend
pip-audit -r requirements.txt
safety check -r requirements.txt

# Tests
cd backend && pytest -n auto --cov=. --cov-fail-under=70

# Frontend lint
cd frontend && npx stylelint "**/*.css" && npx eslint "**/*.js"
```

## Coverage Requirements
- **Minimum**: 70% overall
- **Target**: 85%+ for business logic (orders, users, products)

## Badges
Add to README.md:
```markdown
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/OWNER/REPO/actions/workflows/codeql.yml/badge.svg)
![Coverage](https://codecov.io/gh/OWNER/REPO/branch/main/graph/badge.svg)
```