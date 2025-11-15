# Taiga MCP Bridge Documentation

**A Model Context Protocol (MCP) server for seamless integration with Taiga project management.**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## What is Taiga MCP Bridge?

Taiga MCP Bridge is a production-ready [Model Context Protocol](https://modelcontextprotocol.io) server that enables AI assistants and automation tools to interact with [Taiga](https://taiga.io), an open-source project management platform. It provides a comprehensive set of tools for managing projects, tasks, user stories, issues, epics, milestones, and wiki pages.

## 📖 Documentation Structure

### � [Getting Started](user_guide/getting_started.md)

Quick start guide to get up and running in minutes.

### � [User Guide](user_guide/README.md)

Complete guide for end users and integrators.

### 🔧 [Developer Guide](developer_guide/README.md)

Technical documentation for contributors and developers.

## Key Features

✨ **Comprehensive API Coverage**
:   Full support for Taiga's core features including projects, tasks, user stories, issues, epics, milestones, and wiki pages.

🔐 **Secure Authentication**
:   Multiple authentication methods with secure token storage. Application tokens recommended for production use.

⚡ **High Performance**
:   Built-in rate limiting, request metrics, and optimized API calls for efficient operation.

🚀 **Dual Transport Modes**
:   Supports both stdio (process-based) and SSE (HTTP-based) transport protocols for flexible deployment.

📊 **Production Ready**
:   Comprehensive logging, error handling, health checks, and performance metrics out of the box.

🧪 **Well Tested**
:   99% test coverage with 285 passing tests.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ahojukka5/pytaiga-mcp.git
cd pytaiga-mcp

# Install dependencies using Poetry
poetry install

# Or use the convenience script
./scripts/install.sh
```

For detailed installation instructions, see the [Installation Guide](user_guide/installation.md).

### Basic Usage

See the [Quick Start Guide](user_guide/quickstart_simple.md) for a 2-minute setup, or the [detailed Quick Start](user_guide/quickstart.md) for comprehensive instructions.

## Use Cases

### 🤖 AI Assistant Integration

Integrate Taiga with AI assistants like Claude, enabling natural language project management:

- "Create a new sprint for the mobile app project"
- "Show me all high-priority bugs assigned to the backend team"
- "Update the user story for the login feature with acceptance criteria"

### 🔄 Workflow Automation

Build automated workflows for project management:

- Auto-create tasks from external sources (emails, webhooks, etc.)
- Sync project data with other tools (Jira, GitHub, etc.)
- Generate reports and dashboards from Taiga data

### 📊 Data Analysis

Extract and analyze project data:

- Track team velocity and productivity metrics
- Generate custom reports and visualizations
- Monitor project health and identify bottlenecks

## Architecture Overview

The server acts as a bridge between MCP clients (AI assistants, automation tools) and the Taiga API, providing:

- **Session Management**: Secure authentication and session lifecycle
- **API Abstraction**: Clean, type-safe interface to Taiga's REST API
- **Error Handling**: Comprehensive error messages with actionable guidance
- **Performance Monitoring**: Built-in metrics and health checks

For detailed architecture information, see the [Architecture Guide](developer_guide/architecture.md).

## Transport Modes

### stdio (Default)

Process-based communication ideal for:

- Single-user desktop applications
- IDE integrations (VS Code, Claude Desktop)
- Local automation scripts
- Simple deployment scenarios

### SSE (Server-Sent Events)

HTTP-based communication ideal for:

- Multi-user environments
- Web applications
- Remote access scenarios
- Cloud deployments

See [Transport Modes Guide](user_guide/transport.md) for detailed comparison.

## Project Status

**Current Version**: 0.1.0 (Production Ready)

The project is actively maintained and production-ready. We follow semantic versioning and maintain backward compatibility within major versions.

### Features

- ✅ 99% test coverage with 285 passing tests
- ✅ Type checking with mypy
- ✅ Code quality tools (black, isort, ruff, flake8)
- ✅ Comprehensive CLI with logging options
- ✅ Docker deployment support
- ✅ Rate limiting and performance metrics
- ✅ Health check endpoint
- ✅ Session-based authentication

## Community & Support

- **Repository**: [GitHub](https://github.com/ahojukka5/pytaiga-mcp)
- **Issues**: [GitHub Issues](https://github.com/ahojukka5/pytaiga-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahojukka5/pytaiga-mcp/discussions)

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details on:

- Code of Conduct
- Development setup
- Testing requirements
- Pull request process

See the [Developer Guide](developer_guide/README.md) for technical documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ahojukka5/pytaiga-mcp/blob/master/LICENSE) file for details.

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
- Powered by [pytaigaclient](https://github.com/nephila/pytaiga-client)
- Documentation with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

---

**Ready to get started?** Check out the [Quick Start Guide](user_guide/quickstart_simple.md) or explore the [User Guide](user_guide/README.md).
