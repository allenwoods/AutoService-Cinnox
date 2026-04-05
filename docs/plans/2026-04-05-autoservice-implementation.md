# AutoService Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract a fork-able customer service/sales bot framework from autoservices + SaneLedger.

**Architecture:** Feishu MCP channel (primary) + Web chat (secondary), with declarative plugin system for customer-specific APIs. Each customer = one forked repo.

**Tech Stack:** Python 3.11+, FastAPI, MCP SDK, lark_oapi, Claude Agent SDK, SQLite, uv

**Source repos:**
- `/Users/h2oslabs/Workspace/SaneLedger` — Feishu channel pattern (`feishu/channel.py`)
- `/Users/h2oslabs/Workspace/autoservices` (branch `feat/m800-cinnox-demo`) — skills, web server, shared modules

**Target:** `/Users/h2oslabs/Workspace/AutoService`

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `CLAUDE.md`
- Create: `.mcp.json`
- Create: `.claude/settings.json`

**Step 1: Create pyproject.toml**

Adapt from autoservices `pyproject.toml` (at `/Users/h2oslabs/Workspace/autoservices/pyproject.toml`):

```toml
[project]
name = "autoservice"
version = "0.1.0"
description = "AI-native customer service and sales bot framework"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "beautifulsoup4>=4.14.3",
    "claude-agent-sdk>=0.1.21",
    "fastapi>=0.109.0",
    "httpx>=0.28.1",
    "lark-oapi>=1.3.0",
    "mcp>=1.0.0",
    "openpyxl>=3.1.5",
    "pypdf>=6.7.4",
    "python-docx>=1.2.0",
    "uvicorn[standard]>=0.27.0",
    "pyyaml>=6.0",
    "anyio>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create Makefile**

```makefile
.PHONY: setup run-channel run-web check

setup:
	@echo "Creating symlinks..."
	@mkdir -p .claude
	@ln -sfn ../skills .claude/skills
	@ln -sfn ../commands .claude/commands
	@ln -sfn ../agents .claude/agents
	@ln -sfn ../hooks .claude/hooks
	@# Plugin skills
	@for dir in plugins/*/skills/*/; do \
		[ -d "$$dir" ] || continue; \
		name=$$(basename $$dir); \
		ln -sfn ../../$$dir .claude/skills/$$name; \
	done
	@echo "Creating runtime directories..."
	@mkdir -p .autoservice/database/knowledge_base .autoservice/database/sessions .autoservice/logs
	@echo "Done."

run-channel:
	uv run python3 feishu/channel.py

run-web:
	uv run uvicorn web.app:app --host 0.0.0.0 --port $${DEMO_PORT:-8000}

check:
	uv run python3 -c "from autoservice.plugin_loader import discover; print(discover('plugins'))"
```

**Step 3: Create .gitignore**

```gitignore
# Runtime data
.autoservice/
*.db

# Credentials
.env
.feishu-credentials.json

# Python
__pycache__/
*.pyc
.venv/
uv.lock

# IDE
.idea/
.vscode/

# Claude Code worktrees
.claude/worktrees/
```

**Step 4: Create CLAUDE.md**

```markdown
# AutoService — AI-Native 客服与销售机器人框架

## Project Overview

Fork-based customer service/sales bot framework. Each customer = one forked repo.
Two channels: Feishu IM (primary, MCP) + Web chat (secondary, FastAPI).
Customer-specific APIs via declarative plugins (`plugins/*/plugin.yaml`).

## Directory Structure

- `feishu/` — MCP channel server (Feishu WebSocket → Claude Code)
- `web/` — FastAPI web server (browser chat)
- `autoservice/` — Core Python package
- `skills/` — Claude Code skills (symlinked to .claude/skills/)
- `plugins/` — Declarative plugins (auto-discovered on startup)
- `commands/`, `agents/`, `hooks/` — Claude Code extensions (symlinked)
- `.autoservice/` — Gitignored runtime data

## Commands

- `make setup` — Create symlinks + runtime directories
- `make run-channel` — Start Feishu MCP channel
- `make run-web` — Start web server
- `make check` — Verify plugin discovery

## Plugin Development

Each plugin: `plugins/{name}/plugin.yaml` + `tools.py` + `routes.py` + `references/`
See `plugins/_example/` for template.

## Fork Workflow

