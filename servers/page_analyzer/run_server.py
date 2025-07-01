#!/usr/bin/env python3
"""
Run script for the Page Analyzer MCP Server.

This script can be used to start the server directly or referenced in
Claude Desktop MCP configuration.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from page_analyzer.server import mcp

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()