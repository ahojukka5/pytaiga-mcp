# Transport Modes

Taiga MCP Bridge supports two transport protocols for client-server communication. This guide helps you choose and configure the right one.

## Overview

| Feature | stdio | SSE (HTTP) |
|---------|-------|------------|
| **Connection Type** | Process-based | Network-based |
| **Multiple Clients** | ❌ One per process | ✅ Multiple simultaneous |
| **Network Access** | ❌ Local only | ✅ Remote accessible |
| **Setup Complexity** | ⭐ Simple | ⭐⭐ Moderate |
| **Latency** | ⚡ Lowest | 🔄 Slight HTTP overhead |
| **Use Case** | Desktop, IDE | Web apps, distributed |

## stdio Transport (Default)

### What is stdio?

stdio (standard input/output) is a process-based transport where:

- The MCP server runs as a child process
- Communication happens through stdin/stdout pipes
- One client per server instance
- No network configuration needed

### When to Use stdio

✅ **Perfect for:**

- Claude Desktop integration
- VS Code extensions
- Cursor IDE
- Local automation scripts
- Single-user desktop applications
- Development and testing

❌ **Not suitable for:**

- Web applications
- Remote access
- Multiple simultaneous users
- Containerized deployments

### Starting stdio Server

```bash
# Method 1: Direct Python
python -m pytaiga_mcp.server

# Method 2: Using Poetry
poetry run python -m pytaiga_mcp.server

# Method 3: Using the run script
./run.sh
```

### Client Configuration

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taiga": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pytaiga-mcp",
      "env": {
        "PYTHONPATH": "/path/to/pytaiga-mcp"
      }
    }
  }
}
```

#### Python Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "src.server"],
    env=None
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use the session...
```

## SSE Transport (HTTP)

### What is SSE?

SSE (Server-Sent Events) is an HTTP-based transport where:

- The MCP server runs as an HTTP server
- Clients connect over the network
- Multiple clients can share one server
- Uses standard HTTP ports

### When to Use SSE

✅ **Perfect for:**

- Web applications
- Remote server access
- Multi-user environments
- Cloud deployments
- Docker/Kubernetes
- Microservices architecture

❌ **Not suitable for:**

- Simple desktop use (stdio is simpler)
- Environments where ports can't be opened

### Starting SSE Server

```bash
# Method 1: Direct Python
python -m pytaiga_mcp.server --transport sse --port 8000

# Method 2: Using Poetry
poetry run python -m pytaiga_mcp.server --transport sse --port 8000

# Method 3: Using the run script
./run.sh --sse --port 8000

# Method 4: Environment variable
export TAIGA_TRANSPORT=sse
export TAIGA_SSE_PORT=8000
python -m pytaiga_mcp.server
```

### Server Options

| Option | Default | Description |
|--------|---------|-------------|
| `--transport` | `stdio` | Transport mode: `stdio` or `sse` |
| `--port` | `8000` | HTTP port for SSE server |
| `--host` | `0.0.0.0` | Host to bind to |

### Client Configuration

#### HTTP Client

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8000") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use the session...
```

#### Web Application (JavaScript)

```javascript
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle MCP messages
};

// Send requests via POST
fetch('http://localhost:8000/messages', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
            name: 'list_projects',
            arguments: {session_id: 'xxx'}
        }
    })
});
```

## Production Deployment

### Docker (SSE)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install poetry && poetry install --no-dev

EXPOSE 8000

CMD ["poetry", "run", "python", "-m", "src.server", "--transport", "sse", "--port", "8000"]
```

Build and run:

```bash
docker build -t taiga-mcp .
docker run -p 8000:8000 taiga-mcp
```

### Docker Compose

```yaml
version: '3.8'

services:
  taiga-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TAIGA_TRANSPORT=sse
      - TAIGA_SSE_PORT=8000
      - TAIGA_HOST=https://tree.taiga.io
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taiga-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taiga-mcp
  template:
    metadata:
      labels:
        app: taiga-mcp
    spec:
      containers:
      - name: taiga-mcp
        image: taiga-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: TAIGA_TRANSPORT
          value: "sse"
        - name: TAIGA_SSE_PORT
          value: "8000"
---
apiVersion: v1
kind: Service
metadata:
  name: taiga-mcp
spec:
  selector:
    app: taiga-mcp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### systemd Service (Linux)

```ini
[Unit]
Description=Taiga MCP Bridge
After=network.target

