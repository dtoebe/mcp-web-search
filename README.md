# MCP Web Search

This was a simple experiment to learn to build an MCP server, and use it with a local [Ollama](https://ollama.com) instance. 

There I may be small updates in the future, like adding support for other search engines, but only as I need to experiment .

## How to run

1. Install [Ollama](https://ollama.com) for local LLMs
   1. Note: you will need to chose a model that allows tool use. 
2. Install [UV](https://docs.astral.sh/uv/)
3. Copy and fill out the .env
    ```shell
    cp .env.example .env
    ```
4. Install dependencies
   ```shell
    uv sync
   ```
5. Serve Ollama
   1. Note: There are a few options. Such as if you install Ollama via [Homebrew](https://brew.sh), and can run in the background as a service. This is just the default way of serving.
    ```shell
    ollama serve
    ```
6. Run the app
   ```shell
   uv run mcp-cli
   ```