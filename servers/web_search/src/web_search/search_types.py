"""Type definitions for web search functionality."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchProvider(str, Enum):
    """Available search providers."""
    SERPAPI = "serpapi"
    PERPLEXITY = "perplexity"  
    DUCKDUCKGO = "duckduckgo"
    TAVILY = "tavily"
    CLAUDE = "claude"


class SearchResult(BaseModel):
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: Optional[str] = None
    published_date: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response from a search provider."""
    query: str
    provider: SearchProvider
    results: List[SearchResult]
    total_results: Optional[int] = None
    search_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchConfig(BaseModel):
    """Configuration for search providers."""
    provider: SearchProvider
    api_key: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=100)
    safe_search: bool = True
    region: Optional[str] = None
    language: Optional[str] = None
    timeout: int = Field(default=30, ge=1, le=300)
    
    # Provider-specific settings
    serpapi_engine: str = "google"  # google, bing, duckduckgo, etc.
    perplexity_model: str = "sonar-pro"  # sonar-pro, sonar-small, etc.
    duckduckgo_safesearch: str = "moderate"  # strict, moderate, off