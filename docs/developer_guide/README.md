# Developer Guide

Developer documentation for contributing to and extending Taiga MCP Bridge.

## Architecture

Understanding the codebase:

- **[Architecture Overview](architecture.md)** - System design, modules, and component interaction
- **[Auth Module](auth_module.md)** - Authentication implementation details
- **[Taiga Client](taiga_client.md)** - TaigaClientWrapper and session management

## API References

External API documentation:

- **[MCP SDK Reference](mcp_sdk_reference.md)** - Model Context Protocol Python SDK
- **[Taiga REST API Reference](taiga_rest_api_reference.md)** - Taiga API documentation
- **[API Documentation](api/index.md)** - Auto-generated API docs

## Development Setup

### Prerequisites

- Python 3.10+
- Poetry for dependency management
- Git

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp

# Install dependencies with dev tools
poetry install

# Run tests
poetry run pytest

# Run code quality checks
./scripts/quality.sh

# Run with auto-fix
./scripts/quality.sh --fix
```

## Code Quality

We use multiple tools to maintain code quality:

- **black** - Code formatting
- **isort** - Import sorting
- **ruff** - Fast linting
- **mypy** - Type checking
- **flake8** - Style checking
- **pytest** - Testing (99% coverage)

Run all checks with:

```bash
./scripts/quality.sh
```

## Project Structure

```
pytaiga-mcp/
├── pytaiga_mcp/          # Main package
│   ├── server/           # MCP server modules
│   │   ├── __init__.py
│   │   ├── common.py     # Session management
│   │   ├── auth.py       # Authentication
│   │   ├── projects.py   # Project operations
│   │   ├── user_stories.py
│   │   ├── tasks.py
│   │   ├── issues.py
│   │   ├── epics.py
│   │   ├── milestones.py
│   │   └── wiki.py
│   ├── taiga_client.py   # Taiga API wrapper
│   ├── cli.py            # Command-line interface
│   └── logging_config.py # Logging setup
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for:

- Development workflow
- Pull request process
- Code style guidelines
- Testing requirements

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pytaiga_mcp

# Run specific test markers
poetry run pytest -m "auth"
poetry run pytest -m "integration"
```

### Writing Tests

- Place unit tests in `tests/`
- Use pytest fixtures from `conftest.py`
- Mock external API calls
- Aim for >95% coverage

## Debugging

Use the MCP Inspector for debugging:

```bash
# Stdio mode
./scripts/inspect.sh

# SSE mode
./scripts/inspect.sh --transport sse --port 5001

# Debug logging
./scripts/inspect.sh --log-level DEBUG
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Run quality checks
5. Tag release: `git tag v0.x.x`
6. Push tags: `git push --tags`

## Getting Help

- Review the [Architecture Overview](architecture.md)
- Check existing tests for examples
- Open an issue for questions
- Join discussions on GitHub
