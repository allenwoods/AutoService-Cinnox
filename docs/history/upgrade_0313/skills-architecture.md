# AutoService Skills Architecture

## 1. 两种"入口"的区分

这个项目有两种完全不同的入口概念，之前的文档混淆了它们：

### Python 程序入口（`uv run python xxx.py`）

这些是独立的 Python CLI 程序，用户在终端直接运行。它们通过 `autoservice/claude.py` 调用 Claude Agent SDK：

| 程序 | 运行方式 | 做什么 | Claude 角色 |
|------|---------|--------|------------|
| `main.py` | `uv run python main.py` | 通用 REPL，纯对话 | 自由（无预设角色） |
| `customer_service.py` | `uv run python customer_service.py` | 客服训练，Claude 扮演客户 | 客户（角色扮演） |
| `marketing.py` | `uv run python marketing.py` | 销售训练，菜单驱动 | 按 SKILL.md 指令执行 |

这三个程序**都不是 Skill**，它们是消费 Skill 的应用。

### Claude Code Skill 入口（`/skill-name` 或自然语言触发）

这些是 Claude Code 内部的 Skill，用户在 Claude Code 会话中触发（比如输入 `/cinnox-demo` 或说"开始 CINNOX 演示"）。

**cinnox-demo 是一个 Skill 入口，不是 Python 程序入口。** 它不需要 `main.py` 来运行——用户直接在 Claude Code 里触发即可。

---

## 2. 业务核心 Skills 的关系

5 个业务 Skill 分成 3 组，它们之间**没有运行时调用关系**，但共享基础设施和设计模式：

```
组 A: 通用业务系统（customer-service + marketing）
  ↓ 共用 _shared/ 脚本
  ↓ 共用数据库模式（products/customers/operators）
  ↓ 共用 Mock API Server 架构

组 B: CINNOX 演示（cinnox-demo + knowledge-base）
  ↓ cinnox-demo 强依赖 knowledge-base（必须先 build KB）
  ↓ cinnox-demo 通过 5+2 个 subagent 运行（v1.2 + v1.3）

组 C: 定价（price-system）
  ↓ 分析组 A 的 Skill 组合来设计定价
  ↓ 输出 .docx 文档（用到 docx skill 的能力）
```

### 组 A 详解：customer-service 和 marketing

这两个是**结构对称**的 Skill，区别在于业务领域：

|  | customer-service | marketing |
|--|-----------------|-----------|
| 场景 | 客服应答 | 销售拓客 |
| 方法论 | service-methodologies.md | spin-selling.md (SPIN) |
| Operator 含义 | 客服策略 | 销售策略 |
| Customer 含义 | 来电客户（有问题） | 潜在客户（有需求） |
| 数据库 | .autoservice/database/customer_service/ | .autoservice/database/marketing/ |
| 共用 | _shared/scripts/ 全部 6 个脚本 | 同左 |

共用的 _shared 脚本提供统一的 CRUD + API Mock 能力：

```
_shared/scripts/
  query_api.py          — 统一 REST 查询
  check_permission.py   — 权限校验
  init_session.py       — 会话初始化
  start_mock_server.py  — 启动 FastAPI Mock Server
  stop_mock_server.py   — 停止 Mock Server
  seed_mock_db.py       — JSON → SQLite 播种

数据流: JSON 文件 → seed_mock_db → SQLite → FastAPI → query_api.py
```

这两个 Skill 有两种使用方式：
1. **通过 Python CLI** — `customer_service.py` / `marketing.py` 直接运行
2. **通过 Claude Code** — `/customer-service` / `/marketing` Skill 触发

两种方式操作同一套数据库，但 Python CLI 版本的流程是硬编码的（选产品→选客户→选策略→开始通话→复盘），而 Skill 版本更灵活（支持 create/read/update/delete/list/call 全部命令）。

### 组 B 详解：cinnox-demo 和 knowledge-base

```
knowledge-base                          cinnox-demo (主 agent)
  kb_ingest.py (构建)                    /cinnox-demo 触发
  kb_search.py (搜索)    <── 调用 ──    ┌──────────────────────────┐
  kb_status.py (状态)    <── 检查 ──    │  Subagent 编排层 (v1.2)   │
      |                                │  ┌─ product-query        │
      v                                │  ├─ region-query         │
  .autoservice/database/               │  ├─ copywriting          │
    knowledge_base/                    │  ├─ reviewer             │
      kb.db (SQLite)                   │  ├─ auditor              │
                                       │  └─ [v1.3] red/blue agent│
                                       └──────────────────────────┘
                                            |
                                            v
                                     save_lead.py (保存潜客)
                                     save_session.py (保存会话)
                                     route_query.py (路由辅助)
                                            |
                                            v
                                     .autoservice/database/
                                       knowledge_base/
                                         leads/
                                         sessions/
```

