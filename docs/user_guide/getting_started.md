# Getting Started: Connecting AI Assistants to Your MCP Server

**This is the practical, end-to-end guide** for connecting AI assistants (like GitHub Copilot, Claude, etc.) to your running Taiga MCP server.

## 🎯 The Problem Everyone Faces

You've started the server:

```bash
poetry run pytaiga-mcp --transport sse --host 0.0.0.0 --port 8000
```

The server is running and shows:

```
Taiga MCP Bridge starting
Transport: sse
Server address: http://0.0.0.0:8000
Starting SSE server on 0.0.0.0:8000
Uvicorn running on http://127.0.0.1:8000
```

✅ **Server is working!**

❓ **But now what? How do you actually USE it?**

This guide answers that question with **real, tested steps**.

---

## 📋 Quick Answer: Three Ways to Connect

| Method | Best For | Setup Time | Recommended? |
|--------|----------|------------|--------------|
| **1. Claude Desktop** | End users, easiest | 5 min | ✅ **YES** |
| **2. VS Code + MCP Extension** | Developers using VS Code | 10 min | ⚠️ Experimental |
| **3. Custom Python Client** | Testing, automation | 15 min | For developers |

---

## Method 1: Claude Desktop (RECOMMENDED)

**This is the easiest and most reliable way to use your MCP server.**

### Step 1: Download Claude Desktop

- Go to: <https://claude.ai/download>
- Available for: macOS, Windows, Linux (free)

### Step 2: Configure MCP Server

Create or edit the configuration file:

**macOS:**

```bash
~/.config/Claude/claude_desktop_config.json
```

**Linux:**

```bash
~/.config/Claude/claude_desktop_config.json
```

**Windows:**

