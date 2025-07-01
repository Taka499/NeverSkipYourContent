"""RSS/Atom feed analyzer for content feeds."""

import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import feedparser
import httpx
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException as LangDetectError

from ..analysis_types import (
    FeedDiscovery,
    FeedInfo,
    FeedType,
    PageAnalysis,
    ContentType,
    AnalysisStatus,
    AnalysisConfig
)


class FeedAnalyzer:
    """Analyzer for RSS/Atom feeds and feed discovery."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize feed analyzer with configuration."""
        self.config = config or AnalysisConfig()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=self.config.follow_redirects,
            headers={"User-Agent": self.config.user_agent}
        )
    
    async def discover_feeds(self, url: str, discovery_depth: int = 2) -> FeedDiscovery:
        """
        Discover RSS/Atom feeds from a webpage or domain.
        
        Args:
            url: URL to search for feeds
            discovery_depth: How deep to search for feed links
            
        Returns:
            FeedDiscovery object with found feeds and metadata
        """
        start_time = time.time()
        feeds_found = []
        
        try:
            # Try direct feed analysis first
            direct_feed = await self._analyze_direct_feed(url)
            if direct_feed:
                feeds_found.append(direct_feed)
            else:
                # Search for feeds on the page
                discovered_feeds = await self._discover_feeds_from_page(url)
                
                # Validate discovered feeds
                for feed_url in discovered_feeds[:10]:  # Limit validation to 10 feeds
                    feed_info = await self._analyze_direct_feed(feed_url)
                    if feed_info:
                        feeds_found.append(feed_info)
            
            discovery_time = time.time() - start_time
            
            return FeedDiscovery(
                source_url=url,
                feeds_found=feeds_found,
                discovery_method="automatic",
                total_feeds=len(feeds_found),
                discovery_time=discovery_time
            )
            
        except Exception as e:
            discovery_time = time.time() - start_time
            return FeedDiscovery(
                source_url=url,
                feeds_found=[],
                discovery_method="automatic",
                total_feeds=0,
                discovery_time=discovery_time,
                error_message=str(e)
            )
    
    async def analyze_feed(self, feed_url: str) -> PageAnalysis:
        """
        Analyze an RSS/Atom feed and extract content and metadata.
        
        Args:
            feed_url: URL of the feed to analyze
            
        Returns:
            PageAnalysis object with feed content and metadata
        """
        start_time = time.time()
        
        try:
            # Fetch the feed
            response = await self.client.get(feed_url)
            response.raise_for_status()
            
            # Parse the feed
            parsed_feed = feedparser.parse(response.content)
            
            if parsed_feed.bozo and not parsed_feed.entries:
                return self._error_result(feed_url, "Invalid or empty feed", start_time)
            
            # Extract feed metadata
            feed_info = parsed_feed.feed
            title = feed_info.get('title', '')
            description = feed_info.get('description', '') or feed_info.get('subtitle', '')
            
            # Extract language
            language = self._extract_feed_language(feed_info)
            
            # Extract dates
            published_date = self._parse_feed_date(feed_info.get('published_parsed'))
            last_modified = self._parse_feed_date(feed_info.get('updated_parsed'))
            
            # Generate content summary from recent entries
            main_content = self._extract_feed_content(parsed_feed.entries)
            summary = self._generate_feed_summary(parsed_feed.entries[:5])  # Use first 5 entries
            
            # Determine feed type
            feed_type = self._determine_feed_type(parsed_feed, response.headers)
            
            # Calculate scores
            relevance_score = self._calculate_feed_relevance_score(parsed_feed)
            quality_score = self._calculate_feed_quality_score(parsed_feed)
            freshness_score = self._calculate_feed_freshness_score(parsed_feed.entries)
            
            # Extract links from entries
            external_links = self._extract_feed_links(parsed_feed.entries)
            
            processing_time = time.time() - start_time
            
            return PageAnalysis(
                url=feed_url,
                content_type=ContentType.RSS if feed_type == FeedType.RSS else ContentType.ATOM,
                status=AnalysisStatus.SUCCESS,
                title=title,
                description=description,
                main_content=main_content,
                summary=summary,
                language=language,
                published_date=published_date,
                last_modified=last_modified,
                relevance_score=relevance_score,
                quality_score=quality_score,
                freshness_score=freshness_score,
                external_links=external_links,
                response_time=response.elapsed.total_seconds(),
                content_length=len(response.content),
                status_code=response.status_code,
                analyzed_at=datetime.now(),
                processing_time=processing_time
            )
            
        except httpx.TimeoutException:
            return self._error_result(feed_url, "Request timeout", start_time, AnalysisStatus.TIMEOUT)
        except httpx.HTTPStatusError as e:
            return self._error_result(feed_url, f"HTTP {e.response.status_code}", start_time)
        except Exception as e:
            return self._error_result(feed_url, str(e), start_time)
    
    async def _analyze_direct_feed(self, feed_url: str) -> Optional[FeedInfo]:
        """Analyze a URL to see if it's a valid feed."""
        try:
            response = await self.client.get(feed_url)
            response.raise_for_status()
            
            # Parse feed
            parsed_feed = feedparser.parse(response.content)
            
            if parsed_feed.bozo and not parsed_feed.entries:
                return None
            
            # Extract feed info
            feed_info = parsed_feed.feed
            title = feed_info.get('title', '')
            description = feed_info.get('description', '') or feed_info.get('subtitle', '')
            
            # Determine feed type
            feed_type = self._determine_feed_type(parsed_feed, response.headers)
            
            # Extract last updated
            last_updated = self._parse_feed_date(feed_info.get('updated_parsed'))
            
            # Check if feed is active (has recent entries)
            is_active = self._is_feed_active(parsed_feed.entries)
            
            # Detect language
            language = self._extract_feed_language(feed_info)
            
            return FeedInfo(
                url=feed_url,
                title=title,
                description=description,
                feed_type=feed_type,
                last_updated=last_updated,
                entry_count=len(parsed_feed.entries),
                is_active=is_active,
                language=language
            )
            
        except Exception:
            return None
    
    async def _discover_feeds_from_page(self, url: str) -> List[str]:
        """Discover feed URLs from a webpage."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            feeds = []
            
            # Look for feed links in HTML head
            feed_links = soup.find_all('link', rel=lambda x: x and 'alternate' in x.lower())
            
            for link in feed_links:
                href = link.get('href')
                type_attr = link.get('type', '').lower()
                
                if href and any(feed_type in type_attr for feed_type in 
                              ['rss', 'atom', 'xml', 'feed']):
                    full_url = urljoin(url, href)
                    if full_url not in feeds:
                        feeds.append(full_url)
            
            # Look for common feed URLs
            base_domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            common_feeds = [
                '/feed', '/feeds', '/rss', '/rss.xml', '/atom.xml', 
                '/feeds/all.atom.xml', '/index.xml', '/feed.xml'
            ]
            
            for feed_path in common_feeds:
                feed_url = base_domain + feed_path
                if feed_url not in feeds:
                    feeds.append(feed_url)
            
            return feeds
            
        except Exception:
            return []
    
    def _determine_feed_type(self, parsed_feed, headers: dict) -> FeedType:
        """Determine the type of feed (RSS, Atom, JSON)."""
        # Check content type header
        content_type = headers.get('content-type', '').lower()
        
        if 'json' in content_type:
            return FeedType.JSON
        elif 'atom' in content_type:
            return FeedType.ATOM
        elif 'rss' in content_type or 'xml' in content_type:
            return FeedType.RSS
        
        # Check feed version
        version = parsed_feed.get('version', '').lower()
        if 'atom' in version:
            return FeedType.ATOM
        elif 'rss' in version:
            return FeedType.RSS
        
        # Default to RSS if uncertain
        return FeedType.RSS
    
    def _extract_feed_language(self, feed_info: dict) -> Optional[str]:
        """Extract language from feed metadata."""
        # Try various language fields
        language = (feed_info.get('language') or 
                   feed_info.get('xml:lang') or 
                   feed_info.get('lang'))
        
        if language:
            return language.strip()[:10]  # Limit length
        
        # Try to detect from title/description
        text_sample = (feed_info.get('title', '') + ' ' + 
                      feed_info.get('description', ''))[:1000]
        
        if text_sample.strip():
            try:
                return detect(text_sample)
            except LangDetectError:
                pass
        
        return None
    
    def _parse_feed_date(self, date_parsed) -> Optional[datetime]:
        """Parse feed date from feedparser time struct."""
        if date_parsed:
            try:
                return datetime(*date_parsed[:6])
            except (TypeError, ValueError):
                pass
        return None
    
    def _extract_feed_content(self, entries: List) -> Optional[str]:
        """Extract content from feed entries."""
        if not entries:
            return None
        
        content_parts = []
        
        for entry in entries[:10]:  # Use first 10 entries
            # Extract title
            title = entry.get('title', '')
            if title:
                content_parts.append(f"Title: {title}")
            
            # Extract content/summary
            content = (entry.get('content', [{}])[0].get('value', '') or
                      entry.get('summary', '') or
                      entry.get('description', ''))
            
            if content:
                # Clean HTML if present
                from bs4 import BeautifulSoup
                clean_content = BeautifulSoup(content, 'html.parser').get_text()
                content_parts.append(clean_content[:500])  # Limit entry content
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def _generate_feed_summary(self, entries: List) -> Optional[str]:
        """Generate summary from recent feed entries."""
        if not entries:
            return None
        
        summary_parts = []
        
        for entry in entries[:3]:  # Use first 3 entries for summary
            title = entry.get('title', '')
            if title:
                summary_parts.append(title)
        
        if summary_parts:
            summary = "Recent entries: " + "; ".join(summary_parts)
            return summary[:300]  # Limit summary length
        
        return None
    
    def _is_feed_active(self, entries: List) -> bool:
        """Check if feed has recent entries (within last 30 days)."""
        if not entries:
            return False
        
        now = datetime.now()
        
        for entry in entries[:5]:  # Check first 5 entries
            published = self._parse_feed_date(entry.get('published_parsed'))
            updated = self._parse_feed_date(entry.get('updated_parsed'))
            
            entry_date = updated or published
            if entry_date:
                days_old = (now - entry_date).days
                if days_old <= 30:
                    return True
        
        return False
    
    def _calculate_feed_relevance_score(self, parsed_feed) -> float:
        """Calculate feed relevance score."""
        if not self.config.calculate_scores:
            return 0.0
        
        score = 0.0
        feed_info = parsed_feed.feed
        entries = parsed_feed.entries
        
        # Score based on feed metadata
        if feed_info.get('title'):
            score += 0.2
        if feed_info.get('description'):
            score += 0.2
        
        # Score based on entries
        if entries:
            score += 0.3
            
            # Bonus for multiple entries
            if len(entries) >= 5:
                score += 0.1
            if len(entries) >= 10:
                score += 0.1
            
            # Check for content quality in entries
            content_entries = 0
            for entry in entries[:5]:
                if (entry.get('content') or entry.get('summary') or entry.get('description')):
                    content_entries += 1
            
            if content_entries >= 3:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_feed_quality_score(self, parsed_feed) -> float:
        """Calculate feed quality score."""
        if not self.config.calculate_scores:
            return 0.0
        
        score = 0.0
        feed_info = parsed_feed.feed
        entries = parsed_feed.entries
        
        # Check for proper feed metadata
        if feed_info.get('title') and len(feed_info.get('title', '')) > 5:
            score += 0.2
        if feed_info.get('description') and len(feed_info.get('description', '')) > 20:
            score += 0.2
        if feed_info.get('link'):
            score += 0.1
        
        # Check entry quality
        if entries:
            quality_entries = 0
            for entry in entries[:10]:
                entry_score = 0
                
                # Check for title
                if entry.get('title'):
                    entry_score += 1
                
                # Check for content
                content = (entry.get('content', [{}])[0].get('value', '') or
                          entry.get('summary', '') or
                          entry.get('description', ''))
                if content and len(content) > 50:
                    entry_score += 1
                
                # Check for date
                if (entry.get('published_parsed') or entry.get('updated_parsed')):
                    entry_score += 1
                
                # Check for link
                if entry.get('link'):
                    entry_score += 1
                
                if entry_score >= 3:
                    quality_entries += 1
            
            # Score based on percentage of quality entries
            if entries:
                quality_ratio = quality_entries / min(len(entries), 10)
                score += quality_ratio * 0.5
        
        return min(score, 1.0)
    
    def _calculate_feed_freshness_score(self, entries: List) -> float:
        """Calculate feed freshness score based on recent entries."""
        if not self.config.calculate_scores or not entries:
            return 0.0
        
        now = datetime.now()
        recent_entries = 0
        
        for entry in entries[:10]:
            published = self._parse_feed_date(entry.get('published_parsed'))
            updated = self._parse_feed_date(entry.get('updated_parsed'))
            
            entry_date = updated or published
            if entry_date:
                days_old = (now - entry_date).days
                
                if days_old <= 1:
                    recent_entries += 1.0
                elif days_old <= 7:
                    recent_entries += 0.8
                elif days_old <= 30:
                    recent_entries += 0.4
                elif days_old <= 90:
                    recent_entries += 0.2
        
        # Score based on recent entries
        if entries:
            freshness_ratio = recent_entries / min(len(entries), 10)
            return min(freshness_ratio, 1.0)
        
        return 0.0
    
    def _extract_feed_links(self, entries: List) -> List[str]:
        """Extract links from feed entries."""
        links = []
        
        for entry in entries[:20]:  # Process first 20 entries
            link = entry.get('link')
            if link and link not in links:
                links.append(link)
        
        return links
    
    def _error_result(self, url: str, error_msg: str, start_time: float,
                     status: AnalysisStatus = AnalysisStatus.ERROR) -> PageAnalysis:
        """Create error result for failed feed analysis."""
        processing_time = time.time() - start_time
        
        return PageAnalysis(
            url=url,
            content_type=ContentType.RSS,
            status=status,
            error_message=error_msg,
            analyzed_at=datetime.now(),
            processing_time=processing_time
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()