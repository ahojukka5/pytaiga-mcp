# API Reference

Complete reference for all MCP tools provided by Taiga MCP Bridge.

## Overview

Taiga MCP Bridge provides **50+ tools** organized into the following categories:

- **[Authentication](auth.md)**: Login, logout, session management, token caching
- **[Projects](projects.md)**: List, get, create, update, delete projects
- **[Tasks](tasks.md)**: Manage tasks including CRUD operations
- **[User Stories](user-stories.md)**: Work with user stories
- **[Issues](issues.md)**: Track and manage issues
- **[Epics](epics.md)**: Handle epic-level planning
- **[Milestones](milestones.md)**: Sprint and milestone management
- **[Wiki](wiki.md)**: Create and manage wiki pages

## Common Patterns

### Session ID

All authenticated tools require a `session_id` parameter obtained from login:

```python
# Login first
login_result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": "https://tree.taiga.io",
        "auth_token": "your-token",
        "token_type": "Application"
    }
)

# Save session ID for other calls
session_id = login_result["session_id"]

# Use in subsequent calls
projects = await session.call_tool(
    "list_projects",
    arguments={"session_id": session_id}
)
```

### Error Handling

All tools follow consistent error handling:

```python
try:
    result = await session.call_tool("some_tool", arguments={...})
except PermissionError as e:
    # Authentication required or session expired
    print(f"Auth error: {e}")
except TaigaException as e:
    # Taiga API error (invalid data, not found, etc.)
    print(f"API error: {e}")
except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
```

### Common Return Values

Most tools return dictionaries with:

- **Success**: Requested data or confirmation message
- **Error**: Error message with actionable guidance

Example success response:

```python
{
    "id": 12345,
    "name": "My Project",
    "description": "Project description",
    "created_date": "2024-01-01T00:00:00Z",
    # ... more fields
}
```

### Pagination

List operations support pagination:

```python
# Get first page (default)
projects = await session.call_tool(
    "list_projects",
    arguments={"session_id": session_id}
)

# Get specific page
projects = await session.call_tool(
    "list_projects",
    arguments={
        "session_id": session_id,
        "page": 2,
        "page_size": 50
    }
)
```

### Filtering

Many list operations support filtering:

```python
# Filter by status
tasks = await session.call_tool(
    "list_tasks",
    arguments={
        "session_id": session_id,
        "project_id": 12345,
        "status": 1  # Status ID
    }
)

# Filter by assigned user
tasks = await session.call_tool(
    "list_tasks",
    arguments={
        "session_id": session_id,
        "project_id": 12345,
        "assigned_to": 789  # User ID
    }
)
```

## Tool Categories

### Authentication Tools (9 tools)

Essential tools for authentication and session management:

| Tool | Purpose |
|------|---------|
| `login` | Username/password login (deprecated) |
| `login_with_token` | Token-based login (recommended) |
| `logout` | Close session |
| `session_status` | Check session state |
| `save_session_token` | Cache token for reuse |
| `login_from_cache` | Restore from cached token |
| `delete_cached_token` | Remove cached token |
| `list_cached_tokens` | Show all cached tokens |
| `health_check` | Comprehensive health diagnostics |

[View Authentication API →](auth.md)

### Project Tools (10+ tools)

Manage projects and project settings:

| Tool | Purpose |
|------|---------|
| `list_projects` | Get all accessible projects |
| `get_project` | Get detailed project info |
| `create_project` | Create new project |
| `update_project` | Modify project settings |
| `delete_project` | Remove project |
| `list_project_members` | Get project team |
| `add_project_member` | Invite user to project |
| `remove_project_member` | Remove user from project |
| And more... | Roles, permissions, etc. |

[View Project API →](projects.md)

### Task Tools (10+ tools)

Full CRUD operations for tasks:

| Tool | Purpose |
|------|---------|
| `list_tasks` | Get tasks for project |
| `get_task` | Get task details |
| `create_task` | Create new task |
| `update_task` | Modify task |
| `delete_task` | Remove task |
| `assign_task` | Assign to user |
| `add_task_comment` | Add comment |
| `list_task_comments` | Get comments |
| And more... | Attachments, history, etc. |

[View Task API →](tasks.md)

### User Story Tools (10+ tools)

Manage user stories and sprints:

| Tool | Purpose |
|------|---------|
| `list_user_stories` | Get stories for project |
| `get_user_story` | Get story details |
| `create_user_story` | Create new story |
| `update_user_story` | Modify story |
| `delete_user_story` | Remove story |
| `assign_user_story` | Assign to sprint |
| And more... | Points, status, etc. |

[View User Story API →](user-stories.md)

### Issue Tools (10+ tools)

