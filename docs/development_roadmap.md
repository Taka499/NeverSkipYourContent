# Development Roadmap

## Current Implementation Status

### ✅ Completed Components
- **Query Generator MCP Server** (`servers/query_generator/src/query_generator/server.py`)
  - Fully implemented with keyword-based query generation
  - Supports categories: general, artist, research
  - Generates targeted search queries for different content types

### ❌ Missing/Incomplete Components

#### MCP Servers (Critical Path)
- **Web Search Server** (`servers/web_search/`) - **EMPTY DIRECTORY**
  - Needs complete implementation from scratch
  - Should implement web search functionality via search APIs
  - Must follow MCP server pattern with `@server.tool()` decorators

- **Page Analyzer Server** (`servers/page_analyzer/`) - **EMPTY DIRECTORY** 
  - Needs complete implementation from scratch
  - Should analyze and extract content from web pages
  - Must handle various content types (HTML, RSS, API responses)

#### MCP Client Orchestrator (High Priority)
- **Orchestrator** (`client/src/mcp_client/orchestrator.py`) - **EMPTY FILE**
  - Core coordination logic between MCP servers
  - Workflow management and data aggregation

- **CLI Interface** (`client/src/mcp_client/cli.py`) - **EMPTY FILE**
  - User-facing command line interface
  - Should integrate with orchestrator for end-to-end functionality

- **Workflow Engine** (`client/src/mcp_client/workflow.py`) - **EMPTY FILE**
  - Define and execute multi-step content discovery workflows
  - Handle error recovery and retry logic

#### Additional Components
- **Server Manager** (`client/src/mcp_client/server_manager.py`) - **EMPTY FILE**
- **Aggregator** (`client/src/mcp_client/aggregator.py`) - **EMPTY FILE**
- **LLM Filter Server** - Not yet created, mentioned in CLAUDE.md

## Development Priorities (Ordered)

### Phase 1: Core MCP Servers (Weeks 1-2)
1. **Implement Web Search MCP Server** 
   - Create proper directory structure with `pyproject.toml`
   - Implement search functionality using search APIs (Google, Bing, etc.)
   - Add MCP server boilerplate with stdio transport
   - Test server independently

2. **Implement Page Analyzer MCP Server**
   - Create proper directory structure with `pyproject.toml`  
   - Implement content extraction (BeautifulSoup, newspaper3k)
   - Add RSS feed parsing capabilities
   - Add API response analysis
   - Test server independently

### Phase 2: MCP Client Orchestrator (Weeks 3-4)
3. **Build MCP Client Orchestrator**
   - Implement server connection management
   - Create workflow coordination logic
   - Add data aggregation and result merging
   - Handle inter-server communication

4. **Create CLI Interface**
   - Build user-facing command line tool
   - Integrate with orchestrator
   - Add proper argument parsing and help text
   - Include configuration management

### Phase 3: Advanced Features (Weeks 5-6)
5. **Implement LLM Filter Server**
   - Create relevance scoring and content filtering
   - Add LLM-based content analysis
   - Implement duplicate detection

6. **Add Workflow Engine**
   - Define complex multi-step workflows
   - Add error handling and retry mechanisms
   - Implement workflow persistence

### Phase 4: Integration & Testing (Week 7)
7. **End-to-End Integration Testing**
   - Test complete workflow from CLI to results
   - Verify MCP server communication
   - Performance optimization

8. **Claude Desktop Integration**
   - Update Claude Desktop configuration
   - Test MCP servers with Claude Desktop
   - Documentation updates

## Technical Requirements

### Dependencies Management
- Use `uv` for all Python package management
- Each MCP server has independent `pyproject.toml`
- Main project coordinates shared dependencies

### MCP Protocol Implementation
- All servers use official `mcp` package
- Follow `mcp.server.stdio_server()` pattern
- Async/await throughout
- Tools registered with `@server.tool()` decorator

### Architecture Constraints
- Servers communicate only via MCP protocol
- No direct imports between servers
- Each server independently deployable
- Client orchestrates but doesn't contain business logic

## Success Criteria

### Milestone 1: Basic Workflow
- [ ] Query Generator → Web Search → Page Analyzer chain works
- [ ] CLI can execute simple content discovery requests
- [ ] All MCP servers run independently

### Milestone 2: Full Integration  
- [ ] Complete orchestrator coordinates all servers
- [ ] Claude Desktop integration functional
- [ ] End-to-end content discovery working

### Milestone 3: Production Ready
- [ ] Error handling and retry logic implemented
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Test coverage adequate

## Next Immediate Action

**START WITH: Implement Web Search MCP Server**
- Location: `servers/web_search/`
- Create directory structure following `query_generator` pattern
- Implement basic web search functionality
- Test as standalone MCP server