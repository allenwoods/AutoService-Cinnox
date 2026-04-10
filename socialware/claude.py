"""
Claude Agent SDK wrapper.

Loads agent configuration from .autoservice/.claude directory.
"""

import os
from pathlib import Path
from typing import AsyncIterator, Any
from claude_agent_sdk import query as sdk_query, ClaudeAgentOptions


async def query(prompt: str, cwd: str = None) -> AsyncIterator[Any]:
    """
    Execute a Claude Agent query.

    Args:
        prompt: The query prompt
        cwd: Working directory, defaults to current directory

    Yields:
        Raw message objects
    """
    if cwd is None:
        cwd = str(Path.cwd())

    cwd_path = Path(cwd).absolute()
    plugin_path = cwd_path / ".autoservice" / ".claude"

    env = {}
    http_proxy = os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
    https_proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    if http_proxy:
        env["http_proxy"] = http_proxy
    if https_proxy:
        env["https_proxy"] = https_proxy

    options = ClaudeAgentOptions(
        cwd=cwd,
        setting_sources=None,
        plugins=[{"type": "local", "path": str(plugin_path)}] if plugin_path.exists() else None,
        env=env,
    )

    async for message in sdk_query(prompt=prompt, options=options):
        yield message
