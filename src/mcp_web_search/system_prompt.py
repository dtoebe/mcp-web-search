from pathlib import Path

def load_system_prompt(value: str) -> str:
    """Load system prompt from file (SYSTEM_PROMPT="file:file.md") or return the raw string."""
    if value.startswith("file:"):
        path = Path(value[5:])
        if not path.is_absolute():
            path = Path(__file__).parent.parent.parent / path
        if not path.exists():
            raise FileNotFoundError(f"System Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")
    return value
