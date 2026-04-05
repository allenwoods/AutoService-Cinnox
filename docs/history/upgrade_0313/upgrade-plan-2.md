# v1.2 Multi-Subagent 协作架构计划

## Context

v1.1.2 是单 agent 架构：主 agent 直接调用 `kb_search.py`、处理 gate 逻辑、生成回复。v1.2 引入 Claude Code 原生 subagent 机制（`.claude/agents/`），实现**多 subagent 动态协作**：

- 主 agent 保持 cinnox-demo 流程控制权，动态组队
- 专职 subagent 各司其职（查询、话术、审查、审计）
- Self challenge：审查 subagent 对最终回复进行质量自检
- 审计 subagent 使用 persistent memory 积累跨会话数据

**运行场景**：既用于实时 UAT 演示，也用于离线红队测试。

---

## 架构总览

```
客户提问
    ↓
主 Agent (cinnox-demo skill)
    ├── 1. Gate 检查 (customer_type, gate_cleared)
    ├── 2. route_query.py → domain/region/role
    ├── 3. 动态组队 → 选择 subagent 组合
    │   ├── product-query (KB 按产品线查) ──┐
    │   ├── region-query  (KB 按地区查)    ├→ 返回结构化数据
    │   ├── copywriting   (话术优化)       ├→ 返回润色文本
    │   ├── reviewer      (质量自检)       ├→ 返回 pass/fail
    │   └── auditor       (审计记录)       └→ fire-and-forget
    ├── 4. 整合所有 subagent 结果
    └── 5. 发送最终回复
```

---

## 5 个 Subagent 定义

| # | Subagent | 文件 | 职责 | 工具 |
|---|----------|------|------|------|
| 1 | product-query | `.claude/agents/product-query.md` | 按产品线查 KB（contact_center, ai_sales_bot） | Bash, Read |
| 2 | region-query | `.claude/agents/region-query.md` | 按地区查 KB（global_telecom） | Bash, Read |
| 3 | copywriting | `.claude/agents/copywriting.md` | 话术优化、BANNED PHRASES 检查 | 无（纯文本） |
| 4 | reviewer | `.claude/agents/reviewer.md` | 11 项质量自检（Self Challenge） | Bash, Read |
| 5 | auditor | `.claude/agents/auditor.md` | 审计记录 + 跨会话分析 | Bash, Read, Write, Glob |

### KB 域→源映射表

| Domain | Source Filter | 内容 |
|--------|--------------|------|
| contact_center | `f4,f5,f6,w1,w2` | CINNOX 功能、定价、M800 介绍、官方文档 |
| ai_sales_bot | `f1,f2,f3` | AI Sales Bot 定价、功能、产品概述 |
| global_telecom | `f7,f8,w4` | DID 费率、VN 费率、电信定价 |

---

## 动态组队规则

| 场景 | 调用 subagent（按顺序） |
|------|------------------------|
| gate_cleared=false | 无 subagent（直接 lead/verify） |
| ambiguous=true | 无 subagent（直接问澄清问题） |
| domain=contact_center/ai_bot | product-query → copywriting → reviewer |
| domain=global_telecom | region-query → copywriting → reviewer |
| Discovery phase（模糊请求） | copywriting only |
| Escalation 场景 | reviewer only |
| 简单寒暄/确认 | 无 subagent |

所有场景结束后，auditor 以 fire-and-forget 方式记录。

---

## Reviewer 检查清单（11 项）

| # | 检查项 | 严重级别 |
|---|--------|---------|
| 1 | KB 准确性：每个事实声明是否有 KB 结果支持 | critical |
| 2 | 无幻觉：是否提及 KB 中不存在的功能/价格 | critical |
| 3 | Gate 合规：gate_cleared=false 时是否避免回答产品问题 | critical |
| 4 | 客户类型处理：unknown 时是否先问路由问题 | critical |
| 5 | Lead 收集顺序：新客户是否按 Name→Company→Email→Phone 顺序 | major |
| 6 | 身份验证：老客户是否要求 4 项验证信息 | major |
| 7 | Escalation 措辞：是否用安全措辞（疑问句形式）提议 | major |
| 8 | BANNED PHRASES：是否包含禁用措辞 | major |
| 9 | Escalation 触发词：非确认 escalation 时是否使用了触发词 | major |
| 10 | 回复长度：是否 ≤ 4 句 | minor |
| 11 | 来源引用：KB 来源是否用友好名称引用 | minor |

---

## Context 隔离原则

| Subagent | 接收 | 不接收 |
|----------|------|--------|
| product-query | 客户问题 + domain | 完整对话历史、客户个人信息 |
| region-query | 客户问题 + region + number_type | 完整对话历史 |
| copywriting | 草稿回复 + 客户类型 + 情绪 | 对话历史、KB 原始结果 |
| reviewer | 最终回复 + 会话状态摘要 | 完整对话历史、客户 PII |
| auditor | 匿名编排元数据 | 客户姓名/邮箱/电话 |

---

## 文件变更清单

### 新建文件（6 个）

| 文件 | 说明 |
|------|------|
| `.claude/agents/product-query.md` | 产品线查询 subagent |
| `.claude/agents/region-query.md` | 地区查询 subagent |
| `.claude/agents/copywriting.md` | 话术优化 subagent |
| `.claude/agents/reviewer.md` | 质量审查 subagent |
| `.claude/agents/auditor.md` | 审计 subagent |
| `docs/upgrade_0310/upgrade-plan-2.md` | 本文档 |

### 修改文件（1 个）

| 文件 | 变更 |
|------|------|
| `.claude/skills/cinnox-demo/SKILL.md` | 新增 Step 3.5（编排）、修改 Step 4（subagent 分发）、新增 Step 8（审计） |

---

## 验证计划

### Subagent 单元测试

- **product-query**: query="WhatsApp integration?" domain=contact_center → found=true, sources 包含 f4
- **region-query**: query="US toll-free DID pricing" region=US → 调用 kb_search.py --source-filter "f7,f8,w4"
- **copywriting**: draft 包含 "connect you with" → banned_phrase_caught=true
- **reviewer**: response 包含 KB 中不存在的功能 → passed=false
- **auditor**: 编排元数据 → 追加到 audit_log.jsonl

### 集成测试

- TC-B1 回归: WhatsApp → product-query → copywriting → reviewer 通过
- 歧义检测: "What's the pricing?" → ambiguous → 不调用 subagent
- Escalation: 账单纠纷 → reviewer 验证 escalation 措辞合规

