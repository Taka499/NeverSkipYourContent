#!/usr/bin/env python3
"""Test the web search server tools."""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from web_search.server import search_web, get_available_providers, search_with_fallback

async def test_tools():
    """Test the web search tools."""
    
    print("=== Testing Web Search MCP Server Tools ===\n")
    
    # Test 1: Get available providers
    print("1. Testing get_available_providers()...")
    try:
        providers = await get_available_providers()
        print(f"✅ Available providers: {providers}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Basic search with DuckDuckGo
    print("2. Testing search_web() with DuckDuckGo...")
    try:
        result = await search_web("Python programming", "duckduckgo", 2)
        if result.get("error"):
            print(f"❌ Search error: {result['error']}")
        else:
            print(f"✅ Search successful: {len(result.get('results', []))} results")
            if result.get('results'):
                print(f"   First result: {result['results'][0]['title']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Search with fallback
    print("3. Testing search_with_fallback()...")
    try:
        result = await search_with_fallback("machine learning", 2)
        if result.get("error"):
            print(f"❌ Fallback search error: {result['error']}")
        else:
            print(f"✅ Fallback search successful: {len(result.get('results', []))} results")
            print(f"   Used provider: {result.get('provider')}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("=== All tests completed ===")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_tools())
    print(f"\nOverall result: {'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)