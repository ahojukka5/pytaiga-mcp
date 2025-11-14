# Pytaiga MCP Bridge - API Documentation

## Overview

Pytaiga MCP Bridge is a Model Context Protocol (MCP) server that provides tools for interacting with Taiga project management instances. It offers comprehensive CRUD operations for projects, user stories, tasks, issues, epics, milestones, and wiki pages.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              MCP Tools Layer                        │
│  (FastMCP decorators - @mcp.tool)                   │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│         Server Modules (src/server/)                │
│  auth.py, projects.py, user_stories.py, tasks.py,  │
│  issues.py, epics.py, milestones.py, wiki.py       │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│      TaigaClientWrapper (src/taiga_client.py)       │
│  Session management & authentication wrapper        │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│       pytaigaclient (External Library)              │
│  Low-level Taiga REST API client                    │
└─────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules

- **[taiga_client.py](taiga_client.md)** - TaigaClientWrapper for authentication
- **[auth.py](auth.md)** - Login, logout, and session management
- **[common.py](common.md)** - Shared utilities and session storage

### Entity Modules

- **[projects.py](projects.md)** - Project CRUD, members, invitations
- **[user_stories.py](user_stories.md)** - User story management
- **[tasks.py](tasks.md)** - Task operations
- **[issues.py](issues.md)** - Issue tracking
- **[epics.py](epics.md)** - Epic management
- **[milestones.py](milestones.md)** - Sprint/milestone management
- **[wiki.py](wiki.md)** - Wiki page operations

## Quick Start

### 1. Authentication

```python
from src.server.auth import login

# Login with credentials
result = login(
    host="https://tree.taiga.io",
    username="your_username",
    password="your_password"
)
session_id = result["session_id"]
```

### 2. List Projects

```python
from src.server.projects import list_projects

projects = list_projects(session_id)
for project in projects:
    print(f"{project['name']} (ID: {project['id']})")
```

### 3. Create a User Story

```python
from src.server.user_stories import create_user_story

story = create_user_story(
    session_id=session_id,
    project_id=123,
    subject="Implement authentication",
    kwargs={"description": "Add JWT authentication to the API"}
)
```

### 4. Create a Task

```python
from src.server.tasks import create_task

task = create_task(
    session_id=session_id,
    project_id=123,
    subject="Write unit tests",
    kwargs={"user_story": story['id'], "assigned_to": 42}
)
```

## Common Patterns

### Session Management

All API operations require a valid session_id:

```python
# 1. Login to get session
result = login(host, username, password)
session_id = result["session_id"]

# 2. Use session for operations
projects = list_projects(session_id)

# 3. Logout when done
logout(session_id)
```

### Error Handling

```python
from pytaigaclient.exceptions import TaigaException

try:
    result = create_project(session_id, name="My Project")
except TaigaException as e:
    print(f"Taiga API error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Server error: {e}")
```

### Filtering and Querying

Most list operations support filters via JSON string:

```python
# List user stories for a specific milestone
stories = list_user_stories(
    session_id=session_id,
    project_id=123,
    filters='{"milestone": 456, "status": 2}'
)

# List tasks assigned to user
tasks = list_tasks(
    session_id=session_id,
    project_id=123,
    filters='{"assigned_to": 42}'
)
```

### Updating Resources

Update operations use kwargs dict for flexibility:

```python
# Update multiple fields
updated_project = update_project(
    session_id=session_id,
    project_id=123,
    kwargs={
        "name": "New Project Name",
        "description": "Updated description"
    }
)

# Version is automatically handled
updated_story = update_user_story(
    session_id=session_id,
    user_story_id=789,
    kwargs={"subject": "New title", "status": 3}
)
```

## Testing

The project includes comprehensive pytest-based tests:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific module tests
poetry run pytest tests/test_projects.py -v
```

See [TEST_SUMMARY.md](../TEST_SUMMARY.md) for detailed testing documentation.

## MCP Tool Naming

All functions are exposed as MCP tools with descriptive names:

| Module | Tool Names |
|--------|------------|
| auth | `login`, `login_with_token`, `logout`, `session_status` |
| projects | `list_projects`, `create_project`, `get_project`, `update_project`, `delete_project`, `get_project_members`, `invite_project_user` |
| user_stories | `list_user_stories`, `create_user_story`, `get_user_story`, `update_user_story`, `delete_user_story`, `assign_user_story`, `get_user_story_statuses` |
| tasks | `list_tasks`, `create_task`, `get_task`, `update_task`, `delete_task`, `assign_task` |
| issues | `list_issues`, `create_issue`, `get_issue`, `update_issue`, `delete_issue`, `assign_issue`, `get_issue_statuses`, `get_issue_priorities`, `get_issue_severities`, `get_issue_types` |
| epics | `list_epics`, `create_epic`, `get_epic`, `update_epic`, `delete_epic`, `assign_epic` |
| milestones | `list_milestones`, `create_milestone`, `get_milestone`, `update_milestone`, `delete_milestone` |
| wiki | `list_wiki_pages`, `create_wiki_page`, `get_wiki_page`, `update_wiki_page` |

## Configuration

The server uses Poetry for dependency management:

```bash
# Install dependencies
poetry install

# Run the MCP server
poetry run mcp-server

# Development mode
poetry run python -m pytaiga_mcp.server
```

## API Coverage

Current implementation covers:

✅ Authentication (username/password, token)  
✅ Session management  
✅ Projects (full CRUD + members)  
✅ User Stories (full CRUD + assignments + statuses)  
✅ Tasks (full CRUD + assignments)  
✅ Issues (full CRUD + metadata)  
✅ Epics (full CRUD + assignments)  
✅ Milestones (full CRUD)  
✅ Wiki Pages (CRUD operations)  

## Development

### Project Structure

```
pytaiga-mcp/
├── src/
│   ├── server/          # MCP tool implementations
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── projects.py
│   │   ├── user_stories.py
│   │   ├── tasks.py
│   │   ├── issues.py
│   │   ├── epics.py
│   │   ├── milestones.py
│   │   └── wiki.py
│   ├── taiga_client.py  # Authentication wrapper
│   └── server.py        # MCP server entry point
├── tests/               # Comprehensive test suite
├── docs/                # API documentation
└── pyproject.toml       # Poetry configuration
```

### Adding New Features

1. Implement the function in appropriate `src/server/*.py` module
2. Add `@mcp.tool()` decorator with description
3. Create tests in `tests/test_*.py`
4. Update documentation

## Resources

- [Taiga API Documentation](https://docs.taiga.io/api.html)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [pytaigaclient GitHub](https://github.com/talhaorak/pyTaigaClient)
