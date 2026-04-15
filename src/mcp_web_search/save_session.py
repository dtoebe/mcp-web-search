
from pathlib import Path

def save_history(messages: list[dict], path: str, mode: str) -> None:
    """Save chat history to markdown file
    
    ARGS:
        messages: Full message history
        path: File path to write to
        mode: 'chat' for full history, 'last' for last results output
    """

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    visible = [m for m in messages if m.get("role") not in ("system", "tool")]

    lines = [f"# Chat History\n\n> Saved: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]

    if mode == "last":
        to_save = next((m for m in reversed(visible) if m["role"] == "assistant"))
        for line in to_save["content"]:
            lines.append(line)
    else:
        to_save = visible
        for msg in to_save:
            role = msg.get("role", "unknown")
            content = msg.get("content") or ""
            lines.append(f"\n### {role.upper()}:\n\n{content}\n")

    output.write_text("\n".join(lines), encoding="utf-8")

def parse_save_cmd(user_input: str) -> tuple[str, str] | None:
    """Parse 'save chat|last <path> commands. Returns (mode, path) or None"""
    parts = user_input.strip().split(maxsplit=2)
    if len(parts) == 3 and parts[0].lower() == "save" and parts[1].lower() in ("chat", "last"):
        return parts[1].lower(), parts[2]
    return None
            
