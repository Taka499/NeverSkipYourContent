"""API response analyzer for structured data sources."""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ..analysis_types import (
    ApiAnalysis,
    PageAnalysis,
    ContentType,
    AnalysisStatus,
    AnalysisConfig
)


class ApiAnalyzer:
    """Analyzer for structured API responses and data sources."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize API analyzer with configuration."""
        self.config = config or AnalysisConfig()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=self.config.follow_redirects,
            headers={"User-Agent": self.config.user_agent}
        )
    
    async def analyze_api_response(self, url: str, response_data: Optional[Union[dict, str]] = None,
                                 schema_hint: Optional[str] = None) -> ApiAnalysis:
        """
        Analyze a structured API response and extract relevant content.
        
        Args:
            url: API endpoint URL
            response_data: Pre-fetched response data (optional)
            schema_hint: Expected data structure type (optional)
            
        Returns:
            ApiAnalysis object with structured content extraction
        """
        start_time = time.time()
        
        try:
            # Fetch data if not provided
            if response_data is None:
                response_data = await self._fetch_api_data(url)
                if response_data is None:
                    return self._api_error_result(url, "Failed to fetch API data", start_time)
            
            # Determine response structure
            response_structure = self._analyze_structure(response_data)
            
            # Extract content based on structure
            extracted_content = self._extract_content(response_data, schema_hint)
            
            # Detect schema if possible
            schema_detected = self._detect_schema(response_data, schema_hint)
            
            # Calculate data quality
            data_quality = self._calculate_data_quality(extracted_content, response_data)
            
            processing_time = time.time() - start_time
            
            return ApiAnalysis(
                endpoint_url=url,
                response_structure=response_structure,
                extracted_content=extracted_content,
                schema_detected=schema_detected,
                total_records=len(extracted_content),
                data_quality=data_quality,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ApiAnalysis(
                endpoint_url=url,
                response_structure="error",
                extracted_content=[],
                total_records=0,
                data_quality=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def analyze_api_as_page(self, url: str, response_data: Optional[Union[dict, str]] = None) -> PageAnalysis:
        """
        Analyze API response as a page for integration with general page analysis.
        
        Args:
            url: API endpoint URL
            response_data: Pre-fetched response data (optional)
            
        Returns:
            PageAnalysis object with API content formatted as page data
        """
        start_time = time.time()
        
        try:
            # Get API analysis first
            api_analysis = await self.analyze_api_response(url, response_data)
            
            if api_analysis.error_message:
                return self._page_error_result(url, api_analysis.error_message, start_time)
            
            # Convert API data to page format
            title = self._extract_api_title(response_data, api_analysis.extracted_content)
            description = self._extract_api_description(response_data, api_analysis.extracted_content)
            main_content = self._format_api_content(api_analysis.extracted_content)
            summary = self._generate_api_summary(api_analysis.extracted_content)
            
            # Calculate scores
            relevance_score = min(api_analysis.data_quality, 1.0)
            quality_score = self._calculate_api_quality_score(api_analysis)
            freshness_score = self._calculate_api_freshness_score(api_analysis.extracted_content)
            
            # Extract links if present
            external_links = self._extract_api_links(api_analysis.extracted_content)
            
            processing_time = time.time() - start_time
            
            return PageAnalysis(
                url=url,
                content_type=ContentType.API,
                status=AnalysisStatus.SUCCESS,
                title=title,
                description=description,
                main_content=main_content,
                summary=summary,
                relevance_score=relevance_score,
                quality_score=quality_score,
                freshness_score=freshness_score,
                external_links=external_links,
                response_time=0.0,  # Would need original response
                content_length=len(str(response_data)) if response_data else 0,
                analyzed_at=datetime.now(),
                processing_time=processing_time
            )
            
        except Exception as e:
            return self._page_error_result(url, str(e), start_time)
    
    async def _fetch_api_data(self, url: str) -> Optional[Union[dict, str]]:
        """Fetch data from API endpoint."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                return response.json()
            except:
                # Fall back to text
                return response.text
                
        except Exception:
            return None
    
    def _analyze_structure(self, data: Union[dict, str, list]) -> str:
        """Analyze the structure of the response data."""
        if isinstance(data, dict):
            keys = list(data.keys())
            if len(keys) <= 5:
                return f"object({', '.join(keys)})"
            else:
                return f"object({len(keys)} keys)"
        elif isinstance(data, list):
            if len(data) == 0:
                return "empty_array"
            elif len(data) == 1:
                return f"array(1 item, {type(data[0]).__name__})"
            else:
                return f"array({len(data)} items, {type(data[0]).__name__})"
        elif isinstance(data, str):
            if data.strip().startswith('<'):
                return "xml/html"
            else:
                return f"string({len(data)} chars)"
        else:
            return type(data).__name__
    
    def _extract_content(self, data: Union[dict, str, list], schema_hint: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract structured content from API response."""
        extracted = []
        
        try:
            if isinstance(data, dict):
                extracted.extend(self._extract_from_dict(data))
            elif isinstance(data, list):
                extracted.extend(self._extract_from_list(data))
            elif isinstance(data, str):
                extracted.extend(self._extract_from_string(data))
            
        except Exception:
            pass
        
        return extracted[:100]  # Limit to 100 items
    
    def _extract_from_dict(self, data: dict) -> List[Dict[str, Any]]:
        """Extract content from dictionary response."""
        content = []
        
        # Common patterns for content extraction
        content_fields = [
            'items', 'data', 'results', 'entries', 'posts', 'articles',
            'content', 'records', 'documents', 'objects'
        ]
        
        # Try to find array fields first
        for field in content_fields:
            if field in data and isinstance(data[field], list):
                for item in data[field][:50]:  # Limit items
                    if isinstance(item, dict):
                        content.append(self._normalize_item(item))
                return content
        
        # If no array found, extract from root object
        normalized = self._normalize_item(data)
        if normalized:
            content.append(normalized)
        
        return content
    
    def _extract_from_list(self, data: list) -> List[Dict[str, Any]]:
        """Extract content from list response."""
        content = []
        
        for item in data[:50]:  # Limit items
            if isinstance(item, dict):
                normalized = self._normalize_item(item)
                if normalized:
                    content.append(normalized)
            elif isinstance(item, str):
                content.append({
                    'content': item,
                    'type': 'string'
                })
        
        return content
    
    def _extract_from_string(self, data: str) -> List[Dict[str, Any]]:
        """Extract content from string response (XML, HTML, etc.)."""
        content = []
        
        try:
            # Try to parse as XML/HTML
            if data.strip().startswith('<'):
                soup = BeautifulSoup(data, 'xml')
                
                # Extract text content
                text_content = soup.get_text(strip=True)
                if text_content:
                    content.append({
                        'content': text_content[:1000],
                        'type': 'xml_text',
                        'source': 'xml_parsing'
                    })
                
                # Extract structured elements
                for element in soup.find_all(True)[:20]:  # Limit elements
                    if element.name and element.get_text(strip=True):
                        content.append({
                            'tag': element.name,
                            'content': element.get_text(strip=True)[:500],
                            'type': 'xml_element',
                            'attributes': dict(element.attrs) if element.attrs else {}
                        })
            
            else:
                # Treat as plain text
                content.append({
                    'content': data[:1000],
                    'type': 'plain_text'
                })
                
        except Exception:
            # Fall back to plain text
            content.append({
                'content': data[:1000],
                'type': 'plain_text'
            })
        
        return content
    
    def _normalize_item(self, item: dict) -> Optional[Dict[str, Any]]:
        """Normalize a data item to standard format."""
        if not isinstance(item, dict):
            return None
        
        normalized = {}
        
        # Common field mappings
        title_fields = ['title', 'name', 'headline', 'subject', 'summary']
        content_fields = ['content', 'description', 'body', 'text', 'message']
        url_fields = ['url', 'link', 'href', 'permalink']
        date_fields = ['date', 'created_at', 'updated_at', 'published_at', 'timestamp']
        id_fields = ['id', 'uuid', 'key', 'identifier']
        
        # Extract common fields
        for field in title_fields:
            if field in item and item[field]:
                normalized['title'] = str(item[field])[:200]
                break
        
        for field in content_fields:
            if field in item and item[field]:
                normalized['content'] = str(item[field])[:1000]
                break
        
        for field in url_fields:
            if field in item and item[field]:
                normalized['url'] = str(item[field])
                break
        
        for field in date_fields:
            if field in item and item[field]:
                normalized['date'] = str(item[field])
                break
        
        for field in id_fields:
            if field in item and item[field]:
                normalized['id'] = str(item[field])
                break
        
        # Add other fields as metadata
        metadata = {}
        for key, value in item.items():
            if key not in normalized and value is not None:
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                elif isinstance(value, (list, dict)):
                    metadata[key] = str(value)[:100]  # Truncate complex types
        
        if metadata:
            normalized['metadata'] = metadata
        
        # Only return if we extracted meaningful content
        if normalized.get('title') or normalized.get('content'):
            return normalized
        
        return None
    
    def _detect_schema(self, data: Union[dict, str, list], schema_hint: Optional[str] = None) -> Optional[str]:
        """Detect or infer the data schema."""
        if schema_hint:
            return schema_hint
        
        # Simple schema detection based on structure
        if isinstance(data, dict):
            keys = set(data.keys())
            
            # Common API patterns
            if {'items', 'total', 'page'}.issubset(keys):
                return "paginated_api"
            elif {'data', 'meta'}.issubset(keys):
                return "jsonapi"
            elif {'results'}.issubset(keys):
                return "search_results"
            elif {'feed', 'entries'}.issubset(keys):
                return "feed_api"
            else:
                return "generic_object"
        
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                return "object_array"
            else:
                return "simple_array"
        
        elif isinstance(data, str):
            if data.strip().startswith('<?xml'):
                return "xml"
            elif data.strip().startswith('<'):
                return "html"
            else:
                return "text"
        
        return "unknown"
    
    def _calculate_data_quality(self, extracted_content: List[Dict[str, Any]], raw_data: Any) -> float:
        """Calculate quality score for API data."""
        if not extracted_content:
            return 0.0
        
        quality_score = 0.0
        
        # Score based on extraction success
        quality_score += 0.3  # Base score for successful extraction
        
        # Score based on content richness
        rich_items = 0
        for item in extracted_content[:10]:  # Check first 10 items
            item_score = 0
            
            if item.get('title'):
                item_score += 1
            if item.get('content') and len(item.get('content', '')) > 20:
                item_score += 1
            if item.get('url'):
                item_score += 1
            if item.get('date'):
                item_score += 1
            
            if item_score >= 2:
                rich_items += 1
        
        if extracted_content:
            richness_ratio = rich_items / min(len(extracted_content), 10)
            quality_score += richness_ratio * 0.4
        
        # Score based on structure consistency
        if len(extracted_content) > 1:
            first_keys = set(extracted_content[0].keys())
            consistent_items = sum(
                1 for item in extracted_content[1:6]  # Check first 5 additional items
                if len(set(item.keys()).intersection(first_keys)) >= len(first_keys) * 0.5
            )
            consistency_ratio = consistent_items / min(len(extracted_content) - 1, 5)
            quality_score += consistency_ratio * 0.3
        
        return min(quality_score, 1.0)
    
    def _extract_api_title(self, raw_data: Any, extracted_content: List[Dict[str, Any]]) -> Optional[str]:
        """Extract title for API-based page analysis."""
        # Try to get title from metadata
        if isinstance(raw_data, dict):
            title_fields = ['title', 'name', 'api_name', 'service_name']
            for field in title_fields:
                if field in raw_data and raw_data[field]:
                    return str(raw_data[field])[:200]
        
        # Fall back to first item title
        if extracted_content and extracted_content[0].get('title'):
            return f"API Data: {extracted_content[0]['title']}"
        
        # Generate generic title
        return f"API Response ({len(extracted_content)} items)"
    
    def _extract_api_description(self, raw_data: Any, extracted_content: List[Dict[str, Any]]) -> Optional[str]:
        """Extract description for API-based page analysis."""
        if isinstance(raw_data, dict):
            desc_fields = ['description', 'summary', 'about']
            for field in desc_fields:
                if field in raw_data and raw_data[field]:
                    return str(raw_data[field])[:500]
        
        # Generate description from content
        if extracted_content:
            return f"Structured API data containing {len(extracted_content)} items"
        
        return None
    
    def _format_api_content(self, extracted_content: List[Dict[str, Any]]) -> Optional[str]:
        """Format extracted API content as text."""
        if not extracted_content:
            return None
        
        content_parts = []
        
        for item in extracted_content[:20]:  # Limit to 20 items
            parts = []
            
            if item.get('title'):
                parts.append(f"Title: {item['title']}")
            
            if item.get('content'):
                parts.append(f"Content: {item['content']}")
            
            if item.get('url'):
                parts.append(f"URL: {item['url']}")
            
            if parts:
                content_parts.append('\n'.join(parts))
        
        return '\n\n---\n\n'.join(content_parts) if content_parts else None
    
    def _generate_api_summary(self, extracted_content: List[Dict[str, Any]]) -> Optional[str]:
        """Generate summary from API content."""
        if not extracted_content:
            return None
        
        titles = [item.get('title', '') for item in extracted_content[:5] if item.get('title')]
        
        if titles:
            summary = f"API contains {len(extracted_content)} items. Recent: " + "; ".join(titles[:3])
            return summary[:300]
        
        return f"API response with {len(extracted_content)} structured data items"
    
    def _calculate_api_quality_score(self, api_analysis: ApiAnalysis) -> float:
        """Calculate quality score for API page analysis."""
        return min(api_analysis.data_quality + 0.2, 1.0)  # Bonus for API structure
    
    def _calculate_api_freshness_score(self, extracted_content: List[Dict[str, Any]]) -> float:
        """Calculate freshness score based on API data timestamps."""
        if not extracted_content:
            return 0.0
        
        now = datetime.now()
        fresh_items = 0
        
        for item in extracted_content[:10]:
            date_str = item.get('date')
            if date_str:
                try:
                    from dateutil import parser
                    item_date = parser.parse(date_str)
                    # Make timezone-naive for comparison
                    if item_date.tzinfo is not None:
                        item_date = item_date.replace(tzinfo=None)
                    
                    days_old = (now - item_date).days
                    
                    if days_old <= 1:
                        fresh_items += 1.0
                    elif days_old <= 7:
                        fresh_items += 0.8
                    elif days_old <= 30:
                        fresh_items += 0.4
                
                except Exception:
                    continue
        
        if extracted_content:
            return min(fresh_items / min(len(extracted_content), 10), 1.0)
        
        return 0.0
    
    def _extract_api_links(self, extracted_content: List[Dict[str, Any]]) -> List[str]:
        """Extract links from API content."""
        links = []
        
        for item in extracted_content[:50]:  # Process first 50 items
            url = item.get('url')
            if url and url not in links:
                links.append(url)
        
        return links
    
    def _api_error_result(self, url: str, error_msg: str, start_time: float) -> ApiAnalysis:
        """Create error result for failed API analysis."""
        processing_time = time.time() - start_time
        
        return ApiAnalysis(
            endpoint_url=url,
            response_structure="error",
            extracted_content=[],
            total_records=0,
            data_quality=0.0,
            processing_time=processing_time,
            error_message=error_msg
        )
    
    def _page_error_result(self, url: str, error_msg: str, start_time: float,
                          status: AnalysisStatus = AnalysisStatus.ERROR) -> PageAnalysis:
        """Create error result for failed page analysis of API."""
        processing_time = time.time() - start_time
        
        return PageAnalysis(
            url=url,
            content_type=ContentType.API,
            status=status,
            error_message=error_msg,
            analyzed_at=datetime.now(),
            processing_time=processing_time
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()