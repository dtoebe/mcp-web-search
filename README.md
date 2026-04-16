# 🔍 MCP Web Search & Tools

> Note: I was lazy and had Ai write this readme for me. The code is mine.

A high-performance MCP (Model Context Protocol) server and CLI agent designed for **Ollama**. This project enables local LLMs (like `gemma3`, `llama3.1`, or `qwen2.5`) to perform web searches via Tavily, get real-time date/time information, and save session histories to Markdown.

## ✨ Features

- **MCP Tools**: Web Search (Tavily) and Real-time Clock.
- **Agentic CLI**: A `rich`-powered terminal interface for chatting with Ollama.
- **Smart History**: Save the entire chat or just the last response to Markdown.
- **Configurable**: System prompts via files and environment variable management.
- **Modern Stack**: Built with `uv`, `mcp`, and `ollama`.

## 🛠 Prerequisites

- [Ollama](https://ollama.com/) running locally.
- A model that supports tool calling (e.g., `ollama pull gemma3:27b` or `qwen2.5-coder:32b`).
- A [Tavily API Key](https://tavily.com/) (free tier available).

## 🚀 Getting Started

### 1. Installation
Clone the repository and install dependencies using `uv`:

```bash
git clone <your-repo-url>
cd mcp-web-search
uv sync
```

### 2. Configuration
Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

**`.env` Options:**
- `TAVILY_API_KEY`: Your API key from Tavily.
- `OLLAMA_MODEL`: The model name (default: `gemma3:27b`).
- `SYSTEM_PROMPT`: Direct string or `file:system_prompt.md`.
- `LOG_LEVEL`: `INFO` or `DEBUG`.

### 3. Usage

Run the CLI directly:
```bash
uv run mcp-cli
```

## ⌨️ CLI Commands

While in the chat loop, you can use the following commands:

| Command            | Action                                            |
| :----------------- | :------------------------------------------------ |
| `save chat <path>` | Saves the entire conversation to a Markdown file. |
| `save last <path>` | Saves only the last User/Assistant exchange.      |
| `exit` / `quit`    | Gracefully close the session and MCP server.      |

## 🏗 Project Structure

```text
mcp-web-search/
├── src/
│   └── mcp_web_search/
│       ├── server.py    # MCP Server (The Tools)
│       └── cli.py       # The Client (Ollama & Chat Loop)
├── logs/                # Session and Server logs
├── .env                 # Secrets and Configuration
├── system_prompt.md     # (Optional) External system prompt
└── pyproject.toml       # Build and dependency definition
```

## 🚀 Deployment (Terminal Access)

To access the CLI from anywhere in your terminal, install it as a global tool:

```bash
uv tool install . --force
```

Now you can simply run `mcp-cli` from any directory.

## 📝 License
MIT