Track and resolve issues:

| Tool | Purpose |
|------|---------|
| `list_issues` | Get issues for project |
| `get_issue` | Get issue details |
| `create_issue` | Create new issue |
| `update_issue` | Modify issue |
| `delete_issue` | Remove issue |
| And more... | Priority, severity, etc. |

[View Issue API →](issues.md)

### Epic Tools (8+ tools)

High-level epic management:

| Tool | Purpose |
|------|---------|
| `list_epics` | Get epics for project |
| `get_epic` | Get epic details |
| `create_epic` | Create new epic |
| `update_epic` | Modify epic |
| `delete_epic` | Remove epic |
| And more... | Related stories, etc. |

[View Epic API →](epics.md)

### Milestone Tools (8+ tools)

Sprint and milestone tracking:

| Tool | Purpose |
|------|---------|
| `list_milestones` | Get project sprints |
| `get_milestone` | Get sprint details |
| `create_milestone` | Create new sprint |
| `update_milestone` | Modify sprint |
| `delete_milestone` | Remove sprint |
| And more... | Stats, burndown, etc. |

[View Milestone API →](milestones.md)

### Wiki Tools (8+ tools)

Documentation and wiki pages:

| Tool | Purpose |
|------|---------|
| `list_wiki_pages` | Get project wiki pages |
| `get_wiki_page` | Get page content |
| `create_wiki_page` | Create new page |
| `update_wiki_page` | Edit page content |
| `delete_wiki_page` | Remove page |
| And more... | Attachments, history, etc. |

[View Wiki API →](wiki.md)

## Monitoring & Diagnostics

### Server Metrics

Get performance metrics:

```python
metrics = await session.call_tool("get_server_metrics", arguments={})

print(f"Total requests: {metrics['total_requests']}")
print(f"Total errors: {metrics['total_errors']}")
print(f"Error rate: {metrics['error_rate']}%")

# Per-tool metrics
for tool_name, stats in metrics['tools'].items():
    print(f"{tool_name}:")
    print(f"  Requests: {stats['request_count']}")
    print(f"  Avg time: {stats['avg_time']}s")
```

### Health Check

Verify system health:

```python
health = await session.call_tool(
    "health_check",
    arguments={"session_id": session_id}
)

if health['status'] == 'healthy':
    print("✅ All systems operational")
else:
    print(f"⚠️ Issue: {health['details']}")
```

## Rate Limiting

The server implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per session
- **Enforcement**: Token bucket algorithm
- **Response**: `PermissionError` when exceeded

Example error:

```text
PermissionError: Rate limit exceeded. Too many requests.
Please wait before making more requests.
Limit: 100 requests/minute. Remaining tokens: 0
```

## Best Practices

### 1. Reuse Sessions

```python
# ✅ Good: One login, multiple operations
session_id = login()
for project_id in project_ids:
    data = get_project(session_id, project_id)

# ❌ Bad: Login for each operation
for project_id in project_ids:
    session_id = login()
    data = get_project(session_id, project_id)
    logout(session_id)
```

### 2. Handle Errors Gracefully

```python
# ✅ Good: Specific error handling
try:
    result = await session.call_tool("get_project", arguments={...})
except PermissionError:
    # Re-authenticate
    await re_authenticate()
except TaigaException as e:
    if "not found" in str(e).lower():
        # Handle missing resource
        pass
```

### 3. Use Appropriate Filters

```python
# ✅ Good: Filter on server side
tasks = list_tasks(session_id, project_id, status=1, assigned_to=user_id)

# ❌ Bad: Filter on client side
all_tasks = list_tasks(session_id, project_id)
filtered = [t for t in all_tasks if t['status'] == 1 and t['assigned_to'] == user_id]
```

### 4. Cache Tokens Securely

```python
# ✅ Good: Use built-in token caching
save_session_token(session_id, identifier="prod")
# Later...
session_id = login_from_cache(host, identifier="prod")

# ❌ Bad: Store tokens in code
AUTH_TOKEN = "hardcoded-token"  # Never do this!
```

## Code Generation

### Python Client Template

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Your code here
            login_result = await session.call_tool(
                "login_with_token",
                arguments={
                    "host": "https://tree.taiga.io",
                    "auth_token": "YOUR_TOKEN",
                    "token_type": "Application"
                }
            )
            session_id = login_result["session_id"]
            
            # Use the API...

asyncio.run(main())
```

## Next Steps

- 📖 Read detailed [Authentication API](auth.md)
- 🚀 Explore [Project Management API](projects.md)
- 💡 See [Code Examples](../examples/basic-usage.md)
- 🛠️ Learn [Best Practices](../guides/best-practices.md)
