# NSYC Scripts

## Claude Desktop Config Generator

`generate_claude_config.py` - Cross-platform script to generate and install Claude Desktop configuration for NSYC MCP servers.

### Usage

```bash
# Generate config file only
python3 scripts/generate_claude_config.py

# Validate server paths
python3 scripts/generate_claude_config.py --validate

# Generate and install to Claude Desktop
python3 scripts/generate_claude_config.py --install

# Install without backing up existing config
python3 scripts/generate_claude_config.py --install --no-backup

# Generate to custom location
python3 scripts/generate_claude_config.py --output /path/to/config.json
```

### Platform Support

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Linux**: `~/.config/claude_desktop_config.json`

### Features

- Automatically discovers MCP servers in the project
- Generates absolute paths for cross-platform compatibility
- Validates server entry points before installation
- Backs up existing Claude Desktop config
- Supports custom output locations