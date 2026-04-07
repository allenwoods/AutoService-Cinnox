# /explain Command — Flow Explorer Design

## Overview

Add `/explain` command to the admin management group. Given a natural language query (user question or custom scenario), it generates an interactive flow visualization showing how AutoService processes it. The visualization is a draggable node graph served as a web page, with annotation and discussion prompt generation.

## Architecture

```
管理群 /explain "用户问DID价格"
        │
        ▼
  channel-server ──→ 构造 explain 消息 ──→ route_message (wildcard)
                                              │
                                              ▼
                                     Claude Code 实例 [*]
                                              │
                                         调用 /explain skill
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                  1. 检索 flows/       2. 未命中则          3. 渲染
                  语义匹配已有flow      分析 skills/rules     HTML
                  组合多个atomic flow   生成新 atomic flow    注入 JSON
                          │            保存到 flows/          │
                          └──────────┬───────────┘           │
                                     ▼                       ▼
                              flow 数据 (YAML→JSON)    explain 模板
                                     │                       │
                                     └───────┬───────────────┘
                                             ▼
                                web/static/explain/{id}.html
                                             │
                                             ▼
                              channel-server 回复管理群链接
                              https://{base}/explain/{id}.html
```

## File Structure

```
.autoservice/
  flows/                          # Flow source of truth (YAML)
    _index.yaml                   # flow_id → description/tags/triggers for retrieval
    identify-customer-type.yaml   # Atomic flow example
    new-customer-lead.yaml
    kb-query-routing.yaml
    ...
  config.yaml                     # base_url, company name

skills/
  explain/
    SKILL.md                      # Explain skill definition
    templates/
      explain.html                # Fixed HTML template (node flow graph)

web/static/
  explain/                        # Generated explain pages
    {id}.html
```

## §1 Flow Granularity Principle

Based on function decomposition + DAG subgraph partitioning:

### Atomic Flow

A single decision unit:
- Contains **1 decision point** (branch/judgment) with all exit paths
- **3–8 nodes** (entry → preconditions → decision → branch results)
- Exactly **1 entry node**, **1–3 exit nodes** (resolve / handoff / error)
- Analogy: a function with single responsibility

### Composite Flow

Assembled by connecting atomic flows via exit→entry:
- Exit nodes of type `handoff` annotate `next_flow: <flow_id>`
- `/explain` rendering recursively expands all referenced sub-flows into a complete graph
- Business execution follows `next_flow` chain

### Granularity Rules

| Signal | Action |
|---|---|
| A flow has >1 independent decision point | Split: each decision point becomes its own flow |
| A flow has only 1-2 nodes with no decision | Merge into upstream flow |
| Multiple flows share the same subsequence | Extract as independent flow, reuse via reference |

Most user questions = 2–4 atomic flows composed together.

## §2 Flow YAML Format

### Atomic Flow Example

```yaml
id: identify-customer-type
name: 识别客户类型
description: 根据用户首条消息判断新客户/老客户/合作伙伴
tags: [customer, identification, gate]

entry: check_signal
exits:
  - node: route_new
    type: handoff
    next_flow: new-customer-lead
  - node: route_existing
    type: handoff
    next_flow: existing-customer-verify
  - node: route_partner
    type: handoff
    next_flow: partner-escalation
  - node: ask_type
    type: handoff
    next_flow: identify-customer-type

nodes:
  - id: check_signal
    label: 检查消息信号
    type: process
    note: 从首条消息提取意图关键词

  - id: has_signal
    label: 信号明确？
    type: decision
    condition: 消息包含客户类型关键词

  - id: route_new
    label: → 新客户流程
    type: exit

  - id: route_existing
    label: → 老客户流程
    type: exit

  - id: route_partner
    label: → 合作伙伴流程
    type: exit

  - id: ask_type
    label: 询问客户类型
    type: action
    note: "Happy to help! Are you new to CINNOX, or do you already have an account with us?"

edges:
  - from: check_signal
    to: has_signal
  - from: has_signal
    to: route_new
    label: 新客户信号
  - from: has_signal
    to: route_existing
    label: 老客户信号
  - from: has_signal
    to: route_partner
    label: 合作伙伴信号
  - from: has_signal
    to: ask_type
    label: 无明确信号
```

### Node Types

| type | Meaning | Shape |
|---|---|---|
| `process` | Processing/analysis step | Rounded rectangle |
| `decision` | Judgment/branch | Diamond |
| `action` | Send message / execute operation | Rectangle |
| `exit` | Exit point (resolve/handoff/error) | Circle |

### Index File `_index.yaml`

```yaml
flows:
  - id: identify-customer-type
    name: 识别客户类型
    tags: [customer, identification, gate]
    triggers: ["谁", "客户类型", "新客户还是老客户"]

  - id: new-customer-lead
    name: 新客户信息收集
    tags: [customer, lead, collection]
    triggers: ["收集信息", "lead", "姓名公司邮箱"]

  - id: kb-query-routing
    name: 知识库查询路由
    tags: [kb, query, routing, domain]
    triggers: ["产品问题", "价格", "DID", "功能"]
```

