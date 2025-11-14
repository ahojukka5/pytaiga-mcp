# Installation Guide

This guide walks you through installing Taiga MCP Bridge on your system.

## Prerequisites

Before installing, ensure you have:

- **Python 3.10 or higher**
- **Poetry** for dependency management
- **Git** for cloning the repository
- Access to a **Taiga instance** (cloud or self-hosted)

## Installation Methods

### Method 1: Poetry (Recommended)

Poetry is the recommended package manager for development and production installations.

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Method 2: pip (Standard)

Standard pip installation for simple deployments.

```bash
# Clone the repository
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Verify Installation

After installation, verify everything is working:

```bash
# Check Python version
python --version  # Should be 3.10+

# Run tests
poetry run pytest  # or: pytest

# Check type hints
poetry run mypy src/  # or: mypy src/
```

You should see:

- ✅ All tests passing (285 tests)
- ✅ Type checking successful (0 errors)
- ✅ 85%+ test coverage

## Environment Setup

### Optional: Configure Logging

Create a `logs/` directory for log files:

```bash
mkdir -p logs
```

The logging configuration in `logging.yaml` will automatically create rotating log files.

### Optional: Configure Rate Limiting

By default, the server allows 100 requests per minute per session. To customize:

```python
from src.server.rate_limiter import configure_rate_limit

# Allow 200 requests per minute
configure_rate_limit(200)
```

## IDE Integration

### VS Code

Add to your `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "taiga": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pytaiga-mcp",
      "env": {
        "PYTHONPATH": "/path/to/pytaiga-mcp"
      }
    }
  }
}
```

## Docker Setup (Optional)

For containerized deployments:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ src/

# Install dependencies
RUN poetry install --no-dev

# Run the server
CMD ["poetry", "run", "python", "-m", "src.server"]
```

Build and run:

```bash
docker build -t taiga-mcp .
docker run -p 8000:8000 taiga-mcp
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or reinstall in editable mode
poetry install
```

### Poetry Lock Issues

If `poetry install` fails:

```bash
# Update lock file
poetry lock --no-update

# Install again
poetry install
```

### Type Checking Errors

If mypy reports errors:

```bash
# Update mypy
poetry add --group dev mypy

# Clear cache
mypy --clear-cache src/
```

## Next Steps

- ✅ Installation complete!
- 📖 Continue to [Quick Start Guide](quickstart.md)
- 🔐 Learn about [Authentication](authentication.md)
- 🚀 Choose your [Transport Mode](transport.md)
