# Authentication Module

## Overview

The authentication module (`src/server/auth.py`) provides MCP tools for managing authentication and sessions with Taiga instances. It offers three authentication methods: username/password login, token-based authentication, and session management.

## Functions

### login()

Authenticates with a Taiga instance using username and password.

```python
@mcp.tool("login")
def login(host: str, username: str, password: str) -> Dict[str, str]
```

**Parameters:**

- `host` (str): The URL of the Taiga instance (e.g., "<https://tree.taiga.io>" or "<http://localhost:9000>")
- `username` (str): Taiga username
- `password` (str): Taiga password

**Returns:**

- `Dict[str, str]`: Dictionary containing the session_id

  ```json
  {"session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
  ```

**Raises:**

- `ValueError`: Invalid credentials or authentication error
- `TaigaException`: Taiga API errors
- `RuntimeError`: Unexpected server errors

**Example:**

```python
result = login(
    host="https://tree.taiga.io",
    username="myuser",
    password="mypassword"
)
session_id = result["session_id"]
```

**Session Management:**

- Creates a new UUID session_id
- Stores the authenticated TaigaClientWrapper in `active_sessions` dictionary
- Session remains active until logout() is called or server restarts

### login_with_token()

Authenticates with a Taiga instance using an authentication token (more secure than password).

```python
@mcp.tool("login_with_token")
def login_with_token(
    host: str, 
    auth_token: str, 
    token_type: str = "Bearer", 
    user_id: Optional[int] = None
) -> Dict[str, str]
```

**Parameters:**

- `host` (str): The URL of the Taiga instance
- `auth_token` (str): Authentication token (Bearer or Application token)
- `token_type` (str): Type of token - "Bearer" (default) or "Application"
- `user_id` (Optional[int]): User ID if known (will be fetched from `/users/me` if not provided)

**Returns:**

- `Dict[str, str]`: Dictionary containing the session_id

  ```json
  {"session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
  ```

**Token Types:**

1. **Bearer Token (User Token)**
   - Personal user authentication token
   - Provides full user context
   - Automatically fetches user_id if not provided

2. **Application Token**
   - System/application-level token
   - No user context needed
   - Used for automated tasks

**How to Get Tokens:**

**Option 1: From Previous Login**

```python
# First login with credentials
result = login(host, username, password)
session_id = result["session_id"]

# Token is now stored in the session
# You can extract it for future use
```

**Option 2: Create Application Token**

1. Login to Taiga web interface
2. Go to User Settings → Applications
3. Create a new Application token
4. Use it with `token_type="Application"`

**Example (Bearer Token):**

```python
result = login_with_token(
    host="https://tree.taiga.io",
    auth_token="eyJ0eXAiOiJKV1QiLCJhbGc...",
    token_type="Bearer",
    user_id=42
)
```

**Example (Application Token):**

```python
result = login_with_token(
    host="https://tree.taiga.io",
    auth_token="application_token_here",
    token_type="Application"
)
```

### logout()

Invalidates and removes a session.

```python
@mcp.tool("logout")
def logout(session_id: str) -> Dict[str, Any]
```

**Parameters:**

- `session_id` (str): The session ID to invalidate

**Returns:**

- `Dict[str, Any]`: Status information

**Return Values:**

**Success:**

```json
{
  "status": "logged_out",
  "session_id": "session-uuid"
}
```

**Session Not Found:**

```json
{
  "status": "session_not_found",
  "session_id": "session-uuid"
}
```

**Example:**

```python
result = logout(session_id="abc-123-def-456")
if result["status"] == "logged_out":
    print("Successfully logged out")
```

**Side Effects:**

- Removes session from `active_sessions` dictionary
- Client wrapper is garbage collected
- All subsequent API calls with this session_id will fail

### session_status()

Checks if a session is currently active and valid.

```python
@mcp.tool("session_status")
def session_status(session_id: str) -> Dict[str, Any]
```

**Parameters:**

- `session_id` (str): The session ID to check

**Returns:**

- `Dict[str, Any]`: Status information about the session

**Return Values:**

**Active Session:**

```json
{
  "status": "active",
  "session_id": "session-uuid",
  "host": "https://tree.taiga.io",
  "authenticated": true
}
```

**Inactive Session (exists but not authenticated):**

```json
{
  "status": "inactive",
  "session_id": "session-uuid",
  "authenticated": false
}
```

**Session Not Found:**

```json
{
  "status": "not_found",
  "session_id": "session-uuid",
  "authenticated": false
}
```

**Example:**

```python
status = session_status(session_id="abc-123")
if status["authenticated"]:
    print(f"Session active on {status['host']}")
else:
    print(f"Session status: {status['status']}")
```

## Session Management

