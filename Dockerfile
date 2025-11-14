# Taiga MCP Bridge - Docker Image
# Lightweight Python image for running the MCP server

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual environment (we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY pytaiga_mcp/ ./pytaiga_mcp/
COPY README.md LICENSE ./

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TAIGA_TRANSPORT=sse \
    FASTMCP_HOST=0.0.0.0 \
    FASTMCP_PORT=8000

# Expose default SSE port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the server
CMD ["python", "-m", "pytaiga_mcp.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
