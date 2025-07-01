# servers/query_generator/src/query_generator/server.py
import mcp.server
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

server = Server("query_generator")


@server.tool()
async def generate_queries(keyword: str, category: str = "general") -> list[str]:
    """Generate search queries for a given keyword and category"""
    # Simple implementation for demo
    base_queries = [
        f"{keyword} official website",
        f"{keyword} news RSS feed",
        f"{keyword} social media",
        f"{keyword} API documentation",
    ]

    if category == "artist":
        base_queries.extend(
            [
                f"{keyword} live tour dates",
                f"{keyword} ticket information",
                f"{keyword} fan club",
            ]
        )
    elif category == "research":
        base_queries.extend(
            [
                f"{keyword} recent papers",
                f"{keyword} conference proceedings",
                f"{keyword} arxiv",
            ]
        )

    return base_queries


async def main():
    async with mcp.server.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
