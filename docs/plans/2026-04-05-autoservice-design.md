# AutoService — AI-Native 客服与销售机器人框架

**Date:** 2026-04-05
**Status:** Approved
**Authors:** Allen Woods + Claude

## 1. Problem & Goals

### Problem
autoservices (v0.7.4) 为 Cinnox 客户成功交付了 AI 客服 demo，但架构上客户专属逻辑与通用框架耦合，无法直接复用给其他客户。需要一个可 fork 的通用框架。

### Goals
1. **可迁移性** — 新客户 fork 后只需添加 plugin + 专属 skill，即可启动服务
2. **Feishu 优先** — 飞书 IM 是主通道，提供完整功能（客服、调试、监控）
3. **插件化 API** — 客户专属 API（CRM、资费、账单）通过声明式 plugin 接入
4. **反向贡献** — 客户 fork 中有价值的扩展可抽象后 merge 回 upstream

### Non-Goals
- 不做多租户 SaaS（每个客户 = 独立 repo）
- 不做实时协同编辑
- v1 不做 plugin marketplace / registry

## 2. Architecture

### 2.1 Fork 模型

```
AutoService (upstream)          Customer Fork (e.g. Cinnox)
├── skills/                     ├── skills/
│   ├── customer-service/       │   ├── customer-service/     (inherited)
│   └── knowledge-base/         │   ├── knowledge-base/       (inherited)
├── plugins/                    │   └── cinnox-demo/           (fork-added)
│   └── _example/               ├── plugins/
├── feishu/                     │   ├── _example/              (inherited)
├── web/                        │   └── cinnox/                (fork-added)
├── autoservice/                ├── feishu/                    (inherited)
└── .autoservice/ (gitignored)  ├── web/
                                │   └── static/cinnox.html     (fork-added)
                                └── .autoservice/ (gitignored, customer data)
```

- 每个 git repo 对应一个客户
- `git merge upstream/main` 合并通用改进，不冲突（upstream 不碰客户目录）
- 客户专属扩展 committed in fork，运行时数据 gitignored

### 2.2 目录结构

```
AutoService/
├── feishu/                      # 主通道 — Feishu MCP channel server
│   ├── channel.py               #   WebSocket → MCP bridge + plugin tool host
│   └── channel-instructions.md  #   Channel routing instructions (see §2.6)
│
├── web/                         # 辅通道 — Web chat for non-Feishu users
│   ├── app.py                   #   FastAPI app factory (thin entry point)
│   ├── auth.py                  #   Access code auth + session tokens
│   ├── claude_backend.py        #   Claude Agent SDK / API abstraction
│   ├── websocket.py             #   WebSocket connection handler
│   ├── static/
│   │   ├── index.html           #   通用聊天页
│   │   ├── login.html           #   Access code login
│   │   └── js/                  #   Frontend JS
│   └── templates/               #   Future: product comparison pages etc.
│
├── autoservice/                 # 核心 Python 包
│   ├── __init__.py
│   ├── claude.py                #   Claude Agent SDK wrapper
│   ├── plugin_loader.py         #   扫描 plugins/*/plugin.yaml, 注册 tools + routes
│   ├── mock_db.py               #   SQLite mock database engine
│   ├── session.py               #   Session management
│   ├── permission.py            #   Permission model
│   ├── api_client.py            #   Unified HTTP client (mock/real)
│   ├── database.py              #   Database abstraction layer
│   ├── config.py                #   Domain config loading
│   ├── core.py                  #   Shared utilities (ID gen, name sanitizing)
│   ├── customer_manager.py      #   Customer CRUD
│   └── logger.py                #   Conversation logger
│
├── skills/                      # 通用 skills → symlink 到 .claude/skills/
│   ├── customer-service/        #   HEAR/LAST/LEARN, SPIN, 权限模型
│   │   ├── SKILL.md
│   │   ├── SKILL_WEB.md         #   Web 通道精简版（无文件系统访问）
│   │   ├── config.yaml          #   Skill configuration
│   │   ├── references/
│   │   │   ├── service-methodologies.md
│   │   │   └── customer-personas.md
│   │   └── scripts/
│   ├── knowledge-base/          #   KB ingestion + FTS5 search
│   │   ├── SKILL.md
│   │   ├── config.yaml
│   │   └── scripts/
│   ├── sales-demo/              #   通用销售 demo 编排（从 cinnox-demo 抽象）
│   │   ├── SKILL.md
│   │   ├── SKILL_WEB.md
│   │   └── scripts/
│   └── marketing/               #   营销 skill（从 autoservices 迁移）
│       ├── SKILL.md
│       ├── config.yaml
│       └── scripts/
│
├── plugins/                     # 声明式插件
│   └── _example/                #   示例插件（upstream 提供，见 §2.4.4）
│       ├── plugin.yaml
│       ├── tools.py
│       ├── routes.py
│       ├── references/
│       └── mock_data/
│
├── commands/                    # CLI commands → symlink 到 .claude/commands/
├── agents/                      # Subagent definitions → symlink 到 .claude/agents/
├── hooks/                       # Hooks → symlink 到 .claude/hooks/
│
├── docs/
│   ├── plans/                   #   Design documents
│   ├── changelog/               #   Version history
│   ├── API_ARCHITECTURE.md      #   Plugin API design
│   └── ONBOARDING.md            #   New customer setup guide
│
├── .claude/                     # Symlinks + settings
│   ├── settings.json
│   ├── skills/ → ../skills/
│   ├── commands/ → ../commands/
│   ├── agents/ → ../agents/
│   └── hooks/ → ../hooks/
│
├── .autoservice/                # Gitignored runtime data
│   ├── database/
│   │   ├── knowledge_base/
│   │   │   └── kb.db
│   │   └── sessions/
│   ├── logs/
│   └── config.local.yaml       #   Local overrides (API keys, endpoints)
│
├── .mcp.json                    #   MCP server declarations (see §2.7)
├── pyproject.toml
├── Makefile
├── CLAUDE.md
├── .gitignore
└── README.md
```

