# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NSYC (Never Skip Your Content) is an MCP-based content discovery system that automatically finds relevant data sources (official sites, RSS feeds, social media, APIs) for user-specified topics. The system uses a distributed MCP architecture with specialized servers coordinated by an orchestrator client.

## Development Commands

### Package Management (uv)
```bash
# Install all dependencies
uv sync

# Add dependency to main project
uv add package_name

# Add dependency to specific server
cd servers/query_generator && uv add package_name
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env
# Edit .env to add OPENAI_API_KEY=your_key_here
```

### Running MCP Servers
```bash
# Run query generator server (only working server currently)
python servers/query_generator/src/query_generator/server.py

# Future: Run other servers when implemented
python servers/web_search/src/web_search/server.py
python servers/page_analyzer/src/page_analyzer/server.py
```

### Claude Desktop Integration
Add to Claude Desktop config (`~/.claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "query_generator": {
      "command": "python",
      "args": ["/absolute/path/to/servers/query_generator/src/query_generator/server.py"]
    }
  }
}
```

## Architecture Overview

### MCP-Based Distributed Design
The system implements a **hub-and-spoke architecture** where:
- **MCP Client (Orchestrator)**: Coordinates workflow, aggregates results, provides unified API
- **MCP Servers**: Specialized services that handle specific tasks independently
- **Communication**: Servers communicate via MCP stdio protocol

### Current Server Implementation Status
- ✅ **Query Generator Server**: Fully implemented with keyword-based query generation
- ⏳ **Web Search Server**: Structure exists, implementation needed
- ⏳ **Page Analyzer Server**: Structure exists, implementation needed  
- ⏳ **LLM Filter Server**: Structure exists, implementation needed
- ⏳ **MCP Client**: All orchestrator files are empty stubs

### Key Directories
- `servers/*/src/*/server.py`: MCP server implementations using `mcp.server.stdio_server()`
- `client/src/mcp_client/`: Orchestrator client (needs implementation)
- `configs/`: Configuration files including Claude Desktop MCP setup
- `docs/`: Architecture documentation and implementation guides

## MCP Server Development Pattern

### Standard Server Structure
```python
import mcp.server
from mcp.server import Server

server = Server("server_name")

@server.tool()
async def tool_function(param: str) -> ReturnType:
    """Tool description for MCP protocol"""
    # Implementation
    return result

async def main():
    async with mcp.server.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Each Server is Independent
- Has its own `pyproject.toml` with specific dependencies
- Uses standard Python package structure: `src/package_name/`
- Communicates only via MCP protocol (no direct imports between servers)
- Can be developed, tested, and deployed independently

## Key Implementation Notes

### Dependencies
- Uses **uv** for modern Python package management (not pip)
- Main dependencies: `mcp`, `httpx`, `beautifulsoup4`, `openai`, `pydantic`, `rich`, `typer`
- Requires Python >=3.10

### MCP Protocol Usage
- Uses official `mcp` package (not `fastmcp` as mentioned in some docs)
- Servers communicate via stdio transport
- Tools are registered with `@server.tool()` decorator
- Async/await pattern throughout

### Current Development Priority
1. **Implement remaining MCP servers** (web_search, page_analyzer, llm_filter)
2. **Build MCP client orchestrator** to coordinate server interactions
3. **Create shared utilities** for common functionality (logging, config, etc.)
4. **Add proper error handling** and validation across all components

### Architecture Decisions
- **Modular**: Each server handles one specific task (query generation, web search, etc.)
- **Scalable**: Servers can be scaled independently based on demand
- **Extensible**: New servers can be added without modifying existing code
- **Testable**: Each server can be unit tested in isolation

## Configuration Management

The system uses a multi-level configuration approach:
- **Environment variables**: API keys and secrets in `.env`
- **Claude Desktop config**: MCP server registration in `configs/claude_desktop_config.json`
- **Server-specific config**: Each server manages its own configuration needs

## Development Workflow

Since this is an MCP-based system, development involves:
1. **Server Development**: Implement individual MCP servers with their tools
2. **Client Development**: Build orchestrator to coordinate server workflows
3. **Integration Testing**: Test server communication via MCP protocol
4. **Claude Desktop Testing**: Verify servers work properly with Claude Desktop