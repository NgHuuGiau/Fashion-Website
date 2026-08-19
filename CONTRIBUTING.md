# Contributing to HUUGIAU Fashion Website

Thank you for your interest in contributing! This document outlines the process and guidelines for contributing to this project.

## Quick Start

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/your-username/fashion-website.git
cd fashion-website

# 3. Set up development environment
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 4. Copy environment template
cp .env.example .env
# Edit .env with your local settings

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 6. Run development server
python run_local.py
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming convention:
- `feature/short-description` - New features
- `fix/short-description` - Bug fixes
- `refactor/short-description` - Code refactoring
- `perf/short-description` - Performance improvements
- `docs/short-description` - Documentation updates
- `test/short-description` - Test additions/improvements
- `ci/short-description` - CI/CD changes

### 2. Make Changes
- Follow the code style (Ruff will enforce)
- Add tests for new functionality
- Update documentation if needed
- Keep commits atomic and focused

### 3. Run Checks Locally
```bash
# Linting & formatting
ruff check backend frontend
ruff format --check backend frontend

# Type checking
cd backend && mypy . --config-file=pyproject.toml

# Security
bandit -r backend
pip-audit -r requirements.txt
safety check -r requirements.txt

# Tests
pytest -x -v --cov=. --cov-fail-under=70

# Frontend
cd frontend && npx stylelint "**/*.css" && npx eslint "**/*.js"
```

### 4. Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Longer description if needed

Fixes #123
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `docs` - Documentation
- `test` - Tests
- `ci` - CI/CD
- `chore` - Maintenance
- `security` - Security fix

Scopes: `backend`, `frontend`, `orders`, `products`, `users`, `core`, `auth`, `payment`, `ui`, `api`, `db`, `config`

Examples:
```
feat(orders): add guest checkout support
fix(payment): handle VNPay callback timeout
refactor(products): simplify variant query logic
perf(orders): add database index for order lookup
docs(api): update checkout endpoint documentation
test(orders): add tests for guest checkout flow
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
# Then create PR on GitHub
```

## Code Style

### Python (Backend)
- **Formatter**: Ruff (line length 100, double quotes)
- **Linter**: Ruff (replaces flake8, isort, black)
- **Type Checker**: MyPy (strict mode for new code)
- **Security**: Bandit, pip-audit, Safety

Key rules:
- Line length: 100 chars
- Double quotes for strings
- Type hints for all public functions
- No unused imports/variables
- No bare `except:`
- Prefer `pathlib` over `os.path`

### CSS/JS (Frontend)
- **CSS**: Stylelint with standard config + recess-order
- **JS**: ESLint with standard config
- 2-space indentation
- Double quotes

## Testing

### Running Tests
```bash
# All tests
pytest -v

# Specific test file
pytest backend/orders/tests.py -v

# Specific test class
pytest backend/orders/tests.py::RealismBatchBTests -v

# With coverage
pytest --cov=. --cov-report=term-missing --cov-fail-under=70

# Parallel execution
pytest -n auto
```

### Writing Tests
- Place tests in `tests.py` alongside the module
- Use `TestCase` classes
- Name test methods: `test_<what>_<expected>`
- Use factories for test data
- Mock external services (VNPay, email, SMS)

## Pull Request Checklist

Before submitting, ensure:

- [ ] Code passes all linting (ruff)
- [ ] Type hints added (mypy passes)
- [ ] Tests added/updated
- [ ] All tests pass (`pytest -x`)
- [ ] Coverage >= 70%
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Migrations included if schema changed
- [ ] Breaking changes documented
- [ ] Security reviewed

## Code Review Guidelines

### For Authors
- Keep PRs small and focused (< 400 lines ideal)
- Write clear PR descriptions
- Respond to feedback promptly
- Squash fixup commits before merge

### For Reviewers
- Check logic correctness
- Verify tests are comprehensive
- Check for security issues
- Verify performance impact
- Ensure documentation is updated

## Security

- **Never** commit secrets, API keys, passwords
- Use `.env` for local config (gitignored)
- Report security issues privately: security@huugiau.com
- Run security tools before PR: `bandit`, `pip-audit`, `safety`

## Getting Help

- **Questions**: GitHub Discussions
- **Bugs**: GitHub Issues (use bug template)
- **Features**: GitHub Issues (use feature template)
- **Security**: Email security@huugiau.com

## Code of Conduct

Be respectful, inclusive, and constructive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

---

**Thank you for contributing!** 🎉