`triggers` enables semantic matching against `/explain` parameters.

## §3 HTML Template & Interaction

### Layout

```
+----------------------------------------------------------+
| 🔍 CINNOX Flow Explorer                    [← 返回列表]  |
+----------------------------------------------------------+
|                                                          |
|  Canvas (draggable node flow graph)                      |
|                                                          |
|   [process]──→◇decision◇──→[action]──→(exit)            |
|                    │                                     |
|                    └──→[action]──→(exit)                 |
|                                                          |
+---------------------------+------------------------------+
| 📝 Node Annotation Panel  | 💬 Discussion Output         |
|                           |                              |
| Click node to view/edit   | Progressive: initially shows |
| ─────────────────         | guide text, builds prompt    |
| [Node name]               | as user marks nodes          |
| Type: decision            |                              |
| Note: (editable textarea) | No marks → general prompt:   |
| Mark: ✅ OK ⚠️ Improve ❌ | "请解释这个流程的整体设计思路" |
+---------------------------+------------------------------+
```

### Core Interactions

- **Drag nodes** — free layout on canvas, position persisted in localStorage
- **Click node** — left panel shows note + editable annotation + status mark
- **Mark nodes** — three states (OK / improve / problem); marked nodes appear in discussion prompt
- **Expand composite** — exit nodes with `handoff` show expand button, loads `next_flow` sub-graph inline
- **Progressive discussion prompt** — initially empty with guide text; updates live as user marks nodes; no marks = general overview prompt

### Prompt Output Example

When nodes are marked:
> 我在查看"用户问DID价格"的处理流程，由以下子流程组成：识别客户类型 → 新客户信息收集 → 知识库查询路由。
> 我标记了 2 个需要讨论的节点：
> 1. ⚠️ "知识库查询路由 / 判断 domain" — [user annotation]
> 2. ❌ "新客户信息收集 / 收集全部字段" — [user annotation]
> 请针对这些节点提出改进建议。

When no nodes are marked:
> 请解释"用户问DID价格"这个场景的整体处理流程和设计思路。

### Style (consistent across all generated pages)

- **Light theme** — white background (#ffffff), light gray panels (#f8fafc)
- **Node colors fixed**: process=#3b82f6, decision=#f59e0b, action=#10b981, exit=#6b7280
- **Edges**: dark gray (#374151), solid arrowheads
- **System font** for UI, monospace for code/values
- **All styles inline, zero external dependencies** — single self-contained HTML file

## §4 Base URL Configuration

File: `.autoservice/config.yaml`

```yaml
company: cinnox
base_url: https://cinnox.h2os.cloud
```

The explain skill reads `base_url` from this file to construct the link sent back to the admin group. The web server serves `web/static/explain/` at the `/explain/` path.

## §5 Admin Command Flow

### channel-server.py

New command in `_handle_admin_message`:

```
/explain <natural language query>
```

Behavior:
1. Parse the query text after `/explain `
2. Construct a message with `type: "message"`, `text: "[EXPLAIN] <query>"`, route to wildcard instance
3. Reply to admin group: "正在分析流程，请稍候..."

### channel.py → Claude Code

Claude Code receives `[EXPLAIN] <query>` via channel notification. The `[EXPLAIN]` prefix triggers the explain skill (defined in channel-instructions.md routing).

### explain skill (SKILL.md)

1. Read `.autoservice/flows/_index.yaml`
2. Match query against `triggers` + `tags` to find relevant atomic flows
3. If no match: analyze skills/rules/instructions, generate new atomic flow(s), save to `flows/`, update `_index.yaml`
4. Load matched flow YAML(s), convert to JSON
5. Read `skills/explain/templates/explain.html`
6. Inject flow JSON + metadata into template
7. Save to `web/static/explain/{id}.html`
8. Read `base_url` from `.autoservice/config.yaml`
9. Reply via `reply` tool: link to the generated page

## §6 Integration Points

### channel-instructions.md additions

Data section:
```
- `.autoservice/flows/` — 业务流程定义（atomic flows，YAML）
```

Mode routing — new prefix:
```
### [EXPLAIN] prefix
Use /explain skill. Generate flow visualization.
```

### Business execution

When processing customer messages in production mode, Claude Code can reference `.autoservice/flows/` to understand the expected processing sequence. This is optional context — flows are descriptive, not prescriptive.

## §7 Summary of Components

| Component | Action |
|---|---|
| `channel_server.py` | Add `/explain` admin command, route to wildcard |
| `channel-instructions.md` | Add `[EXPLAIN]` routing + flows data reference |
| `skills/explain/SKILL.md` | New skill: match/generate flows, render HTML |
| `skills/explain/templates/explain.html` | Fixed HTML template with canvas + annotation |
| `.autoservice/flows/*.yaml` | Atomic flow definitions |
| `.autoservice/flows/_index.yaml` | Flow index for retrieval |
| `.autoservice/config.yaml` | Base URL + company name |
| `web/static/explain/` | Generated explain pages |
