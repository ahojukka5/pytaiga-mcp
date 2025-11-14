# Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Step 1: Get Your Application Token

1. **Login to Taiga web interface**
   - Go to <https://tree.taiga.io> (or your company's Taiga URL)
   - Login with your username and password

2. **Open User Settings**
   - Click your profile icon/avatar in the top-right corner
   - Select "Settings" from the dropdown menu

3. **Navigate to Applications**
   - In the left sidebar, find "Applications" or "API Tokens"
   - Click on it

4. **Create New Application Token**
   - Click the button: "Create new application" or "Generate Token"
   - Give it a descriptive name:
     - "MCP Integration"
     - "Development Token"
     - "My Computer"
   - Click "Create" or "Generate"

5. **Copy the Token**
   - A long token will appear (looks like: `eyJ0eXAiOiJKV1Qi...`)
   - **Copy it immediately** - you won't be able to see it again!
   - ⚠️ Keep this secret like a password

### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
TAIGA_HOST=https://api.taiga.io
TAIGA_AUTH_TOKEN=your_application_token_here
TAIGA_TOKEN_TYPE=Application
```

**That's it!** No password storage, no complex setup.

### Step 3: Use It

#### In Claude Desktop or Cursor

Add to your MCP settings:

```json
{
  "mcpServers": {
    "taiga": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "-m",
        "pytaiga_mcp.server"
      ],
      "cwd": "/path/to/pytaiga-mcp",
      "env": {
        "TAIGA_HOST": "https://api.taiga.io",
        "TAIGA_AUTH_TOKEN": "your_application_token_here",
        "TAIGA_TOKEN_TYPE": "Application"
      }
    }
  }
}
```

#### In Python Code

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Login with token
session = client.call_tool("login_with_token", {
    "host": os.getenv("TAIGA_HOST"),
    "auth_token": os.getenv("TAIGA_AUTH_TOKEN"),
    "token_type": "Application"
})

session_id = session["session_id"]

# Now use the session_id for all API calls
projects = client.call_tool("list_projects", {
    "session_id": session_id
})
```

## ✅ You're Done

Now you can:

- ✅ Create projects, epics, user stories, tasks
- ✅ Manage sprints and milestones
- ✅ Track issues and bugs
- ✅ All without ever storing a password!

## 🔒 Security Benefits

- **No passwords in config files** - Only revokable tokens
- **Token scoped to application** - Limited access scope
- **Easy to rotate** - Generate new token anytime
- **Revoke anytime** - Delete token in Taiga settings

## 🆘 Troubleshooting

### "Invalid token"

- Token may have been revoked
- Generate a new application token in Taiga settings
- Update your `.env` file

### "No projects found"

- Your Taiga account might not have any projects yet
- Create a project in Taiga web interface first
- Or use the `create_project` MCP tool

### "Permission denied"

- Your user account may not have necessary permissions
- Check with your Taiga admin
- Or use an admin account's application token

## 📚 Next Steps

- See [README.md](README.md) for complete documentation
- See [TOKEN_AUTH_GUIDE.md](TOKEN_AUTH_GUIDE.md) for advanced authentication options
- See [examples/](examples/) for more code examples

## 💡 Pro Tips

1. **Multiple Environments**: Create different tokens for dev/staging/prod
2. **Team Access**: Each team member should have their own token
3. **CI/CD**: Use application tokens for automated workflows
4. **Rotation**: Generate new tokens every few months for security

---

**Remember**: Application tokens are like API keys - keep them secret, never commit them to git!
