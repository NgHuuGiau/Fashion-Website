# Pull Request Template

## Description
<!-- Provide a clear and concise description of what this PR does -->

## Type of Change
<!-- Check all that apply -->
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] ♻️ Refactoring
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration/Environment
- [ ] 🧪 Tests
- [ ] 🚀 CI/CD
- [ ] 🔒 Security
- [ ] ⚡ Performance
- [ ] ♿ Accessibility

## Related Issues
<!-- Link related issues using keywords like "Fixes #123", "Closes #456", "Related to #789" -->
- Fixes #
- Related to #

## Changes Made
<!-- List the key changes in this PR -->
-
-
-

## Testing
<!-- Describe how you tested these changes -->
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done (describe below)
- [ ] No regression in existing functionality

### Manual Testing Steps
1.
2.
3.

## Screenshots / Recordings
<!-- Add screenshots or recordings for UI changes -->
| Before | After |
|--------|-------|
|        |       |

## Checklist
<!-- Ensure all items are checked before requesting review -->
- [ ] Code follows project style guidelines (ruff, black, isort)
- [ ] Type hints added where applicable (mypy passes)
- [ ] Tests added/updated for new functionality
- [ ] All existing tests pass (`pytest -x`)
- [ ] Coverage maintained or improved (>= 70%)
- [ ] Documentation updated (docstrings, README, CHANGELOG)
- [ ] No hardcoded secrets or sensitive data
- [ ] Database migrations included (if schema changed)
- [ ] Backward compatibility maintained (or breaking changes documented)
- [ ] Security implications considered (no XSS, SQL injection, etc.)

## Breaking Changes
<!-- List any breaking changes and migration steps -->
- None / Describe breaking changes:

## Deployment Notes
<!-- Any special deployment considerations -->
- No special steps required / Steps:

## Additional Context
<!-- Any other information, configuration, or context -->
- Related PRs:
- External references:
- Performance impact:

---

## For Reviewers
- [ ] Code logic correct
- [ ] Tests comprehensive
- [ ] Security reviewed
- [ ] Performance acceptable
- [ ] Documentation sufficient
- [ ] Ready to merge