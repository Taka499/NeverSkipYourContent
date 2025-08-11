# core/agent/tools/mcp_tools.py

from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_config = {} # TODO: Define the MCP configuration here / or fetch from settings


async def get_mcp_tools():
    mcp_client = MultiServerMCPClient(mcp_config)
    tools = await mcp_client.get_tools()
    return tools