- knowledge-base 是**数据层** — 负责构建和检索知识库
- cinnox-demo 是**编排层** — 管理客户交互流程 + 动态组队调度 subagent
- subagent 是**执行层** — 各司其职（查询、润色、审查、审计、对抗测试）
- cinnox-demo 不经过 Mock API Server，通过 subagent 调 kb_search.py

### 组 C 详解：price-system

price-system 是一个**独立的分析+输出 Skill**，它的输入是"组 A 的 Skill 组合"：

```
输入:
  - 用户指定要定价的 Skill 组合（如 customer-service + marketing）
  - docs/pricing/ 下的参考定价文档（.docx）
  - WebSearch 获取最新 API 模型成本

输出:
  - docs/pricing/output/ 下的专业 .docx 定价文档
```

它和组 A 的关系是**概念层面的**（分析 Skill 的功能来设计定价），不是代码调用关系。

---

## 3. Subagent 架构

### 3.1 Subagent 总览

cinnox-demo 作为主 agent，调度以下 subagent：

| # | Subagent | 文件 | 职责 | 工具 | model |
|---|----------|------|------|------|-------|
| 1 | product-query | `.claude/agents/product-query.md` | 按产品线查 KB | Bash, Read | sonnet |
| 2 | region-query | `.claude/agents/region-query.md` | 按地区查 KB | Bash, Read | sonnet |
| 3 | copywriting | `.claude/agents/copywriting.md` | 话术优化 + BANNED PHRASES 检查 | 无（纯文本） | sonnet |
| 4 | reviewer | `.claude/agents/reviewer.md` | 11 项合规清单（Self Challenge） | Bash, Read | sonnet |
| 5 | auditor | `.claude/agents/auditor.md` | 审计记录 + 跨会话分析 | Bash, Read, Write, Glob | sonnet |
| 6 | red-agent | `.claude/agents/red-agent.md` | 对抗攻击（v1.3 计划） | 无 | — |
| 7 | blue-agent | `.claude/agents/blue-agent.md` | 辩护防守（v1.3 计划） | 无 | — |

### 3.2 Context 隔离矩阵

| Subagent | 接收 | 不接收 | 隔离目的 |
|----------|------|--------|----------|
| product-query | query + domain | 对话历史、客户 PII | 防止查询偏向 |
| region-query | query + region + number_type | 对话历史 | 防止查询偏向 |
| copywriting | draft + customer_type + sentiment | 对话历史、KB 原始结果 | 防止事实篡改 |
| reviewer | response + 状态摘要 | 完整对话历史、客户 PII | 独立审查 |
| auditor | 匿名编排元数据 | 客户姓名/邮箱/电话 | PII 保护 |
| red-agent (v1.3) | **仅**问题+响应（脱敏） | 所有规则、KB、gate 状态 | **信息不对称是核心机制** |
| blue-agent (v1.3) | Red 的质疑 + 完整 context | — | 有充分信息进行辩护 |

### 3.3 当前 Subagent 上下文管理的问题诊断

#### 问题 1：product-query 和 region-query 缺乏术语规范化能力

**现状**：subagent 收到客户原始问题后直接传给 `kb_search.py`。KB 搜索使用 BM25 全文匹配，严重依赖用户措辞与 KB 文档措辞的重合度。

**问题**：客户使用的词汇和 CINNOX 官方术语经常不一致：

