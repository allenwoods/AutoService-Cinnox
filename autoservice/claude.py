"""
Claude Agent - 简化版

仅加载代理配置，使用 .autoservice/.claude 作为配置目录。
提供两种查询方式：
  - query()      — 无状态，每次启动新子进程
  - pool_query() — 使用预热实例池，复用子进程
"""

import logging
import os
from pathlib import Path
from typing import AsyncIterator, Any
from claude_agent_sdk import query as sdk_query, ClaudeAgentOptions

log = logging.getLogger("autoservice.claude")


async def query(prompt: str, cwd: str = None) -> AsyncIterator[Any]:
    """
    执行 Claude Agent 查询（无状态，每次启动新子进程）

    Args:
        prompt: 查询提示词
        cwd: 工作目录，默认为当前目录

    Yields:
        原始消息对象
    """
    if cwd is None:
        cwd = str(Path.cwd())

    # 配置目录：.autoservice/.claude
    cwd_path = Path(cwd).absolute()
    plugin_path = cwd_path / ".autoservice" / ".claude"

    # 加载代理配置
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


async def pool_query(prompt: str, cwd: str = None) -> AsyncIterator[Any]:
    """
    使用实例池执行 Claude Agent 查询（复用预热子进程）

    与 query() 签名一致，池未就绪时自动回退到无状态 query()。

    Args:
        prompt: 查询提示词
        cwd: 工作目录，默认为当前目录

    Yields:
        原始消息对象
    """
    from autoservice.cc_pool import get_pool, load_pool_config

    try:
        config = load_pool_config(cwd=cwd or str(Path.cwd()))
        pool = await get_pool(config)
        async for message in pool.query(prompt):
            yield message
    except Exception as e:
        log.warning("Pool query failed, falling back to stateless query: %s", e)
        async for message in query(prompt, cwd):
            yield message
