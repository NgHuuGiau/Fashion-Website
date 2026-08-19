# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CI/CD pipeline with GitHub Actions
- CodeQL security analysis
- Dependabot configuration with grouped updates
- Ruff linting and formatting
- MyPy type checking
- Bandit security scanning
- pip-audit and Safety vulnerability scanning
- Pre-commit hooks
- Issue and PR templates
- CODEOWNERS for review assignment
- Security policy
- Contributing guidelines

### Changed
- Replaced flake8/isort/black with Ruff
- Migrated test workflow to PostgreSQL (from MSSQL)
- Updated Django to 4.2 LTS / 5.0 support
- Improved test coverage requirements (70% minimum)

### Fixed
- Various linting issues resolved by Ruff
- Type annotations added across codebase
- Security vulnerabilities in dependencies addressed

## [1.0.0] - 2024-XX-XX

### Added
- Initial release of HUUGIAU Fashion Website
- Django 4.2 LTS based e-commerce platform
- Product catalog with variants (size/color)
- Shopping cart with session-based persistence
- Checkout with multiple payment methods (COD, Bank Transfer, VNPay)
- User authentication (email/phone, social login ready)
- Order management (admin + customer)
- Return/exchange workflow
- Review system with shop replies
- Loyalty points & tier system (VIP/Thân thiết/Thành viên)
- Birthday rewards & coupon system
- Gift cards
- Referral program
- Guest checkout
- Admin dashboard with analytics
- Blog/Lookbook system
- FAQ system
- Size guide
- Wishlist
- Email notifications
- Rate limiting & security middleware

### Technical Stack
- Django 4.2 LTS / 5.0
- PostgreSQL / SQL Server support
- Redis for caching & Celery
- Celery for async tasks
- Bootstrap 5 + custom CSS (CSS variables, mobile-first)
- Vanilla JS (ES6 modules)
- FontAwesome 6 icons
- Leaflet maps for address selection

---

## Release Process

1. Update version in `pyproject.toml` and `package.json`
2. Update this CHANGELOG.md
3. Create release commit: `git commit -m "chore: release vX.Y.Z"`
3. Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push: `git push origin main --tags`
5. GitHub Actions will build and deploy

---

## Release Types

| Type | Version Bump | When |
|------|--------------|------|
| Major | X.0.0 | Breaking API changes, major redesign |
| Minor | X.Y.0 | New features, backward compatible |
| Patch | X.Y.Z | Bug fixes, security patches |

---

## Links

- [GitHub Releases](https://github.com/your-org/fashion-website/releases)
- [Issues](https://github.com/your-org/fashion-website/issues)
- [Discussions](https://github.com/your-org/fashion-website/discussions)