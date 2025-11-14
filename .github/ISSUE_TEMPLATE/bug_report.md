---
name: Bug Report
about: Report a bug to help us improve Taiga MCP Bridge
title: '[BUG] '
labels: 'bug'
assignees: ''

---

## Bug Description

<!-- A clear and concise description of what the bug is -->

## Environment

**Taiga MCP Bridge Version:**
<!-- e.g., 0.1.0 or git commit hash -->

**Python Version:**
<!-- Run: python --version -->

**Operating System:**
<!-- e.g., Ubuntu 22.04, macOS 14.0, Windows 11 -->

**Taiga Instance:**
<!-- e.g., tree.taiga.io, self-hosted version X.Y.Z -->

**Transport Mode:**
<!-- stdio or SSE -->

**MCP Client:**
<!-- e.g., Claude Desktop, VS Code Extension, Custom -->

## Steps to Reproduce

1.
2.
3.
4.

## Expected Behavior

<!-- What you expected to happen -->

## Actual Behavior

<!-- What actually happened -->

## Error Messages

```
<!-- Paste any error messages, stack traces, or logs here -->
```

## Configuration

<!-- Share relevant configuration (remove sensitive data like tokens!) -->

**.env file:**

```bash
TAIGA_API_URL=https://...
TAIGA_TRANSPORT=stdio
# etc.
```

**MCP Client Config (if applicable):**

```json
{
  "mcpServers": {
    "taiga": {
      // your config
    }
  }
}
```

## Additional Context

<!-- Add any other context, screenshots, or information about the problem -->

## Possible Solution

<!-- Optional: If you have an idea of what might be causing the issue or how to fix it -->

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have included the Taiga MCP Bridge version
- [ ] I have included steps to reproduce the issue
- [ ] I have removed sensitive information (tokens, passwords, etc.)