| 客户可能说 | CINNOX 官方术语 | BM25 能匹配吗 |
|-----------|----------------|--------------|
| "group call" | Broadcast Call Enquiry | ❌ 不同词 |
| "phone number for my company" | DID (Direct Inward Dialing) 或 Virtual Number | ❌ 模糊 |
| "auto reply" | Auto-reply messages / Auto-welcome message | ⚠️ 部分匹配 |
| "forward a call" | Call Transfer / Call Forwarding | ⚠️ 部分匹配 |
| "AI chatbot" | CINNOX Bot / CINNOX Q&A Bot / Claire.AI | ❌ 不同名称 |
| "CRM integration" | Zapier / Zaps | ❌ 完全不同 |
| "screen share" | Share Screen | ✅ 基本匹配 |
| "ticket system" | Enquiry Centre | ❌ 完全不同概念 |
| "free number" | TF (Toll Free) numbers / Toll-free Number | ⚠️ "free" 模糊 |
| "IVR menu" | Interactive Voice Response (IVR) / IVR Menu | ✅ 匹配 |
| "routing rules" | Destination Rules / Routing Rules | ✅ 匹配 |
| "smart routing" | Automatic Enquiry Distribution / Sticky Routing | ❌ 不同概念 |
| "voicemail" | Voicemail | ✅ 匹配 |
| "noise cancel" | Noise Reduction | ⚠️ 部分匹配 |

甲方提供的 **CINNOX Glossary**（355 个术语 + 描述 + 关联词）是解决这个问题的权威资源。

**影响**：
- 搜索结果 relevance 偏低（★★☆☆☆ 或以下）
- subagent 触发 retry 后仍然找不到正确内容
- 主 agent 被迫 escalate 到人工（实际上 KB 中有答案，只是搜不到）
- reviewer 无法发现这个问题（它只检查"响应是否符合 KB 结果"，不检查"KB 搜索是否充分"）

#### 问题 2：region-query 缺乏电信术语消歧

**现状**：`route_query.py` 用硬编码关键词列表做路由，覆盖不全。

**问题**：Glossary 中有 50+ 个电信相关术语，当前关键词只覆盖了最基本的：

| 已覆盖 | 未覆盖（Glossary 中存在） |
|--------|--------------------------|
| DID, virtual number, toll-free, local number, rate, call rate, sms rate | PSTN, SIP Trunk, SIP In, IDD Termination, Voice Network services, A2P, Caller ID (CLI), Intermediary Number, Menu Routing Numbers, Answer Seizure Ratio (ASR), Termination fee, Traffic fee, Number Porting, Alphanumeric Sender ID |

客户问 "IDD termination rates" → `route_query.py` 只匹配到 "rate" → 路由到 `global_telecom` 但 confidence 不足 → 触发 ambiguity 提问 → 客户体验差。如果 "IDD termination" 在关键词表中，可以直接高 confidence 路由。

#### 问题 3：copywriting subagent 缺乏 CINNOX 品牌术语意识

**现状**：copywriting 只做长度/语气/banned phrases 检查，不关心产品术语是否正确。

**问题**：主 agent 草稿中可能使用非官方术语（如 "group call" 而不是 "Broadcast Call"），copywriting 不会纠正。如果有 Glossary 引用，copywriting 可以确保客户面对的术语与 CINNOX 官方一致。

#### 问题 4：reviewer 缺乏术语准确性检查维度

**现状**：reviewer 的 11 项清单没有"术语准确性"检查项。

**问题**：bot 可能用错误的术语描述功能（如称 "Enquiry" 为 "Ticket"），技术上不算"幻觉"（功能是真实的），但对 CINNOX 品牌来说是不准确的表述。Glossary 可以作为术语准确性的参照标准。

### 3.4 Glossary 集成方案

#### 方案概述

将 CINNOX Glossary 作为**术语规范层**注入 subagent 工作流，不改变现有 KB 搜索机制，而是在搜索前做术语扩展、搜索后做术语校正：

```
客户问题
    ↓
route_query.py（扩展关键词覆盖）
    ↓
product-query / region-query
    ├── 1. 术语扩展：客户词汇 → Glossary 同义词/官方术语
    ├── 2. KB 搜索（扩展后的 query）
    └── 3. 返回结果
    ↓
主 agent 草稿
    ↓
copywriting（新增术语校正：非官方术语 → 官方术语）
    ↓
reviewer（新增 #12 术语准确性检查）
```

#### 具体变更

**1. Glossary 数据预处理**

新建脚本将 CSV 转为 JSON，生成两类索引：

```
.claude/skills/cinnox-demo/references/glossary.json  — 完整术语表
.claude/skills/cinnox-demo/references/synonym-map.json — 同义词映射
```