### 2.3 通道架构

```
┌─────────────┐    WebSocket     ┌──────────────────────────────┐  MCP stdio  ┌────────────┐
│  Feishu App  │ ──────────────→ │ channel.py (MCP Server)      │ ──────────→ │ Claude Code│
│  (IM Bot)    │ ←────────────── │  ├─ core tools: reply, react │ ←────────── │  + Skills  │
└─────────────┘   reply/react    │  └─ plugin tools: crm_lookup,│  tool calls └────────────┘
                                 │     billing_query, ...       │
                                 └──────────────────────────────┘
                                       ↑ startup
                                       │ plugin_loader scans plugins/*/plugin.yaml
                                       │ imports tool handlers, registers on MCP server

┌─────────────┐    WebSocket     ┌──────────────────────────────┐  SDK/API    ┌──────────┐
│  Browser     │ ──────────────→ │ web/app.py (FastAPI)         │ ──────────→ │ Claude   │
│  (Web Chat)  │ ←────────────── │  ├─ auth + session           │ ←────────── │ API      │
└─────────────┘   streaming      │  └─ plugin HTTP routes:      │             └──────────┘
                                 │     /api/crm/..., /api/...   │
                                 └──────────────────────────────┘
                                       ↑ startup
                                       │ plugin_loader scans plugins/*/plugin.yaml
                                       │ imports route handlers, mounts on FastAPI
```

**Feishu Channel (主通道):**
- 完整功能：客服对话、系统调试、数据监控、KB 管理
- 从 SaneLedger 的 `feishu/channel.py` 适配
- Core MCP tools: `reply`, `react`
- Plugin MCP tools: 由 `plugin_loader` 在 channel.py 启动时注册

**Web Chat (辅通道):**
- 面向无飞书账户的客户
- Access code 认证，session 管理
- Plugin HTTP routes 自动挂载
- 未来扩展：产品比对页等通过 `web/templates/` 添加

**SKILL_WEB.md 模式:**
- Feishu 通道使用 `SKILL.md`（完整版，可访问文件系统和 Bash）
- Web 通道使用 `SKILL_WEB.md`（精简版，无文件系统访问，仅 HTTP API）
- `web/claude_backend.py` 加载 `SKILL_WEB.md` 作为 system prompt

### 2.4 Plugin 机制