1. Fork this repo
2. Add `plugins/{customer}/` with plugin.yaml, tools, routes, references
3. Add customer-specific skills to `skills/`
4. Customer data goes in `.autoservice/` (gitignored)
5. `git remote add upstream` + `git merge upstream/main` for framework updates
```

**Step 5: Create .mcp.json**

```json
{
  "mcpServers": {
    "autoservice-channel": {
      "command": "uv",
      "args": ["run", "python3", "feishu/channel.py"]
    }
  }
}
```

**Step 6: Create .claude/settings.json**

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Edit(*)",
      "Write(*)",
      "Bash(uv run *)",
      "Bash(make *)",
      "Bash(git *)",
      "Bash(ls *)",
      "Bash(mkdir *)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

**Step 7: Create empty extension directories**

```bash
mkdir -p skills commands agents hooks plugins/_example
```

**Step 8: Commit**

```bash
git add pyproject.toml Makefile .gitignore CLAUDE.md .mcp.json .claude/settings.json
git commit -m "feat: project scaffolding — pyproject, Makefile, CLAUDE.md, .mcp.json"
```

---

## Task 2: Core Python Package (`autoservice/`)

Migrate 12 modules from autoservices `.claude/skills/_shared/` + root `autoservice/`.

**Files:**
- Create: `autoservice/__init__.py`
- Create: `autoservice/core.py` (from `.claude/skills/_shared/core.py`)
- Create: `autoservice/config.py` (from `.claude/skills/_shared/config.py`)
- Create: `autoservice/database.py` (from `.claude/skills/_shared/database.py`)
- Create: `autoservice/mock_db.py` (from `.claude/skills/_shared/mock_db.py`)
- Create: `autoservice/api_client.py` (from `.claude/skills/_shared/api_client.py`)
- Create: `autoservice/api_interfaces.py` (from `.claude/skills/_shared/api_interfaces.py`)
- Create: `autoservice/session.py` (from `.claude/skills/_shared/session.py`)
- Create: `autoservice/permission.py` (from `.claude/skills/_shared/permission.py`)
- Create: `autoservice/customer_manager.py` (from `.claude/skills/_shared/customer_manager.py`)
- Create: `autoservice/importer.py` (from `.claude/skills/_shared/importer.py`)
- Create: `autoservice/logger.py` (merge `.claude/skills/_shared/logger.py` + root `autoservice/logger.py`)
- Create: `autoservice/claude.py` (from root `autoservice/claude.py`)
- Create: `autoservice/plugin_loader.py` (new — Task 3)

**Step 1: Copy modules with import path fixes**

For each file, copy from autoservices source and fix internal imports.

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/_shared/`
Target: `/Users/h2oslabs/Workspace/AutoService/autoservice/`

Import changes needed across all files:
```python
# OLD (autoservices _shared imports)
from _shared.core import generate_id, sanitize_name, ensure_dir
from _shared.config import get_domain_config
from _shared.database import save_record, get_record

# NEW (autoservice package imports)
from autoservice.core import generate_id, sanitize_name, ensure_dir
from autoservice.config import get_domain_config
from autoservice.database import save_record, get_record
```

Files and their internal import dependencies:
- `core.py` — no internal imports (copy as-is)
- `config.py` — no internal imports (copy as-is)
- `database.py` — imports `core`, `config`
- `mock_db.py` — no internal imports (copy as-is, uses sqlite3 only)
- `api_client.py` — no internal imports (copy as-is, uses httpx)
- `api_interfaces.py` — no internal imports (copy as-is)
- `session.py` — imports `core`, `config`
- `permission.py` — no internal imports (copy as-is)
- `customer_manager.py` — imports `core`, `config`
- `importer.py` — imports `core`, `config`
- `logger.py` — merge two loggers, keep ConversationLogger class

**Step 2: Copy `autoservice/claude.py`**

Source: `/Users/h2oslabs/Workspace/autoservices/autoservice/claude.py`
This wraps `claude_agent_sdk`. Copy as-is, fix any path references.

**Step 3: Create `autoservice/__init__.py`**

```python
"""AutoService — AI-native customer service and sales bot framework."""
```

**Step 4: Verify imports work**

```bash
cd /Users/h2oslabs/Workspace/AutoService
uv run python3 -c "from autoservice.core import generate_id; print(generate_id('test'))"
uv run python3 -c "from autoservice.mock_db import MockDB; print('MockDB OK')"
uv run python3 -c "from autoservice.permission import check_permission; print('Permission OK')"
```

**Step 5: Commit**

```bash
git add autoservice/
git commit -m "feat: core autoservice package — migrate 12 modules from autoservices _shared"
```

---

## Task 3: Plugin Loader Framework

**Files:**
- Create: `autoservice/plugin_loader.py`

**Step 1: Implement plugin_loader.py**

This is new code — the core of the plugin system. It needs to:
1. Scan `plugins/*/plugin.yaml`
2. Parse and validate plugin declarations
3. Import tool handler functions (for MCP registration)
4. Import route handler functions (for FastAPI mounting)
5. Initialize mock databases if `mode: mock`

