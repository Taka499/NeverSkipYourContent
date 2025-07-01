# Never Skip Your Content: MCP-Based Content Discovery System

## 1. Executive Summary

This redesigned architecture leverages MCP (Model Context Protocol) to create a modular, distributed content discovery system. The system uses MCP servers as specialized agents for different tasks, enabling better scalability and maintainability.

## 2. MCP-Based Architecture

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
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ - Generate   │ │ - Search APIs│ │ - Extract    │ │ - Classify   │
│   search     │ │ - Fetch URLs │ │   metadata   │ │   sources    │
│   queries    │ │ - Rate limit │ │ - Find RSS   │ │ - Score      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## 3. Core Components

### 3.1 MCP Servers (Specialized Agents)

1. **Query Generation Server** (`query_generator`)
   - Generates optimized search queries based on keywords
   - Uses LLM to create domain-specific queries
   - Tools: `generate_queries`, `expand_keywords`

2. **Web Search Server** (`web_search`)
   - Interfaces with multiple search APIs (Google, Bing, DuckDuckGo)
   - Manages API keys and rate limiting
   - Tools: `search_web`, `fetch_urls`

3. **Page Analyzer Server** (`page_analyzer`)
   - Extracts metadata from web pages
   - Finds RSS feeds, social media links, APIs
   - Tools: `analyze_page`, `extract_feeds`, `find_social_links`

4. **LLM Filter Server** (`filter-server`)
   - Classifies and scores data sources
   - Determines official sites, content types
   - Tools: `classify_source`, `score_relevance`

5. **More Servers may be added**

### 3.2 MCP Client (Orchestrator)

- Manages workflow between MCP servers
- Handles parallel processing
- Aggregates and deduplicates results
- Provides simple API interface

## 4. Implementation Plan for Local Demo

### 4.1 Project Structure

See [`project_structure.md`](project_structure.md)

### 4.2 Core Dependencies
```toml
[project]
dependencies = [
    "mcp",
    "httpx",
    "beautifulsoup4",
    "lxml",
    "python-dotenv",
    "openai",
    "pydantic",
    "rich",  # for nice CLI output
]
```

### 4.3 Simple Demo Flow

1. **User Input**: Artist name or research topic
2. **Query Generation**: Generate 5-8 search queries
3. **Web Search**: Use free APIs (DuckDuckGo) for demo
4. **Page Analysis**: Extract basic metadata
5. **LLM Filtering**: Classify sources (using OpenAI/local LLM)
6. **Output**: Formatted table of data sources

## 7. Future Improvements (TODOs)

### 7.1 Infrastructure
- [ ] Redis for caching search results and page metadata
- [ ] PostgreSQL for persistent storage of discovered sources
- [ ] Docker Compose for easy deployment
- [ ] Message queue (RabbitMQ/Kafka) for async processing

### 7.2 Frontend
- [ ] React/Vue dashboard for visual exploration
- [ ] Real-time updates via WebSocket
- [ ] User authentication and saved searches
- [ ] Export functionality (CSV, JSON, RSS)

### 7.3 Advanced Features
- [ ] Scheduled monitoring of sources
- [ ] Change detection and notifications
- [ ] ML-based relevance scoring
- [ ] Custom RSS feed generation
- [ ] API endpoint for third-party integrations

### 7.4 MCP Enhancements
- [ ] Dynamic server discovery
- [ ] Load balancing between multiple instances
- [ ] Server health monitoring
- [ ] Distributed tracing for debugging

### 7.5 Data Processing
- [ ] Vector embeddings for semantic search
- [ ] Knowledge graph construction
- [ ] Duplicate detection using fuzzy matching
- [ ] Multi-language support

### 7.6 Performance
- [ ] Async batch processing
- [ ] Connection pooling
- [ ] Response streaming
- [ ] Progressive enhancement

## 8. Benefits of MCP Architecture

1. **Modularity**: Each server handles a specific task
2. **Scalability**: Easy to scale individual components
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Add new servers without changing core logic
5. **Reusability**: MCP servers can be used in other projects
6. **Testing**: Each server can be tested independently

## 9. Security Considerations

- API key management via environment variables
- Rate limiting to prevent abuse
- Input validation at each server
- Sandboxed execution for web scraping
- User data privacy (no PII storage in demo)