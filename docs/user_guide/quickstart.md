# Quick Start Guide

Get up and running with Taiga MCP Bridge in 5 minutes!

## Overview

This guide will help you:

1. Set up authentication with Taiga
2. Start the MCP server
3. Make your first API call
4. Explore available tools

## Step 1: Get Your Taiga Credentials

### Option A: Application Token (Recommended)

Application tokens are the most secure method and don't require storing passwords.

1. Log in to your Taiga instance (e.g., <https://tree.taiga.io>)
2. Click your avatar → **Settings**
3. Navigate to **Application Tokens** in the left sidebar
4. Click **+ New token**
5. Give it a name (e.g., "MCP Bridge")
6. Copy the generated token (you won't see it again!)

![Application Token Screenshot](../assets/taiga-app-token.png)

!!! tip "Keep Your Token Safe"
    Store your token securely (e.g., password manager or environment variable).
    Never commit tokens to version control!

### Option B: Username & Password (Not Recommended)

If Application tokens aren't available, you can use username/password authentication:

```python
# This method is deprecated - use tokens when possible
result = await session.call_tool(
    "login",
    arguments={
        "host": "https://tree.taiga.io",
        "username": "your-username",
        "password": "your-password"
    }
)
```

## Step 2: Start the Server

### stdio Mode (Default)

For local use and IDE integrations:

```bash
# Activate your environment
poetry shell  # or: source venv/bin/activate

# Start the server
python -m pytaiga_mcp.server
```

The server will start in stdio mode, waiting for MCP client connections.

### SSE Mode (HTTP Server)

For web applications and remote access:

```bash
# Start SSE server on port 8000
python -m pytaiga_mcp.server --transport sse --port 8000
```

Server will be available at `http://localhost:8000`.

## Step 3: Connect and Authenticate

Here's a complete example using Python's MCP client:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
        env=None
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # Login with application token
            login_result = await session.call_tool(
                "login_with_token",
                arguments={
                    "host": "https://tree.taiga.io",
                    "auth_token": "YOUR_APPLICATION_TOKEN",
                    "token_type": "Application"
                }
            )
            
            print(f"✅ Logged in! Session ID: {login_result['session_id']}")
            
            # Save the session_id for subsequent calls
            session_id = login_result["session_id"]
            
            return session_id

# Run
asyncio.run(main())
```

## Step 4: Make API Calls

Once authenticated, you can use any available tool:

### List Projects

```python
# Get all projects
projects = await session.call_tool(
    "list_projects",
    arguments={
        "session_id": session_id
    }
)

for project in projects["projects"]:
    print(f"📁 {project['name']} (ID: {project['id']})")
```

### Get Project Details

```python
# Get specific project
project = await session.call_tool(
    "get_project",
    arguments={
        "session_id": session_id,
        "project_id": 123456
    }
)

print(f"Project: {project['name']}")
print(f"Description: {project['description']}")
print(f"Members: {len(project['members'])}")
```

### List Tasks

```python
# Get tasks for a project
tasks = await session.call_tool(
    "list_tasks",
    arguments={
        "session_id": session_id,
        "project_id": 123456
    }
)

for task in tasks["tasks"]:
    print(f"✓ {task['subject']} - {task['status_extra_info']['name']}")
```

### Create a Task

```python
# Create new task
new_task = await session.call_tool(
    "create_task",
    arguments={
        "session_id": session_id,
        "project_id": 123456,
        "subject": "Implement user authentication",
        "description": "Add JWT-based auth to API",
        "status_id": 1,  # "New" status
        "assigned_to": 789  # User ID
    }
)

print(f"✅ Task created! ID: {new_task['id']}")
```

## Step 5: Session Management

### Check Session Status

```python
status = await session.call_tool(
    "session_status",
    arguments={
        "session_id": session_id
    }
)

print(f"Active: {status['active']}")
print(f"Authenticated: {status['authenticated']}")
print(f"Host: {status['host']}")
```

### Save Session Token (Optional)

Cache your session token for later use:

```python
# Save token to ~/.cache/taiga-mcp/
save_result = await session.call_tool(
    "save_session_token",
    arguments={
        "session_id": session_id,
        "identifier": "my-main-account"
    }
)

print(f"✅ Token saved: {save_result['token_file']}")
```

### Load Cached Token

```python
# Load previously saved token
login_result = await session.call_tool(
    "login_from_cache",
    arguments={
        "host": "https://tree.taiga.io",
        "identifier": "my-main-account"
    }
)

session_id = login_result["session_id"]
```

## Complete Example

Here's a complete script that demonstrates the full workflow:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def taiga_workflow():
    """Complete Taiga workflow example."""
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # 1. Login
            print("🔐 Logging in...")
            login_result = await session.call_tool(
                "login_with_token",
                arguments={
                    "host": "https://tree.taiga.io",
                    "auth_token": "YOUR_APP_TOKEN",
                    "token_type": "Application"
                }
            )
            session_id = login_result["session_id"]
            print("✅ Authenticated!")
            
            # 2. List projects
            print("\n📁 Fetching projects...")
            projects = await session.call_tool(
                "list_projects",
                arguments={"session_id": session_id}
            )
            
            for project in projects["projects"][:5]:  # Show first 5
                print(f"  • {project['name']}")
            
            # 3. Get first project details
            if projects["projects"]:
                project_id = projects["projects"][0]["id"]
                print(f"\n📊 Project details for ID {project_id}...")
                
                project = await session.call_tool(
                    "get_project",
                    arguments={
                        "session_id": session_id,
                        "project_id": project_id
                    }
                )
                
                print(f"  Name: {project['name']}")
                print(f"  Members: {len(project['members'])}")
                print(f"  Sprints: {len(project.get('milestones', []))}")
            
            # 4. Logout
            print("\n👋 Logging out...")
            await session.call_tool(
                "logout",
                arguments={"session_id": session_id}
            )
            print("✅ Session closed!")

# Run the workflow
asyncio.run(taiga_workflow())
```

## Next Steps

Now that you're up and running:

- 📚 Explore [Available Tools](tools.md) to see what you can do
- 🔐 Learn about [Authentication Options](authentication.md) in detail
- 🚀 Check out [Transport Modes](transport.md) for deployment options
- 💡 See [Examples](../examples/basic-usage.md) for common use cases
- 📖 Read the [API Reference](../api/index.md) for detailed documentation

## Troubleshooting

### "Session not found" Error

Make sure you're using the `session_id` returned from the login call.

### "Not authenticated" Error

Check that your token is valid and hasn't expired. Application tokens don't expire, but Bearer tokens do.

### Connection Issues

Ensure the server is running and accessible. Check logs in `logs/taiga_mcp.log`.

### Rate Limiting

Default limit is 100 requests/minute. If you hit this, wait a moment or configure a higher limit.

---

**Questions?** Check out our [FAQ](../faq.md) or [open an issue](https://github.com/ahojukka5/pytaiga-mcp/issues).