```python
"""Declarative plugin loader for AutoService.

Scans plugins/*/plugin.yaml, imports tool handlers (for MCP) and route handlers (for FastAPI).
"""

import importlib.util
import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from autoservice.mock_db import MockDB


@dataclass
class PluginTool:
    """An MCP tool declared by a plugin."""
    name: str
    description: str
    handler: Callable
    input_schema: dict
    plugin_name: str


@dataclass
class PluginRoute:
    """An HTTP route declared by a plugin."""
    path: str
    method: str
    handler: Callable
    plugin_name: str


@dataclass
class Plugin:
    """A loaded plugin."""
    name: str
    version: str
    description: str
    mode: str  # "mock" | "real"
    installer: str
    tools: list[PluginTool] = field(default_factory=list)
    routes: list[PluginRoute] = field(default_factory=list)
    references: list[Path] = field(default_factory=list)
    db: MockDB | None = None
    plugin_dir: Path = None


def _import_module_from_path(module_name: str, file_path: Path):
    """Import a Python module from an absolute file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_handler(plugin_dir: Path, handler_ref: str, plugin_name: str) -> Callable:
    """Resolve 'tools.crm_lookup' to actual function.
    
    handler_ref format: '{module}.{function}' e.g. 'tools.crm_lookup'
    """
    parts = handler_ref.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid handler ref '{handler_ref}': expected 'module.function'")
    module_name, func_name = parts
    module_path = plugin_dir / f"{module_name}.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Plugin module not found: {module_path}")
    
    full_module_name = f"plugins.{plugin_name}.{module_name}"
    module = _import_module_from_path(full_module_name, module_path)
    func = getattr(module, func_name, None)
    if func is None:
        raise AttributeError(f"Function '{func_name}' not found in {module_path}")
    return func


def load_plugin(plugin_dir: Path) -> Plugin:
    """Load a single plugin from its directory."""
    yaml_path = plugin_dir / "plugin.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"No plugin.yaml in {plugin_dir}")
    
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    
    plugin_name = config["name"]
    plugin = Plugin(
        name=plugin_name,
        version=config.get("version", "0.0.0"),
        description=config.get("description", ""),
        mode=config.get("mode", "mock"),
        installer=config.get("installer", "unknown"),
        plugin_dir=plugin_dir,
    )
    
    # Load MCP tools
    for tool_def in config.get("mcp_tools", []):
        handler = _resolve_handler(plugin_dir, tool_def["handler"], plugin_name)
        plugin.tools.append(PluginTool(
            name=tool_def["name"],
            description=tool_def["description"],
            handler=handler,
            input_schema=tool_def.get("input_schema", {}),
            plugin_name=plugin_name,
        ))
    
    # Load HTTP routes
    for route_def in config.get("http_routes", []):
        handler = _resolve_handler(plugin_dir, route_def["handler"], plugin_name)
        plugin.routes.append(PluginRoute(
            path=route_def["path"],
            method=route_def["method"],
            handler=handler,
            plugin_name=plugin_name,
        ))
    
    # Resolve references
    for ref in config.get("references", []):
        ref_path = plugin_dir / ref
        if ref_path.exists():
            plugin.references.append(ref_path)
    
    # Init mock DB if needed
    mock_config = config.get("mock_server", {})
    if plugin.mode == "mock" and mock_config:
        db_path = Path(mock_config.get("database", f".autoservice/database/{plugin_name}/mock.db"))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        plugin.db = MockDB(str(db_path))
        
        seed_path = plugin_dir / mock_config.get("seed_data", "")
        if seed_path.exists():
            import json
            seed_data = json.loads(seed_path.read_text())
            _seed_db(plugin.db, seed_data)
    
    return plugin


def _seed_db(db: MockDB, seed_data: dict | list):
    """Seed a mock database with initial data."""
    if isinstance(seed_data, list):
        seed_data = {"customers": seed_data}
    for table, records in seed_data.items():
        for record in records:
            if table == "customers":
                db.upsert_customer(record)
            elif table == "products":
                db.upsert_product(record)
            elif table == "subscriptions":
                db.add_subscription(record)


def discover(plugins_dir: str | Path = "plugins") -> list[Plugin]:
    """Discover and load all plugins from the plugins directory."""
    plugins_path = Path(plugins_dir)
    if not plugins_path.exists():
        return []
    
    loaded = []
    for plugin_dir in sorted(plugins_path.iterdir()):
        if not plugin_dir.is_dir():
            continue
        if plugin_dir.name.startswith(".") or plugin_dir.name.startswith("_"):
            # Skip _example in production; keep for development
            if plugin_dir.name == "_example":
                pass  # Load example plugin for testing
            else:
                continue
        
        yaml_path = plugin_dir / "plugin.yaml"
        if not yaml_path.exists():
            continue
        
        try:
            plugin = load_plugin(plugin_dir)
            loaded.append(plugin)
            print(f"  ✓ Plugin '{plugin.name}' loaded ({len(plugin.tools)} tools, {len(plugin.routes)} routes)")
        except Exception as e:
            print(f"  ✗ Plugin '{plugin_dir.name}' failed: {e}")
    
    return loaded
```

**Step 2: Verify plugin loader**

```bash
uv run python3 -c "from autoservice.plugin_loader import discover; plugins = discover('plugins'); print(f'{len(plugins)} plugins')"
```

Expected: `0 plugins` (no plugins yet)

**Step 3: Commit**

```bash
git add autoservice/plugin_loader.py
git commit -m "feat: plugin loader — declarative plugin.yaml discovery and registration"
```

