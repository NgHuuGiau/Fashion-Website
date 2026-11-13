# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Do NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email us at: **security@huugiau.com**

Or use GitHub's private vulnerability reporting:
1. Go to the **Security** tab of this repository
2. Click **Report a vulnerability**
3. Fill in the details privately

### What to Include

Please provide as much detail as possible:

- **Description** of the vulnerability
- **Steps to reproduce** (if applicable)
- **Potential impact** (data exposure, RCE, auth bypass, etc.)
- **Affected versions** (if known)
- **Suggested fix** (if you have one)
- **Your contact info** for follow-up

### Response Timeline

| Severity | Initial Response | Fix Target |
|----------|------------------|------------|
| Critical | 24 hours         | 72 hours   |
| High     | 48 hours         | 1 week     |
| Medium   | 1 week           | 2 weeks    |
| Low      | 2 weeks          | Next release |

We will:
1. Acknowledge receipt within the timeline above
2. Validate and assess the vulnerability
3. Develop and test a fix
4. Release a patch
5. Credit you (if desired) in the security advisory

## Security Best Practices for Contributors

- Never commit secrets, API keys, or passwords
- Use environment variables for all sensitive configuration
- Run `bandit` and `pip-audit` before submitting PRs
- Follow OWASP Top 10 guidelines
- Keep dependencies updated (run `pip-audit` and `safety` regularly)

## Security Features in This Project

- **Authentication**: Django's built-in auth with custom user model
- **Password Security**: PBKDF2 with SHA-256, minimum 8 chars, complexity requirements
- **Session Security**: HttpOnly, Secure, SameSite cookies; CSRF protection
- **Rate Limiting**: django-ratelimit on auth endpoints
- **CORS**: Configured for specific origins only
- **SQL Injection**: Django ORM parameterized queries
- **XSS Protection**: Django template auto-escaping + CSP headers
- **Clickjacking**: X-Frame-Options middleware
- **Content Security Policy**: Configured via middleware
- **Dependency Scanning**: Automated via pip-audit, Safety
- **Static Analysis**: CodeQL, Bandit, Ruff

## Contact

For security concerns: **security@huugiau.com**

For general questions: Create a GitHub Discussion or issue (non-security)