### UAT 回归

- 运行所有 29 个 TC（Round 5 + Round 6）
- 通过率 ≥ v1.1.2
- 检查 auditor 日志覆盖所有 TC

---

## 演化路线

| 版本 | 特性 |
|------|------|
| v1.2 (本次) | 5 个 subagent + 动态组队 + 审计 |
| v1.2.1 (hotfix) | 修复 subagent 未被调度问题（见下方） |
| v1.3 | 并行 subagent（auditor 与回复并行） |
| v1.4 | 基于审计数据的条件组队优化 |
| v1.5 | reviewer 检查清单基于审计模式自适应 |

---

## v1.2.1 Hotfix — 修复 Subagent 未被调度

### 问题描述

Round 7 测试（2026-03-11）发现：**Claude 完全没有调度任何 subagent**，所有产品/定价问题都走了 fallback 路径——直接用 Bash 调 `kb_search.py`，绕过了 Step 3.5 的 subagent 编排管线。

- 7 个 TC 中仅 TC-S4（gate 未通过不调度）通过，通过率 14%
- 前端 Subagent Trace 面板 0 次出现
- 后台 `[subagent]` 日志 0 条
- `audit_log.jsonl` 为空

详见：`docs/upgrade_0310/round7/Test_Result_Round7_v1.2.md`

### 根本原因

SKILL.md 中存在两条冲突路径，Claude 选了更直接的那条：

1. **Step 3 各分支中 `kb_subagent.py` 出现 10 次** — Claude 读到这些指令时直接用 Bash 执行，不走 Step 3.5
2. **第 438 行 fallback 门槛太低** — "If subagents are unavailable, you may call kb_search.py directly" 给了 Claude 跳过 subagent 的理由
3. **Step 3.5 语气不够强** — 只说 "This step runs automatically"，没有 MANDATORY / MUST 等强制语

### 修改方案

#### SKILL.md 变更（3 处）

**变更 A — 替换所有 `kb_subagent.py` 引用**

将 Step 3 中所有 `run kb_subagent.py` / `Do NOT run kb_subagent.py` 统一替换：

| 原文 | 替换为 |
|------|--------|
| `run kb_subagent.py` | `proceed to Step 3.5 (Subagent Orchestration)` |
| `Do NOT run kb_subagent.py` | `Do NOT proceed to Step 3.5` |

涉及行：71, 170, 171, 172, 199, 208, 226, 243, 270, 277

**变更 B — 删除 fallback 路径**

删除第 438-442 行的 fallback 块，替换为禁止直接调用的说明。

**变更 C — Step 3.5 加强制语气**

在 Step 3.5 开头加 MANDATORY 声明，明确要求使用 Agent 工具。

#### 不变的部分

- `web/server.py`：Agent 事件捕获代码不变（已正确实现）
- `web/static/cinnox.html`：Trace 面板代码不变（已正确实现）
- `.claude/agents/*.md`：5 个 subagent 定义不变

### 验证

修改后重启 Web UI，重跑 Round 7 TC-S1。

**结果：仍然失败。** Claude 依然没有调度 subagent。原因见 v1.2.2。

---

## v1.2.2 Hotfix — 禁用 Pre-fetch KB 注入 + 修改 WEB MODE 指令

### 问题描述

v1.2.1 修改 SKILL.md 后重启服务器，重跑 TC-S1，Claude 仍然直接回答产品问题，不调度任何 subagent。Subagent Trace 面板 0 次出现。

### 根本原因

v1.2.1 只修了 SKILL.md prompt 层，但 `web/server.py` 中有两层机制在 SKILL.md 之前就把 KB 数据喂给了 Claude，使其根本不需要调 subagent：

**第一层：`_WEB_KB_OVERRIDE`（系统 prompt 最前面）**

```
## ⚡ WEB MODE — HTTP API ENDPOINTS
**Pre-fetched KB Context (check this FIRST):**
- If present → use it directly, NO curl needed
```

这条指令排在 SKILL.md Step 3.5 之前，Claude 读到这里就决定直接用 pre-fetched 数据回答。

**第二层：`_presearch_kb()` 函数（line 93-125）**

服务端在把用户消息发给 Claude 之前，就已经搜了 KB 并把结果注入到用户消息里：

```python
augmented = f"{user_text}\n\n---\n🔍 KB Context (pre-fetched):\n{injected}\n---"
```

Claude 看到消息自带 KB 数据 + 系统 prompt 说 "use it directly"，当然直接用了，完全不需要调 Agent 工具。

### 修改方案

#### 变更 A — 重写 `_WEB_KB_OVERRIDE`

删除 KB Search curl 指令和 pre-fetch 指引，替换为明确要求用 Agent 工具调 subagent：

```python
# 原来
"### 1. KB Search
curl -s http://127.0.0.1:{server_port}/api/kb_search?query=...
Pre-fetched KB Context (check this FIRST): use it directly, NO curl needed"

# 改为
"### KB Search — USE SUBAGENTS (MANDATORY)
ALL uv run and curl commands for KB search are DISABLED.
You MUST use the Agent tool to dispatch to subagents (product-query / region-query)."
```

#### 变更 B — SDK 模式禁用 `_presearch_kb()`

```python
# 原来（所有模式都 pre-fetch）
augmented_prompt, presearch_hits = _presearch_kb(user_text, ...)

# 改为（只有 API 模式 pre-fetch，SDK 模式跳过）
if DEMO_BACKEND == "api":
    augmented_prompt, presearch_hits = _presearch_kb(user_text, ...)
else:
    augmented_prompt, presearch_hits = user_text, 0
```

API 模式没有 Agent 工具，仍需 pre-fetch。SDK 模式有 Agent 工具，必须让 subagent 处理 KB 搜索。

### 变更文件

| 文件 | 变更 |
|------|------|
| `web/server.py` line 425-455 | 重写 `_WEB_KB_OVERRIDE`，删除 curl KB 搜索和 pre-fetch 指引 |
| `web/server.py` line 1391-1394 | SDK 模式跳过 `_presearch_kb()`，只保留 API 模式 |

### 验证

修改后重启 Web UI，重跑 Round 7 TC-S1~S3。

**结果**：
- ✅ Claude 成功使用 Agent 工具调度 subagent（前端看到 "subagent" 字样）
- ❌ Trace 面板未渲染——原因见 v1.2.3

