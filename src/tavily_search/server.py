"""MCP Server exposing Web Search via Tavily"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from tavily import TavilyClient

load_dotenv()

# Setup Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "server.log"),
    ]
)
logger = logging.getLogger("mcp_web_search.server")

# Setup Tavily
_tavily_api_key = os.getenv("TAVILY_API_KEY")
if not _tavily_api_key:
    raise EnvironmentError("TAVILY_API_KEY not set in environment or .env")

tavily = TavilyClient(api_key=_tavily_api_key)

# MCP Server
app = Server("mcp-web-search")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Advertise available tools to MCP clients"""
    return [
        Tool(
            name="Web Search",
            description=(
                "Search the web using Tavily and return relevant results. "
                "Use for anything that would requre current results. "
                "For example looking up documentation for software libraries, current events, facts, news, ect..."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                    },
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advacned"],
                        "description": "Search depth - 'basic' is faster, 'advanced' id more thorough",
                        "default": "basic",
                    },
                },
                "required": ["query"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls"""
    if name != "Web Search":
        raise ValueError(f"Unknown tool: {name!r}")

    query: str = arguments["query"]
    max_results = arguments.get("max_results", 5)
    search_depth = arguments.get("search_depth", "basic")

    logger.info("Web Search | query=%r depth=%s max=%d", query, search_depth, max_results)

    try:
        response = tavily.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=True,
        )
    except Exception:
        logger.exception("Tavily search failed for query=%r", query)
        raise

    lines: list[str] = []

    if answer := response.get("answer"):
        lines.append(f"**Summary** {answer}\n")

    for i, results in enumerate(response.get("results", []), 1):
        lines.append(
            f"{i}. **{results.get('title', 'No Title')}**\n"
            f"\tURL: {results.get('url', '')}\n"
            f"\tcontent: {results.get('content', '')}\n"
        )

    text = "\n".join(lines) if lines else "No results found."
    logger.debug("Web Search | returning %d chars", len(text))

    return [TextContent(type="text", text=text)]

async def serve() -> None:
    """Start the MCP server"""
    logger.info("Starting MCP Web Search server (stdio transport)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def main() -> None:
    import asyncio
    asyncio.run(serve())

if __name__ == "__main__":
    main()