#### 2.4.1 plugin.yaml 规范
```yaml
name: crm
version: 1.0.0
description: Customer CRM lookup and management
mode: mock                    # mock | real
installer: cinnox             # 标记来源（哪个客户贡献）

mcp_tools:                    # → channel.py 注册为 MCP tools
  - name: crm_lookup
    description: Look up customer by account ID or phone
    handler: tools.crm_lookup
    input_schema:
      type: object
      properties:
        identifier: { type: string, description: "Account ID or phone number" }
      required: [identifier]

  - name: crm_billing
    description: Get customer billing history
    handler: tools.crm_billing
    input_schema:
      type: object
      properties:
        account_id: { type: string }
        date_range: { type: string, description: "e.g. 2026-01 to 2026-03" }
      required: [account_id]

http_routes:                  # → web/app.py 挂载为 FastAPI routes
  - path: /api/crm/customers/{identifier}
    method: GET
    handler: routes.get_customer

  - path: /api/crm/customers/{account_id}/billing
    method: GET
    handler: routes.get_billing

mock_server:
  seed_data: mock_data/customers.json
  database: .autoservice/database/crm/mock.db

references:                   # Skills 通过文件读取访问
  - references/glossary.json
  - references/product-catalog.md
```

#### 2.4.2 Plugin 加载流程

```
channel.py 启动                          web/app.py 启动
  ↓                                        ↓
plugin_loader.discover("plugins/")       plugin_loader.discover("plugins/")
  ↓                                        ↓
对每个 plugin:                           对每个 plugin:
  1. 解析 plugin.yaml                      1. 解析 plugin.yaml
  2. mode=mock → init SQLite + seed        2. mode=mock → init SQLite + seed
  3. import tool handlers                  3. import route handlers
  4. 注册为 MCP tools on server            4. 挂载为 FastAPI routes on app
  ↓                                        ↓
MCP server ready                         FastAPI ready
(core tools + plugin tools)              (auth routes + plugin routes)
```

两个 server 共享 `plugin_loader.discover()` 但各自只取需要的部分。

#### 2.4.3 Skill ↔ Plugin 协作
- Skill 定义**行为模式**（"用 HEAR 方法处理投诉"）
- Plugin 提供**领域数据**（产品术语、CRM API、定价表）
- Skill 中写 `查阅 plugins/*/references/ 获取产品知识`
- Feishu 通道：Claude 通过 MCP tool calls 调用 plugin API
- Web 通道：server.py 通过 plugin HTTP routes 调用 plugin API
- 底层实现共享：MCP handler 和 HTTP handler 调用同一个 Python function

```python
# plugins/crm/tools.py
async def crm_lookup(identifier: str) -> dict:
    """底层实现，MCP 和 HTTP 共享"""
    db = get_plugin_db("crm")
    return db.lookup_customer(identifier)

# channel.py 注册为 MCP tool → Claude 调用 crm_lookup(identifier="ACC-1001")
# web/app.py 注册为 GET /api/crm/customers/{identifier} → browser 调用
```

#### 2.4.4 示例插件 (_example)

```python
# plugins/_example/tools.py
async def echo(message: str) -> dict:
    """Echo back the input — demonstrates tool structure"""
    return {"echo": message, "mode": get_current_mode()}

async def lookup(id: str) -> dict:
    """Look up a record from mock DB"""
    db = get_plugin_db("_example")
    return db.get(id) or {"error": f"Not found: {id}"}
```

```python
# plugins/_example/routes.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/api/example/{id}")
async def get_example(id: str):
    from .tools import lookup
    return await lookup(id)
```

```yaml
# plugins/_example/plugin.yaml
name: _example
version: 0.1.0
description: Example plugin demonstrating the plugin structure
mode: mock
installer: upstream

mcp_tools:
  - name: example_echo
    description: Echo back input
    handler: tools.echo
    input_schema:
      type: object
      properties:
        message: { type: string }
      required: [message]

  - name: example_lookup
    description: Look up a record
    handler: tools.lookup
    input_schema:
      type: object
      properties:
        id: { type: string }
      required: [id]

http_routes:
  - path: /api/example/{id}
    method: GET
    handler: routes.get_example

mock_server:
  seed_data: mock_data/examples.json
  database: .autoservice/database/example/mock.db

references:
  - references/README.md
```

