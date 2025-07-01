"""Pytest configuration and fixtures for page analyzer tests."""

import pytest
import asyncio
from typing import AsyncGenerator

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from page_analyzer.analysis_manager import AnalysisManager
from page_analyzer.analysis_types import AnalysisConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def analysis_manager() -> AsyncGenerator[AnalysisManager, None]:
    """Create an analysis manager for testing."""
    config = AnalysisConfig(
        timeout=10,  # Shorter timeout for tests
        calculate_scores=True,
        detect_language=True
    )
    
    manager = AnalysisManager(config)
    yield manager
    await manager.close()


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return {
        "html": "https://httpbin.org/html",
        "json": "https://httpbin.org/json", 
        "xml": "https://httpbin.org/xml",
        "example": "https://example.com"
    }


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page for unit testing">
        <meta name="author" content="Test Author">
        <link rel="alternate" type="application/rss+xml" href="/feed.xml">
    </head>
    <body>
        <h1>Test Article</h1>
        <p>This is a test article with some content for analysis.</p>
        <p>It has multiple paragraphs to test content extraction.</p>
        <a href="https://external.com">External Link</a>
        <img src="/test.jpg" alt="Test Image">
    </body>
    </html>
    """


@pytest.fixture
def sample_rss():
    """Sample RSS feed content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <description>A test RSS feed</description>
            <link>https://example.com</link>
            <language>en-us</language>
            <item>
                <title>Test Article 1</title>
                <description>First test article</description>
                <link>https://example.com/article1</link>
                <pubDate>Mon, 01 Jul 2024 12:00:00 GMT</pubDate>
            </item>
            <item>
                <title>Test Article 2</title>
                <description>Second test article</description>
                <link>https://example.com/article2</link>
                <pubDate>Sun, 30 Jun 2024 12:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """


@pytest.fixture
def sample_json_api():
    """Sample JSON API response for testing."""
    return {
        "data": [
            {
                "id": "1",
                "title": "Test Item 1",
                "content": "Content for test item 1",
                "url": "https://example.com/item1",
                "date": "2024-07-01T12:00:00Z"
            },
            {
                "id": "2", 
                "title": "Test Item 2",
                "content": "Content for test item 2",
                "url": "https://example.com/item2",
                "date": "2024-06-30T12:00:00Z"
            }
        ],
        "meta": {
            "total": 2,
            "page": 1
        }
    }