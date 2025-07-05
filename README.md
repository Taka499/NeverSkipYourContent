[English](README.md) | [日本語](docs/README.ja.md) | [中文](docs/README.zh.md)

# Never Skip Your Content (NSYC)

An MCP-based content discovery system that automatically finds relevant data sources (official sites, RSS feeds, social media, APIs) for user-specified topics using a distributed MCP architecture.

## 🚀 Current Status

### Available MCP Servers (Ready for Claude Desktop)
- ✅ **Web Search Server** - Multi-provider search with DuckDuckGo (no API keys required), SerpAPI, Perplexity, Tavily, and Claude
- ✅ **Page Analyzer Server** - Comprehensive content analysis for HTML pages, RSS feeds, and API responses

### In Progress
- 🔧 **Query Generator Server** - Keyword-based query generation (pending configuration fix)

### Planned
- ⏳ **LLM Filter Server** - Content relevance and quality filtering
- ⏳ **MCP Client Orchestrator** - Workflow coordination between all servers

## 📋 Quick Start

### 1. Installation
```bash
# Install dependencies
uv sync

# Copy environment templates
cp .env.example .env
cp servers/web_search/.env.example servers/web_search/.env
```

### 2. Environment Setup
Edit `.env` files to add API keys:
```env
# Main project
OPENAI_API_KEY=your_key_here

# Web search (optional - DuckDuckGo works without keys)
SERPAPI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
```

### 3. Claude Desktop Integration

#### Option A: Automatic Configuration (Recommended)
Use the built-in script to automatically generate and install the configuration:
```bash
# Generate and install config to Claude Desktop
python scripts/generate_claude_config.py --install

# Just generate config without installing
python scripts/generate_claude_config.py

# Validate server paths
python scripts/generate_claude_config.py --validate
```

The script automatically:
- Detects your operating system (Windows, macOS, Linux)
- Finds Claude Desktop's config location
- Generates configuration with absolute paths
- Backs up existing config before installing
- Validates all server paths

#### Option B: Manual Configuration
Add to your Claude Desktop config (`~/.claude_desktop_config.json`):
```json
{
  "mcpServers": {
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

### 4. Test the Servers
```bash
# Test web search server
cd servers/web_search && python test_tools.py

# Test page analyzer server  
cd servers/page_analyzer && python test_tools.py
```

## 🏗️ Architecture

The system uses a **hub-and-spoke MCP architecture** where specialized servers handle specific tasks:

```
┌─────────────────┐
│   User Input    │
│  (Artist/Topic) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         MCP Client (Orchestrator)        │
│  - Coordinates MCP servers               │
│  - Manages workflow                      │
│  - Aggregates results                    │
└─────────┬───────────────────────────────┘
          │
          ├──────────────┬──────────────┬──────────────┐
          ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Query Gen    │ │ Web Search   │ │ Page Analyzer│ │ LLM Filter   │
│ MCP Server   │ │ MCP Server   │ │ MCP Server   │ │ MCP Server   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## 🔧 Server Capabilities

### Web Search Server
- **Multi-provider search**: SerpAPI, Perplexity, DuckDuckGo, Tavily, Claude
- **Zero-config option**: Works with DuckDuckGo without API keys
- **Automatic fallback**: Falls back to working providers
- **4 MCP tools**: search_web, search_with_fallback, multi_provider_search, get_available_providers

### Page Analyzer Server  
- **Content analysis**: HTML pages, RSS feeds, API responses
- **Concurrent processing**: Batch analysis with throttling
- **Rich metadata extraction**: Titles, descriptions, dates, language detection
- **6 MCP tools**: analyze_page, analyze_batch, extract_feeds, analyze_api_response, get_page_metadata, get_analyzer_status

## 📚 Documentation

- **[Project Overview](docs/intro.md)** - Complete system architecture and design
- **[Development Guide](CLAUDE.md)** - Setup instructions and development workflow
- **[Project Structure](docs/project_structure.md)** - Directory organization and components
- **[Implementation Progress](docs/progress/)** - Detailed progress tracking for each server

## 🎯 Usage Example

Once integrated with Claude Desktop, you can:

1. **Search for content**: "Find RSS feeds related to AI research"
2. **Analyze pages**: "Extract content and metadata from these URLs"
3. **Discover feeds**: "Find RSS feeds on this news website"
4. **Batch processing**: "Analyze these 10 URLs for content quality"

## 🛠️ Development

### Run Individual Servers
```bash
# Web search server
cd servers/web_search && python run_server.py

# Page analyzer server
cd servers/page_analyzer && python run_server.py

# Query generator server (when fixed)
cd servers/query_generator && uv run python src/query_generator/server.py
```

### Testing
```bash
# Run server tests
cd servers/web_search && python test_tools.py
cd servers/page_analyzer && python test_tools.py

# Run unit tests
cd servers/page_analyzer && uv run python -m pytest tests/
```

## 📈 Project Goals

**Current Goal**: Build a complete MCP-based content discovery pipeline that can:
- Generate targeted search queries for any topic
- Search across multiple providers with fallback
- Analyze and extract content from discovered URLs
- Filter and rank results by relevance and quality

**Long-term Vision**: An intelligent content monitoring system that automatically discovers and tracks relevant information sources for any topic or field of interest.

## 🤝 Contributing

This project follows conventional commit format and maintains comprehensive documentation. See [CLAUDE.md](CLAUDE.md) for development guidelines and workflow.
