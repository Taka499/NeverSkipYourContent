"""Tests for the AnalysisManager class."""

import pytest
from unittest.mock import AsyncMock, patch

from page_analyzer.analysis_manager import AnalysisManager
from page_analyzer.analysis_types import ContentType, AnalysisStatus


class TestAnalysisManager:
    """Test cases for AnalysisManager."""
    
    def test_content_type_detection(self):
        """Test content type detection from URLs."""
        manager = AnalysisManager()
        
        # Test RSS detection
        assert manager._detect_content_type("https://example.com/rss.xml") == ContentType.RSS
        assert manager._detect_content_type("https://example.com/feed") == ContentType.RSS
        
        # Test Atom detection
        assert manager._detect_content_type("https://example.com/atom.xml") == ContentType.ATOM
        
        # Test API detection
        assert manager._detect_content_type("https://api.example.com/v1/data") == ContentType.API
        assert manager._detect_content_type("https://example.com/data.json") == ContentType.API
        
        # Test HTML default
        assert manager._detect_content_type("https://example.com") == ContentType.HTML
        assert manager._detect_content_type("https://example.com/page.html") == ContentType.HTML
    
    def test_content_type_hints(self):
        """Test content type detection with hints."""
        manager = AnalysisManager()
        
        # Test explicit hints
        assert manager._detect_content_type("https://example.com", "rss") == ContentType.RSS
        assert manager._detect_content_type("https://example.com", "atom") == ContentType.ATOM
        assert manager._detect_content_type("https://example.com", "api") == ContentType.API
        assert manager._detect_content_type("https://example.com", "html") == ContentType.HTML
    
    @pytest.mark.asyncio
    async def test_analyze_page_with_mock(self, analysis_manager):
        """Test page analysis with mocked responses."""
        with patch.object(analysis_manager.html_analyzer, 'analyze') as mock_analyze:
            # Setup mock response
            mock_analyze.return_value = type('MockAnalysis', (), {
                'url': 'https://test.com',
                'content_type': ContentType.HTML,
                'status': AnalysisStatus.SUCCESS,
                'title': 'Test Page',
                'description': 'Test Description',
                'main_content': 'Test content',
                'summary': 'Test summary',
                'language': 'en',
                'author': 'Test Author',
                'published_date': None,
                'last_modified': None,
                'relevance_score': 0.8,
                'quality_score': 0.7,
                'freshness_score': 0.5,
                'feeds_discovered': [],
                'images': [],
                'external_links': [],
                'response_time': 1.0,
                'content_length': 1000,
                'status_code': 200,
                'analyzed_at': None,
                'processing_time': 0.5,
                'error_message': None
            })()
            
            # Test analysis
            result = await analysis_manager.analyze_page('https://test.com')
            
            assert result.url == 'https://test.com'
            assert result.content_type == ContentType.HTML
            assert result.status == AnalysisStatus.SUCCESS
            assert result.title == 'Test Page'
            mock_analyze.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, analysis_manager):
        """Test batch analysis functionality."""
        urls = ['https://test1.com', 'https://test2.com']
        
        with patch.object(analysis_manager, 'analyze_page') as mock_analyze:
            # Setup mock responses
            mock_responses = []
            for i, url in enumerate(urls):
                mock_response = type('MockAnalysis', (), {
                    'url': url,
                    'status': AnalysisStatus.SUCCESS,
                    'title': f'Test Page {i+1}',
                    'error_message': None
                })()
                mock_responses.append(mock_response)
            
            mock_analyze.side_effect = mock_responses
            
            # Test batch analysis
            result = await analysis_manager.analyze_batch(urls, max_concurrent=2)
            
            assert result.total_requested == 2
            assert result.successful_analyses == 2
            assert result.failed_analyses == 0
            assert len(result.results) == 2
    
    @pytest.mark.asyncio
    async def test_feed_discovery(self, analysis_manager):
        """Test feed discovery functionality."""
        with patch.object(analysis_manager.feed_analyzer, 'discover_feeds') as mock_discover:
            # Setup mock response
            mock_discover.return_value = type('MockFeedDiscovery', (), {
                'source_url': 'https://test.com',
                'feeds_found': [],
                'discovery_method': 'automatic',
                'total_feeds': 0,
                'discovery_time': 0.5,
                'error_message': None
            })()
            
            # Test feed discovery
            result = await analysis_manager.extract_feeds('https://test.com')
            
            assert result.source_url == 'https://test.com'
            assert result.total_feeds == 0
            mock_discover.assert_called_once_with('https://test.com', 2)
    
    @pytest.mark.asyncio
    async def test_api_analysis(self, analysis_manager):
        """Test API response analysis."""
        test_data = {"test": "data"}
        
        with patch.object(analysis_manager.api_analyzer, 'analyze_api_response') as mock_analyze:
            # Setup mock response
            mock_analyze.return_value = type('MockApiAnalysis', (), {
                'endpoint_url': 'https://api.test.com',
                'response_structure': 'object(test)',
                'extracted_content': [{'content': 'data', 'type': 'string'}],
                'schema_detected': 'generic_object',
                'total_records': 1,
                'data_quality': 0.8,
                'processing_time': 0.3,
                'error_message': None
            })()
            
            # Test API analysis
            result = await analysis_manager.analyze_api_response(
                'https://api.test.com', 
                test_data
            )
            
            assert result.endpoint_url == 'https://api.test.com'
            assert result.total_records == 1
            mock_analyze.assert_called_once_with('https://api.test.com', test_data, None)
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self, analysis_manager):
        """Test quick metadata extraction."""
        with patch.object(analysis_manager, 'analyze_page') as mock_analyze:
            # Setup mock response for full analysis path
            mock_analyze.return_value = type('MockAnalysis', (), {
                'url': 'https://test.com',
                'title': 'Test Page',
                'description': 'Test Description', 
                'language': 'en',
                'author': 'Test Author',
                'published_date': None,
                'last_modified': None,
                'content_type': ContentType.HTML,
                'status_code': 200,
                'response_time': 1.0,
                'content_length': 1000,
                'error_message': None
            })()
            
            # Test metadata extraction (non-quick mode)
            result = await analysis_manager.get_page_metadata('https://test.com', quick_mode=False)
            
            assert result.url == 'https://test.com'
            assert result.title == 'Test Page'
            assert result.content_type == ContentType.HTML