### 2.5 Symlink 策略

```bash
# Makefile target: make setup
setup:
	ln -sfn ../skills .claude/skills
	ln -sfn ../commands .claude/commands
	ln -sfn ../agents .claude/agents
	ln -sfn ../hooks .claude/hooks
	# Plugin skills: scan plugins/*/skills/ and symlink each into .claude/skills/
	@for dir in plugins/*/skills/*/; do \
	  name=$$(basename $$dir); \
	  ln -sfn ../../$$dir .claude/skills/$$name; \
	done
```

- `make setup` 创建所有 symlinks
- `.claude/settings.json` committed，指向 symlink 路径
- Plugin 内的 skills 也通过 symlink 接入 `.claude/skills/`（非动态注册）

### 2.6 channel-instructions.md

```markdown
# AutoService Channel Instructions

你是 AutoService 客服助手，通过飞书 IM 与用户交互。

## 角色
- 对客户消息：使用 /customer-service 或 /sales-demo skill 处理
- 对内部消息（调试/监控）：直接响应，可访问 .autoservice/ 数据
- 对 KB 管理请求：使用 /knowledge-base skill

## 工具使用
- 回复消息：使用 reply tool
- 表情确认：使用 react tool
- 查询客户数据：使用 plugin 提供的 MCP tools（如 crm_lookup, billing_query）
- 查阅产品知识：读取 plugins/*/references/ 目录

## 升级规则
- KB 查无结果 → 告知客户并建议人工客服
- 超出权限操作 → 说明需要主管审批
- 检测到升级触发词 → 调用 reply 告知转接中
```

实际内容需根据客户 fork 调整（例如 Cinnox fork 添加电信术语和产品说明）。

### 2.7 .mcp.json

```json
{
  "mcpServers": {
    "autoservice-channel": {
      "command": "uv",
      "args": ["run", "python3", "feishu/channel.py"],
      "env": {
        "AUTOSERVICE_PLUGINS_DIR": "plugins"
      }
    }
  }
}
```

单一 MCP server：`channel.py` 既负责飞书通道，也负责托管 plugin MCP tools。

## 3. Migration Plan (autoservices → AutoService)

### Source path convention
autoservices 中的路径：
- `skills/_shared/*` = `.claude/skills/_shared/*`
- `skills/<name>/*` = `.claude/skills/<name>/*`
- `autoservice/*` = project root `autoservice/*`

### Phase 1: 通用框架 (upstream)

#### 1a. Core Python 包 (`autoservice/`)

| Source (autoservices) | Target (AutoService) | Action |
|---|---|---|
| `skills/_shared/api_client.py` | `autoservice/api_client.py` | 迁移，去除 Cinnox 硬编码 |
| `skills/_shared/api_interfaces.py` | `autoservice/api_interfaces.py` | 迁移，保留接口定义 |
| `skills/_shared/session.py` | `autoservice/session.py` | 迁移 |
| `skills/_shared/permission.py` | `autoservice/permission.py` | 迁移 |
| `skills/_shared/mock_api_server.py` | `autoservice/plugin_loader.py` | 重构：提取 plugin 发现 + 注册逻辑 |
| `skills/_shared/mock_db.py` | `autoservice/mock_db.py` | 迁移，作为 plugin mock 模式的基础设施 |
| `skills/_shared/database.py` | `autoservice/database.py` | 迁移 |
| `skills/_shared/config.py` | `autoservice/config.py` | 迁移 |
| `skills/_shared/core.py` | `autoservice/core.py` | 迁移 |
| `skills/_shared/customer_manager.py` | `autoservice/customer_manager.py` | 迁移 |
| `skills/_shared/importer.py` | `autoservice/importer.py` | 迁移 |
| `skills/_shared/logger.py` | `autoservice/logger.py` | 合并 `autoservice/logger.py` |
| `autoservice/claude.py` | `autoservice/claude.py` | 迁移（Claude Agent SDK wrapper） |
| `autoservice/logger.py` | `autoservice/logger.py` | 合并到上面 |