---

## Task 4: Example Plugin

**Files:**
- Create: `plugins/_example/plugin.yaml`
- Create: `plugins/_example/tools.py`
- Create: `plugins/_example/routes.py`
- Create: `plugins/_example/mock_data/examples.json`
- Create: `plugins/_example/references/README.md`

**Step 1: Create plugin.yaml**

```yaml
name: _example
version: 0.1.0
description: Example plugin demonstrating the AutoService plugin structure
mode: mock
installer: upstream

mcp_tools:
  - name: example_echo
    description: Echo back the input message
    handler: tools.echo
    input_schema:
      type: object
      properties:
        message:
          type: string
          description: Message to echo back
      required: [message]

  - name: example_lookup
    description: Look up a record from the example database
    handler: tools.lookup
    input_schema:
      type: object
      properties:
        id:
          type: string
          description: Record ID to look up
      required: [id]

http_routes:
  - path: /api/example/echo
    method: POST
    handler: routes.post_echo

  - path: /api/example/{record_id}
    method: GET
    handler: routes.get_record

mock_server:
  seed_data: mock_data/examples.json
  database: .autoservice/database/_example/mock.db

references:
  - references/README.md
```

**Step 2: Create tools.py**

```python
"""Example plugin tool handlers — shared by MCP and HTTP interfaces."""


async def echo(message: str) -> dict:
    """Echo back the input message."""
    return {"echo": message, "plugin": "_example"}


async def lookup(id: str) -> dict:
    """Look up a record from the example database.
    
    In a real plugin, this would query the plugin's MockDB.
    For the example, we return a static response.
    """
    # This demonstrates the pattern — real plugins would use:
    # from autoservice.plugin_loader import get_plugin_db
    # db = get_plugin_db("_example")
    # return db.get_customer(id)
    return {
        "id": id,
        "name": f"Example Record {id}",
        "status": "active",
        "plugin": "_example",
    }
```

**Step 3: Create routes.py**

```python
"""Example plugin HTTP route handlers."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/example", tags=["example"])


@router.post("/echo")
async def post_echo(body: dict):
    from .tools import echo
    return await echo(body.get("message", ""))


@router.get("/{record_id}")
async def get_record(record_id: str):
    from .tools import lookup
    return await lookup(record_id)
```

**Step 4: Create mock_data/examples.json**

```json
{
  "customers": [
    {
      "name": "Demo Customer",
      "phone": "13800000000",
      "email": "demo@example.com",
      "type": "enterprise",
      "account_status": "active",
      "company": "Example Corp"
    }
  ]
}
```

**Step 5: Create references/README.md**

```markdown
# Example Plugin References

This directory contains domain-specific reference data that skills can read.

In a real plugin, you would put:
- Product glossaries (glossary.json)
- Pricing tables (pricing.md)
- Product catalogs (product-catalog.md)
- FAQ documents

Skills access these via: `Read plugins/_example/references/`
```

**Step 6: Verify plugin discovery**

```bash
uv run python3 -c "from autoservice.plugin_loader import discover; plugins = discover('plugins'); print(f'{len(plugins)} plugins: {[p.name for p in plugins]}')"
```

Expected: `1 plugins: ['_example']` with tool/route counts.

**Step 7: Commit**

```bash
git add plugins/_example/
git commit -m "feat: example plugin — demonstrates plugin.yaml, tools, routes, references"
```

---

## Task 5: Feishu Channel Server

Adapt SaneLedger's `feishu/channel.py` for AutoService with plugin tool loading.

**Files:**
- Create: `feishu/__init__.py`
- Create: `feishu/channel.py` (adapted from SaneLedger)
- Create: `feishu/channel-instructions.md`

**Step 1: Create feishu/channel.py**

Source: `/Users/h2oslabs/Workspace/SaneLedger/feishu/channel.py` (472 lines)

Key adaptations:
1. **Remove**: beancount imports, approval handler (`on_approval`), permission filter, output filter
2. **Remove**: SaneLedger-specific paths (`PROJECT_ROOT / ".saneledger"`)
3. **Add**: Plugin loader integration — scan `plugins/`, register tools on MCP server
4. **Change**: Server name from `saneledger-channel` to `autoservice-channel`
5. **Change**: Log file path to `.autoservice/feishu-channel.log`
6. **Change**: Instructions path to `feishu/channel-instructions.md`

The channel.py structure should be:

```python
"""AutoService MCP Channel Server — Feishu WebSocket → Claude Code bridge.

Adapted from SaneLedger's channel.py. Hosts core tools (reply, react)
plus plugin MCP tools discovered from plugins/*/plugin.yaml.
"""

# Section 1: Imports (remove feishu.permissions, feishu.output_filter, approval imports)
# Section 2: Config paths (use .autoservice/ instead of .saneledger/)
# Section 3: Credentials (keep as-is)
# Section 4: Feishu client (keep as-is)
# Section 5: Dedup & queue (keep as-is)
# Section 6: inject_message (keep as-is)
# Section 7: poll_feishu_queue (keep as-is)
# Section 8: setup_feishu — REMOVE on_approval handler, keep on_message
# Section 9: register_tools — ADD plugin tool registration
# Section 10: _handle_reply — REMOVE permission filter
# Section 11: _handle_react (keep as-is)
# Section 12: main() — ADD plugin_loader.discover() before server start
```

