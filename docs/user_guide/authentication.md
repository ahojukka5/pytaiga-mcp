# Authentication Guide

Complete guide to authentication methods and security best practices for Taiga MCP Bridge.

## Authentication Methods

Taiga MCP Bridge supports three authentication methods, listed from most to least recommended:

### 1. Application Tokens (Recommended) 🌟

**Best for**: Production use, automation, long-running processes

Application tokens are:

- ✅ **Secure**: Never expire, can be revoked anytime
- ✅ **Convenient**: No password management required
- ✅ **Scoped**: Can limit access per token
- ✅ **Auditable**: Each token has a name for tracking

#### How to Get an Application Token

1. Log in to your Taiga instance
2. Navigate to **Settings** → **Application Tokens**
3. Click **+ New token**
4. Enter a descriptive name (e.g., "MCP Bridge - Production")
5. Copy the generated token immediately (shown only once!)

#### Using Application Tokens

```python
result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": "https://tree.taiga.io",
        "auth_token": "your-application-token-here",
        "token_type": "Application"  # Important!
    }
)

session_id = result["session_id"]
```

### 2. Bearer Tokens (Session Tokens)

**Best for**: Short-lived sessions, temporary access

Bearer tokens are:

- ✅ **Fast**: No additional API call needed
- ⚠️ **Time-limited**: Expire after a period of inactivity
- ⚠️ **Less secure**: Obtained through username/password login

#### Getting a Bearer Token

Bearer tokens are returned from the standard login endpoint:

```python
# First, login to get a Bearer token
login_result = await session.call_tool(
    "login",
    arguments={
        "host": "https://tree.taiga.io",
        "username": "your-username",
        "password": "your-password"
    }
)

# The session is automatically created
session_id = login_result["session_id"]
```

To reuse a Bearer token later:

```python
# Use the Bearer token from a previous login
result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": "https://tree.taiga.io",
        "auth_token": "bearer-token-from-previous-login",
        "token_type": "Bearer",
        "user_id": 12345  # Optional but recommended
    }
)
```

### 3. Username & Password (Deprecated) ⚠️

**Best for**: Testing only, not recommended for production

Username/password authentication is:

- ❌ **Less secure**: Credentials in memory
- ❌ **Less convenient**: Must store/manage passwords
- ❌ **Legacy**: Being phased out

```python
# Not recommended - use Application tokens instead
result = await session.call_tool(
    "login",
    arguments={
        "host": "https://tree.taiga.io",
        "username": "your-username",
        "password": "your-password"
    }
)
```

## Token Storage & Caching

The MCP Bridge includes secure token caching to avoid repeated authentication.

### Save Session Token

After authenticating, save your token for later use:

```python
save_result = await session.call_tool(
    "save_session_token",
    arguments={
        "session_id": session_id,
        "identifier": "production-server"  # Unique name
    }
)

print(f"Token saved to: {save_result['token_file']}")
# Output: Token saved to: ~/.cache/taiga-mcp/tree.taiga.io_production-server.token
```

### Load Cached Token

Restore a session from a cached token:

```python
login_result = await session.call_tool(
    "login_from_cache",
    arguments={
        "host": "https://tree.taiga.io",
        "identifier": "production-server"
    }
)

session_id = login_result["session_id"]
```

### List Cached Tokens

See all cached tokens:

```python
tokens = await session.call_tool(
    "list_cached_tokens",
    arguments={}
)

for token_info in tokens["tokens"]:
    print(f"Host: {token_info['host']}")
    print(f"Identifier: {token_info['identifier']}")
    print(f"File: {token_info['token_file']}")
```

### Delete Cached Token

Remove a cached token:

```python
result = await session.call_tool(
    "delete_cached_token",
    arguments={
        "host": "https://tree.taiga.io",
        "identifier": "production-server"
    }
)

print(result["message"])  # "Token deleted successfully"
```

## Security Best Practices

### Do's ✅

1. **Use Application Tokens**: Always prefer Application tokens over passwords
2. **Rotate Tokens**: Regularly create new tokens and revoke old ones
3. **Limit Scope**: Use different tokens for different purposes
4. **Secure Storage**: Store tokens in environment variables or secure vaults
5. **Use HTTPS**: Always connect to Taiga over HTTPS
6. **Monitor Access**: Check Taiga's audit logs for unusual activity