---

## v1.2.3 Hotfix — 修复 Subagent 内部消息覆盖 last_tool_name

### 问题描述

v1.2.2 后 subagent 确认被调度（前端出现 "subagent" 字样），但 Trace 面板不渲染。

### 根本原因

通过 `[debug]` 日志发现：SDK 在 Agent 工具执行期间会**流式输出 subagent 内部的所有工具调用**（Bash、Read、ToolSearch 等），这些内部消息带有 `parent_tool_use_id`。

消息流：
```
AssistantMessage: ToolUseBlock(Agent)     ← 设 last_tool_name="Agent" ✅
  UserMessage: parent_tool_use_id=toolu_018z... ← subagent 内部
  AssistantMessage: ToolUseBlock(Bash)           ← 覆盖 last_tool_name="Bash" ❌
  UserMessage: parent_tool_use_id=toolu_018z... ← subagent 内部
  AssistantMessage: ToolUseBlock(Read)           ← 覆盖 last_tool_name="Read" ❌
  ... (更多 subagent 内部工具调用)
UserMessage: tool_use_result=True, parent_tool_use_id=None ← Agent 最终结果
  → 此时 last_tool_name="Bash"，Agent 分支被跳过 ❌
```

### 修改方案

在消息循环中增加 `in_subagent` 状态追踪：

1. 当检测到 `ToolUseBlock(Agent)` 时，设 `in_subagent = True`
2. `in_subagent=True` 期间，跳过所有 `AssistantMessage` 和带 `parent_tool_use_id` 的 `UserMessage`
3. 当收到 `UserMessage(tool_use_result=True, parent_tool_use_id=None)` 时，重置 `in_subagent = False`，正常处理 Agent 结果

### 变更文件

| 文件 | 变更 |
|------|------|
| `web/server.py` SDK 消息循环 | 增加 `in_subagent` 状态，跳过 subagent 内部消息 |

### 验证

v1.2.3 未单独测试——v1.2.2 重测时 Claude 根本没用 Agent 工具，直接 curl 了 `/api/kb_search`，v1.2.3 的消息过滤逻辑未被触发。原因见 v1.2.4。

---

## v1.2.4 Hotfix — 阻断 `/api/kb_search` 端点强制走 Agent 工具

### 问题描述

v1.2.2 + v1.2.3 修复后重启测试，Claude 又回退到用 Bash curl 直接查 `/api/kb_search` 端点，完全不用 Agent 工具。后台日志全部是 `ToolUse Bash: curl -s "http://127.0.0.1:8000/api/kb_search?..."`, 零条 `[subagent]` 记录。

### 根本原因

Prompt 层的 "不要 curl" 指令不够可靠——Claude 从 save_lead 的 curl 模式中推断出 `/api/kb_search` 端点的存在（或从 resumed session 历史中看到过），选择了更简单的直接 curl 路径。**Prompt 约束无法可靠地阻止工具层面的能力。**

### 修改方案

**物理阻断**：在 SDK 模式下，`/api/kb_search` 端点返回错误消息，不再返回搜索结果。

```python
@app.get("/api/kb_search")
async def api_kb_search(...):
    if DEMO_BACKEND == "sdk":
        return {
            "error": "BLOCKED: Direct KB search is disabled. "
            "You MUST use the Agent tool to dispatch to product-query or region-query subagent."
        }
    # ... API 模式正常返回
```

这样即使 Claude 尝试 curl，也只会得到错误提示，被迫转向 Agent 工具。

Subagent 不受影响——它们使用 `uv run kb_search.py`（Python 脚本直接调用），不走 HTTP 端点。

### 变更文件（阻断部分）

| 文件 | 变更 |
|------|------|
| `web/server.py` `/api/kb_search` 端点 | SDK 模式返回 BLOCKED 错误 |

---

## v1.2.5 Hotfix — Glossary Fast-Track 不生效（四层阻断问题）

### 问题描述

v1.2.4 实现了 Glossary 集成（Phase 1~3），`route_query.py` 命令行测试中 `is_glossary_only=true` 正确返回 DID 定义。但在 Web Demo 中测试 "What is toll free number?"，agent 完全忽略 route_query.py，**仍然走 subagent + KB 搜索**，耗时 100s+。

### 根本原因（四层）

问题不是单一的——是**四层阻断叠加**，每一层都独立阻止了 Glossary Fast-Track 的触发：

| 层 | 位置 | 问题 | 影响 |
|----|------|------|------|
| **① 文件未同步** | `.autoservice/.claude/` 目录 | `route_query.py`、`glossary.json`、`synonym-map.json` 只存在于开发目录 `.claude/`，运行时目录 `.autoservice/.claude/` 缺失这三个文件。`SKILL.md` 也是旧版本（667 行 vs 693 行），没有 Glossary Fast-Track 章节 | agent 运行时找不到 route_query.py，也没有 Fast-Track 指令可遵循 |
| **② SKILL.md 语气不足** | SKILL.md 第 94 行 | `"You can optionally run the keyword router"` — 标记为可选；第 325 行 `"After running route_query.py (or determining the route from context)"` — 允许从上下文判断路由 | 即使文件同步了，agent 也可以合理地选择跳过 route_query.py |
| **③ WEB_KB_OVERRIDE 禁用** | `web/server.py` 第 431 行 | `"ALL uv run and curl commands for KB search are DISABLED"` — route_query.py 使用 `uv run` 执行，被此条指令一并禁用 | agent 被明确告知不能用 `uv run`，包括 route_query.py |
| **④ SALES_RUNTIME_BASE 覆盖** | `web/server.py` 第 474-478 行 | `"For ANY product/feature/pricing question, search the KB via HTTP: curl kb_search"` — 直接指示 agent 用 curl 搜 KB，完全绕过 SKILL.md 的路由流程 | 即使前三层都修好，这条指令仍会覆盖 SKILL.md 中的 route_query.py 调用 |

此外：`_skill_text` 在 `web/server.py` 第 419 行模块加载时一次性读取并缓存——即使修改了 SKILL.md 文件，不重启 server 也不会生效。

### 为什么之前没发现

v1.2.2 解决的是 "subagent 不被调度" 的问题（pre-fetch KB 注入 + fallback 路径），修复后 subagent 确实被调度了。但 Glossary Fast-Track 是 v1.2.4 新增的功能，它需要 route_query.py **在 subagent 调度之前**被调用——这个前置步骤被上述四层分别阻断。