Key new code in `register_tools()`:

```python
def register_tools(server: Server, plugin_tools: list):
    """Register core tools + plugin tools on MCP server."""
    
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        core_tools = [
            Tool(name="reply", description="Reply to Feishu chat", inputSchema={...}),
            Tool(name="react", description="Add emoji reaction", inputSchema={...}),
        ]
        dynamic_tools = [
            Tool(
                name=pt.name,
                description=pt.description,
                inputSchema=pt.input_schema,
            )
            for pt in plugin_tools
        ]
        return core_tools + dynamic_tools
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "reply":
            return await _handle_reply(arguments)
        elif name == "react":
            return await _handle_react(arguments)
        
        # Check plugin tools
        for pt in plugin_tools:
            if pt.name == name:
                import asyncio
                result = pt.handler(**arguments)
                if asyncio.iscoroutine(result):
                    result = await result
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        
        raise ValueError(f"Unknown tool: {name}")
```

Key new code in `main()`:

```python
async def main():
    # Discover plugins
    from autoservice.plugin_loader import discover
    plugins = discover("plugins")
    all_plugin_tools = []
    for p in plugins:
        all_plugin_tools.extend(p.tools)
    log.info(f"Loaded {len(all_plugin_tools)} plugin tools from {len(plugins)} plugins")
    
    # Create MCP server
    server = create_server()
    register_tools(server, all_plugin_tools)
    
    # ... rest of main() same as SaneLedger pattern
```

**Step 2: Create feishu/channel-instructions.md**

```markdown
# AutoService Channel Instructions

你是 AutoService 客服助手，通过飞书 IM 与用户交互。

## 角色识别
- **客户消息**（来自外部群/单聊）：使用 /customer-service 或 /sales-demo skill 处理
- **内部消息**（来自团队成员）：直接响应，可执行调试、监控、KB管理等操作
- **系统命令**（以 / 开头）：调用对应 skill

## 工具使用
- 回复消息：使用 `reply` tool（参数：chat_id, text）
- 表情确认：使用 `react` tool（参数：message_id, emoji_type）
- 查询客户数据：使用 plugin MCP tools（如 crm_lookup, billing_query 等，根据已加载的 plugins 可用）
- 查阅产品知识：读取 `plugins/*/references/` 目录中的文件

## 升级规则
- KB 查询无结果 → 告知客户并建议人工客服
- 超出权限操作 → 说明需要主管审批
- 检测到升级触发词（"转接人工"、"找你们经理"、"connect me to"）→ 调用 reply 告知转接中

## 数据目录
- 运行时数据：`.autoservice/`
- 会话日志：`.autoservice/database/sessions/`
- 知识库：`.autoservice/database/knowledge_base/`
```

**Step 3: Create feishu/__init__.py**

```python
```

**Step 4: Verify channel.py loads**

```bash
uv run python3 -c "import feishu.channel; print('channel module OK')"
```

Note: Full runtime test requires Feishu credentials. Verify import-level correctness only.

**Step 5: Commit**

```bash
git add feishu/
git commit -m "feat: Feishu MCP channel server — adapted from SaneLedger with plugin tool loading"
```

---

## Task 6: Skills Migration (Generic)

Migrate 4 skills from autoservices, removing Cinnox-specific content.

**Files:**
- Create: `skills/customer-service/SKILL.md` + `references/` + `scripts/` + `config.yaml`
- Create: `skills/knowledge-base/SKILL.md` + `scripts/`
- Create: `skills/sales-demo/SKILL.md` + `SKILL_WEB.md` + `scripts/`
- Create: `skills/marketing/SKILL.md` + `config.yaml` + `scripts/`
- Create: `skills/_shared/scripts/` (10 shared scripts)

### Step 1: Copy skills/_shared/scripts/

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/_shared/scripts/`

These are the 10 utility scripts used by skills. Copy all and fix imports:
- `init_session.py` — fix `from _shared.` → `from autoservice.`
- `start_mock_server.py` — fix imports
- `stop_mock_server.py` — fix imports
- `query_api.py` — fix imports
- `check_permission.py` — fix imports
- `seed_mock_db.py` — fix imports
- And any others present

### Step 2: Copy customer-service skill

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/customer-service/`
Target: `/Users/h2oslabs/Workspace/AutoService/skills/customer-service/`

Copy `SKILL.md`, `config.yaml`, `references/`, `scripts/`.
- SKILL.md is 90% generic — minimal changes needed
- Fix script imports from `_shared.` to `autoservice.`
- References (`service-methodologies.md`, `customer-personas.md`) are fully generic

### Step 3: Copy knowledge-base skill

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/knowledge-base/`
Target: `/Users/h2oslabs/Workspace/AutoService/skills/knowledge-base/`

**Key changes to SKILL.md:**
- Remove hardcoded domain names (`ai_sales_bot`, `contact_center`, `global_telecom`)
- Remove hardcoded URLs (`docs.cinnox.com`, `cinnox.com`, `m800.com`)
- Remove hardcoded source file references (f1-f8, w1-w4)
- Replace with: "Domains, sources, and URLs are configured per deployment. Check `plugins/*/references/` and `.autoservice/database/knowledge_base/` for available data."
- Keep generic KB engine commands (build, search, status, migrate, subagent)

Fix `scripts/` imports.

### Step 4: Create sales-demo skill (abstracted from cinnox-demo)

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/cinnox-demo/`
Target: `/Users/h2oslabs/Workspace/AutoService/skills/sales-demo/`