### Don'ts ❌

1. **Don't Commit Tokens**: Never commit tokens to version control
2. **Don't Share Tokens**: Each user/system should have their own token
3. **Don't Use HTTP**: Avoid unencrypted connections
4. **Don't Log Tokens**: Exclude tokens from logs and error messages
5. **Don't Store Passwords**: Use tokens instead of saving passwords

## Environment Variable Configuration

Store credentials securely using environment variables:

```bash
# .env file (add to .gitignore!)
TAIGA_HOST=https://tree.taiga.io
TAIGA_APP_TOKEN=your-application-token-here
```

Load in your application:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Use from environment
result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": os.getenv("TAIGA_HOST"),
        "auth_token": os.getenv("TAIGA_APP_TOKEN"),
        "token_type": "Application"
    }
)
```

## Token Security

### Storage Location

Cached tokens are stored in:

- **Linux/macOS**: `~/.cache/taiga-mcp/`
- **Windows**: `%LOCALAPPDATA%\taiga-mcp\cache\`

### File Permissions

Token files are created with restricted permissions:

- **Unix**: `0o600` (user read/write only)
- **Windows**: User-only access via ACLs

### Token Format

Tokens are stored as JSON with metadata:

```json
{
    "auth_token": "your-token-here",
    "token_type": "Application",
    "user_id": 12345,
    "cached_at": "2024-11-14T10:30:00Z"
}
```

## Session Management

### Check Session Status

Verify your session is active:

```python
status = await session.call_tool(
    "session_status",
    arguments={"session_id": session_id}
)

if status["authenticated"]:
    print(f"✅ Authenticated as user {status['user_id']}")
    print(f"📍 Connected to {status['host']}")
else:
    print("❌ Session expired or invalid")
```

### Health Check

Comprehensive system health check:

```python
health = await session.call_tool(
    "health_check",
    arguments={"session_id": session_id}
)

print(f"Status: {health['status']}")  # "healthy" or "unhealthy"
print(f"API Accessible: {health['api_accessible']}")
print(f"Details: {health['details']}")
```

### Logout

Properly close your session:

```python
result = await session.call_tool(
    "logout",
    arguments={"session_id": session_id}
)

print(result["message"])  # "Session logged out successfully"
```

## Multi-User Scenarios

### Separate Sessions

Each user should maintain their own session:

```python
# User 1
user1_result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": "https://tree.taiga.io",
        "auth_token": "user1-token",
        "token_type": "Application"
    }
)
user1_session = user1_result["session_id"]

# User 2
user2_result = await session.call_tool(
    "login_with_token",
    arguments={
        "host": "https://tree.taiga.io",
        "auth_token": "user2-token",
        "token_type": "Application"
    }
)
user2_session = user2_result["session_id"]

# Use different session IDs for different users
```

### Session Isolation

Sessions are completely isolated:

- Each session has its own authentication state
- Sessions don't interfere with each other
- Rate limiting is per-session
- Metrics are tracked per-session

## Troubleshooting

### Invalid Token Error

```
TaigaException: Invalid token
```

**Solutions**:

1. Verify the token is correct (no extra spaces)
2. Check the token hasn't been revoked in Taiga
3. Ensure you're using the right `token_type` ("Application" vs "Bearer")
4. Verify the Taiga instance URL is correct

### Token Expired Error

```
TaigaException: Token expired
```

**Solutions**:

1. For Application tokens: This shouldn't happen - check token validity
2. For Bearer tokens: Re-authenticate with username/password
3. Use Application tokens instead for long-lived sessions

### Permission Denied Error

```
PermissionError: Client not authenticated
```

**Solutions**:

1. Ensure you've called login before other tools
2. Check the session_id is correct
3. Verify the session hasn't been logged out

### Cache Not Found Error

```
FileNotFoundError: No cached token found
```

**Solutions**:

1. Token hasn't been saved yet - use `save_session_token` first
2. Token file was deleted - authenticate again
3. Check the identifier and host match exactly

## Next Steps

- 🚀 Learn about [Transport Modes](transport.md)
- 🛠️ Explore [Available Tools](tools.md)
- 💡 See [Authentication Examples](../examples/basic-usage.md)
- ⚙️ Configure [Logging and Monitoring](configuration.md)
