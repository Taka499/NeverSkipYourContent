# Page Analyzer MCP Server Design

**Date:** July 1, 2025  
**Status:** 🟡 DESIGN PHASE  
**Priority:** Critical Path Component

## Overview

The Page Analyzer MCP server is the third critical component in the NSYC content discovery pipeline. It takes URLs from web search results, extracts and analyzes their content, and returns structured, actionable data for further processing and filtering.

## Position in NSYC Pipeline

```
Query Generator → Web Search → Page Analyzer → LLM Filter → Results
```

**Input**: URLs and metadata from Web Search server  
**Output**: Structured content data for LLM Filter server  
**Purpose**: Transform raw web URLs into analyzed, structured content data

## Core Functionality

### Primary Objective
Transform web URLs into structured, analyzable content data that enables intelligent content discovery and filtering.

### Key Capabilities
- **Content Extraction**: Extract meaningful text, metadata, and structure from web pages
- **Multi-Format Support**: Handle HTML pages, RSS feeds, API responses, and other content types
- **Batch Processing**: Efficiently analyze multiple URLs concurrently
- **Content Scoring**: Assess relevance, quality, and freshness of discovered content
- **Feed Discovery**: Automatically discover RSS/Atom feeds and data sources

## MCP Tools Architecture

### 1. `analyze_page(url, content_type, options)`
**Purpose**: Comprehensive analysis of a single web page or resource

**Parameters**:
- `url` (str): Target URL to analyze
- `content_type` (optional str): Expected content type hint ("html", "rss", "api", "auto")
- `options` (optional dict): Analysis options (timeout, extract_links, full_content, etc.)

**Returns**: `PageAnalysis` object with extracted content and metadata

**Use Cases**:
- Analyze individual search results
- Deep dive into specific content sources
- Extract content for immediate processing

### 2. `analyze_batch(urls, max_concurrent, options)`
**Purpose**: Batch process multiple URLs with concurrent execution

**Parameters**:
- `urls` (List[str]): List of URLs to analyze
- `max_concurrent` (int, default=5): Maximum concurrent requests
- `options` (optional dict): Shared analysis options

**Returns**: List of `PageAnalysis` objects

**Use Cases**:
- Process entire search result sets
- Bulk content discovery
- Efficient pipeline processing

### 3. `extract_feeds(url, discover_depth)`
**Purpose**: Discover and parse RSS/Atom feeds from a webpage or domain

**Parameters**:
- `url` (str): Target URL or domain to search for feeds
- `discover_depth` (int, default=2): How deep to search for feed links

**Returns**: `FeedDiscovery` object with found feeds and their metadata

**Use Cases**:
- Find RSS feeds for ongoing content monitoring
- Discover additional content sources
- Build comprehensive content source lists

### 4. `analyze_api_response(url, response_data, schema_hint)`
**Purpose**: Analyze structured API responses and extract relevant content

**Parameters**:
- `url` (str): Source API endpoint
- `response_data` (dict): Raw API response data
- `schema_hint` (optional str): Expected data structure type

**Returns**: `ApiAnalysis` object with structured content extraction

**Use Cases**:
- Process API-based content sources
- Handle structured data from search results
- Extract content from JSON/XML responses

### 5. `get_page_metadata(url, quick_mode)`
**Purpose**: Fast metadata extraction without full content processing

**Parameters**:
- `url` (str): Target URL
- `quick_mode` (bool, default=True): Skip heavy content extraction

**Returns**: `PageMetadata` object with basic page information

**Use Cases**:
- Quick content preview
- Validation of URL accessibility
- Lightweight content assessment

## Data Models

### PageAnalysis
```python
class PageAnalysis(BaseModel):
    url: str
    content_type: Literal["html", "rss", "api", "pdf", "unknown"]
    status: Literal["success", "error", "timeout", "blocked"]
    
    # Content Data
    title: Optional[str]
    description: Optional[str]
    main_content: Optional[str]
    summary: Optional[str]
    
    # Metadata
    language: Optional[str]
    author: Optional[str]
    published_date: Optional[datetime]
    last_modified: Optional[datetime]
    
    # Analysis Results
    relevance_score: float  # 0.0 to 1.0
    quality_score: float    # 0.0 to 1.0
    freshness_score: float  # 0.0 to 1.0
    
    # Discovered Resources
    feeds_discovered: List[str]
    images: List[str]
    external_links: List[str]
    
    # Technical Details
    response_time: float
    content_length: int
    error_message: Optional[str]
    
    # Processing Metadata
    analyzed_at: datetime
    processing_time: float
```

### FeedDiscovery
```python
class FeedDiscovery(BaseModel):
    source_url: str
    feeds_found: List[FeedInfo]
    discovery_method: str
    total_feeds: int
    
class FeedInfo(BaseModel):
    url: str
    title: Optional[str]
    description: Optional[str]
    feed_type: Literal["rss", "atom", "json"]
    last_updated: Optional[datetime]
    entry_count: int
    is_active: bool
```