`synonym-map.json` 示例：
```json
{
  "group call": ["Broadcast Call Enquiry"],
  "ticket": ["Enquiry"],
  "ticket system": ["Enquiry Centre"],
  "AI chatbot": ["CINNOX Bot", "CINNOX Q&A Bot", "Claire.AI"],
  "free number": ["Toll-free Number", "TF"],
  "phone number": ["DID", "Virtual Number", "Local Number"],
  "forward call": ["Call Transfer", "Call Forwarding"],
  "auto reply": ["Auto-reply messages", "Auto-welcome message"],
  "CRM": ["Zapier"],
  "noise cancel": ["Noise Reduction"],
  "smart routing": ["Automatic Enquiry Distribution", "Routing Rules"],
  "screen share": ["Share Screen"],
  "IDD": ["IDD Termination", "International Direct Dial"]
}
```

**2. product-query.md 修改**

增加 "Query Expansion" 步骤：

```markdown
## Execution

1. **Query Expansion** (NEW): Before searching KB, check if the query contains
   common terms that map to CINNOX official terms. Reference:
   `.claude/skills/cinnox-demo/references/synonym-map.json`

   If a synonym match is found, append the official CINNOX term(s) to the search query.
   Example: "group call features" → search for "group call Broadcast Call Enquiry features"

2. Map the `domain` to the correct `--source-filter`.
3. Run KB search with expanded query.
4. If first search returns ≤ ★★☆☆☆, retry with official CINNOX terms only
   (drop the original colloquial terms).
```

**3. region-query.md 修改**

同样增加 Query Expansion，针对电信术语：

```markdown
## Telecom Term Expansion

Before searching, expand colloquial terms to CINNOX official terms:
- "IDD rates" → add "IDD Termination"
- "SIP pricing" → add "SIP Trunk"
- "phone number" → context-dependent: DID / Virtual Number / Local Number
- "termination fee" → "Termination fee" (already official)
- "A2P SMS" → "A2P (Application to Person)"

Reference: `.claude/skills/cinnox-demo/references/synonym-map.json`
```

**4. route_query.py 扩展**

从 Glossary 自动提取关键词，扩充 `DOMAIN_KEYWORDS` 和 `REGION_MAP`：

```python
# 新增到 global_telecom 关键词：
"pstn", "sip trunk", "sip in", "idd", "idd termination",
"voice network", "a2p", "caller id", "cli",
"intermediary number", "routing number", "menu routing",
"asr", "answer seizure", "termination fee", "traffic fee",
"number porting", "alphanumeric sender",
"dtmf", "webrtc",

# 新增到 contact_center 关键词：
"enquiry", "chatbot", "cinnox bot", "q&a bot", "claire",
"widget", "web link", "tag", "smart calling",
"campaign", "sms campaign", "whatsapp campaign",
"ai assistant", "ai engine", "ai enquiry summary",
"noise reduction", "share screen", "video call",
"ivr", "interactive voice response",
"sticky routing", "automatic enquiry distribution",
"canned response", "zapier", "zaps",
```

**5. copywriting.md 修改**

增加术语校正职责：

```markdown
### Terminology Consistency (NEW)

When polishing, replace common colloquial terms with CINNOX official terms:
- "tickets" → "enquiries"
- "agents" → "Staff members" (when referring to CINNOX users)
- "auto reply" → "auto-reply messages"
- "group call" → "broadcast call"

Reference: `.claude/skills/cinnox-demo/references/glossary.json`

Do NOT over-correct: if the customer used a colloquial term and the bot
is quoting the customer, keep the customer's original wording.
Only correct the bot's own descriptions.
```

Output 增加字段：
```json
{
  "polished": "...",
  "changes_made": [...],
  "banned_phrase_caught": false,
  "terminology_corrected": ["'ticket' → 'enquiry'"]
}
```

**6. reviewer.md 修改**

增加第 12 项检查：

```markdown
| 12 | **Terminology Accuracy**: Bot uses CINNOX official terms, not colloquial alternatives | minor |
```

检查方式：对照 Glossary，标记非官方术语。severity 为 minor（不阻塞发送，但记录改进）。

---

## 4. 全部 Skills 总览

### 业务核心（5 个）

| Skill | 说明 | 关键依赖 |
|-------|------|----------|
| customer-service | 客服系统：CRUD + Mock API + 通话训练 | _shared scripts |
| marketing | 销售系统：CRUD + Mock API + SPIN 通话 | _shared scripts |
| knowledge-base | CINNOX 知识库：构建/搜索/状态 | 无 |
| cinnox-demo | CINNOX UAT 演示：模拟 IM Bot + subagent 编排 | **必须先 build knowledge-base** |
| price-system | AI Agent 定价：分析 + 生成 .docx | docx skill（输出格式） |