### 修改方案

#### 变更 A — 同步开发目录到运行时目录

```bash
cp .claude/skills/cinnox-demo/scripts/route_query.py \
   .autoservice/.claude/skills/cinnox-demo/scripts/
cp .claude/skills/cinnox-demo/references/glossary.json \
   .claude/skills/cinnox-demo/references/synonym-map.json \
   .autoservice/.claude/skills/cinnox-demo/references/
cp .claude/skills/cinnox-demo/SKILL.md \
   .autoservice/.claude/skills/cinnox-demo/SKILL.md
```

#### 变更 B — SKILL.md 强制 route_query.py

```diff
- You can optionally run the keyword router for a suggestion:
+ **MANDATORY**: You MUST run the keyword router before ANY product/pricing response:

- uv run .claude/skills/cinnox-demo/scripts/route_query.py --query "..."
+ uv run .autoservice/.claude/skills/cinnox-demo/scripts/route_query.py --query "..."

- **You always have the final say** — override the suggestion if conversation context
-  makes the correct routing obvious.
+ **You MUST follow the router output** — especially `is_glossary_only` and
+  `expanded_query`. Do NOT skip this step or determine routing from context alone.

- After running `route_query.py` (or determining the route from context), select the
-  subagent team:
+ **MANDATORY**: After running `route_query.py`, select the subagent team based on its
+  output. Do NOT skip `route_query.py` or determine routing from context alone:
```

#### 变更 C — `_WEB_KB_OVERRIDE` 新增 route_query.py 为必须首步

将 route_query.py 作为 WEB MODE 的第一条指令，排在 "KB Search DISABLED" 之前，明确它是例外：

```python
### Route Query — MANDATORY FIRST STEP
Before ANY product/pricing/terminology response, you MUST run route_query.py:
uv run .autoservice/.claude/skills/cinnox-demo/scripts/route_query.py --query "..."
Read the JSON output and follow the routing decision:
- If is_glossary_only=true → use Glossary Fast-Track (skip subagents)
- If is_glossary_only=false → dispatch to subagents using expanded_query
```

#### 变更 D — `_SALES_RUNTIME_BASE` 删除 curl KB 指令

```diff
- For ANY product/feature/pricing question, search the KB via HTTP (fast, no subprocess):
-     curl -s "http://127.0.0.1:{server_port}/api/kb_search?query=YOUR+QUERY&top_k=3"
-   Returns JSON array [{source_name, section, content}]. Cite ONLY from these results.
-   If empty → say you don't have that info and offer to connect with a specialist.
-   DO NOT use uv run kb_search.py — use the HTTP endpoint above.
+ For ANY product/feature/pricing question: FIRST run route_query.py (see WEB MODE
+  overrides above), THEN follow the routing decision (Glossary Fast-Track or subagent).
```

### 变更文件

| 文件 | 变更 |
|------|------|
| `.autoservice/.claude/skills/cinnox-demo/scripts/route_query.py` | 从 `.claude/` 复制（新增） |
| `.autoservice/.claude/skills/cinnox-demo/references/glossary.json` | 从 `.claude/` 复制（新增） |
| `.autoservice/.claude/skills/cinnox-demo/references/synonym-map.json` | 从 `.claude/` 复制（新增） |
| `.autoservice/.claude/skills/cinnox-demo/SKILL.md` | 从 `.claude/` 覆盖 + "MANDATORY" 强化 |
| `.claude/skills/cinnox-demo/SKILL.md` | "MANDATORY" 强化（同步） |
| `web/server.py` `_WEB_KB_OVERRIDE` | 新增 route_query.py 为首步 |
| `web/server.py` `_SALES_RUNTIME_BASE` | 删除 curl KB 指令，改为 route_query.py 优先 |

### 验证

重启 Web UI，开全新 session，测试 "What is toll free number?"。

**结果**：✅ agent 先调用 `route_query.py`，识别 `is_glossary_only=true`，直接从 glossary 返回定义，未调用 subagent。响应时间从 100s+ 降至约 15s。

### 反思：如何做得更好

**1. 开发/运行时目录同步机制**

当前 `.claude/`（开发）和 `.autoservice/.claude/`（运行时）是两套独立文件。任何 skill 修改都需要手动同步，容易遗漏。

改进方案：
- **短期**：新增 `scripts/sync_skills.sh`，一键同步开发目录到运行时目录
- **中期**：让 `web/server.py` 的 `SKILL_MD` 直接指向 `.autoservice/.claude/`，消除路径歧义
- **长期**：合并两个目录，或通过符号链接关联

**2. Server 应在服务端调用 route_query.py**

当前方案依赖 agent 自觉调用 route_query.py（Prompt 约束），这在 v1.2.1~v1.2.4 的经验中反复证明不可靠。

改进方案：将 route_query.py 的调用从 "agent prompt 指令" 改为 "server 端预处理"（类似已删除的 `_presearch_kb()`），在用户消息到达 agent 之前就完成路由判断，将结果注入到 system prompt 或用户消息中。这样 agent 无需自己调用脚本，只需读取已有的路由结果。

```python
# web/server.py — 未来改进方向
routing = _run_route_query(user_text)  # server 端调用 route_query.py
if routing.get("is_glossary_only"):
    # 直接注入 glossary 定义，agent 只需格式化输出
    augmented = f"{user_text}\n\n---\n📖 Glossary Fast-Track:\n{routing['glossary_definition']}\n---"
else:
    augmented = f"{user_text}\n\n---\n🔍 Route: {json.dumps(routing)}\n---"
```

**3. Prompt 指令层级管理**

当前 system prompt 由 `_WEB_KB_OVERRIDE` + `_PERSONA_PREFIX` + `_skill_text` + `_SALES_RUNTIME_BASE` 四段拼接，存在指令冲突时 agent 无法判断优先级。

改进方案：
- 建立明确的指令优先级（WEB MODE overrides > SKILL.md workflow > RUNTIME context）
- 减少重复和冲突的指令
- 定期审查拼接后的完整 prompt，检查是否存在矛盾

---

### Glossary 深度集成计划

#### 背景

当前两个核心问题：
1. **检索慢**：subagent 启动开销 + FTS5 冷查询耗时
2. **准确性一般**：用户用口语词（如 "group call"），KB 中是官方术语（如 "Broadcast Call Enquiry"），FTS5 匹配不上

