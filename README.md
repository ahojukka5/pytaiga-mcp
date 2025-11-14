<p align="center">
<picture>
  <img src="https://taiga.io/media/images/favicon.width-44.png">
</picture>
</p>

# Taiga MCP Bridge

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](https://github.com/ahojukka5/pytaiga-mcp)

> **Note on Origins**: This project was originally forked from
> [talhaorak/pytaiga-mcp](https://github.com/talhaorak/pytaiga-mcp). However, it
> has undergone extensive refactoring and rewriting to the point where it now
> functions as an independent project. We are grateful to the original authors
> for their foundational work, which provided the inspiration and starting point
> for this implementation. Due to the substantial changes, this fork will
> continue its own development path rather than merging back to the original
> repository.

## Overview

The Taiga MCP Bridge is a powerful integration layer that connects
[Taiga](https://taiga.io/) project management platform with the Model Context
Protocol (MCP), enabling AI tools and workflows to interact seamlessly with
Taiga's resources.

This bridge provides a comprehensive set of tools and resources for AI agents to:

- Create and manage projects, epics, user stories, tasks, and issues in Taiga
- Track sprints and milestones
- Assign and update work items
- Query detailed information about project artifacts
- Manage project members and permissions

By using the MCP standard, this bridge allows AI systems to maintain contextual
awareness about project state and perform complex project management tasks
programmatically.

## � Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[User Guide](docs/user_guide/)** - Installation, configuration, and usage guides
- **[Developer Guide](docs/developer_guide/)** - Architecture, API references, and contribution guidelines
- **[Quick Start (Simple)](docs/user_guide/quickstart_simple.md)** - Get started in 2 minutes
- **[Quick Start (Detailed)](docs/user_guide/quickstart.md)** - Comprehensive setup guide

For the full documentation site, see [docs/index.md](docs/index.md).

## 🚀 Quick Start

**Get started in 3 commands:**

```bash
# 1. Clone and install
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp
poetry install

# 2. Run the server
poetry run pytaiga-mcp

# That's it! The server is now running.
```

For authentication and configuration, see the [Quick Start Guide](docs/user_guide/quickstart_simple.md).

### 🐳 Docker (Alternative)

If you prefer Docker:

```bash
# Using Docker Compose
cp .env.docker .env  # Configure your settings
docker-compose up -d
```

**Common Docker Compose commands:**

```bash
docker-compose up              # Start in foreground
docker-compose up -d           # Start in background
docker-compose down            # Stop the server
docker-compose logs -f         # Follow logs
docker-compose ps              # Check status
```

## Features

### Comprehensive Taiga API Coverage

**This bridge provides 100% coverage of essential Taiga API operations**, including all core CRUD (Create, Read, Update, Delete) functionality and key workflows:

#### ✅ Core Resources (Full CRUD + Extended Operations)

- **Projects**: Create, update, delete, list, get by ID/slug, manage members and invitations
- **Epics**: Full CRUD operations, status management, assignment, voting, and watching
- **User Stories**: Full CRUD operations, status management, assignment, voting, and watching
- **Tasks**: Full CRUD operations, status management, assignment, get by reference, voting, and watching
- **Issues**: Full CRUD operations, status/priority/severity/type management, assignment, voting
- **Milestones/Sprints**: Full CRUD operations for sprint planning and tracking
- **Wiki Pages**: Create, update, read, list, watching functionality

#### ✅ Authentication & Session Management

- Secure token-based authentication
- Session management with automatic expiry
- Multiple concurrent sessions supported
- Refresh token support

#### ✅ Metadata & Configuration

- Project member management (invite, remove, list)
- Status workflows (task/issue/user story/epic statuses)
- Priority and severity levels for issues
- Issue type management
- Comprehensive filtering and querying

#### ✅ Collaboration Features

- Vote/upvote/downvote on user stories, tasks, epics
- Watch/unwatch resources for notifications
- Reference-based lookups (get by ref #)
- Assignment and reassignment of work items

**API Coverage**: This implementation covers 100% of the core Taiga API operations needed for project management workflows.

## Installation

This project uses [Poetry](https://python-poetry.org/) for Python package management.

### Prerequisites

- Python 3.10 or higher
- Poetry package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp

# Install dependencies with Poetry
poetry install
```

### Development Installation

For development (includes all dependencies and tools):

```bash
poetry install
```

### Manual Installation

If you prefer to install manually:

```bash
# Using pip in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

The bridge can be configured through environment variables or a `.env` file:

| Environment Variable | Description | Default |
| --- | --- | --- |
| `TAIGA_API_URL` | Base URL for the Taiga API | <http://localhost:9000> |
| `SESSION_EXPIRY` | Session expiration time in seconds | 28800 (8 hours) |
| `TAIGA_TRANSPORT` | Transport mode (stdio or sse) | stdio |
| `REQUEST_TIMEOUT` | API request timeout in seconds | 30 |
| `MAX_CONNECTIONS` | Maximum number of HTTP connections | 10 |
| `MAX_KEEPALIVE_CONNECTIONS` | Max keepalive connections | 5 |
| `RATE_LIMIT_REQUESTS` | Max requests per minute | 100 |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FILE` | Path to log file | taiga_mcp.log |

Create a `.env` file in the project root to set these values:

```bash
TAIGA_API_URL=https://api.taiga.io/api/v1/
TAIGA_TRANSPORT=sse
LOG_LEVEL=DEBUG
```

### 🐳 Docker Configuration

#### Using Docker Compose (Recommended)

1. **Copy the environment template:**

   ```bash
   cp .env.docker .env
   ```

2. **Edit `.env` with your settings:**

   ```bash
   TAIGA_API_URL=https://api.taiga.io
   TAIGA_AUTH_TOKEN=your_application_token_here
   TAIGA_TOKEN_TYPE=Application
   LOG_LEVEL=INFO
   ```

3. **Start the server:**

   ```bash
   docker-compose up -d
   ```

4. **View logs:**

   ```bash
   docker-compose logs -f taiga-mcp
   ```

5. **Stop the server:**

   ```bash
   docker-compose down
   ```

#### Using Docker CLI

```bash
# Build the image
docker build -t taiga-mcp .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e TAIGA_API_URL=https://api.taiga.io \
  -e TAIGA_AUTH_TOKEN=your_token \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/logs:/app/logs \
  --name taiga-mcp-server \
  taiga-mcp

# View logs
docker logs -f taiga-mcp-server

# Stop the server
docker stop taiga-mcp-server
docker rm taiga-mcp-server
```

#### Docker Environment Variables

When running in Docker, the following environment variables are particularly important:

- `TAIGA_API_URL` - Your Taiga instance URL
- `TAIGA_AUTH_TOKEN` - Your application token (recommended)
- `TAIGA_TOKEN_TYPE` - Set to "Application" for app tokens
- `FASTMCP_HOST` - Bind address (default: 0.0.0.0 for Docker)
- `FASTMCP_PORT` - Port to listen on (default: 8000)
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE` - Path to log file inside container

#### Accessing the Server

Once running, the MCP server is accessible at:

- **SSE endpoint:** `http://localhost:8000/sse`
- **Messages endpoint:** `http://localhost:8000/messages`

#### Docker Compose with MCP Clients

To use with MCP clients like Claude Desktop, configure the client to connect to the Docker container:

```json
{
  "mcpServers": {
    "taiga": {
      "url": "http://localhost:8000",
      "transport": "sse"
    }
  }
}
```

#### Kubernetes Deployment

For Kubernetes, create a deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taiga-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: taiga-mcp
  template:
    metadata:
      labels:
        app: taiga-mcp
    spec:
      containers:
      - name: taiga-mcp
        image: taiga-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: TAIGA_API_URL
          value: "https://api.taiga.io"
        - name: TAIGA_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: taiga-mcp-secrets
              key: auth-token
---
apiVersion: v1
kind: Service
metadata:
  name: taiga-mcp
spec:
  selector:
    app: taiga-mcp
  ports:
  - port: 8000
    targetPort: 8000
```

## Usage

### With stdio mode

Paste the following json in your Claude App's or Cursor's mcp settings section:

```json
{
    "mcpServers": {
        "taiga": {
            "command": "poetry",
            "args": ["run", "pytaiga-mcp"],
            "cwd": "/path/to/pytaiga-mcp",
            "env": {
                "TAIGA_TRANSPORT": "stdio",
                "TAIGA_API_URL": "https://api.taiga.io"
            }
        }
    }
}
```

### Running the Server

```bash
# Simple command
poetry run pytaiga-mcp

# Or with full module path
poetry run python -m pytaiga_mcp.server

# With options
poetry run pytaiga-mcp --help
```

### Transport Modes

The server supports two MCP transport protocols for communication between the server and clients:

#### 🔌 stdio (Standard Input/Output) - **Default & Recommended**

**What it is:**

- Uses standard Unix pipes for communication (stdin/stdout)
- Server reads requests from stdin and writes responses to stdout
- Process-based: each client connection spawns a dedicated server process

**When to use:**

- ✅ **Desktop AI applications** (Claude Desktop, Cursor, VS Code)
- ✅ **Command-line tools** and scripts
- ✅ **Local development** and testing
- ✅ **Most common use case** - this is what most MCP clients expect

**Advantages:**

- Simple and reliable
- No network configuration needed
- Automatic process isolation (each client gets its own process)
- Works with standard Unix/Linux process management
- Lower latency for local communication

**Example configuration:**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "poetry",
      "args": ["run", "pytaiga-mcp"],
      "cwd": "/path/to/pytaiga-mcp",
      "env": {"TAIGA_TRANSPORT": "stdio"}
    }
  }
}
```

#### 🌐 SSE (Server-Sent Events) - **For Web/Network Applications**

**What it is:**

- HTTP-based transport using Server-Sent Events
- Server runs as a long-lived HTTP server on a network port
- Multiple clients can connect over the network
- One-way server push (server → client) with HTTP POST for client → server

**When to use:**

- ✅ **Web applications** that need MCP integration
- ✅ **Remote access** (server on one machine, client on another)
- ✅ **Multiple simultaneous clients** connecting to the same server
- ✅ **Browser-based** AI tools
- ✅ **Containerized deployments** (Docker, Kubernetes)

**Advantages:**

- Network-accessible (not limited to local machine)
- Can serve multiple clients simultaneously
- Firewall/proxy friendly (uses standard HTTP)
- Better for distributed architectures
- Built-in reconnection handling

**Disadvantages:**

- Requires port configuration and management
- Slightly higher latency due to HTTP overhead
- Need to handle network security (authentication, TLS)

**Example configuration:**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "poetry",
      "args": ["run", "pytaiga-mcp", "--transport", "sse"],
      "cwd": "/path/to/pytaiga-mcp",
      "env": {"TAIGA_TRANSPORT": "sse"}
    }
  }
}
```

#### 🎯 Which Should You Choose?

| Use Case | Recommended Transport | Why |
|----------|----------------------|-----|
| Claude Desktop App | **stdio** | Built-in support, zero config |
| Cursor IDE | **stdio** | Process-based integration |
| VS Code Extension | **stdio** | Standard MCP pattern |
| Web Application | **SSE** | HTTP-based, network accessible |
| Remote Server | **SSE** | Works across network |
| Docker Container | **SSE** | Better for containerized apps |
| Local Scripts | **stdio** | Simpler, no port management |
| Multiple Clients | **SSE** | Share one server instance |

#### 🔧 Setting the Transport Mode

You can configure the transport mode in several ways:

1. **Command-line flag:**

   ```bash
   poetry run pytaiga-mcp --transport stdio  # Default
   poetry run pytaiga-mcp --transport sse    # SSE mode
   
   # Or use the convenience script:
   ./scripts/run.sh
   ```

2. **Environment variable:**

   ```bash
   export TAIGA_TRANSPORT=stdio  # or 'sse'
   poetry run pytaiga-mcp
   ```

3. **In .env file:**

   ```bash
   TAIGA_TRANSPORT=stdio  # or 'sse'
   ```

**💡 Tip:** If you're not sure which to use, start with **stdio** - it's simpler and works with most MCP clients out of the box.

For more details, see the [Transport Modes Guide](docs/user_guide/transport.md).

### Authentication Flow

This MCP bridge uses a session-based authentication model with **secure token-based authentication**.

#### 🔒 RECOMMENDED: Application Token (Simplest & Most Secure!)

**This is the easiest and most secure way to authenticate:**

1. **Get your Application Token from Taiga**:
   - Login to Taiga web interface
   - Go to: **User Settings → Applications**
   - Click "**Create new application**"
   - Copy the generated token

2. **Add to your `.env` file**:

   ```bash
   TAIGA_HOST=https://api.taiga.io
   TAIGA_AUTH_TOKEN=your_application_token_here
   TAIGA_TOKEN_TYPE=Application
   ```

3. **Use in your code**:

   ```python
   import os
   session = client.call_tool("login_with_token", {
       "host": os.getenv("TAIGA_HOST"),
       "auth_token": os.getenv("TAIGA_AUTH_TOKEN"),
       "token_type": "Application"
   })
   session_id = session["session_id"]
   # Done! No password needed, ever.
   ```

#### Alternative: Cached Session Tokens

If you prefer, you can login once with username/password and cache the session token:

1. **First-time setup** - Login once:

   ```python
   session = client.call_tool("login", {
       "username": "your_username",
       "password": "your_password",
       "host": "https://api.taiga.io"
   })
   # Save token to ~/.cache/taiga-mcp/ (0600 permissions)
   client.call_tool("save_session_token", {
       "session_id": session["session_id"]
   })
   ```

2. **Future logins** - Use cached token:

   ```python
   session = client.call_tool("login_from_cache", {
       "host": "https://api.taiga.io"
   })
   ```

#### ⚠️ Not Recommended: Username/Password Login

Only use this for initial setup to save a token:

```python
session = client.call_tool("login", {
    "username": "your_taiga_username",
    "password": "your_taiga_password",
    "host": "https://api.taiga.io"
})
session_id = session["session_id"]

# IMPORTANT: Save token immediately, then delete password from config
client.call_tool("save_session_token", {"session_id": session_id})
```

#### Using the Session

Once authenticated, follow these steps:

1. **Using Tools and Resources**: Include the `session_id` in every API call:

   ```python
   # For resources, include session_id in the URI
   projects = client.get_resource(f"taiga://projects?session_id={session_id}")
   
   # For project-specific resources
   epics = client.get_resource(f"taiga://projects/123/epics?session_id={session_id}")
   
   # For tools, include session_id as a parameter
   new_project = client.call_tool("create_project", {
       "session_id": session_id,
       "name": "New Project",
       "description": "Description"
   })
   ```

2. **Check Session Status**: You can check if your session is still valid:

   ```python
   status = client.call_tool("session_status", {"session_id": session_id})
   # Returns information about session validity and remaining time
   ```

3. **Logout**: When finished, you can logout to terminate the session:

   ```python
   client.call_tool("logout", {"session_id": session_id})
   ```

### Example: Complete Project Creation Workflow

Here's a complete example of creating a project with epics and user stories:

```python
from mcp.client import Client

# Initialize MCP client
client = Client()

# Authenticate and get session ID
auth_result = client.call_tool("login", {
    "username": "admin",
    "password": "password123",
    "host": "https://taiga.mycompany.com"
})
session_id = auth_result["session_id"]

# Create a new project
project = client.call_tool("create_project", {
    "session_id": session_id,
    "name": "My New Project",
    "description": "A test project created via MCP"
})
project_id = project["id"]

# Create an epic
epic = client.call_tool("create_epic", {
    "session_id": session_id,
    "project_id": project_id,
    "subject": "User Authentication",
    "description": "Implement user authentication features"
})
epic_id = epic["id"]

# Create a user story in the epic
story = client.call_tool("create_user_story", {
    "session_id": session_id,
    "project_id": project_id,
    "subject": "User Login",
    "description": "As a user, I want to log in with my credentials",
    "epic_id": epic_id
})

# Logout when done
client.call_tool("logout", {"session_id": session_id})
```

## Security Best Practices

### 🔐 Authentication Security

**NEVER store passwords in plain text files!** This is a critical security anti-pattern.

#### ✅ Secure Authentication Methods

1. **Token-based authentication with cache** (Recommended)
   - Login once with username/password
   - Use `save_session_token` to cache the auth token
   - Use `login_from_cache` for all future authentications
   - Tokens stored with `0600` permissions (user read/write only)
   - Cache location: `~/.cache/taiga-mcp/` (Linux/macOS) or `%LOCALAPPDATA%/taiga-mcp/` (Windows)

2. **Application tokens** (Most Secure)
   - Create in Taiga web interface (User Settings → Applications)
   - Tokens can be revoked without changing passwords
   - Use `login_with_token` with `token_type="Application"`
   - Store token in environment variable or secrets manager

#### ❌ What NOT to Do

```bash
# ❌ BAD: Never do this!
TAIGA_PASSWORD=my_password_123  # Stored in .env or config
```

```python
# ❌ BAD: Never hardcode passwords
login(username="user", password="hardcoded_password")
```

#### ✅ What TO Do

```bash
# ✅ GOOD: Use token instead
TAIGA_AUTH_TOKEN=abc123...xyz  # Token can be revoked
```

```python
# ✅ GOOD: Login from cached token
session = login_from_cache(host="https://api.taiga.io")

# ✅ GOOD: Or use application token
session = login_with_token(
    host="https://api.taiga.io",
    auth_token=os.getenv("TAIGA_AUTH_TOKEN"),
    token_type="Application"
)
```

### Token Management

**Available MCP tools for secure authentication:**

- `save_session_token` - Save auth token from active session to cache
- `login_from_cache` - Authenticate using cached token (no password needed)
- `login_with_token` - Authenticate with explicit token (Bearer or Application)
- `delete_cached_token` - Remove cached token for a host
- `list_cached_tokens_tool` - List all cached tokens (without exposing values)

### Revoking Access

If a token is compromised:

1. **For cached tokens**: Use `delete_cached_token` tool
2. **For Application tokens**: Revoke in Taiga web interface → User Settings → Applications
3. **For Bearer tokens**: Change your password (invalidates all Bearer tokens)

### Additional Security Measures

1. **Add token file to .gitignore**:

   ```bash
   # Add to .gitignore
   .cache/
   .env
   *.token
   ```

2. **Use environment variables for tokens**:

   ```python
   import os
   token = os.getenv("TAIGA_AUTH_TOKEN")  # Never hardcode
   ```

3. **Rotate tokens regularly** (every 3-6 months)

4. **Use different tokens for different purposes**:
   - Development token
   - Production token
   - CI/CD token

See the [Authentication Guide](docs/user_guide/authentication.md) and [Token Authentication Guide](docs/user_guide/token_authentication.md) for detailed authentication documentation.

## Development

### Project Structure

```
pytaiga-mcp/
├── pytaiga_mcp/           # Main package
│   ├── server.py          # MCP server implementation
│   ├── taiga_client.py    # Taiga API client with all CRUD operations
│   ├── cli.py             # Command-line interface
│   ├── logging_config.py  # Logging configuration
│   └── server/            # Server modules (auth, projects, tasks, etc.)
├── tests/                 # Test suite
│   ├── conftest.py        # Shared pytest fixtures
│   ├── test_*.py          # Test modules
│   └── README.md          # Testing documentation
├── docs/                  # Documentation
│   ├── user_guide/        # End-user documentation
│   └── developer_guide/   # Contributor documentation
├── scripts/               # Utility scripts
│   ├── run.sh             # Server execution script
│   ├── quality.sh         # Code quality checks
│   └── inspect.sh         # Debugging and inspection tool
├── examples/              # Example configurations and usage
├── pyproject.toml         # Poetry configuration and dependencies
└── README.md              # Project overview
```

For detailed documentation, see the [Documentation](docs/) directory.

### Testing

Run tests with pytest:

```bash
# Run all tests with coverage
pytest --cov=pytaiga_mcp

# Run specific test markers
pytest -m "auth"     # Authentication tests
pytest -m "core"     # Core functionality tests

# Use helper scripts
./scripts/run_unit_tests.sh        # Unit tests only
./scripts/run_integration_tests.sh # Integration tests
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

### Code Quality

Run static analysis tools:

```bash
# Check code quality (formatting, linting, type checking)
./scripts/quality.sh

# Automatically fix formatting and import issues
./scripts/quality.sh --fix

# Check only (CI mode, no diffs)
./scripts/quality.sh --check
```

The quality script runs:

- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast linting (replaces flake8 + more)
- **mypy**: Static type checking
- **flake8**: Additional style checking

### Debugging and Inspection

Use the included inspector tool for debugging:

```bash
# Default stdio transport
./scripts/inspect.sh

# For SSE transport with custom port
./scripts/inspect.sh --transport sse --port 5001

# With debug logging
./scripts/inspect.sh --log-level DEBUG --log-file debug.log
```

## Error Handling

All API operations return standardized error responses in the following format:

```json
{
  "status": "error",
  "error_type": "ExceptionClassName",
  "message": "Detailed error message"
}
```

## Performance Considerations

The bridge implements several performance optimizations:

1. **Connection Pooling**: Reuses HTTP connections for better performance
2. **Rate Limiting**: Prevents overloading the Taiga API
3. **Retry Mechanism**: Automatically retries failed requests with exponential backoff
4. **Session Cleanup**: Regularly cleans up expired sessions to free resources

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Development setup (Poetry, code quality tools)
- Commit message format (conventional commits)
- Pull request process and CI expectations
- Code quality standards
- Testing requirements

For technical documentation, see the [Developer Guide](docs/developer_guide/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [dwilson5817](https://github.com/dwilson5817) and contributors to the [original mcp-taiga project](https://github.com/dwilson5817/mcp-taiga) for laying the groundwork that inspired this implementation
- [Taiga](https://www.taiga.io/) for their excellent project management platform
- [Model Context Protocol (MCP)](https://github.com/mcp-foundation/specification) for the standardized AI communication framework
- All contributors who have helped shape this project
