# TaigaClientWrapper

## Overview

`TaigaClientWrapper` is a wrapper class around the `pytaigaclient.TaigaClient` that provides a simplified interface for authenticating and interacting with the Taiga API. It handles both username/password authentication and token-based authentication.

## Class: TaigaClientWrapper

### Location

`src/taiga_client.py`

### Constructor

```python
TaigaClientWrapper(host: str)
```

**Parameters:**

- `host` (str): The Taiga instance URL (e.g., "<https://api.taiga.io>" or "<http://localhost:9000>")

**Raises:**

- `ValueError`: If host is empty or None

**Example:**

```python
from src.taiga_client import TaigaClientWrapper

wrapper = TaigaClientWrapper("https://api.taiga.io")
```

### Methods

#### login()

Authenticates with Taiga using username and password.

```python
def login(self, username: str, password: str) -> bool
```

**Parameters:**

- `username` (str): Taiga username
- `password` (str): Taiga password

**Returns:**

- `bool`: True if login successful, False otherwise

**Side Effects:**

- Sets `self.api` to authenticated TaigaClient instance
- Sets `self.token` to the authentication token
- Sets `self.user_id` to the authenticated user's ID

**Exceptions:**

- Catches `TaigaException` and logs errors
- Catches general exceptions and logs them
- Returns False on any error

**Example:**

```python
wrapper = TaigaClientWrapper("https://api.taiga.io")
success = wrapper.login("myusername", "mypassword")
if success:
    print(f"Logged in as user {wrapper.user_id}")
    print(f"Token: {wrapper.token}")
```

#### login_with_token()

Authenticates with Taiga using an authentication token.

```python
def login_with_token(
    self, 
    auth_token: str, 
    user_id: Optional[int] = None,
    token_type: str = "user"
) -> bool
```

**Parameters:**

- `auth_token` (str): Taiga authentication token
- `user_id` (Optional[int]): User ID (optional, will be fetched if not provided)
- `token_type` (str): Either "user" (default) or "application"

**Returns:**

- `bool`: True if login successful, False otherwise

**Token Types:**

- `"user"`: Personal user token - requires user_id, fetches user information
- `"application"`: Application token - no user_id needed, skips user info

**Side Effects:**

- Sets `self.api` to authenticated TaigaClient instance
- Sets `self.token` to the provided token
- For user tokens: sets `self.user_id` (fetches if not provided)
- For application tokens: leaves `self.user_id` as None

**Example (User Token):**

```python
wrapper = TaigaClientWrapper("https://api.taiga.io")
success = wrapper.login_with_token(
    auth_token="abc123...",
    user_id=42,
    token_type="user"
)
```

**Example (Application Token):**

```python
wrapper = TaigaClientWrapper("https://api.taiga.io")
success = wrapper.login_with_token(
    auth_token="xyz789...",
    token_type="application"
)
```

#### is_authenticated()

Checks if the client is currently authenticated.

```python
def is_authenticated(self) -> bool
```

**Returns:**

- `bool`: True if authenticated (has api client and token), False otherwise

**Example:**

```python
if wrapper.is_authenticated():
    print("Ready to make API calls")
else:
    print("Need to login first")
```

#### ensure_authenticated()

Raises an exception if not authenticated.

```python
def ensure_authenticated(self) -> None
```

**Raises:**

- `ValueError`: If not authenticated (no api client or no token)

**Example:**

```python
def some_api_operation(wrapper):
    wrapper.ensure_authenticated()  # Raises if not logged in
    # Safe to use wrapper.api here
    return wrapper.api.projects.list()
```

### Attributes

#### api

- **Type:** `Optional[TaigaClient]`
- **Description:** The authenticated pytaigaclient TaigaClient instance
- **Set by:** `login()` or `login_with_token()`
- **Used for:** Making actual API calls

#### token

- **Type:** `Optional[str]`
- **Description:** The authentication token
- **Set by:** `login()` or `login_with_token()`

#### user_id

- **Type:** `Optional[int]`
- **Description:** The authenticated user's ID
- **Set by:** `login()` or `login_with_token()` (for user tokens)
- **Note:** None for application tokens

#### host

- **Type:** `str`
- **Description:** The Taiga instance URL

## Authentication Flow

### Username/Password Authentication

```python
# 1. Create wrapper
wrapper = TaigaClientWrapper("https://api.taiga.io")

# 2. Login with credentials
if wrapper.login("username", "password"):
    # 3. Now authenticated and ready to use
    print(f"Token: {wrapper.token}")
    print(f"User ID: {wrapper.user_id}")
    
    # 4. Make API calls
    projects = wrapper.api.projects.list()
```

### Token Authentication (User Token)

```python
# 1. Create wrapper
wrapper = TaigaClientWrapper("https://api.taiga.io")

# 2. Login with token
if wrapper.login_with_token("your-token-here", user_id=42):
    # 3. Authenticated with user context
    projects = wrapper.api.projects.list()
```

### Token Authentication (Application Token)

```python
# 1. Create wrapper
wrapper = TaigaClientWrapper("https://api.taiga.io")

# 2. Login with application token
if wrapper.login_with_token("app-token-here", token_type="application"):
    # 3. Authenticated without user context
    # Good for system operations
    projects = wrapper.api.projects.list()
```

## Error Handling

The wrapper catches exceptions and returns False on authentication failures:

```python
wrapper = TaigaClientWrapper("https://api.taiga.io")

# Bad credentials - returns False
if not wrapper.login("wrong", "credentials"):
    print("Login failed")

# Invalid token - returns False  
if not wrapper.login_with_token("invalid-token"):
    print("Token authentication failed")

# Must authenticate before use
try:
    wrapper.ensure_authenticated()
except ValueError:
    print("Not authenticated!")
```

## Logging

The wrapper uses Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)
```

**Log Levels:**

- `INFO`: Successful operations (login, initialization)
- `ERROR`: Failed operations (authentication failures, exceptions)

**Example Log Output:**

```
INFO - TaigaClientWrapper initialized for host: https://api.taiga.io
INFO - Attempting login for user 'myuser' on https://api.taiga.io
INFO - Login successful for user 'myuser'. User ID: 42
```

## Thread Safety

⚠️ **Warning:** TaigaClientWrapper is not thread-safe. Each thread should create its own instance.

## Best Practices

1. **Always check authentication status:**

   ```python
   if wrapper.is_authenticated():
       # Safe to proceed
   ```

2. **Use ensure_authenticated() in functions:**

   ```python
   def get_projects(wrapper):
       wrapper.ensure_authenticated()
       return wrapper.api.projects.list()
   ```

3. **Store tokens securely:**

   ```python
   # Don't hardcode tokens
   token = os.environ.get("TAIGA_TOKEN")
   wrapper.login_with_token(token)
   ```

4. **Handle authentication failures:**

   ```python
   if not wrapper.login(username, password):
       raise RuntimeError("Failed to authenticate with Taiga")
   ```

## See Also

- [Authentication Module](auth.md) - Higher-level authentication functions
- [Common Module](common.md) - Session management
- [Taiga API Documentation](https://docs.taiga.io/api.html)
