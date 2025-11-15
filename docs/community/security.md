# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (Recommended)
   - Go to <https://github.com/ahojukka5/pytaiga-mcp/security/advisories>
   - Click "Report a vulnerability"
   - Provide detailed information about the vulnerability

2. **Email**
   - Send details to: <ahojukka5@gmail.com>
   - Use subject line: "[SECURITY] Taiga MCP Bridge Vulnerability Report"

### What to Include

Please include the following information:

- Type of vulnerability
- Full paths of source files related to the issue
- Location of the affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability
- Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days of initial report
- **Fix Timeline**: Varies by severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium/Low: Next release cycle

### What to Expect

After submitting a vulnerability report:

1. **Acknowledgment**: We'll confirm receipt within 48 hours
2. **Assessment**: We'll evaluate the severity and impact
3. **Updates**: Regular status updates during investigation
4. **Resolution**:
   - If accepted: We'll work on a fix and coordinate disclosure
   - If declined: We'll explain why it's not considered a vulnerability
5. **Credit**: Security researchers will be credited (unless anonymity is requested)

### Security Best Practices

When using Taiga MCP Bridge:

- **Never hardcode credentials** in configuration files or code
- **Use application tokens** instead of username/password authentication
- **Store tokens securely** using environment variables or secure vaults
- **Rotate tokens regularly** (every 3-6 months recommended)
- **Use HTTPS** for all Taiga API connections
- **Keep dependencies updated** by regularly running `poetry update`
- **Review logs** for suspicious activity

### Disclosure Policy

- Vulnerabilities will be disclosed publicly after a fix is available
- We follow a coordinated disclosure process
- Public disclosure typically occurs 90 days after initial report or when a fix is released, whichever comes first
- Security researchers will be notified before public disclosure

## Security Updates

Security updates are announced via:

- GitHub Security Advisories
- Release notes
- Git commit messages with `[SECURITY]` prefix

To stay informed:

- Watch the repository for security advisories
- Subscribe to release notifications
- Check the CHANGELOG for security fixes
