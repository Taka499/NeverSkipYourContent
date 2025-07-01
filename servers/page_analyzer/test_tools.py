#!/usr/bin/env python3
"""
Test script for Page Analyzer MCP Server tools.

This script tests the individual MCP tools to verify functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from page_analyzer.analysis_manager import AnalysisManager


async def test_page_analysis():
    """Test basic page analysis functionality."""
    print("🧪 Testing page analysis...")
    
    async with AnalysisManager() as manager:
        # Test with a simple HTML page
        result = await manager.analyze_page("https://httpbin.org/html")
        
        print(f"✅ Analysis completed for: {result.url}")
        print(f"   Content type: {result.content_type.value}")
        print(f"   Status: {result.status.value}")
        print(f"   Title: {result.title}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        
        if result.error_message:
            print(f"   ⚠️ Error: {result.error_message}")


async def test_feed_discovery():
    """Test feed discovery functionality."""
    print("\n🧪 Testing feed discovery...")
    
    async with AnalysisManager() as manager:
        # Test feed discovery on a news site
        result = await manager.extract_feeds("https://news.ycombinator.com")
        
        print(f"✅ Feed discovery completed for: {result.source_url}")
        print(f"   Feeds found: {result.total_feeds}")
        print(f"   Discovery time: {result.discovery_time:.2f}s")
        
        for feed in result.feeds_found[:3]:  # Show first 3 feeds
            print(f"   📡 {feed.title or 'Untitled'} ({feed.feed_type.value})")
            print(f"      URL: {feed.url}")
        
        if result.error_message:
            print(f"   ⚠️ Error: {result.error_message}")


async def test_metadata_extraction():
    """Test quick metadata extraction."""
    print("\n🧪 Testing metadata extraction...")
    
    async with AnalysisManager() as manager:
        # Test metadata extraction
        result = await manager.get_page_metadata("https://httpbin.org/html", quick_mode=True)
        
        print(f"✅ Metadata extraction completed for: {result.url}")
        print(f"   Title: {result.title}")
        print(f"   Description: {result.description}")
        print(f"   Language: {result.language}")
        print(f"   Content type: {result.content_type.value}")
        print(f"   Response time: {result.response_time:.2f}s")
        
        if result.error_message:
            print(f"   ⚠️ Error: {result.error_message}")


async def test_batch_analysis():
    """Test batch analysis functionality."""
    print("\n🧪 Testing batch analysis...")
    
    async with AnalysisManager() as manager:
        # Test batch analysis with multiple URLs
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://example.com"
        ]
        
        result = await manager.analyze_batch(urls, max_concurrent=2)
        
        print(f"✅ Batch analysis completed")
        print(f"   Total requested: {result.total_requested}")
        print(f"   Successful: {result.successful_analyses}")
        print(f"   Failed: {result.failed_analyses}")
        print(f"   Total time: {result.total_processing_time:.2f}s")
        
        for analysis in result.results:
            print(f"   📄 {analysis.url} - {analysis.status.value}")
            if analysis.title:
                print(f"      Title: {analysis.title}")


async def test_api_analysis():
    """Test API response analysis."""
    print("\n🧪 Testing API analysis...")
    
    async with AnalysisManager() as manager:
        # Test API analysis with JSON endpoint
        result = await manager.analyze_api_response("https://httpbin.org/json")
        
        print(f"✅ API analysis completed for: {result.endpoint_url}")
        print(f"   Response structure: {result.response_structure}")
        print(f"   Schema detected: {result.schema_detected}")
        print(f"   Records extracted: {result.total_records}")
        print(f"   Data quality: {result.data_quality:.2f}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        
        if result.error_message:
            print(f"   ⚠️ Error: {result.error_message}")


async def main():
    """Run all tests."""
    print("🚀 Starting Page Analyzer MCP Server Tests\n")
    
    try:
        await test_page_analysis()
        await test_feed_discovery()
        await test_metadata_extraction()
        await test_batch_analysis()
        await test_api_analysis()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())