### 文档生成（4 个，均独立）

| Skill | 说明 |
|-------|------|
| docx | Word 文档创建/编辑/分析 |
| pptx | PPT 演示文稿 |
| pdf | PDF 处理 |
| xlsx | Excel 表格 |

### 开发工具（5 个，均独立）

| Skill | 说明 |
|-------|------|
| agent-browser | 浏览器自动化（agent-browser CLI） |
| webapp-testing | Playwright Web 测试 |
| setup-lsp | LSP 配置指南 |
| mcp-builder | MCP Server 构建指南 |
| cc-nano-banana | 图片生成（Gemini CLI） |

### 元能力（5 个）

| Skill | 说明 | 衔接 |
|-------|------|------|
| brainstorming | 需求探索与设计 | 设计完成 → planning-with-files |
| autoservice-design | brainstorming 的 AutoService wrapper | 非技术用户协作 + 多 Agent 设计 |
| planning-with-files | 文件式任务规划 | 无 |
| skill-creator | Skill 创建指南 | 无 |
| autoservice-skill-guide | skill-creator 的 AutoService wrapper | 两层架构 + 版本演进设计 |

### 审计与测试（1 个，v1.3 计划新增）

| Skill | 说明 | 状态 |
|-------|------|------|
| architecture-audit | 架构审计：扫描 Skill → 依赖映射 → 漂移检测 | 已创建 |
| skill-redteaming | Red/Blue 对抗测试 | **v1.3 计划** |

---

## 5. Subagent 上下文管理评估

### 评估标准

| 维度 | 说明 |
|------|------|
| 输入充分性 | subagent 是否获得了完成任务所需的全部信息？ |
| 输入最小性 | subagent 是否只获得了完成任务所需的最小信息？（隔离） |
| 输出可用性 | subagent 的输出是否足以让下游消费者（主 agent 或其他 subagent）做出决策？ |
| 术语一致性 | subagent 是否使用/理解与 CINNOX 官方一致的术语？ |

### 逐 Subagent 评估

#### product-query

| 维度 | 评分 | 说明 |
|------|------|------|
| 输入充分性 | ⚠️ 不足 | **缺少术语扩展能力。** 客户说 "group call"，subagent 只搜 "group call"，找不到 "Broadcast Call Enquiry"。需要 Glossary synonym-map。 |
| 输入最小性 | ✅ 合格 | 只接收 query + domain，隔离正确。 |
| 输出可用性 | ✅ 合格 | 返回结构化 JSON，主 agent 可直接使用。 |
| 术语一致性 | ⚠️ 不足 | summary 中可能使用 KB chunk 的原始措辞，不一定是标准 CINNOX 术语。 |

**改进**：
1. 在 agent prompt 中注入 synonym-map 引用
2. 增加 "Query Expansion" 步骤
3. summary 中使用 Glossary 官方术语

#### region-query

| 维度 | 评分 | 说明 |
|------|------|------|
| 输入充分性 | ⚠️ 不足 | **电信术语覆盖不全。** "IDD termination"、"SIP trunk pricing"、"A2P rates" 等客户可能问的术语无法正确扩展。 |
| 输入最小性 | ✅ 合格 | 只接收 query + region + number_type。 |
| 输出可用性 | ✅ 合格 | 结构化 rates 数组，清晰明确。 |
| 术语一致性 | ⚠️ 不足 | 同 product-query，summary 可能用非标准表述。 |

**改进**：
1. 注入 Glossary 电信术语子集（~50 个术语）
2. 增加 telecom-specific Query Expansion
3. 扩展 `route_query.py` 关键词以覆盖 Glossary 中的电信术语

#### copywriting

| 维度 | 评分 | 说明 |
|------|------|------|
| 输入充分性 | ⚠️ 部分不足 | 有 draft + customer_type + sentiment，但**缺少术语校正参照**。无法判断 draft 中的术语是否为 CINNOX 官方表述。 |
| 输入最小性 | ✅ 合格 | 不接触 KB 原始结果和对话历史。 |
| 输出可用性 | ✅ 合格 | polished + changes_made + banned_phrase_caught 结构清晰。 |
| 术语一致性 | ❌ 缺失 | 当前完全没有术语校正能力。 |

**改进**：
1. 在 agent prompt 中注入 Glossary 高频术语映射（不需要全量 355 个，取前 30-50 个高频的即可）
2. 输出增加 `terminology_corrected` 字段
3. 明确规则：只校正 bot 自己的描述，不改客户原话的引用