#### 1b. Skills (通用)

| Source (autoservices) | Target (AutoService) | Action |
|---|---|---|
| `skills/customer-service/SKILL.md` | `skills/customer-service/SKILL.md` | 去除 Cinnox 硬编码，保留 HEAR/LAST/LEARN/SPIN |
| `skills/customer-service/SKILL_WEB.md` | (如果存在) `skills/customer-service/SKILL_WEB.md` | 迁移 Web 精简版 |
| `skills/customer-service/config.yaml` | `skills/customer-service/config.yaml` | 迁移 |
| `skills/customer-service/references/*` | `skills/customer-service/references/` | 保留通用方法论 |
| `skills/customer-service/scripts/*` | `skills/customer-service/scripts/` | 保留通用 CRUD (7 scripts) |
| `skills/knowledge-base/SKILL.md` | `skills/knowledge-base/SKILL.md` | 去除 3-domain 硬编码，改为 config 驱动 |
| `skills/knowledge-base/scripts/*` | `skills/knowledge-base/scripts/` | 保留通用 KB 引擎 (5 scripts) |
| `skills/cinnox-demo/SKILL.md` | `skills/sales-demo/SKILL.md` | 抽象为通用销售 demo 编排 |
| `skills/cinnox-demo/SKILL_WEB.md` | `skills/sales-demo/SKILL_WEB.md` | 抽象为通用 Web 版本 |
| `skills/cinnox-demo/scripts/*` | `skills/sales-demo/scripts/` | 通用化 (route_query, save_lead, save_session) |
| `skills/marketing/SKILL.md` | `skills/marketing/SKILL.md` | 迁移（通用营销 skill） |
| `skills/marketing/config.yaml` | `skills/marketing/config.yaml` | 迁移 |
| `skills/marketing/scripts/*` | `skills/marketing/scripts/` | 迁移 |
| `skills/_shared/scripts/*` | `skills/_shared/scripts/` | 迁移通用脚本 (10 scripts) |

#### 1c. Feishu Channel

| Source | Target (AutoService) | Action |
|---|---|---|
| SaneLedger `feishu/channel.py` | `feishu/channel.py` | 适配：去掉 beancount/approval，加 plugin_loader |
| SaneLedger `feishu/channel-instructions.md` | `feishu/channel-instructions.md` | 重写为客服场景（见 §2.6） |

#### 1d. Web Server (拆分 autoservices `web/server.py` 2174 行)

| Source (autoservices) | Target (AutoService) | Action |
|---|---|---|
| `web/server.py` (auth 部分) | `web/auth.py` | 提取：access code, token, one-time use |
| `web/server.py` (Claude SDK/API 部分) | `web/claude_backend.py` | 提取：SDK vs API 模式抽象 |
| `web/server.py` (WebSocket 部分) | `web/websocket.py` | 提取：WS handler, streaming |
| `web/server.py` (app factory) | `web/app.py` | 薄入口：组装 auth + ws + plugin routes |
| `web/static/index.html` | `web/static/index.html` | 迁移 |
| `web/static/login.html` | `web/static/login.html` | 迁移 |
| `web/static/js/*` | `web/static/js/` | 迁移 |

#### 1e. 配置与文档

| Source (autoservices) | Target (AutoService) | Action |
|---|---|---|
| `pyproject.toml` | `pyproject.toml` | 适配依赖列表 |
| `CLAUDE.md` | `CLAUDE.md` | 重写为 AutoService |
| `docs/API_ARCHITECTURE.md` | `docs/API_ARCHITECTURE.md` | 更新为 plugin 架构 |
| `docs/ONBOARDING.md` | `docs/ONBOARDING.md` | 更新为 fork 流程 |
| `web/CHANGELOG.md` | `docs/changelog/CHANGELOG.md` | 作为版本基线 |
| `docs/SDK_PERFORMANCE_OPTIMIZATION.md` | `docs/SDK_PERFORMANCE_OPTIMIZATION.md` | 迁移 |

#### 1f. 环境变量

