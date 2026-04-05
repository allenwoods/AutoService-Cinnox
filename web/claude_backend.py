"""
Claude backend — dual-mode (SDK subprocess / direct API) chat engine.

SDK mode: persistent Claude CLI subprocess via claude_agent_sdk.
API mode: direct Anthropic API streaming with tool execution.
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import WebSocket

from web.plugin_kb import get_kb_search, get_route_query


# ── Configuration (set by app.py) ─────────────────────────────────────────
ROOT: Path = Path(".")
SERVER_PORT: int = 8000
DEMO_MODEL: str = "claude-sonnet-4-6"
_CLAUDE_CLI: str | None = None


def configure(root: Path, server_port: int) -> None:
    global ROOT, SERVER_PORT, DEMO_MODEL, _CLAUDE_CLI
    ROOT = root
    SERVER_PORT = server_port
    DEMO_MODEL = os.getenv("DEMO_MODEL", "claude-sonnet-4-6")
    _CLAUDE_CLI = _find_claude_cli()


# ── Claude CLI discovery ──────────────────────────────────────────────────
def _find_claude_cli() -> str | None:
    """Find the claude CLI binary."""
    import shutil

    try:
        import claude_agent_sdk._internal.transport.subprocess_cli as _t
        _cli_name = "claude.exe" if sys.platform == "win32" else "claude"
        bundled = Path(_t.__file__).parent.parent.parent / "_bundled" / _cli_name
        if bundled.exists():
            return str(bundled)
    except Exception:
        pass

    if found := shutil.which("claude"):
        return found

    candidates = [
        Path.home() / "AppData" / "Roaming" / "npm" / "claude",
        Path.home() / ".claude" / "local" / "claude",
        Path.home() / ".local" / "bin" / "claude",
        Path("/usr/local/bin/claude"),
        Path("/usr/bin/claude"),
    ]
    nvm_dir = Path.home() / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        for ver_dir in sorted(nvm_dir.iterdir(), reverse=True):
            candidates.append(ver_dir / "bin" / "claude")
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def get_claude_cli() -> str | None:
    return _CLAUDE_CLI


# ── Proxy env pass-through ────────────────────────────────────────────────
def proxy_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for k in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"):
        v = os.environ.get(k)
        if v:
            env[k] = v
    env["CLAUDECODE"] = ""
    env["ANTHROPIC_API_KEY"] = ""
    return env


# ── Model selection ───────────────────────────────────────────────────────
def sdk_model_name() -> str | None:
    """Map DEMO_MODEL env to SDK short name."""
    m = DEMO_MODEL.lower()
    if "haiku" in m:
        return "haiku"
    if "opus" in m:
        return "opus"
    if "sonnet" in m:
        return "sonnet"
    return None


def pick_model(session_data: dict | None, user_text: str = "") -> str:
    """Auto-select model based on session state.

    - Before gate cleared: haiku (fast lead collection)
    - After gate cleared: sonnet (KB reasoning)
    - Human agent mode: haiku (simple roleplay)
    """
    if session_data and session_data.get("human_agent_active"):
        return "haiku"
    if session_data and session_data.get("gate_cleared"):
        return "sonnet"
    return "haiku"


# ── Bash tool definition for API mode ─────────────────────────────────────
_BASH_TOOL_DEF: dict = {
    "name": "Bash",
    "description": (
        "Run a bash command. In web mode only HTTP calls to the local API server "
        "and approved uv run scripts are permitted."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "command":     {"type": "string", "description": "The bash command to run"},
            "description": {"type": "string", "description": "What the command does"},
        },
        "required": ["command"],
    },
}


# ── Tool execution (in-process fast path) ─────────────────────────────────
async def execute_tool(cmd: str) -> str:
    """Execute a Bash tool call from the model.

    Fast path: intercepts local HTTP API patterns and executes them in-process.
    Fallback: subprocess.
    """
    port = str(SERVER_PORT)

    # KB search: direct Python call (0ms)
    if f":{port}/api/kb_search" in cmd:
        m_q  = re.search(r'[?&]query=([^&\s"\']+)', cmd)
        m_k  = re.search(r'[?&]top_k=(\d+)', cmd)
        m_sf = re.search(r'[?&]source_filter=([^&\s"\']+)', cmd)
        if m_q:
            query = m_q.group(1).replace("+", " ").replace("%20", " ")
            top_k = int(m_k.group(1)) if m_k else 3
            sf    = [s for s in m_sf.group(1).split(",") if s] if m_sf else None
            mod   = get_kb_search()
            if mod:
                results = mod.search(query, top_k=top_k, source_filter=sf)
                return json.dumps(
                    [{"source_name": r["source_name"], "section": r.get("section", ""), "content": r["content"]}
                     for r in results],
                    ensure_ascii=False,
                )
        return "[]"

    # Route query: direct Python call (0ms)
    if f":{port}/api/route_query" in cmd or "route_query.py" in cmd:
        m_q = re.search(r'[?&]query=([^&\s"\']+)', cmd)
        if not m_q:
            m_q = re.search(r'--query\s+["\'](.+?)["\']', cmd)
        if m_q:
            query = m_q.group(1).replace("+", " ").replace("%20", " ")
            mod = get_route_query()
            if mod:
                result = mod.route(query)
                return json.dumps(result, ensure_ascii=False, indent=2)
        return json.dumps({"error": "missing query parameter"})

    # Save lead: direct Python call
    if f":{port}/api/save_lead" in cmd:
        m = re.search(r"""-d\s+['"](\{.*?\})['"]""", cmd, re.DOTALL)
        if m:
            try:
                from datetime import datetime
                body = json.loads(m.group(1))
                customer_type = body.get("type", "")
                data = body.get("data", {})
                if customer_type in ("new_customer", "existing_customer", "partner"):
                    leads_dir = ROOT / ".autoservice" / "database" / "knowledge_base" / "leads"
                    leads_dir.mkdir(parents=True, exist_ok=True)
                    now = datetime.now()
                    record = {"type": customer_type, "data": data, "created_at": now.isoformat()}
                    fname = f"{customer_type}_{now.strftime('%Y%m%d_%H%M%S')}.json"
                    (leads_dir / fname).write_text(
                        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    print(f"[save_lead] {customer_type} -> {fname}", flush=True)
                    return json.dumps({"status": "ok", "file": fname})
            except Exception as exc:
                return json.dumps({"status": "error", "message": str(exc)})
        return json.dumps({"status": "error", "message": "could not parse body"})

    # Subprocess fallback
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ROOT),
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        out = stdout.decode("utf-8", errors="replace")
        err = stderr.decode("utf-8", errors="replace")
        return out + (f"\n[stderr]: {err}" if err.strip() else "")
    except asyncio.TimeoutError:
        return "Error: command timed out after 30s"
    except Exception as exc:
        return f"Error: {exc}"


