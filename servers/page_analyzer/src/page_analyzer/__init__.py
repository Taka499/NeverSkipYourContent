"""
NSYC Page Analyzer MCP Server

A comprehensive MCP server for web page content analysis and extraction.
Supports HTML pages, RSS feeds, API responses, and other content formats.
"""

__version__ = "0.1.0"
__author__ = "NSYC"

from .analysis_manager import AnalysisManager
from .analysis_types import (
    PageAnalysis,
    PageMetadata,
    FeedDiscovery,
    ApiAnalysis,
    AnalysisConfig,
    ContentType,
    AnalysisStatus
)

__all__ = [
    "AnalysisManager",
    "PageAnalysis", 
    "PageMetadata",
    "FeedDiscovery",
    "ApiAnalysis",
    "AnalysisConfig",
    "ContentType",
    "AnalysisStatus"
]