#### reviewer

| 维度 | 评分 | 说明 |
|------|------|------|
| 输入充分性 | ✅ 合格 | response + 状态摘要 + kb_results_summary，足够做 11 项检查。 |
| 输入最小性 | ✅ 合格 | 不接触完整对话历史和 PII。 |
| 输出可用性 | ✅ 合格 | pass/fail + score + issues + recommendation 结构完善。 |
| 术语一致性 | ⚠️ 不足 | **11 项清单没有术语准确性检查。** bot 可以把 "Enquiry" 叫成 "Ticket" 而 reviewer 不会发现。 |

**改进**：
1. 新增第 12 项检查：Terminology Accuracy（severity: minor）
2. 在 prompt 中注入 Glossary 核心术语列表作为参照
3. 与 copywriting 形成双重保障：copywriting 校正 → reviewer 验证

#### auditor

| 维度 | 评分 | 说明 |
|------|------|------|
| 输入充分性 | ✅ 合格 | 编排元数据足够做模式分析。 |
| 输入最小性 | ✅ 合格 | 匿名化，无 PII。 |
| 输出可用性 | ✅ 合格 | audit_log.jsonl + strategy_summary.json。 |
| 术语一致性 | N/A | auditor 不生成客户面对的文本。 |

**改进**：
1. 记录 copywriting 的 `terminology_corrected` 数据，积累术语纠正模式
2. strategy_summary 增加"常见术语问题"维度

### 评估总结

| 问题 | 受影响 subagent | 严重度 | Glossary 能解决吗 |
|------|----------------|--------|-----------------|
| 客户措辞与 KB 术语不匹配 → 搜索失败 | product-query, region-query | **High** — 直接导致"KB 有答案但搜不到" | ✅ synonym-map Query Expansion |
| 路由关键词覆盖不全 → 错误路由或低 confidence | route_query.py（影响所有查询 subagent） | **Medium** — 导致不必要的 ambiguity 提问 | ✅ Glossary 术语补充关键词 |
| bot 回复使用非官方术语 → 品牌不一致 | copywriting | **Low** — 不影响功能，影响专业度 | ✅ Glossary 术语校正 |
| reviewer 不检查术语准确性 | reviewer | **Low** — 与上一条配合 | ✅ 新增第 12 项检查 |
| subagent summary 使用 KB 原始措辞 | product-query, region-query | **Low** — 主 agent 会重写 | ⚠️ 部分解决 |

### Glossary 集成优先级

```
P0（必须做）：
  1. synonym-map.json 生成 — 解决搜索不到的核心问题
  2. product-query Query Expansion — 最高频使用的 subagent
  3. route_query.py 关键词扩展 — 影响所有查询路由

P1（应该做）：
  4. region-query Query Expansion — 电信术语消歧
  5. copywriting 术语校正 — 品牌一致性

P2（可以做）：
  6. reviewer 第 12 项检查 — 双重保障
  7. auditor 术语纠正统计 — 跨会话学习
```

---

## 6. 数据库结构

```
.autoservice/database/
  history/                  全部入口共用的会话日志
  customer_service/
    products/               产品 JSON
    customers/              客户 JSON
    operators/              客服策略 JSON
    sessions/               通话记录
    mock.db                 SQLite（Mock API 数据源）
  marketing/
    products/               产品 JSON
    customers/              客户 JSON
    operators/              销售策略 JSON
    sessions/               通话记录
    mock.db                 SQLite（Mock API 数据源）
  knowledge_base/
    kb.db                   SQLite KB（chunks + FTS5 索引）
    leads/                  潜客线索 JSON
    sessions/               会话记录 JSON

.claude/agent-memory/
  auditor/
    audit_log.jsonl         编排决策日志（append-only）
    strategy_summary.json   跨会话分析摘要
```

---

## 7. Skill 存放位置

Skills 分布在两个目录，部分有副本：

| 目录 | 加载方式 | 包含 |
|------|---------|------|
| `.claude/skills/` | Claude Code 直接识别 | 用户侧全部 Skill |
| `.autoservice/.claude/skills/` | `autoservice/claude.py` 作为 plugin 加载 | docx, pptx, pdf, xlsx, mcp-builder + 3 个副本 |

3 个副本 Skill（knowledge-base, cinnox-demo, skill-creator）在两处都有，内容相同。

Subagent 定义统一存放在 `.claude/agents/` 目录。
