"""HTML content analyzer for web pages."""

import re
import time
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Comment
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException as LangDetectError
from readability import Document

from ..analysis_types import (
    PageAnalysis, 
    ContentType, 
    AnalysisStatus, 
    AnalysisConfig
)


class HtmlAnalyzer:
    """Analyzer for HTML web pages with content extraction and metadata analysis."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize HTML analyzer with configuration."""
        self.config = config or AnalysisConfig()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=self.config.follow_redirects,
            headers={"User-Agent": self.config.user_agent}
        )
    
    async def analyze(self, url: str) -> PageAnalysis:
        """
        Analyze an HTML page and extract content, metadata, and structure.
        
        Args:
            url: URL of the web page to analyze
            
        Returns:
            PageAnalysis object with extracted content and metadata
        """
        start_time = time.time()
        
        try:
            # Fetch the page
            response = await self._fetch_page(url)
            if not response:
                return self._error_result(url, "Failed to fetch page", start_time)
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metadata
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            
            # Extract main content using readability
            main_content = self._extract_main_content(response.text, url)
            
            # Generate summary from main content
            summary = self._generate_summary(main_content)
            
            # Extract additional metadata
            author = self._extract_author(soup)
            published_date = self._extract_published_date(soup)
            last_modified = self._extract_last_modified(soup, response.headers)
            
            # Detect language
            language = self._detect_language(main_content or title or "")
            
            # Calculate quality scores
            relevance_score = self._calculate_relevance_score(main_content, title, description)
            quality_score = self._calculate_quality_score(main_content, soup)
            freshness_score = self._calculate_freshness_score(published_date, last_modified)
            
            # Extract resources if configured
            feeds_discovered = []
            images = []
            external_links = []
            
            if self.config.discover_feeds:
                feeds_discovered = self._discover_feeds(soup, url)
            
            if self.config.extract_images:
                images = self._extract_images(soup, url)
                
            if self.config.extract_links:
                external_links = self._extract_external_links(soup, url)
            
            processing_time = time.time() - start_time
            
            return PageAnalysis(
                url=url,
                content_type=ContentType.HTML,
                status=AnalysisStatus.SUCCESS,
                title=title,
                description=description,
                main_content=main_content,
                summary=summary,
                language=language,
                author=author,
                published_date=published_date,
                last_modified=last_modified,
                relevance_score=relevance_score,
                quality_score=quality_score,
                freshness_score=freshness_score,
                feeds_discovered=feeds_discovered,
                images=images,
                external_links=external_links,
                response_time=response.elapsed.total_seconds(),
                content_length=len(response.content),
                status_code=response.status_code,
                analyzed_at=datetime.now(),
                processing_time=processing_time
            )
            
        except httpx.TimeoutException:
            return self._error_result(url, "Request timeout", start_time, AnalysisStatus.TIMEOUT)
        except httpx.HTTPStatusError as e:
            return self._error_result(url, f"HTTP {e.response.status_code}", start_time)
        except Exception as e:
            return self._error_result(url, str(e), start_time)
    
    async def _fetch_page(self, url: str) -> Optional[httpx.Response]:
        """Fetch web page with error handling."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Check content length
            if len(response.content) > self.config.max_content_length:
                return None
                
            return response
        except:
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title from HTML."""
        # Try various title sources
        title_selectors = [
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'h1'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get('content') if element.has_attr('content') else element.get_text()
                if title and title.strip():
                    return title.strip()[:200]  # Limit title length
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description from HTML."""
        # Try various description sources
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            'meta[name="twitter:description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element and element.get('content'):
                desc = element.get('content').strip()
                if desc:
                    return desc[:500]  # Limit description length
        
        return None
    
    def _extract_main_content(self, html: str, url: str) -> Optional[str]:
        """Extract main content using readability algorithm."""
        try:
            if not self.config.extract_main_content:
                return None
                
            doc = Document(html)
            content = doc.summary()
            
            if content:
                # Parse the extracted content to get clean text
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                    element.decompose()
                
                # Extract text content
                text = soup.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Check minimum length
                if len(text) >= self.config.min_content_length:
                    return text
            
        except Exception:
            pass
        
        return None
    
    def _generate_summary(self, content: Optional[str]) -> Optional[str]:
        """Generate a summary from main content."""
        if not content:
            return None
        
        # Simple summary: first few sentences up to 300 characters
        sentences = re.split(r'[.!?]+', content)
        summary = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(summary + sentence) <= 300:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() if summary else None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information from HTML."""
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="twitter:creator"]',
            '[rel="author"]',
            '.author',
            '.byline'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content') if element.has_attr('content') else element.get_text()
                if author and author.strip():
                    return author.strip()[:100]
        
        return None
    
    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract published date from HTML."""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'meta[name="publishdate"]',
            'time[datetime]',
            '[datetime]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content') or element.get('datetime') or element.get_text()
                if date_str:
                    try:
                        from dateutil import parser
                        return parser.parse(date_str)
                    except:
                        continue
        
        return None
    
    def _extract_last_modified(self, soup: BeautifulSoup, headers: dict) -> Optional[datetime]:
        """Extract last modified date from HTML or headers."""
        # Try HTML meta tags first
        modified_selectors = [
            'meta[property="article:modified_time"]',
            'meta[name="last-modified"]'
        ]
        
        for selector in modified_selectors:
            element = soup.select_one(selector)
            if element and element.get('content'):
                try:
                    from dateutil import parser
                    return parser.parse(element.get('content'))
                except:
                    continue
        
        # Try HTTP headers
        last_modified = headers.get('last-modified')
        if last_modified:
            try:
                from dateutil import parser
                return parser.parse(last_modified)
            except:
                pass
        
        return None
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of the content."""
        if not self.config.detect_language or not text:
            return None
        
        try:
            # Use only first 1000 characters for language detection
            sample = text[:1000]
            return detect(sample)
        except LangDetectError:
            return None
    
    def _calculate_relevance_score(self, content: Optional[str], title: Optional[str], 
                                 description: Optional[str]) -> float:
        """Calculate content relevance score."""
        if not self.config.calculate_scores:
            return 0.0
        
        score = 0.0
        
        # Basic scoring based on content presence and quality
        if title and len(title) > 10:
            score += 0.2
        
        if description and len(description) > 20:
            score += 0.2
        
        if content:
            # Score based on content length and structure
            content_length = len(content)
            if content_length >= 500:
                score += 0.4
            elif content_length >= 200:
                score += 0.2
            
            # Check for structured content (presence of meaningful sentences)
            sentences = re.split(r'[.!?]+', content)
            meaningful_sentences = [s for s in sentences if len(s.strip()) > 20]
            if len(meaningful_sentences) >= 3:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_quality_score(self, content: Optional[str], soup: BeautifulSoup) -> float:
        """Calculate content quality score."""
        if not self.config.calculate_scores:
            return 0.0
        
        score = 0.0
        
        # Check for semantic HTML structure
        if soup.find('main') or soup.find('article'):
            score += 0.2
        
        if soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            score += 0.2
        
        # Check content quality
        if content:
            # Ratio of text to HTML
            text_length = len(content)
            html_length = len(str(soup))
            if html_length > 0 and text_length / html_length > 0.1:
                score += 0.3
            
            # Check for lists, which often indicate structured content
            if soup.find_all(['ul', 'ol']):
                score += 0.1
            
            # Check for images with alt text
            images_with_alt = soup.find_all('img', alt=True)
            if images_with_alt:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_freshness_score(self, published_date: Optional[datetime], 
                                 last_modified: Optional[datetime]) -> float:
        """Calculate content freshness score."""
        if not self.config.calculate_scores:
            return 0.0
        
        now = datetime.now()
        most_recent = last_modified or published_date
        
        if not most_recent:
            return 0.0
        
        # Make datetime timezone-naive for comparison
        if most_recent.tzinfo is not None:
            most_recent = most_recent.replace(tzinfo=None)
        
        days_old = (now - most_recent).days
        
        # Scoring based on age
        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.8
        elif days_old <= 30:
            return 0.6
        elif days_old <= 90:
            return 0.4
        elif days_old <= 365:
            return 0.2
        else:
            return 0.1
    
    def _discover_feeds(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Discover RSS/Atom feeds on the page."""
        feeds = []
        
        # Look for feed links in HTML head
        feed_links = soup.find_all('link', rel=lambda x: x and 'alternate' in x.lower())
        
        for link in feed_links:
            href = link.get('href')
            type_attr = link.get('type', '').lower()
            
            if href and any(feed_type in type_attr for feed_type in 
                          ['rss', 'atom', 'xml', 'feed']):
                full_url = urljoin(base_url, href)
                if full_url not in feeds:
                    feeds.append(full_url)
        
        # Look for common feed URLs
        common_feeds = ['/feed', '/rss', '/rss.xml', '/atom.xml', '/feeds/all.atom.xml']
        base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        
        for feed_path in common_feeds:
            feed_url = base_domain + feed_path
            if feed_url not in feeds:
                feeds.append(feed_url)
        
        return feeds[:10]  # Limit to 10 feeds
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs from the page."""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                if full_url not in images:
                    images.append(full_url)
        
        return images[:20]  # Limit to 20 images
    
    def _extract_external_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract external links from the page."""
        base_domain = urlparse(base_url).netloc
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)
                
                # Check if it's an external link
                if parsed.netloc and parsed.netloc != base_domain:
                    if full_url not in external_links:
                        external_links.append(full_url)
        
        return external_links[:50]  # Limit to 50 external links
    
    def _error_result(self, url: str, error_msg: str, start_time: float, 
                     status: AnalysisStatus = AnalysisStatus.ERROR) -> PageAnalysis:
        """Create error result for failed analysis."""
        processing_time = time.time() - start_time
        
        return PageAnalysis(
            url=url,
            content_type=ContentType.HTML,
            status=status,
            error_message=error_msg,
            analyzed_at=datetime.now(),
            processing_time=processing_time
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()