```bash
# .env (gitignored)
FEISHU_APP_ID=...               # 飞书应用 ID
FEISHU_APP_SECRET=...           # 飞书应用 Secret
ANTHROPIC_API_KEY=...           # Web 通道 API mode 使用
DEMO_BACKEND=sdk                # sdk | api
DEMO_MODEL=claude-sonnet-4-6
DEMO_PORT=8000
IDLE_TIMEOUT_MINUTES=15
DEMO_ADMIN_KEY=...              # Web admin API key
AUTOSERVICE_PLUGINS_DIR=plugins # Plugin 扫描目录
```

#### 1g. 不迁移（丢弃）

| Source (autoservices) | Reason |
|---|---|
| `skills/agent-browser/` | 通用 Claude Code plugin，非项目专属 |
| `skills/architecture-audit/` | 开发工具，非运行时 |
| `skills/autoservice-design/` | 设计参考，已融入本设计文档 |
| `skills/autoservice-skill-guide/` | 开发指南，融入 ONBOARDING.md |
| `skills/brainstorming/` | 通用 Claude Code plugin |
| `skills/cc-nano-banana/` | 图片生成，非核心 |
| `skills/ci-sync/` | CI 工具，按需重建 |
| `skills/demo-changelog/` | 替换为标准 changelog 流程 |
| `deploy/*` | 重建部署配置 |
| `Dockerfile`, `docker-compose.yml` | 重建 |
| `main.py`, `customer_service.py`, `marketing.py` | CLI 入口，被 channel.py + web/app.py 替代 |
| `workspace/` (PPT builder) | Cinnox 专属产出物 |

### Phase 2: Cinnox Fork (首个客户实例)

在 upstream Phase 1 完成后，fork 并添加：

| Source (autoservices) | Target (Cinnox Fork) | Action |
|---|---|---|
| `skills/cinnox-demo/SKILL.md` (Cinnox 专属部分) | `skills/cinnox-demo/SKILL.md` | 保留完整 Cinnox 编排逻辑 |
| `skills/cinnox-demo/references/glossary.json` | `plugins/cinnox/references/glossary.json` | 移入 plugin |
| `skills/cinnox-demo/references/synonym-map.json` | `plugins/cinnox/references/synonym-map.json` | 移入 plugin |
| `skills/_shared/mock_api_server.py` (Cinnox 端点) | `plugins/cinnox/tools.py` | 提取 Cinnox CRM/billing handlers |
| `skills/_shared/mock_api_server.py` (Cinnox routes) | `plugins/cinnox/routes.py` | 提取 Cinnox HTTP routes |
| `web/mock_accounts.py` + `cinnox_accounts.db` | `plugins/cinnox/mock_data/accounts.json` | 转为 seed data |
| `web/static/cinnox.html` | `web/static/cinnox.html` | 客户品牌页 |
| `docs/resource/OneSyn/*` | `docs/resource/` 或 `.autoservice/` | KB 源文件 |
| `docs/UAT_0305/*` | `docs/history/UAT_0305/` | 迭代历史 |
| `docs/upgrade_0313/*` | `docs/history/upgrade_0313/` | 迭代历史 |
| `docs/pricing/*` | `docs/pricing/` | 定价文档 |
| `docs/CINNOX_DEMO_SETUP.md` | `docs/SETUP.md` | 环境配置 |
| `docs/CINNOX_MOCK_DATA.md` | `plugins/cinnox/mock_data/README.md` | Mock 数据说明 |

### Phase 2 plugin.yaml (Cinnox)

```yaml
name: cinnox
version: 1.0.0
description: CINNOX/M800 CRM, billing, and telecom product catalog
mode: mock
installer: cinnox

mcp_tools:
  - name: cinnox_customer_lookup
    description: Look up CINNOX customer by account ID, phone, or company name
    handler: tools.customer_lookup
  - name: cinnox_billing
    description: Get billing history and invoice status
    handler: tools.billing_query
  - name: cinnox_subscriptions
    description: Get active subscriptions and DID numbers
    handler: tools.subscription_query
  - name: cinnox_permission_check
    description: Check if an action is permitted for the current operator
    handler: tools.permission_check

http_routes:
  - path: /api/cinnox/customers/{identifier}
    method: GET
    handler: routes.get_customer
  - path: /api/cinnox/customers/{account_id}/billing
    method: GET
    handler: routes.get_billing
  - path: /api/cinnox/customers/{account_id}/subscriptions
    method: GET
    handler: routes.get_subscriptions

mock_server:
  seed_data: mock_data/accounts.json
  database: .autoservice/database/cinnox/mock.db

references:
  - references/glossary.json
  - references/synonym-map.json
  - references/product-catalog.md
```

