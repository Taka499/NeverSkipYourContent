# core/agent/tools/mcp_tools.py

from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path


mcp_config = {
        "web_search": {
            "command": "uv",
            "args": [
                "--directory",
                str(Path(__file__).parent / "../../../../../servers/web_search/"),
                "run",
                "python",
                "run_server.py"
            ],
            "transport": "stdio",
        },
        "page_analyzer": {
            "command": "uv",
            "args": [
                "--directory",
                str(Path(__file__).parent / "../../../../../servers/page_analyzer/"),
                "run",
                "python",
                "run_server.py"
            ],
            "transport": "stdio",
        }
    } # TODO: Define the MCP configuration here / or fetch from settings


async def get_mcp_tools():
    mcp_client = MultiServerMCPClient(mcp_config)
    tools = await mcp_client.get_tools()
    return tools