`docs/resource/CINNOX Glossary.csv` 有 ~355 个官方术语 + 描述 + 关联词，目前完全未使用。通过 Glossary 深度集成，可同时改善速度和准确性。

#### 架构总览

```
CSV → build_glossary.py → glossary.json + synonym-map.json
                                ↓
客户提问 → route_query.py (term expand) → subagent (精准 FTS5)
              ↓ (纯术语问题)
         直接返回 glossary 定义，跳过 subagent
```

#### Phase 1：Glossary 预处理管线

**新建脚本**：`.autoservice/.claude/skills/knowledge-base/scripts/build_glossary.py`

**输入**：`docs/resource/CINNOX Glossary.csv`（355 条）

**输出**（存放 `.autoservice/.claude/skills/cinnox-demo/references/`）：

| 文件 | 结构 | 用途 |
|------|------|------|
| `glossary.json` | `{ "DID": { "description": "...", "related": ["VN", "IDD"] }, ... }` | 术语快速查找 + reviewer 校验 |
| `synonym-map.json` | `{ "group call": "Broadcast Call Enquiry", "noise cancel": "Noise Reduction", ... }` | route_query.py 查询扩展 |

**synonym-map 生成逻辑**：
1. 从 CSV 的 `Related Glossary` 列提取交叉引用关系
2. 从 `Description` 中提取 "See: XXX"、"Also known as: XXX" 模式
3. 常见缩写映射（如 `2FA` → `Two-Factor Authentication`）
4. **人工可编辑**：生成后可手动补充口语映射

**执行时机**：KB 构建时（`/knowledge-base build`）顺带执行，或独立 `uv run build_glossary.py`

#### Phase 2：route_query.py 查询扩展

**改动**：`.autoservice/.claude/skills/cinnox-demo/scripts/route_query.py`

当前输出：
```json
{ "domain": "contact_center", "region": null, "role": "product", "confidence": 0.8 }
```

新增输出字段：
```json
{
  "domain": "contact_center",
  "region": null,
  "role": "product",
  "confidence": 0.85,
  "expanded_query": "Broadcast Call Enquiry pricing",
  "matched_terms": [{"original": "group call", "official": "Broadcast Call Enquiry"}],
  "is_glossary_only": false
}
```

**新增逻辑**（在现有路由判断之后）：
1. **加载** `synonym-map.json`（启动时加载一次，缓存在内存）
2. **扫描用户 query**：对每个 synonym key 做子串匹配，命中则替换为官方术语
3. **输出 `expanded_query`**：替换后的查询字符串，传给 subagent 作为搜索词
4. **输出 `matched_terms`**：记录哪些词被替换了，供 auditor 追踪
5. **判断 `is_glossary_only`**：纯术语定义类问题（"什么是 DID？"、"What is 1:1 Call?"）标记为 `true`
6. **domain confidence 提升**：用 glossary 术语做二次分类，匹配 domain 高频词时 confidence 加分

**核心链路**：
```
客户说 "group call"
  → synonym-map 映射为 "Broadcast Call Enquiry"
  → subagent 用官方术语查 FTS5
  → 精确命中 KB chunk
```

#### Phase 3：术语快速通道

**改动**：`.autoservice/.claude/skills/cinnox-demo/SKILL.md`

当 `route_query.py` 返回 `is_glossary_only: true` 时：
- 主 agent 直接读 `glossary.json` 取定义
- 可选经 copywriting 润色
- 返回回复，**跳过 product-query / region-query subagent**

**触发条件**（`is_glossary_only` 判定逻辑）：
- 问题匹配 "什么是X"、"What is X"、"X是什么意思"、"define X" 等模式
- X 在 `glossary.json` 中存在精确匹配
- 问题不涉及定价、对比、使用方法等复杂意图

**回复示例**：
> **DID (Direct Inward Dialling)**: A virtual phone number that allows customers to receive calls...
>
> Would you like to know more about DID pricing or availability in your region?

**好处**：完全跳过 subagent 启动 + FTS5 查询，术语定义来自官方 glossary 准确性 100%，追问引导用户进入产品问答流程。

#### Phase 4：Copywriting 术语纠正

**改动**：`.claude/agents/copywriting.md`

在现有 BANNED PHRASES 检查之后，新增 **Terminology Correction** 步骤：
1. 加载 `synonym-map.json`（反向使用——检查回复中是否出现非官方术语）
2. 扫描草稿回复，synonym key（口语词）替换为官方术语
3. 输出中标记替换项，供审计追踪

**示例**：
```
草稿: "CINNOX supports group call for up to 100 participants"
纠正: "CINNOX supports Broadcast Call Enquiry for up to 100 participants"
标记: [{"original": "group call", "corrected": "Broadcast Call Enquiry"}]
```

不改变句意，只替换术语。不处理 glossary 中没有的词。

#### Phase 5：Reviewer 第 12 项检查

**改动**：`.claude/agents/reviewer.md`

现有 11 项检查清单新增：

| # | 检查项 | 严重级别 |
|---|--------|---------|
| 12 | 术语准确性：回复中的产品术语是否使用官方 CINNOX 术语（对照 glossary.json） | minor |

`minor` 级别：不阻断回复，但记录到 reviewer 输出和 auditor 日志。copywriting 阶段应已纠正大部分，reviewer 是兜底。

#### 变更文件清单

| 文件 | 变更类型 | 阶段 |
|------|---------|------|
| `.autoservice/.claude/skills/knowledge-base/scripts/build_glossary.py` | 新建 | Phase 1 |
| `.autoservice/.claude/skills/cinnox-demo/references/glossary.json` | 新建（生成） | Phase 1 |
| `.autoservice/.claude/skills/cinnox-demo/references/synonym-map.json` | 新建（生成） | Phase 1 |
| `.autoservice/.claude/skills/cinnox-demo/scripts/route_query.py` | 修改 | Phase 2 |
| `.autoservice/.claude/skills/cinnox-demo/SKILL.md` | 修改（新增快速通道分支） | Phase 3 |
| `.claude/agents/copywriting.md` | 修改 | Phase 4 |
| `.claude/agents/reviewer.md` | 修改 | Phase 5 |

#### 验证计划

