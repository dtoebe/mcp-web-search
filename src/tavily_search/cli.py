"""CLI Client: chat with ollama server using the mcp-web-search"""

import asyncio
import json
import logging
import os
from pathlib import Path
import sys
from mcp.client.stdio import stdio_client
from mcp.types import Tool
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from mcp import ClientSession, StdioServerParameters


# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "cli.log")
    ],
)
logger = logging.getLogger("mcp_web_search.cli")

console = Console()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

def mcp_tool_to_ollama_tool(tool: Tool) -> dict:
    """convert an MCP Tool definition to Ollama's tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema,
        },
    }

async def run_cli() -> None:
    """CLI's Main Loop"""
    server_script = Path(__file__).parent / "server.py"
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("MCP Server initialized")

            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            ollama_tools = [mcp_tool_to_ollama_tool(t) for t in mcp_tools]
            
            tool_map = {t.name: t for t in mcp_tools}
            logger.info("Loaded MCP tools: %s", [t.name for t in mcp_tools])

            console.print(
                Panel(
                    f"[bold green]MCP Web Search CLI[/bold green]\n"
                    f"Model: [cyan]{OLLAMA_MODEL}[/cyan]"
                    f"Tools: [yellow]{', '.join(tool_map)}[/yellow]"
                    f"Type [bold]exit[/bold] or [bold]quit[/bold] to leave.",
                    expand=False
                )
            )

            messages = list[dict] = []

            while True:
                try:
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                except (EOFError, KeyboardInterrupt):
                    console.print("[dim]Good Bye[/dim]")
                    break

                if user_input.strip().lower() in {"exit", "quit", "q"}:
                    console.print("[dim]Good Bye[/dim]")
                    break
                
                if not user_input.strip():
                    continue

                messages.append({"role": "user", "content": user_input})
                logger.debug("User: %s", user_input)

                while True:
                    pass


