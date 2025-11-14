# User Guide

Welcome to the Taiga MCP Bridge user guide! This documentation will help you install, configure, and use the MCP server.

## Getting Started

New to Taiga MCP Bridge? Start here:

1. **[Installation Guide](installation.md)** - Install and set up the MCP server
2. **[Quick Start (Simple)](quickstart_simple.md)** - Get up and running in 2 minutes
3. **[Quick Start (Detailed)](quickstart.md)** - Comprehensive getting started guide

## Configuration

Learn how to configure and authenticate:

- **[Authentication Guide](authentication.md)** - Complete authentication methods and best practices
- **[Token Authentication](token_authentication.md)** - How to use application tokens (recommended)
- **[Transport Modes](transport.md)** - Choose between stdio and SSE transport

## Common Tasks

### Authentication

The server supports three authentication methods:

1. **Application Tokens** (Recommended) - Secure, never expire, can be revoked
2. **User Tokens** - Generated from password login, expire after time
3. **Password** - Direct username/password authentication

See the [Authentication Guide](authentication.md) for detailed information.

### Transport Modes

- **stdio** (Default) - Process-based communication, best for desktop AI apps
- **SSE** - HTTP-based Server-Sent Events, best for web applications

See the [Transport Guide](transport.md) for more details.

## Need Help?

- Check the [main README](../../README.md) for overview and features
- See [Developer Guide](../developer_guide/README.md) for API details
- Report issues on [GitHub](https://github.com/ahojukka5/pytaiga-mcp/issues)
