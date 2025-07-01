"""Analysis manager for coordinating different content analyzers."""

import asyncio
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .analysis_types import (
    PageAnalysis,
    PageMetadata,
    FeedDiscovery,
    ApiAnalysis,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ContentType,
    AnalysisStatus,
    AnalysisConfig
)
from .analyzers.html_analyzer import HtmlAnalyzer
from .analyzers.feed_analyzer import FeedAnalyzer
from .analyzers.api_analyzer import ApiAnalyzer


class AnalysisManager:
    """Manager for coordinating different content analyzers."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize analysis manager with configuration."""
        self.config = config or AnalysisConfig()
        
        # Initialize analyzers
        self.html_analyzer = HtmlAnalyzer(self.config)
        self.feed_analyzer = FeedAnalyzer(self.config)
        self.api_analyzer = ApiAnalyzer(self.config)
        
        # Throttling for batch operations
        self._semaphore: Optional[asyncio.Semaphore] = None
    
    async def analyze_page(self, url: str, content_type: Optional[str] = None,
                          options: Optional[Dict[str, Any]] = None) -> PageAnalysis:
        """
        Analyze a single page or content source.
        
        Args:
            url: URL to analyze
            content_type: Hint for content type ("html", "rss", "api", "auto")
            options: Additional analysis options
            
        Returns:
            PageAnalysis object with extracted content and metadata
        """
        start_time = time.time()
        
        try:
            # Merge options with config if provided
            if options:
                config = self._merge_config_with_options(options)
                # Update analyzers with new config if needed
                if config != self.config:
                    await self._update_analyzer_configs(config)
            
            # Determine content type
            detected_type = self._detect_content_type(url, content_type)
            
            # Route to appropriate analyzer
            if detected_type == ContentType.RSS or detected_type == ContentType.ATOM:
                return await self.feed_analyzer.analyze_feed(url)
            elif detected_type == ContentType.API:
                return await self.api_analyzer.analyze_api_as_page(url)
            else:
                # Default to HTML analysis
                return await self.html_analyzer.analyze(url)
                
        except Exception as e:
            processing_time = time.time() - start_time
            return PageAnalysis(
                url=url,
                content_type=ContentType.UNKNOWN,
                status=AnalysisStatus.ERROR,
                error_message=str(e),
                analyzed_at=datetime.now(),
                processing_time=processing_time
            )
    
    async def analyze_batch(self, urls: List[str], max_concurrent: int = 5,
                           options: Optional[Dict[str, Any]] = None) -> BatchAnalysisResponse:
        """
        Analyze multiple URLs concurrently with throttling.
        
        Args:
            urls: List of URLs to analyze
            max_concurrent: Maximum concurrent analyses
            options: Additional analysis options
            
        Returns:
            BatchAnalysisResponse with results and statistics
        """
        start_time = time.time()
        
        # Setup semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create analysis tasks
        tasks = [
            self._analyze_with_semaphore(url, options)
            for url in urls
        ]
        
        # Execute tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_analyses = []
        failed_analyses = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_analyses.append(urls[i])
                errors.append(f"{urls[i]}: {str(result)}")
            elif isinstance(result, PageAnalysis):
                if result.status == AnalysisStatus.SUCCESS:
                    successful_analyses.append(result)
                else:
                    failed_analyses.append(result.url)
                    if result.error_message:
                        errors.append(f"{result.url}: {result.error_message}")
        
        total_processing_time = time.time() - start_time
        
        return BatchAnalysisResponse(
            total_requested=len(urls),
            successful_analyses=len(successful_analyses),
            failed_analyses=len(failed_analyses),
            results=successful_analyses,
            total_processing_time=total_processing_time,
            errors=errors
        )
    
    async def extract_feeds(self, url: str, discover_depth: int = 2) -> FeedDiscovery:
        """
        Discover RSS/Atom feeds from a webpage or domain.
        
        Args:
            url: URL to search for feeds
            discover_depth: How deep to search for feed links
            
        Returns:
            FeedDiscovery object with found feeds and metadata
        """
        return await self.feed_analyzer.discover_feeds(url, discover_depth)
    
    async def analyze_api_response(self, url: str, response_data: Optional[Dict[str, Any]] = None,
                                 schema_hint: Optional[str] = None) -> ApiAnalysis:
        """
        Analyze structured API response data.
        
        Args:
            url: API endpoint URL
            response_data: Pre-fetched response data (optional)
            schema_hint: Expected data structure type (optional)
            
        Returns:
            ApiAnalysis object with structured content extraction
        """
        return await self.api_analyzer.analyze_api_response(url, response_data, schema_hint)
    
    async def get_page_metadata(self, url: str, quick_mode: bool = True) -> PageMetadata:
        """
        Extract basic page metadata without full content processing.
        
        Args:
            url: URL to analyze
            quick_mode: Skip heavy content extraction
            
        Returns:
            PageMetadata object with basic page information
        """
        start_time = time.time()
        
        try:
            # Create lightweight config for quick analysis
            if quick_mode:
                quick_config = AnalysisConfig(
                    extract_main_content=False,
                    extract_links=False,
                    extract_images=False,
                    discover_feeds=False,
                    calculate_scores=False,
                    timeout=10  # Shorter timeout for quick mode
                )
                
                # Create temporary analyzer with quick config
                html_analyzer = HtmlAnalyzer(quick_config)
                
                try:
                    # Fetch and parse basic metadata only
                    response = await html_analyzer._fetch_page(url)
                    if not response:
                        return self._metadata_error_result(url, "Failed to fetch page")
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract basic metadata
                    title = html_analyzer._extract_title(soup)
                    description = html_analyzer._extract_description(soup)
                    language = html_analyzer._detect_language(title or description or "")
                    author = html_analyzer._extract_author(soup)
                    published_date = html_analyzer._extract_published_date(soup)
                    last_modified = html_analyzer._extract_last_modified(soup, response.headers)
                    
                    # Determine content type
                    content_type = self._detect_content_type(url)
                    
                    return PageMetadata(
                        url=url,
                        title=title,
                        description=description,
                        language=language,
                        author=author,
                        published_date=published_date,
                        last_modified=last_modified,
                        content_type=content_type,
                        status_code=response.status_code,
                        response_time=response.elapsed.total_seconds(),
                        content_length=len(response.content)
                    )
                    
                finally:
                    await html_analyzer.close()
            
            else:
                # Full analysis but extract only metadata
                analysis = await self.analyze_page(url)
                
                return PageMetadata(
                    url=analysis.url,
                    title=analysis.title,
                    description=analysis.description,
                    language=analysis.language,
                    author=analysis.author,
                    published_date=analysis.published_date,
                    last_modified=analysis.last_modified,
                    content_type=analysis.content_type,
                    status_code=analysis.status_code,
                    response_time=analysis.response_time,
                    content_length=analysis.content_length,
                    error_message=analysis.error_message
                )
                
        except Exception as e:
            return self._metadata_error_result(url, str(e))
    
    async def _analyze_with_semaphore(self, url: str, options: Optional[Dict[str, Any]] = None) -> PageAnalysis:
        """Analyze URL with semaphore-based concurrency control."""
        async with self._semaphore:
            return await self.analyze_page(url, options=options)
    
    def _detect_content_type(self, url: str, content_type_hint: Optional[str] = None) -> ContentType:
        """Detect content type from URL and hints."""
        if content_type_hint:
            hint_lower = content_type_hint.lower()
            if hint_lower in ["rss", "atom"]:
                return ContentType.RSS if hint_lower == "rss" else ContentType.ATOM
            elif hint_lower == "api":
                return ContentType.API
            elif hint_lower == "html":
                return ContentType.HTML
        
        # Analyze URL patterns
        url_lower = url.lower()
        parsed = urlparse(url_lower)
        path = parsed.path
        
        # Check for feed patterns
        feed_patterns = ['/feed', '/rss', '/atom', '.rss', '.xml', '.atom']
        if any(pattern in path for pattern in feed_patterns):
            if 'atom' in path:
                return ContentType.ATOM
            else:
                return ContentType.RSS
        
        # Check for API patterns
        api_patterns = ['/api/', '/v1/', '/v2/', '/json', '.json']
        if any(pattern in path for pattern in api_patterns):
            return ContentType.API
        
        # Default to HTML
        return ContentType.HTML
    
    def _merge_config_with_options(self, options: Dict[str, Any]) -> AnalysisConfig:
        """Merge analysis options with base configuration."""
        config_dict = self.config.model_dump()
        
        # Update with provided options
        for key, value in options.items():
            if hasattr(self.config, key):
                config_dict[key] = value
        
        return AnalysisConfig(**config_dict)
    
    async def _update_analyzer_configs(self, new_config: AnalysisConfig):
        """Update analyzer configurations if needed."""
        # For now, keep using existing analyzers
        # In a production system, might want to recreate analyzers with new config
        pass
    
    def _metadata_error_result(self, url: str, error_msg: str) -> PageMetadata:
        """Create error result for metadata extraction."""
        return PageMetadata(
            url=url,
            content_type=ContentType.UNKNOWN,
            error_message=error_msg
        )
    
    async def close(self):
        """Close all analyzers and cleanup resources."""
        await asyncio.gather(
            self.html_analyzer.close(),
            self.feed_analyzer.close(),
            self.api_analyzer.close(),
            return_exceptions=True
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()