**Key changes to SKILL.md:**
- Rename all "CINNOX" → generic references ("your product", "the platform")
- Remove M800/CINNOX brand identity section
- Keep: Mandatory gate workflow, customer type identification, subagent orchestration, Q&A flow, escalation, session management
- Replace domain references with: "Check `plugins/*/references/` for product-specific terminology and knowledge"
- Keep scripts: `route_query.py`, `save_lead.py`, `save_session.py` (fix imports)

**Create SKILL_WEB.md** (from cinnox-demo/SKILL_WEB.md):
- Same genericization as SKILL.md
- Keep web-specific tool instructions (curl instead of scripts)
- Remove CINNOX brand references

### Step 5: Copy marketing skill

Source: `/Users/h2oslabs/Workspace/autoservices/.claude/skills/marketing/`
Target: `/Users/h2oslabs/Workspace/AutoService/skills/marketing/`

This is 99% generic — copy as-is, only fix script imports.

### Step 6: Run make setup to create symlinks

```bash
make setup
ls -la .claude/skills/
```

Verify symlinks point to `../skills/*`.

### Step 7: Commit

```bash
git add skills/
git commit -m "feat: migrate 4 generic skills — customer-service, knowledge-base, sales-demo, marketing"
```

---

## Task 7: Web Server Decomposition

Decompose autoservices `web/server.py` (2174 lines) into focused modules.

**Files:**
- Create: `web/__init__.py`
- Create: `web/app.py` (~150 lines) — FastAPI factory + startup + HTTP routes
- Create: `web/auth.py` (~250 lines) — access codes, tokens, idle timeout
- Create: `web/claude_backend.py` (~350 lines) — SDK/API dual mode
- Create: `web/websocket.py` (~500 lines) — WebSocket handlers
- Create: `web/system_prompts.py` (~400 lines) — persona, skill loading, prompt assembly
- Create: `web/session_persistence.py` (~150 lines) — session save/load
- Create: `web/plugin_kb.py` (~80 lines) — KB search + route query lazy loading
- Copy: `web/static/index.html`, `web/static/login.html`, `web/static/js/`

### Step 1: Create web/auth.py

Extract from server.py lines 1166-1429:
- `_Code` dataclass
- Auth state globals
- `_save_auth()`, `_load_auth()`
- `_evict_token()`, `_purge()`, `_idle_purge_loop()`
- `_valid_token()`
- Auth endpoint handler functions (not the route decorators — those go in app.py)

### Step 2: Create web/session_persistence.py

Extract from server.py lines 383-506:
- `_new_web_session_id()`
- `_session_dir_for_code()`
- `_infer_session_meta()`
- `_save_session_data()`, `_load_session_data()`

### Step 3: Create web/plugin_kb.py

Extract from server.py lines 80-148:
- `_get_kb_search()` — lazy loader
- `_get_route_query()` — lazy loader
- `_presearch_kb()` — KB pre-search with gate check

### Step 4: Create web/system_prompts.py

Extract from server.py lines 527-920, 1015-1109:
- Skill loading from file
- `_web_skill_text()` — strip CLI sections
- `_get_web_skill()` — cached
- `_conditional_skill()` — gate-based trimming
- `_make_system_prompt()` — final assembly
- Escalation detection: `_ESCALATION_RE`, `_should_escalate()`
- Human agent prompt: `_make_human_agent_prompt()`

**Key genericization:** Remove hardcoded CINNOX persona. Make persona configurable:
```python
def load_persona(plugins_dir: Path = Path("plugins")) -> str:
    """Load persona from first plugin's references/persona.md, or use default."""
    for plugin_dir in sorted(plugins_dir.iterdir()):
        persona_path = plugin_dir / "references" / "persona.md"
        if persona_path.exists():
            return persona_path.read_text()
    return DEFAULT_PERSONA
```

### Step 5: Create web/claude_backend.py