| 测试 | 预期结果 |
|------|---------|
| `build_glossary.py` 生成 JSON | glossary.json ≥ 350 条，synonym-map.json ≥ 30 条映射 |
| "What is DID?" | `is_glossary_only=true`，跳过 subagent，直接返回定义 |
| "group call pricing" | `expanded_query` 包含 "Broadcast Call Enquiry"，FTS5 命中 |
| 回复包含 "noise cancel" | copywriting 纠正为 "Noise Reduction" |
| reviewer 检测 | 第 12 项标记未纠正的非官方术语 |
| Round 7 TC 回归 | 通过率 > v1.2.3 |

---

## v1.2.6 Hotfix — 输入框冻结 bug（WebSocket 断连恢复）

### 问题描述

subagent 调用完成并回答客户问题后，session 未结束，但输入框不可点击/无法发送消息。终端日志显示 `connection closed` 紧随 `turn done` 之后。

### 根本原因

**双层问题叠加**：

| 层 | 位置 | 问题 | 影响 |
|----|------|------|------|
| **① WebSocket 静默超时** | `web/server.py` SDK 消息循环 | subagent 执行期间（81s+），`in_subagent=True` 跳过内部消息，不向前端发送任何数据。WebSocket 因长时间无数据被断开 | 服务端的 `done` 消息无法送达客户端 |
| **② 前端状态未重置** | `web/static/cinnox.html` | `waitingReply` 仅在 `done` handler 中重置为 `false`。连接断开后前端自动重连，收到 `ready` 消息后调用 `enableInput(true)`（输入框可见可输入），但 `send()` 函数检查 `waitingReply` 仍为 `true`，静默拒绝发送 | 输入框看起来可用，但发送按钮/回车无效 |

### 修改方案

#### 变更 A — 前端：重连时重置状态

在 `ready` 和 `session_resumed` handler 中重置 `waitingReply = false` 和清理 typing indicator：

```javascript
// ready handler
removeTyping();
waitingReply = false;
enableInput(true);

// session_resumed handler
waitingReply = false;
enableInput(true);
```

新增 `heartbeat` case 处理服务端 keepalive 消息（忽略即可）。

#### 变更 B — 服务端：subagent 期间发送 heartbeat

在 SDK 消息循环中追踪 `last_ws_send_t`，当 `in_subagent=True` 且超过 15s 未向前端发送任何数据时，发送 `{"type": "heartbeat"}` 保持连接存活：

```python
if in_subagent and (now_t - last_ws_send_t) > 15:
    await websocket.send_json({"type": "heartbeat"})
    last_ws_send_t = now_t
```

### 变更文件

| 文件 | 变更 |
|------|------|
| `web/static/cinnox.html` 'ready' handler | 新增 `removeTyping()` + `waitingReply = false` |
| `web/static/cinnox.html` 'session_resumed' handler | 新增 `waitingReply = false` |
| `web/static/cinnox.html` handleMsg switch | 新增 `heartbeat` case |
| `web/server.py` SDK 消息循环 | 新增 `last_ws_send_t` 追踪 + 15s heartbeat + `subagent_start` 后更新时间戳 |

---

## v1.2.7 — 国家/地区名模糊匹配修复 + 专有名词澄清机制

### 问题描述

**来源 1**：Round 8 测试 session `session_20260312_164702.json`

用户问 "How much does DID cost in the US?"，bot 回复 "I don't have specific US DID pricing in our documentation"。但 xlsx 数据源 `M800 VN, Call and SMS Rates.xlsx` 第 218 行明确包含 **United States** 的完整 DID 定价（MRC $19, 各项通话/SMS 费率齐全）。

**来源 2**：Round 8 测试 session `session_20260313_090316.json`

用户先问 "I want to know if you support DID in America"（bot 正确识别 US、询问 toll-free 还是 local），用户回复 "local DID"，bot 回答 "CINNOX does support local DID numbers in the US" 但接着说 "I don't have the specific US local DID pricing in the materials I have access to"。

**两个 session 的根本原因相同**：FTS5 搜索丢失国家信息，KB 中明确存在的 United States DID 数据（MRC=$19）未被检索到。

### 根本原因分析

**三层问题叠加**：

| 层 | 位置 | 问题 | 影响 |
|----|------|------|------|
| **① FTS5 丢弃短词** | `kb_search.py:build_fts_query()` L62 | 单词 < 3 字符被丢弃。"US" 只有 2 个字符，被直接忽略 | 查询 "US DID pricing" → FTS 表达式 `"DID" OR "pricing"`，完全不含国家信息。返回所有国家的 DID 结果，未命中 United States |
| **② route_query 检测但未传递** | `route_query.py` L206-219 | `route()` 正确检测 region=US，但这个信息仅用于路由决策（选 region-query subagent）。subagent 的搜索查询中没有把 "US" 展开为 "United States" | region-query subagent 拿到的 query 仍然是 "US DID pricing"，FTS5 仍然丢弃 "US" |
| **③ synonym-map 无国家映射** | `synonym-map.json` | 只有电信术语映射（did→DID, virtual number→VN 等），没有国家别名映射（US→United States, UK→United Kingdom 等） | `_expand_query()` 不会把 "US" 展开为 "United States"，即使路由正确也无法提升 FTS5 搜索质量 |

**完整链路复盘**：
```
用户: "How much does DID cost in the US?"
  → route_query.py: region=US, domain=global_telecom ✅ (正确检测)
  → region-query subagent 接收: query="How much does DID cost in the US?"
  → kb_search.py: build_fts_query("How much does DID cost in the US?")
    → tokens: ["How", "much", "does", "DID", "cost", "in", "the", "US?"]
    → 过滤 < 3 字符: 丢弃 "in", "US" (清理标点后)
    → FTS 表达式: "How" OR "much" OR "does" OR "DID" OR "cost" OR "the"
    → 结果: 返回包含 "DID" 和 "cost" 的泛化结果，不一定含 United States
  → bot: "I don't have specific US DID pricing" ❌
```

**session_20260313_090316 链路复盘**（多轮对话场景）：
```
用户第1轮: "I want to know if you support DID in America"
  → route_query: region=US, ambiguous=True (需要确认 toll-free 还是 local)
  → bot 正确回应: "Are you looking for toll-free or local DID numbers?"

用户第3轮: "local DID"
  → route_query("local DID"): region=None, expanded="local DID (Direct Inward Dialing)"
     ⚠️ 上下文中的 "US" 信息不在当前 query 里，route_query 无法检测
  → bot 从对话历史知道是 US，构造搜索: "US local DID pricing"
  → FTS5: build_fts_query("US local DID pricing")
    → "US" 被丢弃 (< 3 字符)
    → FTS 表达式: "local" OR "DID" OR "pricing"
    → 返回 Benin ($89)、Tajikistan ($59) 等泛化结果
    → United States ($19) 未出现在 top-k 中
  → bot: "I don't have the specific US local DID pricing" ❌
```

