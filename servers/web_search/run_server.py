#!/usr/bin/env python3
"""Run script for the web search MCP server."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the server
if __name__ == "__main__":
    from web_search.server import mcp
    mcp.run()