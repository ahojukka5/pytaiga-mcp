# Contributing to Taiga MCP Bridge

Thank you for your interest in contributing! We welcome contributions of all kinds: bug fixes, features, documentation improvements, and more.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/pytaiga-mcp.git
cd pytaiga-mcp
```

### 2. Set Up Development Environment

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies (including dev dependencies)
poetry install

# Or use the helper script
./scripts/install.sh
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Making Changes

1. **Write your code** following the existing code style
2. **Add tests** for new functionality in the `tests/` directory
3. **Update documentation** if you're changing behavior or adding features
4. **Run quality checks** before committing:

```bash
# Run all quality checks (formatting, linting, type checking)
./scripts/quality.sh

# Auto-fix formatting and import issues
./scripts/quality.sh --fix
```

### Running Tests

```bash
# Run all unit tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pytaiga_mcp

# Run specific test file
poetry run pytest tests/test_specific.py

# Run integration tests (requires live Taiga instance)
poetry run pytest -m integration
```

### Code Quality Standards

We use several tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast linting (replaces flake8 + pylint)
- **mypy**: Static type checking
- **flake8**: Additional style checks

All of these run automatically via `./scripts/quality.sh`.

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```
feat(auth): add support for application tokens

Add new login_with_token function that accepts application tokens
from Taiga. This provides a more secure authentication method than
username/password.

fix: resolve session timeout handling

Fixes #123
```

## Pull Request Process

### Before Submitting

1. ✅ **Run quality checks**: `./scripts/quality.sh`
2. ✅ **Run tests**: `poetry run pytest`
3. ✅ **Update documentation** if needed
4. ✅ **Write clear commit messages** following conventional commits

### Submitting Your PR

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Description of changes
   - Related issues (if any)
   - Testing performed
   - Screenshots (if UI changes)

4. **Wait for CI checks** to pass:
   - Code quality (black, isort, ruff, mypy, flake8)
   - Tests (Python 3.10, 3.11, 3.12)
   - Documentation build

5. **Respond to review feedback** if requested

### PR Guidelines

- ✅ Keep PRs focused on a single feature or fix
- ✅ Include tests for new functionality
- ✅ Update relevant documentation
- ✅ Ensure all CI checks pass
- ✅ Write clear, descriptive PR titles and descriptions
- ❌ Don't include unrelated changes
- ❌ Don't submit WIP PRs without marking them as draft

## Development Tips

### Running the Server Locally

```bash
# stdio mode (default)
poetry run python -m pytaiga_mcp.server

# SSE mode
poetry run python -m pytaiga_mcp.server --transport sse

# With helper script
./scripts/run.sh
```

### Docker Development

```bash
# Build and run with Docker
./scripts/docker.sh build
./scripts/docker.sh start

# View logs
./scripts/docker.sh logs -f
```

### Debugging

- Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging
- Use `./scripts/inspect.sh` for interactive debugging
- Check logs in `taiga_mcp.log`

## Project Structure

```
pytaiga-mcp/
├── pytaiga_mcp/          # Main package
│   ├── server/           # MCP server modules
│   │   ├── auth.py       # Authentication
│   │   ├── projects.py   # Project management
│   │   └── ...           # Other modules
│   └── taiga_client.py   # Taiga API client
├── tests/                # Test suite
│   ├── conftest.py       # Shared fixtures
│   └── test_*.py         # Test files
├── scripts/              # Helper scripts
│   ├── quality.sh        # Code quality checks
│   └── docker.sh         # Docker helpers
└── docs/                 # Documentation
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Numbered steps to reproduce the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**:
  - OS and version
  - Python version
  - Package version
  - Taiga server version (if applicable)
- **Logs**: Relevant error messages or logs

### Feature Requests

For feature requests, please include:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Any alternative approaches considered?
- **Additional context**: Screenshots, examples, etc.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions?

- 💬 **Discussions**: Use [GitHub Discussions](https://github.com/ahojukka5/pytaiga-mcp/discussions) for questions
- 🐛 **Issues**: Use [GitHub Issues](https://github.com/ahojukka5/pytaiga-mcp/issues) for bug reports
- 📖 **Documentation**: Check the [documentation](https://ahojukka5.github.io/pytaiga-mcp/) first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
