# Examples

This folder contains example scripts demonstrating different authentication and usage patterns.

## 🚀 Quick Start

### `simple_token_auth.py` - **START HERE!**

The simplest way to authenticate with Taiga using an Application Token.

**No passwords, no caching, just copy/paste your token and go!**

```bash
# 1. Get token from Taiga (Settings → Applications)
# 2. Add to .env file:
#    TAIGA_AUTH_TOKEN=your_token_here
# 3. Run the example
python examples/simple_token_auth.py
```

## 🔐 Advanced Examples

### `secure_authentication.py`

Comprehensive demonstration of all authentication methods:

1. **First-time setup** - Login with password and cache token
2. **Secure login** - Use cached token (no password)
3. **Application token** - Use Taiga application token
4. **Token management** - List and delete cached tokens

```bash
python examples/secure_authentication.py
```

**Use Cases:**

- Learning different authentication patterns
- Managing multiple Taiga instances
- Understanding token caching workflow

## 📋 Choosing the Right Method

### Use `simple_token_auth.py` if you want

- ✅ Simplest setup (just copy/paste token)
- ✅ No password storage ever
- ✅ Production-ready authentication
- ✅ Easy token rotation

### Use `secure_authentication.py` if you

- 🔍 Want to understand all authentication options
- 🔍 Need to manage multiple Taiga accounts
- 🔍 Prefer session token caching over Application tokens
- 🔍 Are migrating from password-based auth

## 🔧 Setup

All examples require:

1. **Environment configuration**:

   ```bash
   cp ../.env.example ../.env
   # Edit .env with your values
   ```

2. **Dependencies installed**:

   ```bash
   cd ..
   ./install.sh
   ```

## 💡 Best Practices

1. **Never commit tokens or passwords** to version control
2. **Use Application Tokens** for production (most secure)
3. **Rotate tokens regularly** (every few months)
4. **One token per environment** (dev, staging, prod)
5. **Revoke old tokens** when no longer needed

## 🆘 Troubleshooting

### "TAIGA_AUTH_TOKEN not found"

**Solution**: Create `.env` file with your token:

```bash
cp ../.env.example ../.env
# Edit .env and add your token
```

### "Authentication failed"

**Possible causes:**

- Token has been revoked in Taiga
- Token copied incorrectly (extra spaces?)
- Wrong host URL
- Network connectivity issues

**Solution**: Generate a new Application Token in Taiga

### "No projects found"

**This is normal** if your Taiga account doesn't have projects yet.

**Solution**: Create a project in Taiga web interface or use the `create_project` MCP tool

## 📚 More Information

- [QUICKSTART.md](../QUICKSTART.md) - 2-minute setup guide
- [TOKEN_AUTH_GUIDE.md](../TOKEN_AUTH_GUIDE.md) - Detailed authentication documentation
- [README.md](../README.md) - Complete project documentation
