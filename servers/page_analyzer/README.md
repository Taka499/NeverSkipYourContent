# Page Analyzer MCP Server

A comprehensive MCP server for web page content analysis and extraction with multi-format support.

## Overview

The Page Analyzer MCP server is the third critical component in the NSYC content discovery pipeline. It analyzes web pages, RSS feeds, and API responses to extract structured content and metadata for further processing.

## Features

### Content Analysis
- **HTML Page Analysis**: Extract titles, descriptions, main content, and metadata
- **RSS/Atom Feed Parsing**: Parse feeds and extract entry information
- **API Response Analysis**: Handle structured JSON/XML API responses
- **Batch Processing**: Analyze multiple URLs concurrently
- **Content Scoring**: Calculate relevance, quality, and freshness scores

### Extraction Capabilities
- Main content extraction using readability algorithms
- Metadata extraction (title, description, author, dates)
- Feed discovery and validation
- Image and link extraction
- Language detection
- Content summarization

### Performance Features
- Concurrent processing with configurable limits
- Request timeouts and error handling
- Graceful degradation for failed requests
- Caching-friendly design

## MCP Tools

### 1. `analyze_page`
Comprehensive analysis of a single web page or content source.

```python
await analyze_page(
    url="https://example.com",
    content_type="auto",  # "html", "rss", "api", "auto"
    extract_links=False,
    extract_images=False,
    discover_feeds=True,
    timeout=30
)
```

### 2. `analyze_batch`
Batch process multiple URLs with concurrent execution.

```python
await analyze_batch(
    urls=["https://example1.com", "https://example2.com"],
    max_concurrent=5,
    timeout_per_url=30,
    extract_feeds=True,
    extract_links=False,
    full_content=True
)
```

### 3. `extract_feeds`
Discover and analyze RSS/Atom feeds from a webpage.

```python
await extract_feeds(
    url="https://example.com",
    discover_depth=2,
    validate_feeds=True
)
```

### 4. `analyze_api_response`
Analyze structured API responses and extract content.

```python
await analyze_api_response(
    url="https://api.example.com/data",
    response_data=None,  # Optional pre-fetched data
    schema_hint="jsonapi"
)
```

### 5. `get_page_metadata`
Quick metadata extraction without full content processing.

```python
await get_page_metadata(
    url="https://example.com",
    quick_mode=True
)
```

### 6. `get_analyzer_status`
Get analyzer capabilities and configuration information.

```python
await get_analyzer_status()
```

## Installation

### Dependencies
```bash
cd servers/page_analyzer
uv sync
```

### Environment Setup
No API keys required for basic functionality. All dependencies are Python packages.

## Usage

### Running the Server

#### Standalone
```bash
python run_server.py
```

#### Claude Desktop Integration
Add to `~/.claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "page_analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/servers/page_analyzer/run_server.py"]
    }
  }
}
```

### Testing
```bash
# Run functional tests
python test_tools.py

# Run unit tests (if implemented)
python -m pytest tests/
```

## Configuration

The analyzer can be configured through the `AnalysisConfig` class:

```python
config = AnalysisConfig(
    timeout=30,                    # Request timeout
    max_content_length=1_000_000,  # Max content size
    extract_main_content=True,     # Extract main content
    extract_links=False,           # Extract external links
    extract_images=False,          # Extract image URLs
    discover_feeds=True,           # Discover RSS feeds
    calculate_scores=True,         # Calculate quality scores
    detect_language=True,          # Detect content language
    user_agent="NSYC Page Analyzer 1.0"
)
```

## Content Types Supported

### HTML Pages
- Title and metadata extraction
- Main content using readability algorithm
- Feed discovery
- Link and image extraction
- Language detection

### RSS/Atom Feeds
- Feed metadata and entries
- Content extraction from entries
- Feed validation and activity checking
- Update frequency analysis

### API Responses
- JSON/XML structure analysis
- Content field extraction
- Schema detection
- Data quality scoring

## Data Models

### PageAnalysis
Complete analysis result with content, metadata, and scores.

### FeedDiscovery
Results of feed discovery with validated feed information.

### ApiAnalysis
Structured analysis of API responses with extracted content.

### PageMetadata
Basic page information for quick metadata extraction.

## Integration with NSYC Pipeline

```
Query Generator → Web Search → Page Analyzer → LLM Filter
```

### Input Sources
- URLs from Web Search results
- Direct URL analysis requests
- API endpoints for structured data

### Output Format
Structured data ready for:
- LLM-based filtering and ranking
- Content aggregation
- Further processing steps

## Performance Characteristics

- **Single page analysis**: 1-5 seconds
- **Batch processing**: 10 URLs in 15-30 seconds
- **Memory usage**: ~50MB per concurrent request
- **Error handling**: Graceful degradation for failed requests
- **Timeout protection**: Configurable per-request timeouts

## Error Handling

The analyzer provides comprehensive error handling:
- Network timeouts and connection errors
- Invalid content formats
- Parsing errors
- Memory and size limits
- Graceful degradation for partial failures

## Future Enhancements

- PDF and document analysis
- Image content analysis (OCR)
- Video/audio metadata extraction
- Enhanced content scoring algorithms
- Caching layer for improved performance
- Distributed processing capabilities

## License

MIT License - See LICENSE file for details.