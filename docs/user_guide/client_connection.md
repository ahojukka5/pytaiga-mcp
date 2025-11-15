# Connecting MCP Clients to Taiga MCP Bridge

This guide shows you how to connect various MCP clients to your running Taiga MCP Bridge server.

## Prerequisites

Before connecting a client, ensure:

1. ✅ You have authenticated with Taiga (see README.md Authentication section)
2. ✅ Your `.env` file contains valid credentials:

   ```bash
   TAIGA_API_URL=https://api.taiga.io
   TAIGA_AUTH_TOKEN=your-token-here
   # OR
   TAIGA_USERNAME=your-username
   TAIGA_PASSWORD=your-password
   ```

3. ✅ The server is installed: `poetry install`

## 🎯 Quick Start: Claude Desktop (Most Common)

### Step 1: Find Your Configuration File

**macOS:**

```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**

```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**

```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add Taiga MCP Bridge Configuration

Open the config file and add this configuration:

```json
{
  "mcpServers": {
    "taiga": {
      "command": "poetry",
      "args": ["run", "pytaiga-mcp"],
      "cwd": "/home/juajukka/dev/pytaiga-mcp",
      "env": {
        "TAIGA_API_URL": "https://api.taiga.io"
      }
    }
  }
}
```

**⚠️ Important:** Replace `/home/juajukka/dev/pytaiga-mcp` with the **absolute path** to your pytaiga-mcp directory.

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. The Taiga MCP Bridge will be available!

### Step 4: Verify Connection

In Claude Desktop, you should see:

- 🔌 A "taiga" server connection indicator
- 🛠️ Available tools (100+ tools for managing Taiga projects)

Try asking Claude: "List all my Taiga projects" or "What tools do you have for Taiga?"

## 🔧 Other MCP Clients

### Cursor IDE

Add to your Cursor settings (`~/.cursor/config.json` or via Settings UI):

```json
{
  "mcp": {
    "servers": {
      "taiga": {
        "command": "poetry",
        "args": ["run", "pytaiga-mcp"],
        "cwd": "/home/juajukka/dev/pytaiga-mcp",
        "env": {
          "TAIGA_API_URL": "https://api.taiga.io"
        }
      }
    }
  }
}
```

### VS Code (with MCP extension)

In VS Code settings or `settings.json`:

```json
{
  "mcp.servers": {
    "taiga": {
      "command": "poetry",
      "args": ["run", "pytaiga-mcp"],
      "cwd": "/home/juajukka/dev/pytaiga-mcp",
      "env": {
        "TAIGA_API_URL": "https://api.taiga.io"
      }
    }
  }
}
```

### Custom MCP Client (Python)

If you're building your own MCP client:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_taiga():
    server_params = StdioServerParameters(
        command="poetry",
        args=["run", "pytaiga-mcp"],
        cwd="/home/juajukka/dev/pytaiga-mcp",
        env={
            "TAIGA_API_URL": "https://api.taiga.io"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            
            # Call a tool
            result = await session.call_tool("taiga_list_projects", {})
            print(result)

asyncio.run(connect_to_taiga())
```

## 🐳 Docker-based Connection (SSE Transport)

If you're running the server in Docker with SSE transport:

```json
{
  "mcpServers": {
    "taiga": {
      "url": "http://localhost:8000",
      "transport": "sse"
    }
  }
}
```

Start the Docker server:

```bash
docker-compose up -d
```

## 🔍 Troubleshooting

### "Server not responding" or "Connection failed"

1. **Check server starts correctly:**

   ```bash
   cd /home/juajukka/dev/pytaiga-mcp
   poetry run pytaiga-mcp
   ```

   You should see: `Server ready for stdio communication...`

2. **Verify credentials:**

   ```bash
   cat .env
   ```

   Make sure `TAIGA_AUTH_TOKEN` or username/password are set.

3. **Test authentication:**

   ```bash
   poetry run pytaiga-mcp login --test
   ```

4. **Check logs:**
   - Server logs appear in the terminal where you ran `poetry run pytaiga-mcp`
   - Client logs vary by client (Claude Desktop: Help → View Logs)

### "Command 'poetry' not found"

The client can't find Poetry. Use the full path:

**Find Poetry path:**

```bash
which poetry
# Example output: /home/juajukka/.local/bin/poetry
```

**Update config with full path:**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "/home/juajukka/.local/bin/poetry",
      "args": ["run", "pytaiga-mcp"],
      "cwd": "/home/juajukka/dev/pytaiga-mcp"
    }
  }
}
```

### "Module not found" errors

Make sure you've installed the project:

```bash
cd /home/juajukka/dev/pytaiga-mcp
poetry install
```

### Authentication token expired

Refresh your token:

```bash
poetry run pytaiga-mcp login
```

Or generate a new application token in Taiga:

1. Go to <https://api.taiga.io/user-settings/applications>
2. Create new application token
3. Update `.env`:

   ```bash
   TAIGA_AUTH_TOKEN=your-new-token
   ```

## 📊 Verifying Connection

Once connected, try these commands in your MCP client (e.g., Claude):

1. **"List all my Taiga projects"**
   - Should return your 3 projects: JuliaFEM, OpenPFC, pytaiga-mcp

2. **"Show me the available Taiga tools"**
   - Should list 100+ tools for projects, tasks, stories, etc.

3. **"Get details about the pytaiga-mcp project"**
   - Should return project info (ID: 1750861, slug: ahojukka5-pytaiga-mcp)

4. **"List user stories in pytaiga-mcp"**
   - Should return user stories (or empty list if none exist)

## 🎯 Working with Multiple Projects

Remember: **One server connection = Access to ALL your projects!**

Your current projects:

- **JuliaFEM** (slug: `ahojukka5-juliafem`)
- **OpenPFC** (slug: `ahojukka5-openpfc`)
- **pytaiga-mcp** (slug: `ahojukka5-pytaiga-mcp`, ID: `1750861`)

Examples:

- "Create a task in JuliaFEM project"
- "List all user stories in OpenPFC"
- "Show me milestones for pytaiga-mcp"

The MCP client (Claude, etc.) will automatically use the correct `project_id` or `project_slug` parameter when calling tools.

## 🔐 Security Notes

- **Credentials**: Never commit `.env` file to version control
- **Auth Token**: Tokens are scoped to your Taiga account - treat them like passwords
- **Local Only**: The stdio transport is localhost-only by default (secure)
- **SSE Transport**: If using SSE, ensure it's behind a firewall or VPN for remote access

## 📚 Additional Resources

- **README.md**: Full documentation and architecture overview
- **QUICK_START.md**: Getting started guide
- **TOKEN_AUTH_GUIDE.md**: Detailed authentication setup
- **MCP_SDK.md**: Understanding the MCP protocol

## 💡 Pro Tips

1. **Keep server logs visible**: Run `poetry run pytaiga-mcp` in a dedicated terminal to see real-time activity

2. **Test before connecting**: Use `poetry run pytaiga-mcp login --test` to verify auth

3. **Use absolute paths**: Always use full paths in client configs (e.g., `/home/user/...`)

4. **Restart after config changes**: Most MCP clients need a restart to pick up config changes

5. **Check client logs**: If things don't work, check your MCP client's logs first

---

**Need Help?**

- 🐛 Report issues: <https://github.com/ahojukka5/pytaiga-mcp/issues>
- 📖 Read the docs: See README.md for detailed architecture and usage
- 💬 Check existing issues for common problems
