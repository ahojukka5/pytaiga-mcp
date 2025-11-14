# Token-Based Authentication Guide

## Why Use Token Authentication?

**Security Concerns with Password Storage:**

- ❌ Storing passwords in `.env` files is risky
- ❌ Passwords can be stolen if repository is compromised
- ❌ Hard to revoke access without changing password everywhere

**Benefits of Token Authentication:**

- ✅ Tokens can be revoked without changing password
- ✅ More secure - token has limited scope
- ✅ Easier to manage for automation/scripts
- ✅ Can create multiple tokens for different purposes

## ⚡ TL;DR - Simplest Method

**Just want to get started?** Use Application Tokens (Method 1 below):

1. Get token from Taiga: Settings → Applications → Create
2. Add to `.env`: `TAIGA_AUTH_TOKEN=your_token`
3. Use: `login_with_token(auth_token=os.getenv("TAIGA_AUTH_TOKEN"))`

**Done!** No password storage, no complex setup. See [QUICKSTART.md](QUICKSTART.md) for details.

---

## Method 1: Application Token (Recommended - Simplest!)

**This is the easiest and most secure method.** No password storage, no caching complexity.

### Step-by-Step Guide

1. **Go to Taiga Web Interface**
   - Navigate to: <https://tree.taiga.io> (or your instance)
   - Click on your profile icon (top right)
   - Select "Settings" or "User Settings"

2. **Navigate to Applications Section**
   - Look for "Applications" or "API Tokens" in the sidebar
   - Click "Create new application" or "Generate Token"

3. **Create Application Token**
   - Give it a name (e.g., "MCP Server" or "Development")
   - Copy the generated token
   - **Save it securely** - you won't be able to see it again!

4. **Add to `.env` file** (recommended):

   ```bash
   TAIGA_HOST=https://api.taiga.io
   TAIGA_AUTH_TOKEN=your_application_token_here
   TAIGA_TOKEN_TYPE=Application
   ```

5. **Use in your code**:

   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   result = login_with_token(
       host=os.getenv("TAIGA_HOST"),
       auth_token=os.getenv("TAIGA_AUTH_TOKEN"),
       token_type="Application",
       user_id=None  # Optional: specify if known
   )
   
   session_id = result["session_id"]
   # That's it! Use session_id for all API calls
   ```

**Benefits:**

- ✅ Simplest setup (just copy/paste token)
- ✅ No password storage required
- ✅ No caching complexity
- ✅ Easy to rotate (generate new token)
- ✅ Easy to revoke (delete in Taiga settings)

## Method 2: Secure Token Cache (Advanced)

**NEW:** We now have built-in secure token caching!

1. **Login with username/password once**:

   ```python
   # This returns a session_id
   result = login(host="https://api.taiga.io", username="your_username", password="your_password")
   session_id = result["session_id"]
   ```

2. **Save the token to secure cache**:

   ```python
   # Save token to ~/.cache/taiga-mcp/ with 0600 permissions (user-only access)
   save_session_token(session_id)
   # Token is now saved securely!
   ```

3. **Future logins - NO PASSWORD NEEDED**:

   ```python
   # Just use the cached token
   result = login_from_cache(host="https://api.taiga.io")
   session_id = result["session_id"]
   # That's it! No password required!
   ```

4. **Delete password from config files**:
   - Remove `TAIGA_PASSWORD` from `.env`
   - Delete any password references
   - You can now authenticate without exposing credentials!

## Method 2: Create Application Token (Recommended)

### Step-by-Step Guide

1. **Go to Taiga Web Interface**
   - Navigate to: <https://tree.taiga.io> (or your instance)
   - Click on your profile icon (top right)
   - Select "Settings" or "User Settings"

2. **Navigate to Applications Section**
   - Look for "Applications" or "API Tokens" in the sidebar
   - Click "Create new application" or "Generate Token"

3. **Create Application Token**
   - Give it a name (e.g., "OpenPFC MCP Server")
   - Copy the generated token
   - **Save it securely** - you won't be able to see it again!

4. **Use the Application Token**:

   ```python
   result = login_with_token(
       host="https://api.taiga.io",
       auth_token="application_token_here",
       token_type="Application",  # Note: "Application" not "Bearer"
       user_id=157593  # Optional: your user ID for faster startup
   )
   ```

## Using Token in Python Scripts

### Example 1: Basic Token Login

```python
from pytaiga_mcp_client import TaigaMCPClient

# Load token from environment or secure storage
import os
token = os.getenv("TAIGA_AUTH_TOKEN")

# Login with token
client = TaigaMCPClient()
session = client.login_with_token(
    host="https://api.taiga.io",
    auth_token=token,
    token_type="Bearer"
)

# Use the session
projects = client.list_projects(session_id=session["session_id"])
```

### Example 2: With Environment Variables

Create `.env` file (add to `.gitignore`!):

```bash
TAIGA_HOST=https://api.taiga.io
TAIGA_AUTH_TOKEN=your_token_here
TAIGA_TOKEN_TYPE=Bearer
TAIGA_USER_ID=157593  # Optional
```

Python script:

```python
import os
from dotenv import load_dotenv

load_dotenv()