[Service]
Type=simple
User=taiga-mcp
WorkingDirectory=/opt/taiga-mcp
Environment="TAIGA_TRANSPORT=sse"
Environment="TAIGA_SSE_PORT=8000"
ExecStart=/opt/taiga-mcp/.venv/bin/python -m pytaiga_mcp.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable taiga-mcp
sudo systemctl start taiga-mcp
sudo systemctl status taiga-mcp
```

## Security Considerations

### stdio Security

- ✅ **Process isolation**: Each client gets its own process
- ✅ **No network exposure**: Communication through pipes only
- ✅ **OS-level security**: Standard file permissions apply
- ⚠️ **Single user**: Not suitable for multi-user environments

### SSE Security

For production SSE deployments:

1. **Use HTTPS/TLS**:

   ```bash
   # Use a reverse proxy like nginx or traefik
   # Don't expose port 8000 directly
   ```

2. **Add Authentication**:

   ```python
   # Add authentication middleware
   from fastapi import Header, HTTPException
   
   async def verify_token(authorization: str = Header(...)):
       if not is_valid_token(authorization):
           raise HTTPException(status_code=401)
   ```

3. **Rate Limiting**:

   ```python
   # Already built-in per session
   # Configure in rate_limiter.py
   from src.server.rate_limiter import configure_rate_limit
   configure_rate_limit(requests_per_minute=100)
   ```

4. **Firewall Rules**:

   ```bash
   # Only allow specific IPs
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

## Performance Comparison

### Latency

| Transport | Avg Latency | Notes |
|-----------|-------------|-------|
| stdio | 1-5ms | Direct pipe communication |
| SSE (local) | 5-10ms | HTTP overhead minimal |
| SSE (remote) | 10-100ms | Depends on network |

### Throughput

| Transport | Requests/sec | Limiting Factor |
|-----------|--------------|-----------------|
| stdio | ~1000 | Process overhead |
| SSE | ~500 | HTTP parsing |

Both are more than adequate for typical MCP workloads.

### Resource Usage

| Transport | Memory | CPU | Notes |
|-----------|--------|-----|-------|
| stdio | Low | Low | One process per client |
| SSE | Medium | Low | Shared process |

## Troubleshooting

### stdio Issues

**Problem**: "Server process terminated unexpectedly"

```bash
# Check if Python path is correct
which python

# Verify server starts
python -m pytaiga_mcp.server
```

**Problem**: "Broken pipe error"

```bash
# Client disconnected unexpectedly
# Check client logs for errors
```

### SSE Issues

**Problem**: "Connection refused on port 8000"

```bash
# Check if port is in use
lsof -i :8000

# Try a different port
python -m pytaiga_mcp.server --transport sse --port 8001
```

**Problem**: "CORS errors in browser"

```python
# Add CORS middleware (for web clients)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Migration Guide

### stdio to SSE

If you're currently using stdio and want to switch to SSE:

1. **Update server command**:

   ```bash
   # Before
   python -m pytaiga_mcp.server
   
   # After
   python -m pytaiga_mcp.server --transport sse --port 8000
   ```

2. **Update client connection**:

   ```python
   # Before
   from mcp.client.stdio import stdio_client
   
   # After
   from mcp.client.sse import sse_client
   async with sse_client("http://localhost:8000") as (read, write):
       # Same code as before...
   ```

3. **Configure networking**: Ensure firewalls allow the port

### SSE to stdio

If you want to switch from SSE back to stdio:

1. **Stop the HTTP server**: Kill the SSE server process
2. **Update client**: Use `stdio_client` instead of `sse_client`
3. **Remove port configurations**: No longer needed

## Next Steps

- 🔐 Configure [Authentication](authentication.md)
- 🛠️ Explore [Available Tools](tools.md)
- 💡 See [Deployment Examples](../examples/deployment.md)
- ⚙️ Review [Configuration Options](configuration.md)
