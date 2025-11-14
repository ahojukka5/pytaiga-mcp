# Documentation Structure

This directory contains all documentation for Taiga MCP Bridge, organized by audience.

## Directory Structure

```
docs/
├── index.md                   # Main documentation landing page
├── user_guide/                # 📘 End-user documentation
│   ├── README.md             # User guide overview
│   ├── installation.md       # Installation instructions
│   ├── quickstart_simple.md  # 2-minute quick start
│   ├── quickstart.md         # Detailed getting started guide
│   ├── authentication.md     # Authentication methods and security
│   ├── token_authentication.md # Application token usage
│   └── transport.md          # Transport modes (stdio vs SSE)
├── developer_guide/           # 🔧 Developer documentation
│   ├── README.md             # Developer guide overview
│   ├── architecture.md       # System architecture and design
│   ├── auth_module.md        # Authentication module details
│   ├── taiga_client.md       # TaigaClientWrapper documentation
│   ├── mcp_sdk_reference.md  # MCP Python SDK reference
│   ├── taiga_rest_api_reference.md # Taiga API reference
│   └── api/                  # Auto-generated API documentation
└── project_management/        # 📋 Internal project documentation
    ├── README.md             # Project management overview
    ├── api_coverage_analysis.md # API implementation tracking
    └── archive/              # Historical development docs
        ├── BUG_FIX.md
        ├── REFACTORING.md
        ├── AUTHENTICATION_SIMPLIFICATION.md
        ├── SECURE_AUTH_IMPLEMENTATION.md
        ├── TASK_API_FIX.md
        └── TEST_SUMMARY.md
```

## Documentation by Audience

### 📘 For End Users

**Location**: `user_guide/`

Documentation for people who want to **use** the Taiga MCP Bridge:

- How to install and configure the server
- Authentication setup and best practices
- Choosing the right transport mode
- Quick start guides for getting up and running

**Start here**: [User Guide](user_guide/README.md)

### 🔧 For Developers

**Location**: `developer_guide/`

Documentation for people who want to **contribute** or **understand** the codebase:

- System architecture and design decisions
- Module-level documentation
- API references (both Taiga and MCP)
- Development setup and testing
- Code quality standards

**Start here**: [Developer Guide](developer_guide/README.md)

### 📋 For Project Management

**Location**: `project_management/`

Internal documentation tracking development progress:

- API coverage analysis
- Historical bug fixes and refactoring notes
- Development decisions and rationale

**Note**: This is internal documentation not relevant to end users or external contributors.

## Community Documentation

Community and governance documents are in the repository root:

- `../CODE_OF_CONDUCT.md` - Community guidelines
- `../CONTRIBUTING.md` - How to contribute
- `../SECURITY.md` - Security policy and reporting
- `../README.md` - Project overview and quick reference

## Navigation

### Quick Links

- **New users**: Start with [Quick Start (Simple)](user_guide/quickstart_simple.md)
- **Setting up**: See [Installation Guide](user_guide/installation.md)
- **Contributing**: Read [Developer Guide](developer_guide/README.md)
- **Understanding the code**: Check [Architecture](developer_guide/architecture.md)

### Documentation Website

The documentation is built using MkDocs Material and published at:
<https://talhaorak.github.io/pytaiga-mcp>

Build locally:

```bash
# Install MkDocs
poetry install

# Serve documentation locally
poetry run mkdocs serve

# Build static site
poetry run mkdocs build
```

## Naming Conventions

All documentation files use lowercase with underscores for consistency:

- ✅ `quickstart_simple.md`
- ✅ `token_authentication.md`
- ✅ `api_coverage_analysis.md`
- ❌ ~~`QUICKSTART.md`~~
- ❌ ~~`TOKEN_AUTH_GUIDE.md`~~
- ❌ ~~`API_COVERAGE_ANALYSIS.md`~~

## Contributing to Documentation

When adding or updating documentation:

1. **Choose the right directory**:
   - End-user features → `user_guide/`
   - Technical/API details → `developer_guide/`
   - Internal tracking → `project_management/`

2. **Use lowercase filenames** with underscores

3. **Update navigation**:
   - Add to appropriate README.md file
   - Update `mkdocs.yml` if needed
   - Update this file if adding new sections

4. **Follow markdown best practices**:
   - Use proper heading hierarchy
   - Add code examples where helpful
   - Link to related documentation

5. **Test locally**:

   ```bash
   poetry run mkdocs serve
   ```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.
