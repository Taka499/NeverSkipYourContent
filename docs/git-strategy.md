# Git Repository Strategy - NSYC (Never Skip Your Content)

## Branching Model

We'll use a **simplified Git Flow** approach suitable for a distributed MCP system with independent server development.

### Branch Structure

```
main (production-ready releases)
├── develop (integration branch)
├── feature/server-* (MCP server implementations)
├── feature/client-* (orchestrator client features)
├── feature/enhancement-* (specific improvements)
├── hotfix/* (critical fixes)
└── docs/* (documentation updates)
```

### Branch Descriptions

#### `main` Branch
- **Purpose**: Production-ready, stable releases
- **Protection**: Protected branch, no direct commits
- **Merges from**: `develop` branch only
- **Tagging**: All releases tagged with version numbers
- **Status**: Always deployable with Claude Desktop

#### `develop` Branch  
- **Purpose**: Integration branch for ongoing development
- **Merges from**: Feature branches, server branches
- **Merges to**: `main` for releases
- **Status**: Latest development state, may be unstable

#### `feature/server-*` Branches
- **Purpose**: Individual MCP server implementations
- **Naming**: `feature/server-web-search`, `feature/server-page-analyzer`, etc.
- **Lifespan**: Duration of server development
- **Base**: `develop`
- **Merge to**: `develop`

#### `feature/client-*` Branches
- **Purpose**: MCP client orchestrator features
- **Naming**: `feature/client-orchestrator`, `feature/client-cli`, etc.
- **Lifespan**: Medium-lived (1-2 weeks)
- **Base**: `develop`
- **Merge to**: `develop`

#### `feature/enhancement-*` Branches
- **Purpose**: Specific features or improvements
- **Naming**: `feature/enhancement-error-handling`, `feature/enhancement-caching`
- **Lifespan**: Short-lived (1-3 days)
- **Base**: `develop`
- **Merge to**: `develop`

#### `hotfix/*` Branches
- **Purpose**: Critical bug fixes for production
- **Naming**: `hotfix/fix-mcp-connection`, `hotfix/fix-api-timeout`
- **Base**: `main`
- **Merge to**: Both `main` and `develop`

#### `docs/*` Branches
- **Purpose**: Documentation updates
- **Naming**: `docs/update-roadmap`, `docs/api-documentation`
- **Base**: `develop`
- **Merge to**: `develop`

## Commit Message Convention

We'll use **Conventional Commits** format for clear, searchable history.

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Scopes
- **query-gen**: Query Generator MCP server
- **web-search**: Web Search MCP server
- **page-analyzer**: Page Analyzer MCP server
- **llm-filter**: LLM Filter MCP server
- **client**: MCP client orchestrator
- **cli**: Command line interface
- **config**: Configuration files
- **deps**: Dependencies
- **mcp**: MCP protocol related changes

### Examples
```bash
feat(web-search): implement multi-provider search with fallback
fix(query-gen): handle empty category parameters correctly
docs(roadmap): update completion status for web search server
refactor(client): simplify server connection management
chore(deps): update mcp package to latest version
test(page-analyzer): add content extraction test cases
```

## Release Strategy

### Version Numbering
We'll use **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible MCP API changes
- **MINOR**: New MCP servers or major features (backward compatible)
- **PATCH**: Bug fixes and minor improvements (backward compatible)

### Release Schedule
- **v0.1.0**: Query Generator server completion
- **v0.2.0**: Web Search server completion (current milestone)
- **v0.3.0**: Page Analyzer server completion
- **v0.4.0**: MCP Client orchestrator completion
- **v0.5.0**: LLM Filter server completion
- **v1.0.0**: Full system integration and production readiness

### Release Process
1. **Feature complete** on `develop`
2. **Create release branch**: `release/v0.x.0`
3. **Final testing** and integration verification
4. **Merge to main** and tag release
5. **Merge back to develop**
6. **Create GitHub release** with changelog

## Workflow Examples

### Starting a New MCP Server
```bash
# From develop branch
git checkout develop
git pull origin develop
git checkout -b feature/server-page-analyzer
# Work on page analyzer server...
git add .
git commit -m "feat(page-analyzer): implement content extraction from HTML pages"
git push origin feature/server-page-analyzer
# Create PR to develop when ready
```

