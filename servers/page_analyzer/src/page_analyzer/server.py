"""Page Analyzer MCP Server

Provides comprehensive web page content analysis and extraction.
"""

import asyncio
import json
from typing import Optional, List, Dict, Any, Union

from mcp.server.fastmcp import FastMCP

try:
    from .analysis_manager import AnalysisManager
    from .analysis_types import AnalysisConfig, ContentType
except ImportError:
    # For running as script
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from analysis_manager import AnalysisManager
    from analysis_types import AnalysisConfig, ContentType

# Initialize FastMCP server
mcp = FastMCP("page_analyzer")

# Initialize analysis manager
analysis_manager = AnalysisManager()


@mcp.tool()
async def analyze_page(
    url: str,
    content_type: str = "auto",
    extract_links: bool = False,
    extract_images: bool = False,
    discover_feeds: bool = True,
    timeout: int = 30
) -> dict:
    """
    Analyze a single web page and extract content, metadata, and structure.
    
    Args:
        url: URL of the web page to analyze
        content_type: Expected content type hint ("html", "rss", "api", "auto")
        extract_links: Whether to extract external links from the page
        extract_images: Whether to extract image URLs from the page
        discover_feeds: Whether to discover RSS/Atom feeds on the page
        timeout: Request timeout in seconds (5-120)
        
    Returns:
        Dictionary containing extracted content, metadata, and analysis results
    """
    try:
        # Validate inputs
        content_type = content_type.lower() if content_type != "auto" else None
        timeout = max(5, min(timeout, 120))
        
        # Create analysis options
        options = {
            "extract_links": extract_links,
            "extract_images": extract_images,
            "discover_feeds": discover_feeds,
            "timeout": timeout
        }
        
        # Perform analysis
        analysis = await analysis_manager.analyze_page(
            url=url,
            content_type=content_type,
            options=options
        )
        
        # Convert to dictionary for JSON serialization
        return {
            "url": analysis.url,
            "content_type": analysis.content_type.value,
            "status": analysis.status.value,
            "title": analysis.title,
            "description": analysis.description,
            "main_content": analysis.main_content,
            "summary": analysis.summary,
            "language": analysis.language,
            "author": analysis.author,
            "published_date": analysis.published_date.isoformat() if analysis.published_date else None,
            "last_modified": analysis.last_modified.isoformat() if analysis.last_modified else None,
            "relevance_score": analysis.relevance_score,
            "quality_score": analysis.quality_score,
            "freshness_score": analysis.freshness_score,
            "feeds_discovered": analysis.feeds_discovered,
            "images": analysis.images,
            "external_links": analysis.external_links,
            "response_time": analysis.response_time,
            "content_length": analysis.content_length,
            "status_code": analysis.status_code,
            "analyzed_at": analysis.analyzed_at.isoformat(),
            "processing_time": analysis.processing_time,
            "error_message": analysis.error_message
        }
        
    except Exception as e:
        return {
            "error": f"Page analysis failed: {str(e)}",
            "url": url,
            "status": "error"
        }


@mcp.tool()
async def analyze_batch(
    urls: List[str],
    max_concurrent: int = 5,
    timeout_per_url: int = 30,
    extract_feeds: bool = True,
    extract_links: bool = False,
    full_content: bool = True
) -> dict:
    """
    Analyze multiple URLs concurrently with configurable options.
    
    Args:
        urls: List of URLs to analyze (1-50 URLs)
        max_concurrent: Maximum concurrent analyses (1-10)
        timeout_per_url: Timeout per URL in seconds (5-120)
        extract_feeds: Whether to discover feeds on pages
        extract_links: Whether to extract external links
        full_content: Whether to extract full content or just metadata
        
    Returns:
        Dictionary containing batch analysis results and statistics
    """
    try:
        # Validate inputs
        if not urls or len(urls) == 0:
            return {"error": "No URLs provided"}
        
        if len(urls) > 50:
            return {"error": "Too many URLs. Maximum is 50."}
        
        max_concurrent = max(1, min(max_concurrent, 10))
        timeout_per_url = max(5, min(timeout_per_url, 120))
        
        # Create analysis options
        options = {
            "extract_links": extract_links,
            "discover_feeds": extract_feeds,
            "extract_main_content": full_content,
            "timeout": timeout_per_url
        }
        
        # Perform batch analysis
        batch_response = await analysis_manager.analyze_batch(
            urls=urls,
            max_concurrent=max_concurrent,
            options=options
        )
        
        # Convert results to dictionaries
        results = []
        for analysis in batch_response.results:
            results.append({
                "url": analysis.url,
                "content_type": analysis.content_type.value,
                "status": analysis.status.value,
                "title": analysis.title,
                "description": analysis.description,
                "main_content": analysis.main_content if full_content else None,
                "summary": analysis.summary,
                "language": analysis.language,
                "relevance_score": analysis.relevance_score,
                "quality_score": analysis.quality_score,
                "freshness_score": analysis.freshness_score,
                "feeds_discovered": analysis.feeds_discovered if extract_feeds else [],
                "external_links": analysis.external_links if extract_links else [],
                "response_time": analysis.response_time,
                "processing_time": analysis.processing_time,
                "error_message": analysis.error_message
            })
        
        return {
            "total_requested": batch_response.total_requested,
            "successful_analyses": batch_response.successful_analyses,
            "failed_analyses": batch_response.failed_analyses,
            "total_processing_time": batch_response.total_processing_time,
            "results": results,
            "errors": batch_response.errors
        }
        
    except Exception as e:
        return {
            "error": f"Batch analysis failed: {str(e)}",
            "total_requested": len(urls) if urls else 0,
            "successful_analyses": 0,
            "failed_analyses": len(urls) if urls else 0
        }