### ApiAnalysis
```python
class ApiAnalysis(BaseModel):
    endpoint_url: str
    response_structure: str
    extracted_content: List[dict]
    schema_detected: Optional[str]
    total_records: int
    data_quality: float
```

## Content Analysis Logic

### HTML Page Processing
1. **Content Extraction**:
   - Use readability algorithm for main content
   - Extract title, meta description, headers
   - Identify and clean main text content
   - Remove navigation, ads, and boilerplate

2. **Structure Analysis**:
   - Parse semantic HTML structure
   - Extract meaningful links and references
   - Identify content sections and hierarchy
   - Detect social media references and sharing data

3. **Feed Discovery**:
   - Parse `<link rel="alternate">` tags
   - Search for common feed URL patterns
   - Validate discovered feed URLs
   - Extract feed metadata

### RSS/Atom Feed Processing
1. **Feed Parsing**:
   - Parse feed structure and metadata
   - Extract recent entries with full content
   - Identify update patterns and frequency
   - Assess content completeness (full text vs summaries)

2. **Content Quality Assessment**:
   - Evaluate entry content richness
   - Check for consistent publishing patterns
   - Assess source credibility indicators
   - Analyze content freshness and relevance

### API Response Processing
1. **Structure Detection**:
   - Auto-detect JSON/XML structure
   - Identify key data fields
   - Handle nested and complex data structures
   - Extract pagination and metadata

2. **Content Extraction**:
   - Map API fields to content structure
   - Extract text content from various fields
   - Preserve important metadata and relationships
   - Handle different API response formats

## Technical Architecture

### Core Dependencies
- **BeautifulSoup4**: HTML parsing and content extraction
- **feedparser**: RSS/Atom feed parsing
- **requests**: HTTP client for web requests
- **readability-lxml**: Content extraction algorithm
- **langdetect**: Language detection
- **python-dateutil**: Date parsing and handling

### Performance Considerations
- **Concurrent Processing**: Use asyncio for batch operations
- **Request Timeouts**: Configurable timeouts for different content types
- **Rate Limiting**: Respect robots.txt and implement polite delays
- **Caching**: Cache analysis results to avoid duplicate processing
- **Memory Management**: Stream large content and clean up resources

### Error Handling Strategy
- **Graceful Degradation**: Return partial results when possible
- **Timeout Protection**: Hard limits on processing time
- **Network Resilience**: Retry logic for transient failures
- **Content Validation**: Validate extracted content quality
- **Error Reporting**: Detailed error context for debugging

## Integration Points

### Input Sources
- **Web Search Results**: URLs from search provider results
- **Direct URLs**: User-provided URLs for analysis
- **Feed URLs**: RSS/Atom feed URLs for content monitoring
- **API Endpoints**: Structured data sources

### Output Consumers
- **LLM Filter Server**: Structured content for relevance filtering
- **MCP Client**: Direct content analysis results
- **Caching Layer**: Processed content for future reference

### Configuration
- **Content Extraction Settings**: Readability thresholds, content length limits
- **Performance Tuning**: Timeout values, concurrency limits
- **Quality Scoring**: Relevance algorithm parameters
- **Feed Discovery**: Search depth and validation rules

## Success Metrics

### Functional Requirements
- [ ] Successfully extract content from 95%+ of HTML pages
- [ ] Parse RSS/Atom feeds with 100% accuracy
- [ ] Handle API responses for common formats (JSON, XML)
- [ ] Discover feeds on 80%+ of pages that have them
- [ ] Process batch requests efficiently with concurrent execution

### Performance Requirements
- [ ] Single page analysis: < 5 seconds
- [ ] Batch processing: 10 URLs in < 30 seconds
- [ ] Memory usage: < 100MB per concurrent request
- [ ] Error rate: < 5% for accessible URLs

### Quality Requirements
- [ ] Content extraction accuracy: > 90%
- [ ] Relevance scoring consistency
- [ ] Language detection accuracy: > 95%
- [ ] Feed discovery completeness: > 80%

## Future Enhancements

### Advanced Content Processing
- **PDF/Document Analysis**: Extract content from document formats
- **Image Content Analysis**: OCR and image metadata extraction
- **Video/Audio Metadata**: Extract metadata from media content
- **Social Media Integration**: Specialized handlers for social platforms

### Intelligence Features
- **Content Similarity Detection**: Identify duplicate or similar content
- **Topic Classification**: Automatic content categorization
- **Sentiment Analysis**: Content tone and sentiment assessment
- **Entity Extraction**: Identify people, places, organizations

### Performance Optimizations
- **Distributed Processing**: Scale analysis across multiple workers
- **Intelligent Caching**: ML-driven cache invalidation
- **Predictive Pre-fetching**: Anticipate content analysis needs
- **Content Prioritization**: Smart ordering of analysis tasks

This design provides a comprehensive foundation for the Page Analyzer MCP server while maintaining flexibility for future enhancements and integration with the broader NSYC content discovery ecosystem.