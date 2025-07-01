# project sturcture

```
mcp-research-system/
├── pyproject.toml                 # uv project configuration
├── README.md
├── .gitignore
├── .env.example
│
├── servers/                       # Each subdirectory is a standalone MCP server
│   ├── query_generator/          # MCP Server 1: Query Generation
│   │   ├── pyproject.toml        # Individual server config
│   │   ├── src/
│   │   │   └── query_generator/
│   │   │       ├── __init__.py
│   │   │       ├── server.py     # FastMCP server implementation
│   │   │       ├── generators.py # Sample, may not needed
│   │   │       └── templates.py # Sample, may not needed
│   │   └── tests/
│   │
│   ├── web_search/               # MCP Server 2: Web Search
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── web_search/
│   │   │       ├── __init__.py
│   │   │       ├── server.py     # FastMCP server implementation
│   │   │       ├── search_apis.py # Sample, may not needed
│   │   │       ├── rate_limiter.py # Sample, may not needed
│   │   │       └── fetcher.py # Sample, may not needed
│   │   └── tests/
│   │
│   ├── page_analyzer/            # MCP Server 3: Page Analysis
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── page_analyzer/
│   │   │       ├── __init__.py
│   │   │       ├── server.py     # FastMCP server implementation
│   │   │       ├── metadata_extractor.py # Sample, may not needed
│   │   │       ├── rss_finder.py # Sample, may not needed
│   │   │       └── content_parser.py # Sample, may not needed
│   │   └── tests/
│   │
│   └── llm-filter/               # MCP Server 4: LLM Filtering
│       ├── pyproject.toml
│       ├── src/
│       │   └── llm_filter/
│       │       ├── __init__.py
│       │       ├── server.py     # FastMCP server implementation
│       │       ├── classifier.py # Sample, may not needed
│       │       └── scorer.py # Sample, may not needed
│       └── tests/
│
├── shared/                       # Shared utilities across servers
│   ├── __init__.py
│   ├── models.py                 # Shared Pydantic models
│   ├── http_client.py            # Shared HTTP utilities
│   └── logging.py                # Shared logging setup
│
├── configs/                      # Configuration for all servers
│   ├── claude_desktop_config.json  # Claude Desktop MCP config
│   ├── development.yaml
│   └── logging.yaml
│
├── client/                       # Self-implemented MCP client
│   ├── pyproject.toml           # Client-specific dependencies
│   ├── src/
│   │   └── mcp_client/
│   │       ├── __init__.py
│   │       ├── orchestrator.py  # Main client orchestrator
│   │       ├── server_manager.py # Manages connections to servers
│   │       ├── workflow.py      # Research workflow coordination
│   │       ├── aggregator.py    # Results aggregation
│   │       └── cli.py           # Command-line interface
│   ├── tests/
│   └── examples/
│       ├── basic_research.py
│       └── advanced_pipeline.py
│
├── scripts/
│   ├── install_all_servers.py   # Install all servers to Claude Desktop
│   ├── test_all_servers.py      # Test all servers
│   └── start_dev_servers.py     # Start servers for development
│
└── docs/
    ├── setup.md
    ├── claude-integration.md
    └── server-development.md
```

### 1. Each Server is Independent
```python
# servers/query-generator/src/query_generator/server.py
from fastmcp import FastMCP

# Each server is a standalone FastMCP instance
mcp = FastMCP("Query Generator")

@mcp.tool()
def generate_search_queries(topic: str) -> list[str]:
    """Generate multiple search queries for a given topic."""
    # Your query generation logic here
    return [
        f"{topic} latest research",
        f"{topic} trends 2024",
        f"{topic} best practices"
    ]

if __name__ == "__main__":
    mcp.run()  # This runs the server
```

### 2. Claude Desktop Connects to Each Server
```json
// configs/claude_desktop_config.json
{
  "mcpServers": {
    "query_gen": {
      "command": "python",
      "args": ["/path/to/servers/query_gen/src/query_gen/server.py"]
    },
    "search": {
      "command": "python", 
      "args": ["/path/to/servers/search/src/search/server.py"]
    },
    "page_analysis": {
      "command": "python",
      "args": ["/path/to/servers/page_analysis/src/page_analysis/server.py"]
    },
    "scraping": {
      "command": "python",
      "args": ["/path/to/servers/scraping/src/scraping/server.py"]
    }
  }
}
```