@mcp.tool()
async def extract_feeds(
    url: str,
    discover_depth: int = 2,
    validate_feeds: bool = True
) -> dict:
    """
    Discover and analyze RSS/Atom feeds from a webpage or domain.
    
    Args:
        url: URL to search for feeds
        discover_depth: How deep to search for feed links (1-5)
        validate_feeds: Whether to validate discovered feeds
        
    Returns:
        Dictionary containing discovered feeds and their metadata
    """
    try:
        # Validate inputs
        discover_depth = max(1, min(discover_depth, 5))
        
        # Discover feeds
        feed_discovery = await analysis_manager.extract_feeds(
            url=url,
            discover_depth=discover_depth
        )
        
        # Convert feed info to dictionaries
        feeds_found = []
        for feed_info in feed_discovery.feeds_found:
            feeds_found.append({
                "url": feed_info.url,
                "title": feed_info.title,
                "description": feed_info.description,
                "feed_type": feed_info.feed_type.value,
                "last_updated": feed_info.last_updated.isoformat() if feed_info.last_updated else None,
                "entry_count": feed_info.entry_count,
                "is_active": feed_info.is_active,
                "language": feed_info.language
            })
        
        return {
            "source_url": feed_discovery.source_url,
            "total_feeds": feed_discovery.total_feeds,
            "discovery_method": feed_discovery.discovery_method,
            "discovery_time": feed_discovery.discovery_time,
            "feeds_found": feeds_found,
            "error_message": feed_discovery.error_message
        }
        
    except Exception as e:
        return {
            "error": f"Feed discovery failed: {str(e)}",
            "source_url": url,
            "total_feeds": 0,
            "feeds_found": []
        }


@mcp.tool()
async def analyze_api_response(
    url: str,
    response_data: Optional[Union[dict, str]] = None,
    schema_hint: Optional[str] = None
) -> dict:
    """
    Analyze structured API responses and extract relevant content.
    
    Args:
        url: API endpoint URL
        response_data: Pre-fetched response data (optional)
        schema_hint: Expected data structure type (optional)
        
    Returns:
        Dictionary containing structured content extraction results
    """
    try:
        # Perform API analysis
        api_analysis = await analysis_manager.analyze_api_response(
            url=url,
            response_data=response_data,
            schema_hint=schema_hint
        )
        
        # Convert to dictionary for JSON serialization
        return {
            "endpoint_url": api_analysis.endpoint_url,
            "response_structure": api_analysis.response_structure,
            "schema_detected": api_analysis.schema_detected,
            "total_records": api_analysis.total_records,
            "data_quality": api_analysis.data_quality,
            "processing_time": api_analysis.processing_time,
            "extracted_content": api_analysis.extracted_content,
            "error_message": api_analysis.error_message
        }
        
    except Exception as e:
        return {
            "error": f"API analysis failed: {str(e)}",
            "endpoint_url": url,
            "total_records": 0,
            "data_quality": 0.0
        }


@mcp.tool()
async def get_page_metadata(
    url: str,
    quick_mode: bool = True
) -> dict:
    """
    Extract basic page metadata without full content processing.
    
    Args:
        url: URL to analyze
        quick_mode: Skip heavy content extraction for faster results
        
    Returns:
        Dictionary containing basic page metadata and information
    """
    try:
        # Get page metadata
        metadata = await analysis_manager.get_page_metadata(
            url=url,
            quick_mode=quick_mode
        )
        
        # Convert to dictionary for JSON serialization
        return {
            "url": metadata.url,
            "title": metadata.title,
            "description": metadata.description,
            "language": metadata.language,
            "author": metadata.author,
            "published_date": metadata.published_date.isoformat() if metadata.published_date else None,
            "last_modified": metadata.last_modified.isoformat() if metadata.last_modified else None,
            "content_type": metadata.content_type.value,
            "status_code": metadata.status_code,
            "response_time": metadata.response_time,
            "content_length": metadata.content_length,
            "error_message": metadata.error_message
        }
        
    except Exception as e:
        return {
            "error": f"Metadata extraction failed: {str(e)}",
            "url": url,
            "content_type": "unknown"
        }


# Additional utility tool for configuration and status
@mcp.tool()
async def get_analyzer_status() -> dict:
    """
    Get status and configuration information for the page analyzer.
    
    Returns:
        Dictionary showing analyzer capabilities and current configuration
    """
    try:
        config = analysis_manager.config
        
        return {
            "analyzer_version": "1.0.0",
            "supported_content_types": [ct.value for ct in ContentType],
            "available_analyzers": ["html", "feed", "api"],
            "configuration": {
                "timeout": config.timeout,
                "max_content_length": config.max_content_length,
                "extract_main_content": config.extract_main_content,
                "extract_metadata": config.extract_metadata,
                "discover_feeds": config.discover_feeds,
                "calculate_scores": config.calculate_scores,
                "user_agent": config.user_agent,
                "follow_redirects": config.follow_redirects,
                "max_redirects": config.max_redirects,
                "detect_language": config.detect_language
            },
            "features": {
                "html_content_extraction": True,
                "rss_atom_feed_parsing": True,
                "api_response_analysis": True,
                "batch_processing": True,
                "concurrent_analysis": True,
                "metadata_extraction": True,
                "feed_discovery": True,
                "language_detection": True,
                "content_scoring": True
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get analyzer status: {str(e)}",
            "analyzer_version": "1.0.0",
            "available_analyzers": ["html", "feed", "api"]
        }


if __name__ == "__main__":
    mcp.run()