Extract from server.py lines 150-380, 772-828, 1115-1163:
- Model selection (`_sdk_model_name`, `_pick_model`)
- Tool execution (`_execute_tool` with in-process fast paths)
- API streaming (`_api_chat_stream`)
- CLI finder (`_find_claude_cli`)
- SDK options builder (`_make_options`)
- SDK client management (`_sdk_connect`, `_sdk_ensure`, `_sdk_turn`, `_sdk_disconnect`)

### Step 6: Create web/websocket.py

Extract from server.py lines 1636-2132:
- Generic `/ws` handler
- Main `/ws/cinnox` handler → rename to `/ws/chat` (generic)
- Auth verification step
- Session init/resume
- Message loop with dual backend routing
- Escalation detection + human agent handoff
- Post-turn session save

Remove Cinnox-specific hardcoding (brand names, account patterns).

### Step 7: Create web/app.py

The thin entry point that assembles everything:

```python
"""AutoService Web Server — FastAPI app factory."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from autoservice.plugin_loader import discover
from web.auth import load_auth, idle_purge_loop
from web.session_persistence import migrate_old_sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    # Load auth state
    load_auth()
    
    # Discover plugins and mount HTTP routes
    plugins = discover("plugins")
    for plugin in plugins:
        for route in plugin.routes:
            # Mount plugin routes on the app
            pass  # Implementation in Step 7
    
    # Start background tasks
    import asyncio
    asyncio.create_task(idle_purge_loop())
    
    yield


app = FastAPI(title="AutoService", lifespan=lifespan)

# Static files
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

# Import route modules (registers endpoints via decorators)
from web import auth  # noqa: register auth endpoints
from web import websocket  # noqa: register websocket handlers
```

### Step 8: Copy static files

Source: `/Users/h2oslabs/Workspace/autoservices/web/static/`
Target: `/Users/h2oslabs/Workspace/AutoService/web/static/`

Copy: `index.html`, `login.html`, `js/` directory.
Do NOT copy `cinnox.html` — that's fork-specific.

### Step 9: Verify web server starts

```bash
uv run uvicorn web.app:app --host 127.0.0.1 --port 8000
# Should start without errors (Ctrl+C to stop)
```

### Step 10: Commit

```bash
git add web/
git commit -m "feat: web server — decomposed from autoservices server.py into 7 focused modules"
```

---

## Task 8: Documentation & Changelog

**Files:**
- Create: `docs/changelog/CHANGELOG.md`
- Create: `docs/API_ARCHITECTURE.md`
- Create: `docs/ONBOARDING.md`
- Copy: `docs/SDK_PERFORMANCE_OPTIMIZATION.md`
- Update: `README.md`

### Step 1: Create CHANGELOG.md

```markdown
# AutoService Changelog

## v0.1.0 (2026-04-05)

Initial release — extracted from autoservices v0.7.4.

### New
- Fork-based multi-customer architecture
- Declarative plugin system (plugin.yaml auto-discovery)
- Feishu MCP channel with plugin tool hosting
- Web chat server with access code auth
- 4 generic skills: customer-service, knowledge-base, sales-demo, marketing
- Example plugin template

### Migrated from autoservices
- Core package: 12 modules from _shared/
- Web server: decomposed from 2174-line monolith into 7 modules
- Skills: genericized (removed Cinnox-specific content)

### Architecture
- Based on autoservices v0.7.4 (Cinnox demo, 8 UAT rounds)
- Feishu channel adapted from SaneLedger
```

### Step 2: Create docs/ONBOARDING.md

Write a customer onboarding guide covering:
1. Fork the repo
2. Create `plugins/{name}/` with plugin.yaml
3. Add references (glossary, product docs)
4. Add customer-specific skills if needed
5. Configure Feishu app credentials
6. `make setup && make run-channel`

### Step 3: Create docs/API_ARCHITECTURE.md

Adapt from autoservices `docs/API_ARCHITECTURE.md`, updated for plugin architecture.

### Step 4: Copy SDK performance doc

```bash
cp /Users/h2oslabs/Workspace/autoservices/docs/SDK_PERFORMANCE_OPTIMIZATION.md docs/
```

### Step 5: Create README.md

Brief intro + link to CLAUDE.md and docs/ONBOARDING.md.

### Step 6: Commit

```bash
git add docs/ README.md
git commit -m "docs: changelog, onboarding guide, API architecture, README"
```

---

## Task 9: Integration Test

**Files:**
- No new files — validation only

### Step 1: Verify plugin discovery

```bash
uv run python3 -c "
from autoservice.plugin_loader import discover
plugins = discover('plugins')
for p in plugins:
    print(f'{p.name}: {len(p.tools)} tools, {len(p.routes)} routes, mode={p.mode}')
    for t in p.tools:
        print(f'  tool: {t.name}')
    for r in p.routes:
        print(f'  route: {r.method} {r.path}')
"
```

### Step 2: Verify core package imports

```bash
uv run python3 -c "
from autoservice.core import generate_id, sanitize_name
from autoservice.config import get_domain_config
from autoservice.mock_db import MockDB
from autoservice.permission import check_permission
from autoservice.session import generate_session_id
from autoservice.customer_manager import CustomerManager
from autoservice.plugin_loader import discover
print('All core imports OK')
"
```