### Active Sessions Dictionary

Sessions are stored in a module-level dictionary:

```python
from .common import active_sessions

# Structure: {session_id: TaigaClientWrapper}
active_sessions: Dict[str, TaigaClientWrapper] = {}
```

### Session Lifecycle

```
┌─────────────┐
│   login()   │  Creates session
└──────┬──────┘
       │
       v
┌─────────────────────┐
│  Session Active     │  Ready for API calls
│  session_id → wrapper│
└──────┬──────────────┘
       │
       v
┌─────────────┐
│  logout()   │  Destroys session
└─────────────┘
```

### Best Practices

**1. Always Check Session Status**

```python
status = session_status(session_id)
if not status["authenticated"]:
    # Re-authenticate
    result = login(host, username, password)
    session_id = result["session_id"]
```

**2. Handle Authentication Errors**

```python
try:
    result = login(host, username, password)
except ValueError as e:
    print(f"Invalid credentials: {e}")
except TaigaException as e:
    print(f"Taiga API error: {e}")
except RuntimeError as e:
    print(f"Server error: {e}")
```

**3. Clean Up Sessions**

```python
# Always logout when done
try:
    # ... do work ...
finally:
    logout(session_id)
```

**4. Use Tokens for Production**

```python
# More secure than storing passwords
import os

token = os.environ.get("TAIGA_TOKEN")
result = login_with_token(
    host="https://tree.taiga.io",
    auth_token=token,
    token_type="Bearer"
)
```

## Authentication Flow Examples

### Basic Username/Password Flow

```python
# 1. Login
result = login(
    host="https://tree.taiga.io",
    username="developer",
    password="secret123"
)
session_id = result["session_id"]

# 2. Verify session
status = session_status(session_id)
assert status["authenticated"] == True

# 3. Use session for API calls
projects = list_projects(session_id)

# 4. Logout when done
logout(session_id)
```

### Token-Based Flow

```python
# 1. Authenticate with token
result = login_with_token(
    host="https://tree.taiga.io",
    auth_token="your-token-here",
    user_id=42
)
session_id = result["session_id"]

# 2. Make API calls
projects = list_projects(session_id, user_id=42)

# 3. Logout
logout(session_id)
```

### Long-Running Service

```python
import os
import time

# Use environment variable for token
token = os.environ["TAIGA_TOKEN"]
host = os.environ["TAIGA_HOST"]

# Authenticate once at startup
result = login_with_token(
    host=host,
    auth_token=token,
    token_type="Application"
)
session_id = result["session_id"]

# Keep session alive and use it
while True:
    # Check session is still valid
    status = session_status(session_id)
    if not status["authenticated"]:
        # Re-authenticate if needed
        result = login_with_token(host, token, "Application")
        session_id = result["session_id"]
    
    # Do work...
    projects = list_projects(session_id)
    time.sleep(60)
```

## Error Handling

### Common Errors

**Invalid Credentials:**

```python
try:
    login(host, "wrong", "credentials")
except ValueError as e:
    print("Authentication failed")
```

**Network Errors:**

```python
try:
    login("http://invalid-host", user, pass)
except TaigaException as e:
    print(f"Cannot reach Taiga: {e}")
```

**Invalid Token:**

```python
try:
    login_with_token(host, "invalid-token")
except ValueError as e:
    print("Token authentication failed")
```

## Logging

The module uses structured logging:

```python
import logging
logger = logging.getLogger(__name__)
```

**Log Levels:**

- `INFO`: Successful operations, session creation
- `WARNING`: Session not found during logout
- `ERROR`: Authentication failures, API errors
- `DEBUG`: Session status checks

**Example Logs:**

```
INFO - Executing login tool for user 'developer' on host 'https://tree.taiga.io'
INFO - Login successful for 'developer'. Session ID: abc12345...
INFO - Session abc12345 logged out successfully.
```

## Security Considerations

1. **Never log passwords:**
   - Passwords are not logged anywhere
   - Only usernames and host URLs appear in logs

2. **Use tokens in production:**
   - Tokens are more secure than passwords
   - Can be rotated without changing password
   - Can be scoped to specific permissions

3. **Session isolation:**
   - Each session is independent
   - Sessions don't interfere with each other
   - Memory is cleaned up on logout

4. **Environment variables:**

   ```python
   # Good: Use environment variables
   token = os.environ.get("TAIGA_TOKEN")
   
   # Bad: Hardcode credentials
   token = "abc123..."  # Don't do this!
   ```

## See Also

- [TaigaClientWrapper](taiga_client.md) - Low-level client wrapper
- [Common Module](common.md) - Session utilities
- [Taiga API Authentication](https://docs.taiga.io/api.html#authentication)