**关键洞察**：即使 bot 从对话上下文正确知道用户问的是 US，但搜索链路中 "US" 无法被 FTS5 使用，需要在搜索前扩展为 "United States"。

### 相关问题：国家/地区名模糊匹配

除了 "US" 问题，还存在更广泛的国家名歧义问题：

#### 问题 A：substring 匹配导致错误路由

`route_query.py` 对 > 3 字符的别名使用 substring 匹配（L214-215: `if alias in q`），会导致：

| 用户输入 | alias 匹配 | 路由结果 | 正确结果 |
|---------|-----------|---------|---------|
| "American Samoa rates" | "america" in "american samoa" | region=US ❌ | 应为 American Samoa（不在 REGION_MAP 中） |
| "American DID" (泛指) | "america" in "american" | region=US ✅ | 需要澄清：指 US 还是 American Samoa？ |

#### 问题 B：xlsx 中存在大量歧义国名

从 xlsx 232 个国家/地区中发现的 substring 重叠对：

| 短名 | 长名 | 搜索风险 |
|------|------|---------|
| Congo | Democratic Republic of the Congo | FTS 搜 "Congo" 可能返回任一 |
| Dominica | Dominican Rep | FTS 搜 "Dominican" 可能混淆 |
| Guinea | Equatorial Guinea / Guinea Bissau / Papua New Guinea | 4 个国家共享 "Guinea" |
| Niger | Nigeria | FTS 搜 "Niger" 会同时命中 Nigeria |
| Sudan | South Sudan | FTS 搜 "Sudan" 会同时命中 |
| Netherlands | Netherlands Antilles | FTS 搜 "Netherlands" 会同时命中 |
| United States | United States (Alaska) / United States (Hawaii) | 变体问题 |
| Vietnam | Vietnam (120/121/122 网络变体) | 变体问题 |

#### 问题 C：REGION_MAP 覆盖不全

xlsx 含 232 个国家/地区，REGION_MAP 只覆盖 17 个。用户问 "UAE DID pricing" 时 region=None，触发 "Which country are you asking about?" 澄清——但用户已经说了国家，体验差。

#### 问题 D：专有名词模糊检索需澄清（用户明确要求）

当用户使用的国家/地区名或产品名词可能匹配多个实体时，**必须主动向客户确认（clarify）**而非猜测。这是硬性要求：
- "America" / "American" → **必须先确认**是 United States 还是 American Samoa
- "Guinea" → 可能指 Guinea、Equatorial Guinea、Guinea Bissau、Papua New Guinea
- "Congo" → 可能指 Congo 或 Democratic Republic of the Congo
- "Netherlands" → 可能指 Netherlands 或 Netherlands Antilles
- 其他存在歧义的国家/地区名同理

### 修改方案

#### 变更 1 — `route_query.py` 新增国家名扩展映射 `COUNTRY_ALIAS_MAP`

新增完整的国家别名映射表，将常见别名/缩写映射到 xlsx 中使用的**精确国名**：

```python
COUNTRY_ALIAS_MAP: dict[str, str] = {
    # 短缩写 → xlsx 精确国名
    "us": "United States",
    "usa": "United States",
    "uk": "United Kingdom",
    "uae": "United Arab Emirates",
    "hk": "Hong Kong",
    "sg": "Singapore",
    # 常见别名 → xlsx 精确国名
    "america": "United States",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",     # 技术上不精确但用户常用
    "south korea": "Korea South",    # 或 xlsx 中的实际名称
    "mainland china": "China",
    "deutschland": "Germany",
    # ... 其他高频别名
}
```

在 `_expand_query()` 中增加国家名扩展逻辑：当检测到 `COUNTRY_ALIAS_MAP` 中的 key 时，在查询中**追加**（非替换）对应的 xlsx 精确国名，确保 FTS5 能用精确国名命中数据。

```python
def _expand_query(query: str) -> tuple[str, list[dict]]:
    # ... 现有 synonym-map 扩展 ...

    # 国家名扩展：追加 xlsx 精确国名
    q_lower = expanded.lower()
    for alias, full_name in sorted(COUNTRY_ALIAS_MAP.items(), key=lambda x: -len(x[0])):
        if len(alias) <= 3:
            if re.search(rf"\b{re.escape(alias)}\b", q_lower):
                expanded += f" {full_name}"
                matched_terms.append({"original": alias, "official": full_name})
                break  # 只匹配第一个国家
        else:
            if alias in q_lower:
                expanded += f" {full_name}"
                matched_terms.append({"original": alias, "official": full_name})
                break

    return expanded, matched_terms
```

**效果**：
```
"US DID pricing" → expanded_query = "US DID pricing United States"
  → FTS: "DID" OR "pricing" OR "United States"  ← 精确命中 xlsx
```

#### 变更 2 — `kb_search.py` 保留短缩写

修改 `build_fts_query()` 的短词过滤逻辑：保留全大写的 2 字符缩写（如 US, UK, HK, SG），因为它们通常是有意义的国家/地区代码：

```python
# 现在: 丢弃 < 3 字符
if len(tokens[i]) >= 3:
    terms.append(f'"{tokens[i]}"')

# 改为: 保留全大写 2 字符词（国家/地区代码）
if len(tokens[i]) >= 3 or (len(tokens[i]) == 2 and tokens[i].isupper()):
    terms.append(f'"{tokens[i]}"')
```

**效果**：
```
"US DID pricing" → FTS: "US" OR "DID" OR "pricing"  (US 不再被丢弃)
```

注意：这是辅助措施。FTS5 用 "US" 搜索可能命中 "US Virgin Islands" 等包含 "US" 的条目，所以变更 1 的精确国名扩展仍然是主要修复手段。

#### 变更 3 — `route_query.py` 修复 substring 匹配精度

将长别名的 substring 匹配改为**词边界匹配**，避免 "america" 匹配 "american"：

```python
# 现在: substring 匹配
if alias in q:
    detected_region = code

# 改为: 词边界匹配（所有长度的 alias 统一用 word boundary）
if re.search(rf"\b{re.escape(alias)}\b", q):
    detected_region = code
```