result = login_with_token(
    host=os.getenv("TAIGA_HOST"),
    auth_token=os.getenv("TAIGA_AUTH_TOKEN"),
    token_type=os.getenv("TAIGA_TOKEN_TYPE", "Bearer"),
    user_id=int(os.getenv("TAIGA_USER_ID")) if os.getenv("TAIGA_USER_ID") else None
)
```

## Token Management Best Practices

### Security

1. **Never commit tokens to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables
   - Or use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

2. **Rotate tokens regularly**
   - Create new token every few months
   - Delete old tokens after replacing

3. **Use different tokens for different purposes**
   - Development token
   - Production token
   - CI/CD token

### Revocation

If a token is compromised:

1. **For Application Tokens**:
   - Go to Taiga Settings > Applications
   - Find the token and click "Revoke" or "Delete"

2. **For Bearer Tokens** (from login):
   - Change your password (invalidates all Bearer tokens)
   - Or wait for token expiration (usually 24 hours)

## Troubleshooting

### "Token is invalid or expired"

**Problem**: Token no longer works

**Solutions**:

1. Token may have expired (Bearer tokens expire after ~24 hours)
2. Generate a new Application token
3. Or login again with username/password to get fresh token

### "Could not fetch user info"

**Problem**: Token works but user ID not retrieved

**Solutions**:

1. Provide `user_id` parameter explicitly:

   ```python
   login_with_token(..., user_id=157593)
   ```

2. Find your user ID:
   - Login with username/password first
   - Check the login response for `id` field

### "No projects found"

**Problem**: After token login, `list_projects` returns empty list

**Cause**: User ID not set, so member filtering doesn't work

**Solution**: Provide user_id when logging in with token

## Comparison: Password vs Token

| Feature | Password Login | Token Login |
|---------|---------------|-------------|
| Security | ❌ Password exposed | ✅ Token can be revoked |
| Revocation | ❌ Must change password | ✅ Delete token only |
| Multiple Apps | ❌ Same password | ✅ Different tokens |
| Expiration | ✅ Never expires | ⚠️ May expire (Bearer) |
| Setup | ✅ Easier | ⚠️ Requires token generation |

## Migration Path

**Current (insecure):**

```python
# .env file
TAIGA_PASSWORD=my_password  # ❌ Security risk
```

**Step 1: Get token from password login**

```python
result = login(username="ahojukka5", password="my_password")
session_id = result["session_id"]

# Extract token (implementation needed)
token = extract_token(session_id)
print(f"Your token: {token}")
```

**Step 2: Store token instead**

```python
# .env file
TAIGA_AUTH_TOKEN=your_token_here  # ✅ More secure
# Remove TAIGA_PASSWORD line
```

**Step 3: Use token for authentication**

```python
result = login_with_token(
    host="https://api.taiga.io",
    auth_token=os.getenv("TAIGA_AUTH_TOKEN")
)
```

## ✨ NEW: MCP Tools for Token Management

The following MCP tools are now available for secure authentication:

### `save_session_token`

Extracts and saves the authentication token from an active session.

```python
# After logging in with password
session = login(host="https://api.taiga.io", username="user", password="pass")
session_id = session["session_id"]

# Save the token
save_session_token(session_id)
# Returns: {"status": "success", "message": "Token saved...", "cache_location": "..."}
```

### `login_from_cache`

Login using a previously saved token (no password needed!)

```python
# Login with cached token
session = login_from_cache(host="https://api.taiga.io")
session_id = session["session_id"]
# No password required!
```

### `login_with_token`

Login with an explicit token (Bearer or Application).

```python
# Using application token
session = login_with_token(
    host="https://api.taiga.io",
    auth_token="your_application_token",
    token_type="Application"
)
```

### `list_cached_tokens_tool`

List all cached tokens (without revealing token values).

```python
result = list_cached_tokens_tool()
# Returns: {"status": "success", "count": 2, "tokens": {...}}
```

### `delete_cached_token`

Delete a cached token for a specific host.

```python
result = delete_cached_token(host="https://api.taiga.io")
# Returns: {"status": "success", "message": "Token deleted..."}
```

## Cache Security

Tokens are stored securely with:

- **Location**: `~/.cache/taiga-mcp/` (Linux/macOS) or `%LOCALAPPDATA%/taiga-mcp/` (Windows)
- **Permissions**: `0600` (user read/write only)
- **Format**: JSON with host, token, type, and user_id
- **Encryption**: File system permissions (no additional encryption needed)

## Future Enhancement Ideas

1. **Token refresh automation**
   - Automatically refresh Bearer tokens before expiration
   - Implement in TaigaClientWrapper

2. **Keyring integration** (Optional)
   - Store tokens in OS keychain for extra security
   - Cross-platform support (keyring library)

3. **Multi-account management**
   - Manage multiple tokens for different Taiga instances
   - Easy switching between accounts

## Next Steps

1. **Try token login now**:

   ```python
   # First, login normally to get a token
   login_result = login(host="https://api.taiga.io", username="ahojukka5", password="...")
   
   # Then you can use the token later (after window reload, etc.)
   token_result = login_with_token(host="https://api.taiga.io", auth_token="...", user_id=157593)
   ```

2. **Reload VS Code window** to pick up new MCP tools

3. **Test the new `login_with_token` tool**

4. **Remove password from `.env` file** once token works
