"""CLI Client: chat with ollama server using the mcp-web-search"""

from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import asyncio
import os
import sys
import ollama
from mcp.client.stdio import stdio_client
from mcp.types import Tool
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from mcp import ClientSession, StdioServerParameters
from mcp_web_search.system_prompt import load_system_prompt
from mcp_web_search import init_logger
from mcp_web_search.save_session import parse_save_cmd, save_history


# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = init_logger(
    "mcp_web_search.cli",
    LOG_LEVEL,
    os.path.join(LOG_DIR, "cli.log")
)

console = Console()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant with tools.")

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
                    f"Model: [cyan]{OLLAMA_MODEL}[/cyan]\n"
                    f"Tools: [yellow]{', '.join(tool_map)}[/yellow]\n"
                    f"Type [bold]save chat|last <path>[/bold] to save | "
                    f"Type [bold]exit[/bold] or [bold]quit[/bold] to leave.",
                    expand=False
                )
            )

            messages: list[dict] = [
                {
                    "role": "system",
                    "content": load_system_prompt(SYSTEM_PROMPT),
                }
            ]
            logger.info("SYSTEM PROMPT: %s", SYSTEM_PROMPT)

            while True:
                try:
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                except (EOFError, KeyboardInterrupt):
                    console.print("[dim]Good Bye[/dim]")
                    break

                if user_input.strip().lower() in {"exit", "quit", "q"}:
                    console.print("[dim]Good Bye[/dim]")
                    break

                if save_cmd := parse_save_cmd(user_input):
                    mode, path = save_cmd
                    try:
                        # logger.info(messages)
                        save_history(messages, path, mode)
                        console.print(f"[dim] Saved {mode} history to [bold]{path}[/bold][/dim]")
                    except Exception as e:
                        logger.exception("Failed to save history")
                        console.print(f"[red]Failed to save: {e}[/red]")
                    continue
                
                if not user_input.strip():
                    continue

                messages.append({"role": "user", "content": user_input})
                logger.debug("User: %s", user_input)

                while True:
                    client = ollama.Client(host=OLLAMA_HOST)
                    response = client.chat(
                        model=OLLAMA_MODEL,
                        messages=messages,
                        tools=ollama_tools,
                    )

                    msg = response.message
                    messages.append(msg.model_dump())

                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.function.name
                            tool_args = tc.function.arguments or {}

                            logger.info("Tool call: %s(%s)", tool_name, tool_args)
                            console.print(
                                f"[dim]🔧 Calling tool [bold]{tool_name}[/bold] "
                                f"with {tool_args}[/dim]"
                            )

                            if tool_name not in tool_map:
                                tool_result = f"Error: unknown tool {tool_name!r}"
                            else:
                                result = await session.call_tool(tool_name, dict(tool_args))
                                tool_result = "\n".join(
                                    c.text for c in result.content if hasattr(c, "text") # type: ignore
                                )

                            logger.debug("Tool result (%d chars) %.200s", len(tool_result), tool_result)
                            messages.append({
                                "role": "tool",
                                "content": tool_result,
                            })

                        continue   
                    
                    final_text = msg.content or ""
                    logger.debug("Assistant: %.200s", final_text)
                    console.print("\n[bold green]Assistant[/bold green]")
                    console.print(Markdown(final_text))
                    break

def main() -> None:
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
