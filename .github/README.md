# GitHub Configuration

This directory contains GitHub-specific configuration files for the Taiga MCP Bridge project.

## Structure

```
.github/
├── ISSUE_TEMPLATE/           # Issue templates
│   ├── bug_report.md        # Bug report template
│   ├── documentation.md     # Documentation issue template
│   ├── feature_request.md   # Feature request template
│   ├── question.md          # Question/help template
│   └── config.yml           # Issue template configuration
├── workflows/                # GitHub Actions workflows
│   ├── quality.yml          # Code quality checks (black, ruff, mypy, flake8)
│   ├── tests.yml            # Test suite (Python 3.10, 3.11, 3.12)
│   └── docs.yml             # Documentation deployment
└── pull_request_template.md # PR template
```

## Issue Templates

We provide four types of issue templates:

### 🐛 Bug Report (`bug_report.md`)

For reporting bugs with detailed environment information:

- Version information
- Steps to reproduce
- Expected vs actual behavior
- Configuration details

### 📚 Documentation (`documentation.md`)

For reporting documentation issues:

- Missing documentation
- Unclear explanations
- Incorrect information
- Broken links

### ✨ Feature Request (`feature_request.md`)

For suggesting new features:

- Use case description
- Proposed solution
- Benefits and priority
- Implementation notes

### ❓ Question (`question.md`)

For asking questions or getting help:

- What you're trying to do
- What you've tried
- Environment details
- Code examples

### Configuration (`config.yml`)

Provides links to:

- GitHub Discussions
- Security advisory reporting
- Full documentation

## Pull Request Template

The PR template (`pull_request_template.md`) ensures contributors provide:

- Clear description of changes
- Type of change (bug fix, feature, etc.)
- Testing performed
- Code quality checklist
- Documentation updates

## GitHub Actions Workflows

### Code Quality (`quality.yml`)

Runs on every push and PR to master/main/develop:

- **Black**: Code formatting check
- **isort**: Import sorting check
- **Ruff**: Fast linting
- **mypy**: Type checking
- **flake8**: Style checking

### Tests (`tests.yml`)

Runs comprehensive test suite:

- Tests on Python 3.10, 3.11, and 3.12
- Coverage reporting
- Uploads results to Codecov

### Documentation (`docs.yml`)

Deploys documentation to GitHub Pages:

- Triggered on docs changes or manual dispatch
- Builds with MkDocs Material
- Deploys to gh-pages branch

## Using the Templates

### For Users

When creating an issue:

1. Click "New Issue" on the GitHub repository
2. Select the appropriate template
3. Fill in the requested information
4. Remove any sections not applicable
5. Submit the issue

### For Contributors

When creating a PR:

1. The PR template will auto-populate
2. Fill in all sections
3. Check off completed items
4. Request review

### For Maintainers

**Updating Templates:**

1. Edit files in `.github/ISSUE_TEMPLATE/`
2. Test by creating a draft issue
3. Commit changes

**Managing Workflows:**

1. Edit files in `.github/workflows/`
2. Test with workflow_dispatch if available
3. Monitor Actions tab for results

## Best Practices

### Issue Creation

- Search existing issues first
- Use the most specific template
- Provide reproduction steps
- Remove sensitive information
- Be clear and concise

### Pull Requests

- Link related issues
- Keep changes focused
- Run quality checks locally first: `./scripts/quality.sh`
- Update documentation if needed
- Respond to review feedback

### Workflow Maintenance

- Keep actions up to date
- Monitor for deprecation warnings
- Test workflow changes in forks first
- Use caching for faster builds

## Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Issue Template Documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [Contributing Guide](../CONTRIBUTING.md)