### Step 3: Verify Feishu channel module

```bash
uv run python3 -c "
import feishu.channel
print('Feishu channel module OK')
# Note: cannot run main() without Feishu credentials
"
```

### Step 4: Verify web server starts

```bash
timeout 5 uv run uvicorn web.app:app --host 127.0.0.1 --port 18000 2>&1 || true
# Should see "Uvicorn running on" before timeout
```

### Step 5: Verify symlinks

```bash
make setup
ls -la .claude/skills/ | head -20
# Should show symlinks to ../skills/*
```

### Step 6: Commit (if any fixes were needed)

```bash
git add -A
git commit -m "fix: integration test fixes"
```

---

## Task 10: Cinnox Fork Preparation (Phase 2 Scaffold)

This task prepares the Cinnox-specific content that will go into the first fork.
Create the content in a `_cinnox_fork/` staging directory (not deployed to upstream).

**Files:**
- Create: `_cinnox_fork/plugins/cinnox/plugin.yaml`
- Create: `_cinnox_fork/plugins/cinnox/tools.py`
- Create: `_cinnox_fork/plugins/cinnox/routes.py`
- Create: `_cinnox_fork/plugins/cinnox/mock_data/accounts.json`
- Create: `_cinnox_fork/plugins/cinnox/references/` (glossary, synonym-map)
- Create: `_cinnox_fork/skills/cinnox-demo/SKILL.md`
- Create: `_cinnox_fork/web/static/cinnox.html`
- Create: `_cinnox_fork/docs/history/` (UAT records)

### Step 1: Create Cinnox plugin

**plugin.yaml** — use the spec from design doc §Phase 2.

**tools.py** — extract Cinnox-specific endpoints from autoservices `mock_api_server.py`:
- `customer_lookup` — by account_id, phone, company name
- `billing_query` — billing history with date range
- `subscription_query` — active subscriptions + DIDs
- `permission_check` — action authorization

**routes.py** — FastAPI router wrapping the tools.

**mock_data/accounts.json** — convert from `web/mock_accounts.py` (6 test accounts).

**references/** — copy from autoservices:
- `cinnox-demo/references/glossary.json`
- `cinnox-demo/references/synonym-map.json`

### Step 2: Create Cinnox-specific demo skill

Copy the original `cinnox-demo/SKILL.md` (with all Cinnox branding intact) into `_cinnox_fork/skills/cinnox-demo/`.

### Step 3: Copy web assets

Copy `web/static/cinnox.html` and related assets.

### Step 4: Copy UAT history

```bash
mkdir -p _cinnox_fork/docs/history
cp -r /Users/h2oslabs/Workspace/autoservices/docs/UAT_0305 _cinnox_fork/docs/history/
cp -r /Users/h2oslabs/Workspace/autoservices/docs/upgrade_0313 _cinnox_fork/docs/history/
```

### Step 5: Add _cinnox_fork/ to .gitignore

```gitignore
# Fork staging (not part of upstream)
_cinnox_fork/
```

### Step 6: Commit

```bash
git add _cinnox_fork/ .gitignore
git commit -m "feat: Cinnox fork staging — plugin, demo skill, web assets, UAT history"
```

### Step 7: Document fork creation process

After upstream is stable, the Cinnox fork is created by:
```bash
# 1. Fork AutoService on GitHub
# 2. Clone the fork
git clone git@github.com:ezagent42/AutoService-cinnox.git
cd AutoService-cinnox

# 3. Copy fork content
cp -r _cinnox_fork/plugins/cinnox plugins/
cp -r _cinnox_fork/skills/cinnox-demo skills/
cp -r _cinnox_fork/web/static/cinnox.html web/static/
cp -r _cinnox_fork/docs/history docs/

# 4. Remove staging dir
rm -rf _cinnox_fork/

# 5. Setup
make setup

# 6. Configure credentials
cp .env.example .env
# Edit .env with Feishu credentials

# 7. Import KB data
# Copy OneSyn docs to .autoservice/database/knowledge_base/
# Run /knowledge-base build
```

---

## Execution Summary

| Task | Description | Est. Files | Dependencies |
|------|-------------|------------|--------------|
| 1 | Project scaffolding | 7 | None |
| 2 | Core Python package | 14 | Task 1 |
| 3 | Plugin loader | 1 | Task 2 |
| 4 | Example plugin | 5 | Task 3 |
| 5 | Feishu channel | 3 | Task 2, 3 |
| 6 | Skills migration | ~30 | Task 2 |
| 7 | Web server decomposition | ~15 | Task 2, 3 |
| 8 | Documentation | 5 | Task 1-7 |
| 9 | Integration test | 0 | Task 1-8 |
| 10 | Cinnox fork prep | ~15 | Task 1-9 |

**Parallelizable:** Tasks 4, 5, 6, 7 can run in parallel after Task 3 completes.