```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Add This Configuration

If using **SSE transport** (server on port 8000):

```json
{
  "mcpServers": {
    "taiga": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

If using **stdio transport** (default):

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

**⚠️ Important:** Replace `/home/juajukka/dev/pytaiga-mcp` with YOUR actual project path!

### Step 4: Restart Claude Desktop

Close and reopen the app completely.

### Step 5: Test It

In Claude Desktop, say:

- "List all my Taiga projects"
- "What tools do you have for Taiga?"
- "Create a task in pytaiga-mcp project"

**✅ You should see Claude accessing your Taiga projects!**

---

## Method 2: VS Code with GitHub Copilot (EXPERIMENTAL)

**Current Status:** GitHub Copilot doesn't natively support MCP servers yet, but there are experimental extensions.

### Option A: Use MCP-Client Extension

1. **Install the extension:**

   ```vscode-extensions
   m1self.mcp-client
   ```

2. **Create configuration file:**

   In your workspace: `.vscode/mcp.json`

   ```json
   {
     "taiga": {
       "url": "http://localhost:8000/sse",
       "transport": "sse"
     }
   }
   ```

3. **Reload VS Code:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Run: "Developer: Reload Window"

4. **Test:**
   - The extension should bridge MCP tools to GitHub Copilot
   - Try asking Copilot: "List my Taiga projects"

**⚠️ Note:** This is experimental. Results may vary.

### Option B: Use Cline (Claude-based VS Code Extension)

1. **Install Cline:**

   ```vscode-extensions
   saoudrizwan.claude-dev
   ```

2. **Configure Cline for MCP:**
   - Open Cline settings in VS Code
   - Add MCP server configuration
   - Cline has built-in MCP support

---

## Method 3: Python Test Script (FOR DEVELOPERS)

If you want to test the server directly or build your own client:

### Step 1: Create Test Script

Save as `test_mcp_tools.py`:

```python
#!/usr/bin/env python3
"""
Direct test of Taiga MCP server tools.
"""
import asyncio
import httpx
import json


async def call_mcp_tool(session_id: str, tool_name: str, arguments: dict):
    """Call an MCP tool via HTTP."""
    url = f"http://localhost:8000/messages/?session_id={session_id}"
    
    # MCP protocol message
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=message)
        return response.json()


async def main():
    """Test listing projects."""
    print("🧪 Testing Taiga MCP Server\n")
    
    # Get session ID from SSE endpoint first
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://localhost:8000/sse") as response:
            async for line in response.aiter_lines():
                if "session_id=" in line:
                    session_id = line.split("session_id=")[1].strip()
                    print(f"✅ Got session ID: {session_id}\n")
                    break
    
    # First: Login/authenticate
    print("🔐 Authenticating...")
    # Note: You need to implement authentication first
    # For now, this assumes you have TAIGA_AUTH_TOKEN in .env
    
    # Call list_projects tool
    print("📋 Listing projects...")
    result = await call_mcp_tool(
        session_id=session_id,
        tool_name="list_projects",
        arguments={"session_id": "your-session-id"}  # Replace with real session
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Run It

```bash
python test_mcp_tools.py
```

---

## 🔍 Troubleshooting

### "Server not responding"

1. **Check server is running:**

   ```bash
   curl http://localhost:8000/sse
   ```

   Should return: `event: endpoint` message

2. **Check ports:**

   ```bash
   lsof -i :8000
   ```

   Should show `python` process

3. **Check logs:**
   Look at terminal where server is running for error messages

### "Cannot connect from Claude Desktop"

1. **Check config file path:**

   ```bash
   # macOS/Linux
   cat ~/.config/Claude/claude_desktop_config.json
   ```

2. **Validate JSON:**
   - Must be valid JSON (no trailing commas)
   - Use <https://jsonlint.com/> to validate

3. **Check server URL:**
   - For local: `http://localhost:8000/sse`
   - NOT: `http://0.0.0.0:8000/sse` (won't work from clients)

### "No tools available in Claude"

1. **Restart Claude Desktop completely** (not just close window)

2. **Check Claude logs:**
   - Help → View Logs
   - Look for MCP connection errors

3. **Verify server has tools:**

   ```bash
   curl http://localhost:8000/sse
   ```

### VS Code Extension Issues

1. **Extension not loaded:**
   - Check: Extensions → MCP-Client → Enabled
   - Reload window: `Ctrl+Shift+P` → "Reload Window"

2. **Config not found:**
   - Ensure `.vscode/mcp.json` exists in workspace
   - Check file permissions

3. **Copilot doesn't see tools:**
   - This is experimental - may not work yet
   - Try Cline extension instead

---

## 📊 Verifying It Works

Once connected, try these test commands in your AI assistant:

### Test 1: List Projects

```
"List all my Taiga projects"
```

**Expected:** Should return your projects (e.g., JuliaFEM, OpenPFC, pytaiga-mcp)

### Test 2: Get Project Details

```
"Get details about the pytaiga-mcp project"
```

**Expected:** Project info with ID, name, slug, description

### Test 3: Create a Task

```
"Create a task in pytaiga-mcp project with subject 'Test MCP connection'"
```

**Expected:** New task created, returns task ID and details

### Test 4: List Available Tools

```
"What Taiga tools do you have available?"
```

**Expected:** List of 100+ tools like `list_projects`, `create_task`, `list_user_stories`, etc.

---

## 📝 Which Transport Mode Should I Use?

### Use **stdio** (default) if

- ✅ Using Claude Desktop
- ✅ Using Cursor IDE
- ✅ Running locally on same machine
- ✅ Want simplest setup

**Configuration:**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "poetry",
      "args": ["run", "pytaiga-mcp"],
      "cwd": "/path/to/pytaiga-mcp"
    }
  }
}
```

### Use **SSE** if

- ✅ Building web application
- ✅ Need remote access (server on different machine)
- ✅ Want to keep server running continuously
- ✅ Multiple clients connecting to same server

**Configuration:**

```json
{
  "mcpServers": {
    "taiga": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

**Start server:**

```bash
poetry run pytaiga-mcp --transport sse --port 8000
```

---

## 🎓 Understanding the Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Taiga Account                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │Project 1 │  │Project 2 │  │Project 3 │  ...             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
              ┌───────▼────────┐
              │  Taiga REST    │
              │     API        │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  Taiga MCP     │  ◄─── You start this
              │    Server      │       (poetry run pytaiga-mcp)
              │  (100+ tools)  │
              └───────┬────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼────┐  ┌────▼────┐  ┌───▼────┐
    │ Claude  │  │ VS Code │  │ Custom │
    │ Desktop │  │ Copilot │  │ Client │
    └─────────┘  └─────────┘  └────────┘
       ▲
       │
       └─── You configure this
            (~/.config/Claude/claude_desktop_config.json)
```

**Key Points:**

1. **One server** = access to **all your projects**
2. **Authentication** happens once (via .env file)
3. **Tools** accept `project_id` parameter to work with different projects
4. **No restart needed** to switch between projects

---

## 🚀 Next Steps

After connecting successfully:

1. **Read the tool documentation:**
   - See `docs/developer_guide/api/` for detailed tool reference
   - 100+ tools available for managing everything in Taiga

2. **Try common workflows:**
   - Create tasks across multiple projects
   - Update wiki pages
   - Manage sprints and milestones
   - Track issues and user stories

3. **Build automations:**
   - Use Python scripts with MCP client SDK
   - Create custom integrations
   - Automate project management tasks

---

## 💡 Pro Tips

1. **Keep server running:** Start it in a dedicated terminal or use tmux/screen

2. **Check logs:** Watch server terminal for authentication or API errors

3. **Use project slugs:** Easier than remembering project IDs
   - Example: `ahojukka5-pytaiga-mcp` instead of `1750861`

4. **Test with simple commands first:** List projects before trying complex operations

5. **Authentication matters:** Make sure `.env` has valid credentials

---

## 📚 Additional Resources

- **Main README:** Full documentation and architecture overview
- **CLIENT_CONNECTION.md:** Detailed connection guide for all clients
- **TOKEN_AUTH_GUIDE.md:** Authentication setup
- **API Documentation:** `docs/developer_guide/api/`

---

## ❓ Still Having Issues?

1. **Check GitHub Issues:** <https://github.com/ahojukka5/pytaiga-mcp/issues>
2. **Read troubleshooting sections** in this document
3. **Verify server logs** for error messages
4. **Test with curl** to ensure server responds
5. **Try stdio mode first** - it's simpler and more reliable

---

**Last Updated:** November 15, 2025  
**Tested With:** Claude Desktop 1.0, VS Code 1.95, MCP-Client extension 0.1.0
