"""Type definitions for page analysis functionality."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class ContentType(str, Enum):
    """Supported content types for analysis."""
    HTML = "html"
    RSS = "rss"
    ATOM = "atom"
    API = "api"
    PDF = "pdf"
    UNKNOWN = "unknown"


class AnalysisStatus(str, Enum):
    """Status of content analysis."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    PARTIAL = "partial"


class FeedType(str, Enum):
    """Types of content feeds."""
    RSS = "rss"
    ATOM = "atom"
    JSON = "json"


class PageMetadata(BaseModel):
    """Basic page metadata without full content processing."""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    content_type: ContentType = ContentType.UNKNOWN
    status_code: Optional[int] = None
    response_time: float = 0.0
    content_length: int = 0
    error_message: Optional[str] = None


class PageAnalysis(BaseModel):
    """Comprehensive analysis of a web page or content source."""
    url: str
    content_type: ContentType
    status: AnalysisStatus
    
    # Content Data
    title: Optional[str] = None
    description: Optional[str] = None
    main_content: Optional[str] = None
    summary: Optional[str] = None
    
    # Metadata
    language: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    # Analysis Results
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    freshness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Discovered Resources
    feeds_discovered: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    external_links: List[str] = Field(default_factory=list)
    
    # Technical Details
    response_time: float = 0.0
    content_length: int = 0
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # Processing Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)
    processing_time: float = 0.0


class FeedInfo(BaseModel):
    """Information about a discovered feed."""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    feed_type: FeedType
    last_updated: Optional[datetime] = None
    entry_count: int = 0
    is_active: bool = True
    language: Optional[str] = None


class FeedDiscovery(BaseModel):
    """Results of feed discovery on a webpage or domain."""
    source_url: str
    feeds_found: List[FeedInfo] = Field(default_factory=list)
    discovery_method: str = "automatic"
    total_feeds: int = 0
    discovery_time: float = 0.0
    error_message: Optional[str] = None


class ApiAnalysis(BaseModel):
    """Analysis results for structured API responses."""
    endpoint_url: str
    response_structure: str
    extracted_content: List[Dict[str, Any]] = Field(default_factory=list)
    schema_detected: Optional[str] = None
    total_records: int = 0
    data_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_time: float = 0.0
    error_message: Optional[str] = None


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis of multiple URLs."""
    urls: List[str] = Field(min_items=1, max_items=50)
    max_concurrent: int = Field(default=5, ge=1, le=10)
    timeout_per_url: int = Field(default=30, ge=5, le=120)
    extract_feeds: bool = True
    extract_links: bool = False
    full_content: bool = True


class BatchAnalysisResponse(BaseModel):
    """Response from batch analysis operation."""
    total_requested: int
    successful_analyses: int
    failed_analyses: int
    results: List[PageAnalysis] = Field(default_factory=list)
    total_processing_time: float = 0.0
    errors: List[str] = Field(default_factory=list)


class AnalysisConfig(BaseModel):
    """Configuration for page analysis operations."""
    timeout: int = Field(default=30, ge=5, le=120)
    max_content_length: int = Field(default=1_000_000, ge=10_000)  # 1MB default
    extract_main_content: bool = True
    extract_metadata: bool = True
    extract_links: bool = False
    extract_images: bool = False
    discover_feeds: bool = True
    calculate_scores: bool = True
    user_agent: str = "NSYC Page Analyzer 1.0"
    follow_redirects: bool = True
    max_redirects: int = Field(default=5, ge=0, le=10)
    
    # Content extraction settings
    min_content_length: int = Field(default=100, ge=0)
    readability_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Language detection
    detect_language: bool = True
    
    # Feed discovery settings  
    feed_discovery_depth: int = Field(default=2, ge=1, le=5)
    validate_feeds: bool = True