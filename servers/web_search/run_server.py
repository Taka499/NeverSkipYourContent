#!/usr/bin/env python3
"""Run script for the web search MCP server."""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from web_search.server import mcp

# Import and run the server
if __name__ == "__main__":
    mcp.run()