**效果**：
```
"American Samoa rates" → "america" 不再匹配 "american"
  → region=None → 进入未知国家处理流程
```

#### 变更 4 — 歧义国名检测 + 主动澄清

在 `route_query.py` 中新增 `AMBIGUOUS_COUNTRIES` 表，当检测到可能匹配多个国家时返回 `ambiguous=true` + `clarify_message`：

```python
AMBIGUOUS_COUNTRIES: dict[str, list[str]] = {
    "guinea": ["Guinea", "Equatorial Guinea", "Guinea Bissau", "Papua New Guinea"],
    "congo": ["Congo", "Democratic Republic of the Congo"],
    "sudan": ["Sudan", "South Sudan"],
    "niger": ["Niger", "Nigeria"],
    "dominica": ["Dominica", "Dominican Rep"],
    "netherlands": ["Netherlands", "Netherlands Antilles"],
    "samoa": ["Samoa", "American Samoa"],
    "america": ["United States", "American Samoa"],
    "korea": ["Korea South", "Korea North"],  # 如果 xlsx 中有
    "vietnam": ["Vietnam", "Vietnam (120 - VNPT network)", "Vietnam (121 - Mobifone network)", "Vietnam (122 - Viettel network)"],
}
```

在路由逻辑中，当检测到的国家关键词在 `AMBIGUOUS_COUNTRIES` 中时：
- 设置 `ambiguous=true`
- 生成 `clarify_message`: "Did you mean X, Y, or Z?"
- **不进行 KB 搜索**，先向客户确认

**效果**：
```
用户: "Guinea DID rates"
→ ambiguous=true
→ clarify_message: "Could you clarify which country you mean? We have rates for Guinea, Equatorial Guinea, Guinea Bissau, and Papua New Guinea."
```

#### 变更 5 — region-query subagent 使用 expanded_query

修改 `.claude/agents/region-query.md`，在搜索指令中明确要求使用 `expanded_query`（如果有的话）而非原始 query：

```markdown
## Execution

1. If route_query has returned an `expanded_query`, use that as the search query.
2. Include the FULL country name (from route_query output) in the search query.
   - Example: if region=US → include "United States" in query
   - Example: if region=UK → include "United Kingdom" in query
3. Run the KB search:
```

同时修改 SKILL.md 中调度 region-query 时传递 `expanded_query`。

### 变更文件清单

| 文件 | 变更 | 优先级 |
|------|------|--------|
| `.autoservice/.claude/skills/cinnox-demo/scripts/route_query.py` | 新增 `COUNTRY_ALIAS_MAP` + `AMBIGUOUS_COUNTRIES` + 修复 substring 匹配 | P0 |
| `.autoservice/.claude/skills/knowledge-base/scripts/kb_search.py` | `build_fts_query()` 保留 2 字符大写缩写 | P0 |
| `.claude/agents/region-query.md` | 使用 expanded_query + 精确国名搜索 | P1 |
| `.autoservice/.claude/skills/cinnox-demo/SKILL.md` | 传递 expanded_query 给 subagent | P1 |
| `.claude/skills/cinnox-demo/scripts/route_query.py` | 同步变更（开发目录） | P1 |
| `.claude/skills/knowledge-base/scripts/kb_search.py` | 同步变更（开发目录） | P1 |

### 验证计划

| 测试 | 预期结果 |
|------|---------|
| "US DID pricing" | expanded_query 含 "United States"，返回 US DID MRC=$19 |
| "How much does DID cost in the US?" | 同上 |
| "UK toll-free rates" | expanded_query 含 "United Kingdom"，返回 UK 数据 |
| "American Samoa rates" | "america" 不误匹配，正确返回 American Samoa 数据 |
| "American DID" | ambiguous=true，提示 "United States or American Samoa?" |
| "Guinea SMS rates" | ambiguous=true，列出 4 个 Guinea 选项 |
| "Congo DID" | ambiguous=true，列出 2 个 Congo 选项 |
| "UAE DID pricing" | COUNTRY_ALIAS_MAP 扩展为 "United Arab Emirates"，返回 UAE 数据 |
| "DID rates in France" | region=FR，正常工作（回归测试） |
| Round 8 TC 全量回归 | 通过率 ≥ v1.2.6 |

### 已验证 ✅

v1.2.7 所有变更（FTS5 短词保留、COUNTRY_ALIAS_MAP 国名扩展、AMBIGUOUS_COUNTRIES 歧义国名澄清、词边界匹配、DID=local 自动识别、region-query 两步搜索策略、escalation 正则收紧）均已通过测试验证。

---

## v1.2.8 — Lead 确认流程修复（all-at-once shortcut）

### 问题描述

**来源**：session `session_20260313_134247.json`

用户在一条消息中同时提供了全部 4 个字段（姓名、公司、邮箱、电话）以及产品问题（"I want to know French number rates"），bot 在确认信息后**未等待用户确认**就直接保存 lead 并回答了产品问题。

**期望行为**：即使用户一次性提供所有信息，bot 也必须先确认 → 等待用户回复 "yes" → 才能保存和回答。

### 根本原因

SKILL.md 中已有 "confirm before saving" 和 "If 'yes' → run save_lead.py" 的规则，但没有针对 "all-at-once" 场景的显式约束。当用户在同一消息中提供所有信息 + 问题时，Claude 倾向于一次性完成所有操作（确认 + 保存 + 回答），因为没有明确的 "STOP" 指令。

### 修改方案

在 SKILL.md 的 New Customer Flow 中，"After all 4 fields collected → confirm before saving" 之前新增一段强制规则：

```markdown
**CRITICAL — All-at-once shortcut**: If the customer provides all 4 fields (and optionally a question) in a single message, you MUST still confirm their details and **STOP**. Do NOT save lead info, do NOT answer their question, do NOT run save_lead.py in the same response as the confirmation question. Your response must end with the confirmation question. Wait for their next message before proceeding.
```

### 变更文件

| 文件 | 变更 |
|------|------|
| `.autoservice/.claude/skills/cinnox-demo/SKILL.md` | New Customer Flow 新增 CRITICAL all-at-once 规则 |
| `.claude/skills/cinnox-demo/SKILL.md` | 同步变更 |

### 已验证 ✅

用户确认修复后 bot 正确等待确认再继续。