### Client Development
```bash
# From develop branch
git checkout develop
git pull origin develop
git checkout -b feature/client-orchestrator
# Build orchestrator functionality...
git add .
git commit -m "feat(client): implement MCP server coordination workflow"
git push origin feature/client-orchestrator
# Create PR to develop
```

### Quick Enhancement
```bash
# From develop branch
git checkout develop
git pull origin develop
git checkout -b feature/enhancement-error-handling
# Add better error handling...
git add .
git commit -m "feat(web-search): add retry logic for failed API requests"
git push origin feature/enhancement-error-handling
# Create PR to develop
```

### Hotfix Process
```bash
# From main branch
git checkout main
git pull origin main
git checkout -b hotfix/fix-mcp-connection
# Fix the connection issue...
git add .
git commit -m "fix(mcp): resolve stdio transport connection timeout"
git push origin hotfix/fix-mcp-connection
# Create PR to main, then merge to develop
```

### Documentation Update
```bash
# From develop branch
git checkout develop
git pull origin develop
git checkout -b docs/update-implementation-progress
# Update documentation...
git add .
git commit -m "docs(progress): add web search server completion report"
git push origin docs/update-implementation-progress
# Create PR to develop
```

## Repository Setup Commands

### Initial Setup
```bash
# Initialize repository
git init
git branch -M main

# Create develop branch
git checkout -b develop

# Add all files
git add .
git commit -m "feat(project): initial NSYC MCP system setup

- Set up distributed MCP architecture with hub-and-spoke design
- Implement Query Generator MCP server with keyword generation
- Create project structure for web search, page analyzer servers
- Add comprehensive documentation and development roadmap
- Configure uv environment with Python 3.10+ requirements
- Include Claude Desktop MCP integration configuration"

# Push to remote (when ready)
git remote add origin <repository-url>
git push -u origin main
git push -u origin develop
```

### Branch Protection Rules (GitHub)
When setting up the remote repository:

1. **Protect `main` branch**:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date
   - Restrict pushes to matching branches

2. **Protect `develop` branch**:
   - Require pull request reviews (optional)
   - Allow force pushes (for rebasing)

## File Organization

### `.gitignore` Contents
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# uv lock files
.venv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment files
.env
.env.local
.env.*.local

# API Keys and Secrets
*.key
secrets/
credentials/

# Logs
*.log
logs/

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# MCP specific
mcp_servers.log
server_connections.log
```

## Collaboration Guidelines

### Pull Request Process
1. **Create feature branch** from `develop`
2. **Implement changes** with clear commits
3. **Test MCP server independently** before creating PR
4. **Write descriptive PR title** and description
5. **Link related issues** if applicable
6. **Request review** (self-review for solo project)
7. **Merge using squash** for clean history

### Code Review Checklist
- [ ] MCP server follows protocol standards
- [ ] All tests pass independently
- [ ] Documentation updated if needed
- [ ] No API keys or secrets committed
- [ ] Error handling implemented
- [ ] Type hints and validation added
- [ ] Claude Desktop integration tested

## MCP-Specific Considerations

### Server Independence
- Each MCP server developed in separate branches
- No direct imports between servers
- Independent testing and deployment
- Separate `pyproject.toml` for each server

### Integration Testing
- Test individual servers with MCP stdio protocol
- Verify Claude Desktop integration works
- Validate server communication through orchestrator
- Performance testing with multiple concurrent requests

### Configuration Management
- Environment variables for API keys
- Separate configuration for each server
- Claude Desktop MCP configuration updates
- Development vs production environment handling

## Maintenance Schedule

### Weekly Tasks
- Review and merge completed server implementations
- Update development roadmap and progress documentation
- Check for dependency updates across all servers
- Clean up merged feature branches

### Monthly Tasks
- Create release if milestone servers are complete
- Review and update architecture documentation
- Archive old branches and clean repository
- Update Claude Desktop integration guides

### Per-Server Completion
- Comprehensive testing of MCP tools
- Documentation update
- Integration with existing servers
- Performance benchmarking

This strategy provides structure for the distributed MCP architecture while maintaining independence between server implementations and clear integration pathways.