# ── Conversation format helpers ───────────────────────────────────────────
def conversation_to_api_messages(conversation: list[dict]) -> list[dict]:
    """Convert saved conversation (role: user/bot) to Anthropic API message format."""
    return [
        {"role": "user" if t["role"] == "user" else "assistant", "content": t["content"]}
        for t in conversation
    ]


# ── Direct Anthropic API streaming ────────────────────────────────────────
async def api_chat_stream(
    websocket: WebSocket,
    system_prompt: str,
    api_messages: list[dict],
) -> str:
    """Stream one chat turn via Anthropic API (no subprocess).

    Mutates api_messages in-place (appends assistant + tool-result messages).
    Streams bot_text_delta tokens to WebSocket as they arrive.
    Returns the full bot_text for the turn.
    """
    import anthropic as _anthropic

    client   = _anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    bot_text = ""

    for tool_turn in range(5):
        t_api = time.perf_counter()

        async with client.messages.stream(
            model=DEMO_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=api_messages,
            tools=[_BASH_TOOL_DEF],
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                    delta = event.delta.text
                    if delta:
                        bot_text += delta
                        await websocket.send_json({"type": "bot_text_delta", "content": delta})
            final_msg = await stream.get_final_message()

        elapsed = time.perf_counter() - t_api
        print(
            f"[timing] API turn {tool_turn + 1}: {elapsed:.2f}s  stop={final_msg.stop_reason}",
            flush=True,
        )

        api_messages.append({"role": "assistant", "content": final_msg.content})

        if final_msg.stop_reason != "tool_use":
            break

        # Execute tool calls
        tool_results = []
        for block in final_msg.content:
            if block.type != "tool_use" or block.name != "Bash":
                continue
            cmd    = block.input.get("command", "")
            t_tool = time.perf_counter()
            print(f"[timing] ToolUse: {cmd[:120]}", flush=True)

            if "kb_search" in cmd:
                m    = re.search(r'[?&]query=([^&\s"\']+)', cmd)
                kb_q = m.group(1).replace("+", " ") if m else cmd[:60]
                await websocket.send_json({"type": "kb_searching", "query": kb_q})

            result = await execute_tool(cmd)
            print(f"[timing] tool done: {time.perf_counter() - t_tool:.3f}s", flush=True)

            if "kb_search" in cmd:
                try:
                    sources = json.loads(result)
                    if isinstance(sources, list) and sources:
                        await websocket.send_json({
                            "type": "kb_sources",
                            "sources": [
                                {"source_name": r.get("source_name", ""), "section": r.get("section", ""), "snippet": r.get("content", "")[:300]}
                                for r in sources[:5]
                            ],
                        })
                except Exception:
                    pass

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        api_messages.append({"role": "user", "content": tool_results})

    return bot_text


# ── SDK client options builder ────────────────────────────────────────────
_sdk_stderr_lines: list[str] = []


def make_options(
    session_id: str | None,
    system_prompt: str,
    session_data: dict | None = None,
):
    """Build ClaudeAgentOptions for SDK backend."""
    from claude_agent_sdk import ClaudeAgentOptions

    _sdk_stderr_lines.clear()

    def _capture_stderr(line: str):
        print(f"[claude stderr] {line}", flush=True)
        _sdk_stderr_lines.append(line)
        if len(_sdk_stderr_lines) > 50:
            _sdk_stderr_lines.pop(0)

    model = pick_model(session_data)
    gate_cleared = bool(session_data and session_data.get("gate_cleared"))

    # haiku pre-gate: no tools needed, fewer turns
    if model == "haiku" and not gate_cleared:
        return ClaudeAgentOptions(
            cwd=str(ROOT),
            system_prompt=system_prompt,
            setting_sources=[],
            plugins=[],
            permission_mode="bypassPermissions",
            model=model,
            allowed_tools=[],
            resume=session_id,
            max_turns=1,
            cli_path=_CLAUDE_CLI,
            env=proxy_env(),
            stderr=_capture_stderr,
        )

    return ClaudeAgentOptions(
        cwd=str(ROOT),
        system_prompt=system_prompt,
        setting_sources=[],
        plugins=[],
        permission_mode="bypassPermissions",
        model=model,
        allowed_tools=["Bash"],
        resume=session_id,
        max_turns=12,
        cli_path=_CLAUDE_CLI,
        env=proxy_env(),
        stderr=_capture_stderr,
    )
