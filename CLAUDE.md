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
# Copy environment templates
cp .env.example .env
cp servers/web_search/.env.example servers/web_search/.env

# Edit .env files to add API keys:
# Main project: OPENAI_API_KEY=your_key_here
# Web search: SERPAPI_API_KEY, PERPLEXITY_API_KEY, etc. (optional - DuckDuckGo works without keys)
# Page analyzer: No API keys required
```

### Running MCP Servers
```bash
# Run query generator server
cd servers/query_generator && uv run python src/query_generator/server.py

# Run web search server
cd servers/web_search && uv run python run_server.py

# Run page analyzer server
cd servers/page_analyzer && uv run python run_server.py

# Future: Run other servers when implemented
cd servers/llm_filter && uv run python run_server.py
```

### Claude Desktop Integration
Add to Claude Desktop config (`~/.claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "query_generator": {
      "command": "python",
      "args": ["/absolute/path/to/servers/query_generator/src/query_generator/server.py"]
    },
    "web_search": {
      "command": "python",
      "args": ["/absolute/path/to/servers/web_search/run_server.py"]
    },
    "page_analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/servers/page_analyzer/run_server.py"]
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
- ✅ **Web Search Server**: Fully implemented with multi-provider search (SerpAPI, Perplexity, DuckDuckGo, Tavily, Claude)
- ✅ **Page Analyzer Server**: Fully implemented with HTML/RSS/API content analysis
- ⏳ **LLM Filter Server**: Structure exists, implementation needed
- ⏳ **MCP Client**: All orchestrator files are empty stubs

### Key Directories
- `servers/*/src/*/server.py`: MCP server implementations using FastMCP framework
- `servers/*/run_server.py`: Server execution scripts for web_search and page_analyzer
- `client/src/mcp_client/`: Orchestrator client (needs implementation)
- `configs/`: Configuration files including Claude Desktop MCP setup
- `docs/`: Architecture documentation and implementation guides
- `docs/progress/`: Implementation progress tracking for each component

## MCP Server Development Pattern

### Standard Server Structure
```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("server_name")

@mcp.tool()
async def tool_function(param: str) -> dict:
    """Tool description for MCP protocol"""
    try:
        # Implementation
        return {"result": "success", "data": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
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
- Uses official `mcp` package with FastMCP framework
- Servers communicate via stdio transport
- Tools are registered with `@mcp.tool()` decorator
- Async/await pattern throughout
- Returns dict objects for JSON serialization
- Comprehensive error handling in all tools

### Current Development Priority
1. **Build MCP client orchestrator** to coordinate server interactions
2. **Implement LLM Filter Server** for content relevance and quality filtering
3. **End-to-end integration testing** of the complete pipeline
4. **Performance optimization** and caching implementation

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

## Implemented Server Capabilities

### Query Generator Server
- **Tools**: `generate_queries(topic, category, num_queries)`
- **Categories**: general, artist, research
- **Output**: Optimized search queries for different content types
- **Status**: ✅ Production ready

### Web Search Server  
- **Tools**: `search_web()`, `search_with_fallback()`, `multi_provider_search()`, `get_available_providers()`
- **Providers**: SerpAPI, Perplexity, DuckDuckGo, Tavily, Claude
- **Features**: Automatic fallback, concurrent search, zero-config option
- **Status**: ✅ Production ready

### Page Analyzer Server
- **Tools**: `analyze_page()`, `analyze_batch()`, `extract_feeds()`, `analyze_api_response()`, `get_page_metadata()`, `get_analyzer_status()`
- **Content Types**: HTML pages, RSS/Atom feeds, API responses
- **Features**: Concurrent processing, content scoring, language detection, feed discovery
- **Status**: ✅ Production ready

## Testing Commands

### Individual Server Testing
```bash
# Test web search server
cd servers/web_search && uv run python test_tools.py

# Test page analyzer server  
cd servers/page_analyzer && uv run python test_tools.py

# Run unit tests
cd servers/page_analyzer && uv run python -m pytest tests/
```

## Development Workflow

Since this is an MCP-based system, development involves:
1. **Server Development**: Implement individual MCP servers with their tools
2. **Client Development**: Build orchestrator to coordinate server workflows
3. **Integration Testing**: Test server communication via MCP protocol
4. **Claude Desktop Testing**: Verify servers work properly with Claude Desktop

### Git Strategy
- **Feature Branches**: `feature/server-*` for individual servers
- **Commit Convention**: `feat(server-name): description`
- **Documentation**: Track progress in `docs/progress/`
- **Testing**: Validate functionality before commits