## 4. Data Flow

### Customer Inquiry (Feishu Channel)
```
Customer sends message in Feishu group
  ↓
channel.py receives via WebSocket (P2ImMessageReceiveV1)
  ↓
Dedup check → ACK with emoji reaction (react tool)
  ↓
Inject as MCP notification → Claude Code
  ↓
Claude reads channel-instructions.md
  ↓
Claude invokes skill (e.g. /customer-service)
  ↓
Skill reads plugins/*/references/ for domain knowledge
  ↓
Skill calls plugin MCP tools (e.g. cinnox_customer_lookup) via channel.py
  ↓
Plugin tool queries mock/real DB, returns structured data
  ↓
Claude composes response using skill methodology (HEAR/SPIN/etc.)
  ↓
Claude calls reply tool → message back to Feishu
```

### Customer Inquiry (Web Chat)
```
Customer opens web page → login with access code
  ↓
WebSocket connection to web/app.py
  ↓
claude_backend.py invokes Claude Agent SDK with SKILL_WEB.md as system prompt
  ↓
Claude calls plugin HTTP routes for data (or server calls on behalf)
  ↓
Response streamed back via WebSocket → browser renders
```

## 5. Plugin Lifecycle

### Install (新客户 fork 后)
1. `mkdir plugins/{name}`
2. Create `plugin.yaml` with tool/route declarations
3. Implement `tools.py` (共享逻辑) + `routes.py` (HTTP wrappers)
4. Add `mock_data/` for development, `references/` for domain knowledge
5. `make setup` → 创建 plugin skills symlinks（如果 plugin 有 skills/）
6. Server restart → auto-discovered

### Update
1. Modify `plugin.yaml` (add tools/routes, change mode)
2. Update handlers
3. Server restart → changes picked up
4. 如果有通用价值 → 抽象为模板，PR 回 upstream

### Mock → Real 切换
1. `plugin.yaml`: `mode: mock` → `mode: real`
2. Add real API credentials to `.autoservice/config.local.yaml`
3. `tools.py` reads mode from config, routes to real endpoints
4. 无需改 skill 或 channel 代码

## 6. Error Handling

- **Plugin load failure**: Log warning with plugin name + error, skip plugin, server continues
- **Plugin load failure (startup)**: If zero plugins loaded, log critical warning but still start (core tools work)
- **MCP tool failure**: Return `{"error": "...", "recoverable": true/false}` to Claude, Claude 告知用户
- **KB search empty**: Skill escalates to human agent (不编造，anti-hallucination rule)
- **Feishu disconnection**: Auto-reconnect with exponential backoff (SaneLedger pattern)
- **Web session timeout**: Auto-release after idle timeout, resumable via session_id
- **Channel startup failure**: `.mcp.json` server fails → Claude Code reports MCP error, user sees in terminal

## 7. Security

- `.autoservice/config.local.yaml` — gitignored, contains API keys and real endpoints
- `.feishu-credentials.json` — gitignored
- `.env` — gitignored, contains secrets
- Plugin `mode: mock` — no external API calls in development
- Web access codes — one-time use, admin key protected
- Permission model — action-level authorization (can_approve / requires_supervisor / forbidden)
- `.claude/settings.json` permissions — restrict Bash to known script patterns

## 8. Future Extensions

- **更多 Web 页面**: 产品比对页、报价生成器 — 通过 `web/templates/` 添加
- **更多通道**: Slack、WhatsApp — 新建 `channels/{name}/channel.py`，共享 plugin_loader
- **Plugin Registry**: 如果客户数量增长，可引入 `plugins.lock.yaml` 版本锁定
- **Lark Skills**: 从 SaneLedger 选择性 symlink lark-im, lark-doc 等通用飞书技能
- **Plugin 模板生成器**: `make new-plugin name=xxx` 脚手架
