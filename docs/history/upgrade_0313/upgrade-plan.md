# AutoService Skill System Upgrade Plan

## Context

d57eb42 commit 建立了完整的 `_shared` 基础设施（Mock API、权限检查、多语言配置），但后续 web/server.py 在 UAT 迭代中绕过了这套体系，重新发明了 Mock 账户、system prompt、会话管理。同时，3 个元 Skill（brainstorming、planning-with-files、skill-creator）只支持单 Agent 单任务工作流，缺少两层架构、KB 切片、subagent 协调等概念。

本次目标：
1. **Phase 1** — 升级 KB 基础设施 + 3 个元 Skill，引入两层架构、KB 切片、subagent、数据溯源
2. **Phase 2** — 用升级后的元 Skill 指导重建 cinnox-demo Skill

web/server.py 本次不动。

---

## 本次升级要解决的问题清单

### 架构与基础设施问题（v1.0 解决）

| # | 问题 | 根因 | 影响 | 解决方案 | Phase |
|---|------|------|------|----------|-------|
| P1 | web/server.py 绕过 `_shared` 基础设施 | d57eb42 后的 UAT 迭代重新发明了 Mock 账户、system prompt、会话管理 | 架构漂移，两套重复实现 | 新建 architecture-audit Skill 检测漂移；本次不合并，留作后续重构依据 | 0.1 |
| P2 | KB 无 domain/region 维度切片 | 原 KB 只有全量搜索，无法区分产品线和地区 | 搜索结果混杂（CINNOX 功能与电信费率混在一起） | Schema 新增 domain/region 字段 + 搜索过滤 | 1.1-1.5 |
| P3 | PDF 切块缺少语义分段 | 原 PDF ingest 使用固定字符数切割 | 表格结构被拆散、段落上下文断裂 | 语义分段 + 表格结构保持 | 1.2 |
| P4 | XLSX 费率表缺少地区提取 | 原 XLSX ingest 不解析 country 列 | 无法按国家过滤费率 | 费率表行级地区提取 + toll-free/local 子分类 | 1.3 |
| P5 | 无 subagent 机制 | cinnox-demo 直接调用 kb_search.py | L1/L2 架构缺失，路由和检索耦合 | 新建 kb_subagent.py（v1: Python 脚本） | 1.6 |
| P6 | cinnox-demo 缺少 query routing | 所有问题走同一搜索路径 | 无法按产品线/地区精准检索 | SKILL.md 路由表 + route_query.py 辅助脚本 | 2.2-2.3 |
| P7 | 无 ambiguity detection | 用户问题模糊时 bot 直接猜测回答 | 回答可能驴唇不对马嘴 | SKILL.md prompt 规则（v1: 纯 prompt） | 2.5 |
| P8 | 搜索结果缺少数据溯源 | 原搜索只返回文本，无来源标注 | 测试人员无法追溯答案出处 | 溯源输出（文件/Sheet/行/页码） | 2.4 |

### 元 Skill 缺陷（v1.0 Phase 0/1B 解决）

| # | 问题 | 影响 | 解决方案 | Phase |
|---|------|------|----------|-------|
| P9 | brainstorming 不支持非技术用户协作和多 Agent 设计 | 复杂需求探索效率低 | 创建 autoservice-design wrapper Skill | 0.2 / 1.8 |
| P10 | planning-with-files 无决策追踪和演进路线图 | 方案选择过程不可追溯 | 新增模板区块 | 0.3 / 1.9 |
| P11 | skill-creator 不支持两层架构和版本演进设计 | 新 Skill 缺少架构指导 | 创建 autoservice-skill-guide wrapper Skill | 0.4 / 1.10 |

### UAT 驱动的运行时问题（v1.1 ~ v1.1.2 解决）

| # | 问题 | 发现于 | 根因 | 影响 | 解决方案 | 版本 |
|---|------|--------|------|------|----------|------|
| P12 | KB 预注入短路 MANDATORY GATE | Round 4 (Issue 2) | `_presearch_kb()` 在客户识别前就注入 KB 结果，Claude 看到答案直接回答 | TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 全部失败 | `gate_cleared` 状态机：customer_type 确认前阻止 KB 注入 | v1.1 |
| P13 | 转人工不等客户确认 | Round 4 (Issue 1) | SKILL.md 无两步确认流程 + `_ESCALATION_RE` 自动触发 | 浪费人工资源，客户体验差 | SKILL.md 两步 escalation（提议→确认→触发） | v1.1 |
| P14 | `_ESCALATION_RE` 无法区分提议和执行 | Round 4 (Issue 3) | 纯字符串匹配，"shall I connect you with...?" 也被当成转接指令 | 所有涉及转人工的 TC 受影响 | SKILL.md 措辞控制：提议用安全措辞，确认后用触发词 | v1.1 |
| P15 | 自由回答中触发词泄漏 | Round 4 补测 | v1.1 只规范了 Step 5 的措辞，Discovery Phase / 产品推荐中仍自然使用触发词 | 非 escalation 场景意外触发 handoff | SKILL.md Step 6 全局 BANNED PHRASES 规则 | v1.1.1 |
| P16 | 纯 prompt BANNED PHRASES 不可靠 | Round 5 前置测试 | Claude 将 BANNED PHRASES 视为建议而非硬约束 | 连续两个 session 违反措辞限制 | `_should_escalate()` 代码级句子过滤——疑问句中触发词不触发 | v1.1.2 |

### 问题解决进度

```
v1.0  ─── P1~P11 ─── Phase 0/1A/1B/2 ─── Round 4 UAT
                                              │
v1.1  ─── P12~P14 ─── server.py gate + SKILL.md 两步 ─── Round 4 补测
                                                              │
v1.1.1 ── P15 ─── SKILL.md BANNED PHRASES ─── Round 5 前置测试
                                                    │
v1.1.2 ── P16 ─── _should_escalate() 代码过滤 ─── Round 5 UAT (19/19 PASS)
                                                        │
                                                   Round 6 UAT (新能力验证, 5/10 PASS)
```

---

## Skill 来源分类与修改策略

### 来源分类

| Skill | 来源 | 证据 | 可直接修改 |
|---|---|---|---|
| brainstorming | **外部**: `obra/superpowers` (GitHub) | skills-lock.json | 不能 |
| skill-creator | **外部包** | LICENSE.txt (Apache 2.0) | 不能 |
| planning-with-files | 本地创建 | git 历史 | 能 |
| customer-service | 本地创建 | git 历史 | 能 |
| marketing | 本地创建 | git 历史 | 能 |
| knowledge-base | 本地创建 | git 历史 | 能 |
| cinnox-demo | 本地创建 | git 历史 | 能 |
| price-system | 本地创建 | git 历史 | 能 |
| agent-browser, webapp-testing, setup-lsp, cc-nano-banana | 外部包 | LICENSE.txt / 批量引入 | 不能 |
| docx, pptx, pdf, xlsx, mcp-builder | 外部包 | LICENSE.txt | 不能 |

### 修改策略

外部 Skill（brainstorming, skill-creator）不能直接修改，否则更新会覆盖。采用以下策略：

**方式 1: CLAUDE.md 扩展** — 在项目级 `CLAUDE.md` 中添加规则，对所有 Skill 生效。适合全局性的行为约束（如"所有 plan 都必须包含决策记录表"）。

**方式 2: 本地 wrapper Skill** — 创建一个本地 Skill（如 `autoservice-design`），在描述中声明"用于代替 brainstorming 进行需求设计"，内部引用 brainstorming 的核心流程并扩展。不修改原 Skill。

**方式 3: 独立补充 Skill** — 创建独立的新 Skill 来补充缺失能力（如 `architecture-audit`），与外部 Skill 平级共存，不依赖也不修改它们。

**方式 4: references 扩展** — 在外部 Skill 的 `references/` 目录下放自定义文件。外部 Skill 更新通常只覆盖 SKILL.md，不清理 references/。风险较低但不保证安全。

**本次 plan 采用的策略**：

| 原计划 | 新策略 |
|---|---|
| 修改 brainstorming/SKILL.md | **方式 2**: 创建 `autoservice-design` Skill（wrapper） |
| 修改 skill-creator/SKILL.md | **方式 2**: 创建 `autoservice-skill-guide` Skill（wrapper） |
| 修改 planning-with-files | **直接修改**（本地创建，无更新风险） |
| 新建 architecture-audit | **方式 3**: 独立新 Skill |
| 修改 knowledge-base / cinnox-demo | **直接修改**（本地创建） |

---

## 决策记录

| 问题 | 决策 | 备注 |
|------|------|------|
| Q1 数据来源展示 | 前端展示给测试人员 | 粒度: 产品线 > 文件名 > Sheet/章节 > 页码/行范围 |
| Q2 KB 切片维度 | 产品线 + 地区 | 产品线: Global Telecom / AI Sales Bot / Contact Center |
| Q3 PDF 处理 | 无扫描版，有表格需保持结构 | 语义分段 + 表格结构保持 |
| Q4 模糊确认 | **方案 A: 纯 Prompt** | 当前阶段够用，未来可升级为代码检测 |
| Q5 Subagent 实现 | **方案 A: Python 脚本** | 临时方案，未来可替换为 SDK subagent |
| Q6 L1 通用 API | Skill 内部路由层 | L1 路由 Skill, L2 路由 subagent |
| Q7 Subagent 生命周期 | **方案 A: 按需无状态** | 未来可升级为方案 C（按需 + L1 传上下文） |

### 产品线分类（已修正）

| Domain ID | 产品线 | 子分类 | 对应 source |
|---|---|---|---|
| `global_telecom` | Global Telecom | Toll-free / Local Numbers | f7, f8, w4 |
| `ai_sales_bot` | AI Sales Bot | — | f1, f2, f3 |
| `contact_center` | Contact Center | — | f4, f5, f6, w1, w2, w3 |

---

## 演进路线图

本次实现标记为 **v1**，以下记录未来可升级的方向：

### 模糊确认（Q4）

**v1（本次）**: 纯 Prompt 指导 — 在 SKILL.md 中写明规则，Claude 自行判断是否需要澄清。

**v2（未来）**: 代码检测 + Prompt 兜底
- 在 `route_query.py` 中加关键词匹配，命中多个 domain 或 confidence < 阈值时返回 `{"action": "clarify"}`
- 优点：一致性高、可测试、可复现
- 缺点：需要维护关键词规则，有新产品线时要更新代码

**v3（未来）**: 双重检测 — 在 v2 基础上，即使路由成功，如果搜索结果 BM25 分数低（<= 2 星）也触发澄清
- 优点：覆盖"路由对了但 KB 没数据"的情况
- 缺点：实现成本最高

### Subagent 实现（Q5）

**v1（本次）**: Python 脚本（`kb_subagent.py`）
- 纯本地 SQLite 查询，< 1 秒，零 API 成本
- 只能搜索，不能推理/总结/对比
- 接口设计为 `--role`, `--domain`, `--region`, `--query`，**保持与未来 SDK subagent 的参数兼容**

**v2（未来）**: Claude Agent SDK Subagent
- 每个 subagent 是独立 Claude 实例，有专属 system prompt 和工具
- 能自主推理（如对比两个地区费率、总结多文档、处理非结构化数据）
- 代价：每次调用 +3-8 秒延迟 + API token 成本
- 迁移路径：L1 的调用接口不变（同样的 role/domain/region/query 参数），只需把 `kb_subagent.py` 替换为 SDK 调用

### Subagent 生命周期（Q7）

**v1（本次）**: 按需调用，无状态 — 每次提问临时执行，返回后退出。

**v2（未来）**: 按需调用 + L1 传上下文
- Subagent 仍按需调用（无状态），但 L1 在调用时把相关历史上下文作为 `--context` 参数传入
- 使 subagent 能处理"和刚才那个对比"之类的跨轮次请求
- 实现成本低（只加一个参数），资源占用不变
- 注意：上下文传递质量取决于 L1 主 Agent 的判断

**v3（未来）**: Session 内长驻（仅 SDK subagent 有意义）
- 好处：完整跨轮次推理
- 代价：进程管理、状态持久化、超时清理、高资源占用

---

## Phase 0: 元 Skill 从本次 Session 中学到的改进

本次 session 本身就是一次完整的 brainstorming → planning 流程。以下是实际工作中暴露出的元 Skill 缺陷，应在 Phase 1B 中一并修复。

### 0.1 新建 architecture-audit Skill

本次 session 中做了：探索全部 Skill → 对比历史 commit (d57eb42) → 发现 web/server.py 与 _shared 的架构漂移 → 生成架构分析文档。

这是一个可复用的工作流，目前没有任何 Skill 覆盖。

**New Skill**: `.claude/skills/architecture-audit/SKILL.md`

工作流：
1. **Inventory** — 扫描 Skill 目录，列出全部 Skill 及其 references/scripts
2. **Dependency mapping** — 分析 Skill 间的调用关系、共享资源、数据库依赖
3. **Historical comparison** — 对比关键 commit，识别架构意图 vs 当前实际的偏差
4. **Drift detection** — 找出绕过共享基础设施的重复实现（如 web/server.py 重写了 _shared）
5. **Output** — 生成架构分析文档（`docs/analysis/` 下），包含：分层分类表、依赖关系图、漂移清单、修复建议

### 0.2 创建 autoservice-design Skill（brainstorming 的本地 wrapper）

brainstorming 来自外部包 `obra/superpowers`，不能直接修改。创建本地 wrapper Skill 来扩展它。

**New Skill**: `.claude/skills/autoservice-design/SKILL.md`

描述：`用于 AutoService 项目的需求设计。在 brainstorming 核心流程基础上，增加非技术用户协作、多 Agent 架构设计、对比分析等能力。`

内容：
- 引用 brainstorming 的核心流程（探索 → 提问 → 提案 → 展示 → 审批 → 文档 → 交接）
- 新增 "## Requirements Elicitation from Non-Technical Users" 章节：
  - **需求翻译**：收到模糊需求时，拆解为具体技术问题，用非技术语言解释每个问题的影响
  - **确定性分档**：A 类（可直接执行）/ B 类（方向明确，细节待确认）/ C 类（架构级，需深入讨论）
  - **对比分析模板**：当有多种方案时，用统一的表格对比（维度：实现成本、灵活性、一致性、可调试性、适合场景），让用户选择
  - **输出格式**：`questions-for-tech.md`（分档问题清单 + 对比分析）
- 新增 "## Multi-Agent Design Exploration" 章节：
  - Agent 边界识别、两层架构模板、KB 切片设计、模糊处理设计、数据溯源设计

### 0.3 planning-with-files 增加"决策追踪"和"演进路线图"模板

本次 plan 自然演化出两个模式，当前模板里没有：

**增加到 1.9 planning-with-files**：

1. **决策记录表** — 在 task_plan.md 模板中新增：
   ```markdown
   ## 决策记录
   | 问题 | 决策 | 备选方案 | 备注 |
   |------|------|---------|------|
   ```
   用于追踪 plan 中每个需要选择的点和最终决定。

2. **演进路线图** — 在 task_plan.md 模板中新增：
   ```markdown
   ## 演进路线图
   ### <功能名>
   **v1（本次）**: ...
   **v2（未来）**: ... [触发条件: ...]
   **v3（未来）**: ... [触发条件: ...]
   ```
   用于标注 MVP 实现和未来升级路径，包括每一步的触发条件和迁移方式。

### 0.4 创建 autoservice-skill-guide Skill（skill-creator 的本地 wrapper）

skill-creator 来自外部包，不能直接修改。创建本地 wrapper Skill 来扩展它。

**New Skill**: `.claude/skills/autoservice-skill-guide/SKILL.md`

描述：`AutoService 项目的 Skill 创建指南。在 skill-creator 基础上，增加两层架构模式、版本演进设计、KB 集成模式等 AutoService 特有的最佳实践。`

内容：
- 引用 skill-creator 的核心原则（简洁、渐进式加载、前置描述触发）
- 新增 "## Two-Layer Architecture Pattern"：L1 路由 / L2 subagent、KB 集成、模糊处理模板
- 新增 "## Designing for Evolution"：
  - **接口先行**：v1 的参数接口要兼容 v2 的实现
  - **标注演进点**：用 `> 演进说明：v1 用...，未来可替换为...` 格式
  - **迁移约束**：明确"替换时调用方无需改动"还是"调用方也需要改"
  - **触发条件**：什么情况下应该升级到 v2
- 新增 "## Multi-Agent Workflow" 模式（补充 workflows.md 的内容）
- 新增 "## Traceable Answer Pattern"（补充 output-patterns.md 的内容）

---

## Phase 1A: KB 基础设施升级

### 1.1 Schema 迁移 — 新增 domain/region/language 字段

**File**: `.claude/skills/knowledge-base/scripts/kb_ingest.py`

- `init_db()` 中用 `ALTER TABLE ADD COLUMN` 添加：
  - `domain TEXT DEFAULT ''` (global_telecom / ai_sales_bot / contact_center)
  - `region TEXT DEFAULT ''` (global / US / HK / ...)
  - `language TEXT DEFAULT 'en'`
  - `page_number INTEGER` (PDF 溯源)
- 创建索引 `idx_kb_domain`, `idx_kb_region`
- 不重建 FTS5 表（新字段通过 JOIN 过滤，不走 MATCH）

**New file**: `.claude/skills/knowledge-base/scripts/kb_migrate.py`
- 一次性迁移脚本，给现有 chunk 回填 domain/region/language
- 幂等（安全重复运行）

**New file**: `.claude/skills/knowledge-base/references/sources.json`
- 每个 source 的 domain/region/language 元数据
- 映射:

| Source | Domain | 说明 |
|---|---|---|
| f1, f2, f3 | ai_sales_bot | AI Sales Bot 相关 |
| f4, f5 | contact_center | CINNOX 功能和定价 |
| f6 | contact_center | M800 介绍（CINNOX 母公司） |
| f7, f8 | global_telecom | 全球电信费率 |
| w1, w2 | contact_center | CINNOX 官网和文档 |
| w3 | contact_center | M800 官网 |
| w4 | global_telecom | M800 定价页 |

### 1.2 PDF 语义切块 + 表格保持

**File**: `.claude/skills/knowledge-base/scripts/kb_ingest.py` — 替换 `ingest_pdf()`

- 用 pypdf 逐页提取文本（无新依赖）
- 检测标题模式（全大写行、编号章节如 "2.1 Features"、短行后接正文）
- 按标题分段，每段内按 max_chars 切块
- **表格检测**：识别制表符/等宽分隔的行（连续 3+ 行含 2+ 个 `|` 或 `\t`），整表作为一个 chunk 保持完整（即使超过 max_chars）
- `section` 存标题文本，`page_number` 存页码
- 检测不到标题时回退到原有 600 字符切块

### 1.3 XLSX 地区提取

**File**: `.claude/skills/knowledge-base/scripts/kb_ingest.py` — 修改 `ingest_xlsx()`

- 当 `is_rate_table=True` 且存在 "country" 列时，从每批行中提取 country 值
- 用查找表映射国家名 -> 地区代码
- Global Telecom 的子分类（Toll-free / Local Numbers）：检测列名或 sheet 名中的 "toll-free" / "local" / "DID" 关键词，存入 `region` 字段的子标签（如 `US/toll-free`, `US/local`）
- 只影响费率表（f7, f8），其他 XLSX 用 sources.json 的 source 级 region

### 1.4 搜索增加 domain/region 过滤

**File**: `.claude/skills/knowledge-base/scripts/kb_search.py`

- 新增 CLI 参数 `--domain`, `--region`
- `search()` 函数签名扩展，SQL 加 WHERE 过滤
- 输出增加溯源信息，格式：
  ```
  [1] [Contact Center] CINNOX Feature List 2026
      File: EN_CINNOX_Feature_List_v2026.xlsx | Sheet: Features | Row 42
      Relevance: ****
  ```

### 1.5 Status 增加 domain/region 统计

**File**: `.claude/skills/knowledge-base/scripts/kb_status.py`

- 增加 `SELECT domain, region, COUNT(*) GROUP BY domain, region` 汇总

### 1.6 Subagent 执行脚本（v1: Python 脚本）

**New file**: `.claude/skills/knowledge-base/scripts/kb_subagent.py`

> **演进说明**：v1 用 Python 脚本实现，只做 KB 搜索。接口设计（--role/--domain/--region/--query）保持与未来 SDK subagent 兼容，届时只需替换实现，调用方无需改动。

- 参数: `--role`, `--domain`, `--region`, `--query`
- 调用 `kb_search.search()` 并强制 domain/region 过滤
- 返回结构化 JSON（含 role, results, sources_consulted, confidence）
- 用法示例:
  ```bash
  uv run .claude/skills/knowledge-base/scripts/kb_subagent.py \
    --role region_specialist --domain global_telecom --region US \
    --query "DID number pricing"
  ```

### 1.7 KB SKILL.md 更新

**File**: `.claude/skills/knowledge-base/SKILL.md`

- 文档化 `--domain` / `--region` 参数
- 新增 "Domain Slicing" 章节：source-to-domain 映射表、搜索示例
- 新增 "Subagent" 章节：kb_subagent.py 用法

---

## Phase 1B: 元 Skill 升级

### 1.8 autoservice-design Skill（替代直接修改 brainstorming）

**New Skill**: `.claude/skills/autoservice-design/SKILL.md`

brainstorming 是外部包，不直接修改。创建本地 wrapper Skill，内容见 Phase 0.2。

用户触发方式：`/autoservice-design` 或说"帮我设计一个需求"。

### 1.9 planning-with-files SKILL.md + 模板

**File**: `.claude/skills/planning-with-files/SKILL.md`

新增 "## Multi-Agent Task Planning" 章节：
- Agent 分解：task_plan.md 中增加 "Agent Architecture" 区块
- Subagent 任务追踪：Phase 下支持 per-agent 子任务
- KB 感知的 findings：provenance 字段（source, page, section, domain, region）

**File**: `.claude/skills/planning-with-files/templates/task_plan.md`

增加可选 "Agent Architecture" 区块模板

### 1.10 autoservice-skill-guide Skill（替代直接修改 skill-creator）

**New Skill**: `.claude/skills/autoservice-skill-guide/SKILL.md`

skill-creator 是外部包，不直接修改。创建本地 wrapper Skill，内容见 Phase 0.4。

用户触发方式：`/autoservice-skill-guide` 或说"帮我创建一个 AutoService Skill"。

---

## Phase 2: 重建 cinnox-demo Skill

### 2.1 两层架构重构

**File**: `.claude/skills/cinnox-demo/SKILL.md`

- L1 保留：客户识别、lead 收集、会话管理、升级规则
- L2 改造：将直接 `kb_search.py` 调用替换为 `kb_subagent.py` 调用

### 2.2 Query 路由逻辑

**File**: `.claude/skills/cinnox-demo/SKILL.md` — 新增 "## Query Routing"

| Query 类型 | domain | region | role |
|---|---|---|---|
| CINNOX 功能/集成 | contact_center | (上下文) | product_specialist |
| CINNOX 定价/套餐 | contact_center | (上下文) | pricing_specialist |
| AI Sales Bot 功能 | ai_sales_bot | (上下文) | product_specialist |
| DID/VN 费率 (Toll-free) | global_telecom | (提取国家)/toll-free | region_specialist |
| DID/VN 费率 (Local Numbers) | global_telecom | (提取国家)/local | region_specialist |
| M800 公司信息 | contact_center | global | product_specialist |

### 2.3 路由辅助脚本

**New file**: `.claude/skills/cinnox-demo/scripts/route_query.py`

- 基于关键词的路由器（非 LLM），输入 query，输出 domain/region/role 建议
- Agent 可参考也可覆盖

### 2.4 溯源增强

更新 source citation 规则：
- 测试人员面向（前端折叠区域）：
  ```
  [Global Telecom] M800 Global Rates.xlsx | Sheet: US Rates | Rows 15-17
  [Contact Center] CINNOX Feature List.xlsx | Sheet: Features | Row 42
  [AI Sales Bot] AI Sales Bot Charging.pdf | Section: 2.1 Pricing | Page 3
  ```
- 客户面向输出（不变）：友好描述如 "According to our pricing documentation..."

### 2.5 模糊处理（v1: 纯 Prompt）

新增 "## Ambiguity Detection" 章节：
- Domain 模糊（"多少钱" — CINNOX 套餐还是电信费率？）→ 反问
- Region 模糊（问费率没说国家）→ 反问
- Toll-free vs Local Numbers 模糊 → 反问
- 每轮最多 1 个澄清问题，上下文已有的不重复问

> **演进说明**：v1 纯 Prompt 指导。未来可在 `route_query.py` 中加代码检测（命中多 domain 时返回 clarify 信号），提升一致性和可测试性。

---

## 文件变更总览

### 修改的文件

| File | 变更幅度 | 来源 |
|---|---|---|
| `.claude/skills/knowledge-base/scripts/kb_ingest.py` | 大 — schema + PDF 切块 + 表格保持 + XLSX 地区 | Phase 1A |
| `.claude/skills/knowledge-base/scripts/kb_search.py` | 中 — domain/region 过滤 + 溯源输出 | Phase 1A |
| `.claude/skills/knowledge-base/scripts/kb_status.py` | 小 — domain/region 统计 | Phase 1A |
| `.claude/skills/knowledge-base/SKILL.md` | 中 — 文档化新功能 | Phase 1A |
| ~~`.claude/skills/brainstorming/SKILL.md`~~ | ~~不修改（外部包）~~ → 用 autoservice-design 替代 | Phase 0 + 1B |
| `.claude/skills/planning-with-files/SKILL.md` | 中 — Multi-Agent 规划章节 | Phase 1B |
| `.claude/skills/planning-with-files/templates/task_plan.md` | 中 — Agent Architecture + 决策追踪 + 演进路线图 | Phase 0 + 1B |
| ~~`.claude/skills/skill-creator/SKILL.md`~~ | ~~不修改（外部包）~~ → 用 autoservice-skill-guide 替代 | Phase 0 + 1B |
| `.claude/skills/cinnox-demo/SKILL.md` | 大 — L1/L2 + 路由 + 溯源 + 模糊处理 | Phase 2 |

### 新增的文件

| File | 说明 | 来源 |
|---|---|---|
| `.claude/skills/architecture-audit/SKILL.md` | 架构审计 Skill（探索 → 对比 → 漂移检测 → 报告） | Phase 0 |
| `.claude/skills/autoservice-design/SKILL.md` | brainstorming 的本地 wrapper（非技术用户协作 + Multi-Agent 设计） | Phase 0 |
| `.claude/skills/autoservice-skill-guide/SKILL.md` | skill-creator 的本地 wrapper（两层架构 + 版本演进设计） | Phase 0 |
| `.claude/skills/knowledge-base/scripts/kb_subagent.py` | Subagent 执行器（v1: 脚本） | Phase 1A |
| `.claude/skills/knowledge-base/scripts/kb_migrate.py` | 一次性 DB 迁移 | Phase 1A |
| `.claude/skills/knowledge-base/references/sources.json` | Source 元数据 | Phase 1A |
| `.claude/skills/cinnox-demo/scripts/route_query.py` | Query 路由器 | Phase 2 |

---

## 执行顺序（有依赖关系）

```
Phase 0（从本次 session 学到的改进，融入 Phase 1B）:
  0.1 新建 architecture-audit Skill
  0.2 brainstorming 增加非技术用户协作模式      -- 融入 1.8
  0.3 planning-with-files 增加决策追踪 + 演进路线图 -- 融入 1.9
  0.4 skill-creator 增加版本演进设计             -- 融入 1.10

Phase 1A（KB 基础设施）:
  1.1 Schema 迁移设计 (kb_ingest.py)
  1.2 PDF 语义切块 + 表格保持 (kb_ingest.py)    -- 依赖 1.1
  1.3 XLSX 地区提取 (kb_ingest.py)              -- 依赖 1.1
  1.4 搜索过滤 (kb_search.py)                   -- 依赖 1.1
  1.5 Status 统计 (kb_status.py)                -- 依赖 1.1
  1.6 Subagent 脚本 v1 (kb_subagent.py)         -- 依赖 1.4
  1.7 KB SKILL.md                               -- 依赖 1.4, 1.6
  迁移脚本 (kb_migrate.py)                      -- 依赖 1.1

Phase 1B（元 Skill，可与 1A 并行，包含 Phase 0 的改进）:
  0.1 architecture-audit Skill (新建)
  1.8 autoservice-design Skill (新建，wrapper brainstorming + 0.2)
  1.9 planning-with-files (直接修改 + 0.3 决策追踪/演进路线图)
  1.10 autoservice-skill-guide Skill (新建，wrapper skill-creator + 0.4)
                                                 -- 引用 1.6 的 subagent 模式

Phase 2（cinnox-demo，依赖 Phase 1 全部完成）:
  2.1 两层架构重构
  2.2 路由逻辑
  2.3 路由脚本 (route_query.py)
  2.4 溯源增强
  2.5 模糊处理 v1 (纯 Prompt)
```

---

## Verification

### Phase 1 验证

```bash
# 1. Schema 迁移
uv run .claude/skills/knowledge-base/scripts/kb_migrate.py
sqlite3 .autoservice/database/knowledge_base/kb.db ".schema kb_chunks"
# 确认: domain, region, language, page_number 列存在

# 2. 重新 ingest
uv run .claude/skills/knowledge-base/scripts/kb_ingest.py --source files
# 确认: chunk 有 domain/region 字段

# 3. Domain 过滤搜索
uv run .claude/skills/knowledge-base/scripts/kb_search.py \
  --query "WhatsApp" --domain contact_center
# 确认: 只返回 contact_center domain 的结果

# 4. Region 过滤搜索
uv run .claude/skills/knowledge-base/scripts/kb_search.py \
  --query "DID price" --domain global_telecom --region US
# 确认: 只返回 US region 的结果

# 5. PDF 溯源 + 表格
uv run .claude/skills/knowledge-base/scripts/kb_search.py --query "voice bot"
# 确认: 结果包含 page_number，表格 chunk 结构完整

# 6. Subagent
uv run .claude/skills/knowledge-base/scripts/kb_subagent.py \
  --role region_specialist --domain global_telecom --region US \
  --query "DID pricing"
# 确认: 结构化 JSON 输出

# 7. Status
uv run .claude/skills/knowledge-base/scripts/kb_status.py
# 确认: 显示 domain/region 分布 (global_telecom / ai_sales_bot / contact_center)

# 8. 向后兼容
uv run .claude/skills/knowledge-base/scripts/kb_search.py --query "CINNOX"
# 确认: 不加过滤仍返回全部结果
```

### Phase 2 验证

- TC-B1: "Does CINNOX support WhatsApp?" -> subagent 用 `--domain contact_center`，答案含溯源
- TC-C1: "How much is a US toll-free number?" -> subagent 用 `--domain global_telecom --region US/toll-free`
- 模糊测试: "What's the pricing?" -> bot 反问是 Contact Center 套餐还是电信费率
- Region 模糊: "DID rates?" -> bot 反问哪个国家
- Toll-free vs Local: "US number pricing" -> bot 反问 Toll-free 还是 Local Numbers
- 全量回归: TC-A ~ TC-H 无退化

---

## v1.1: Web 端门控修复（Round 4 UAT 驱动）

> **背景**：Phase 1-2 完成后进行 Round 4 UAT（19 TC），在 TC-A1 ~ TC-B3 阶段发现 3 个结构性问题。v1.0 计划中声明"web/server.py 本次不动"，但 UAT 证明 **不修改 server.py 就无法通过 TC**。详细根因分析见 [round4/Issues_Round4.md](round4/Issues_Round4.md)。

### 问题摘要

| # | 根因 | 影响的 TC | 严重度 |
|---|------|----------|--------|
| 1 | `_presearch_kb()` 在 MANDATORY GATE 前注入 KB 结果，短路门控 | TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 | Critical |
| 2 | Bot 转人工不等客户确认（新需求：避免浪费人工资源） | TC-B2, TC-C2, TC-E1/E2, TC-F1 | High |
| 3 | `_ESCALATION_RE` 正则匹配"connect you with"等短语后自动触发 handoff，即使 bot 只是在**询问**客户是否要转 | 所有涉及转人工的 TC | High |

### 确定性分类（autoservice-design A/B/C）

| 修复项 | 分类 | 理由 |
|--------|------|------|
| SKILL.md 增加"转人工前先问客户" | **A — 直接可执行** | 规则明确，只改 SKILL.md |
| `_presearch_kb()` 门控感知 | **B — 方向明确，需选方案** | 有 3 种实现方式，见对比分析 |
| `_ESCALATION_RE` 区分"提议"和"确认" | **B — 方向明确，需选方案** | regex 改法或状态追踪，见对比分析 |

### 对比分析: Pre-fetch KB 门控

| 维度 | A: 禁用 pre-fetch | B: 门控感知 pre-fetch | C: 仅 prompt 强化 |
|------|-------------------|----------------------|-------------------|
| 实现成本 | 低 — 删除/注释调用 | 中 — 需 session 状态追踪 | 低 — 只改 prompt |
| 可靠性 | 高 — 不注入就不会短路 | 高 — 精确控制注入时机 | 低 — prompt 竞争仍存在 |
| 延迟影响 | 差 — 每次产品问题多 2-4 秒（Claude 需手动调 API） | 无影响 — gate 通过后恢复 pre-fetch | 无影响 |
| 未来兼容 | 差 — 完全失去优化 | 好 — 保留优化，按需启用 | 差 — 不解决根因 |
| **推荐** | | **选择 B** | |

方案 B 实现思路：在 session_data 中追踪 `gate_cleared` 状态。`_presearch_kb()` 检查此字段，只在 gate 通过后注入 KB 结果。gate 通过的信号 = lead 已保存（通过 `/api/save_lead` 被调用）或现有客户身份已验证。

### 对比分析: Escalation 确认

| 维度 | A: 改 regex（排除疑问句） | B: 两阶段 escalation（状态机） |
|------|--------------------------|------------------------------|
| 实现成本 | 低 — regex 加负向断言 | 中 — 需 escalation_proposed 状态 |
| 可靠性 | 中 — regex 难覆盖所有措辞 | 高 — 状态明确 |
| 复杂度 | 低 | 中 |
| **推荐** | **选择 A**（先用简单方案） | 作为 v2 备选 |

方案 A 实现思路：
- SKILL.md：转人工前先问"Would you like me to transfer you to..."，等客户确认后再说"Connecting you now."
- `_ESCALATION_RE`：只匹配明确的执行动作（"connecting you now"、"let me transfer you now"），排除疑问句式

### 元 Skill 验证（autoservice-design）

对 v1.1 三个修复项逐项验证必要性、可行性，以及实现方案的调整：

#### v1.1-1 SKILL.md 转人工确认 — 通过

- **必要性**：确认。用户明确要求避免浪费人工资源。
- **可行性**：确认。只改 SKILL.md。但必须和 v1.1-3 配合——措辞需避开 `_ESCALATION_RE` 触发词。

#### v1.1-2 pre-fetch 门控 — 通过，实现方案调整

- **必要性**：确认。不修复无法通过 8 个 TC。
- **原方案问题**："/api/save_lead 调用时设置 gate_cleared" 不可行——HTTP endpoint 和 `_fast_tool()` 都不持有 session_data 引用。
- **调整方案**：在 conversation loop 中（第 1231 行附近），基于 `customer_type` 状态设置 `gate_cleared`：
  ```python
  # 在 bot 回复处理后，escalation 检测之前
  if session_data.get("customer_type", "unknown") != "unknown":
      session_data["gate_cleared"] = True
  ```
  然后改 `_presearch_kb()` 签名，接受 `gate_cleared` 参数。
- 这样不需要改 save_lead 路径，改动更小。

#### v1.1-3 escalation regex — 方案调整

- **原方案风险**：改 regex 排除疑问句不可靠——Claude 措辞不可控，负向断言难覆盖所有变体。
- **调整方案**：**不改 regex**，改为 SKILL.md 措辞控制：
  - 提议阶段：使用不含 regex 触发词的措辞（如 "I'd recommend speaking with a specialist. Would you like me to arrange that?"）
  - 确认后：使用触发词（如 "Connecting you now."）
  - 这样 regex 原样保留，只有客户确认后的执行消息才触发 handoff。

### v1.1 执行计划（验证后调整版）

```
v1.1-1: SKILL.md 转人工两步流程 (Class A)
  → 修改 .claude/skills/cinnox-demo/SKILL.md
  → 提议措辞避开 _ESCALATION_RE 触发词
  → 客户确认后用触发词（"Connecting you now."）

v1.1-2: _presearch_kb() 门控感知 (Class B, 方案 B 调整版)
  → 修改 web/server.py
  → session_data 初始化增加 gate_cleared: False
  → conversation loop 中: customer_type != "unknown" 时设 gate_cleared = True
  → _presearch_kb() 签名增加 gate_cleared 参数，False 时跳过注入

v1.1-3: 不改 regex，用 SKILL.md 措辞控制 (调整为 Class A)
  → 不修改 _ESCALATION_RE
  → SKILL.md 中规定提议措辞不含触发词，确认后才用触发词
  → 依赖 v1.1-1 的措辞规范
```

### v1.1 文件变更（验证后调整版）

| File | 变更 |
|---|---|
| `.claude/skills/cinnox-demo/SKILL.md` | escalation 消息改为两步（提议用安全措辞 → 等客户确认 → 用触发词执行） |
| `web/server.py` | `_presearch_kb()` 加 gate_cleared 参数 + session_data 增加 gate_cleared 字段 + conversation loop 中基于 customer_type 设置 gate |

注意：`_ESCALATION_RE` 不需要修改。

### v1.1 验证

```
# Issue 2 修复验证（pre-fetch 门控）
1. 新 session 第一条消息问产品问题 → bot 应先识别客户类型，不直接回答
2. 收集完 lead 后问产品问题 → bot 应正常搜索 KB 回答（pre-fetch 恢复）
3. 恢复已有 session（customer_type 已知）→ pre-fetch 正常工作

# Issue 1+3 修复验证（转人工确认）
4. Bot 发现 KB 无法回答 → 提议措辞不含触发词 → human agent 不自动触发
5. 客户确认要转 → bot 说"Connecting you now." → regex 匹配 → human agent 接管
6. 客户说不转 → bot 继续对话 → 无 handoff 发生

# 回归验证
7. TC-F2（直接要求人工）→ bot 立即说"Connecting you now." → 正常触发 handoff
8. Support mode escalation → 不受影响（support 有自己的 prompt 和流程）
```

---

## v1.1.1: 自由回答中的触发词泄漏修复（Round 4 UAT 补测）

> **背景**：v1.1 执行完毕后补测时发现，Step 5 的两步规则虽然生效了，但 bot 在 Discovery Phase / 产品推荐等**自由回答**中仍会使用 `_ESCALATION_RE` 触发词，导致意外 handoff。

### 问题

| Session | TC | 现象 |
|---------|-----|------|
| session_20260309_135557 | TC-H2 变体 | Bot 在 Discovery Phase 推荐完 OCC 方案后，说 "shall I **connect you with** our sales team"，被 `_ESCALATION_RE` 匹配，自动触发 human agent handoff（Michael Liu 加入），客户尚未确认 |

### 根因

v1.1 的 SKILL.md 修改只覆盖了 Step 5 的升级消息模板。但 Claude 在 Step 3（Discovery Phase）和 Step 4（产品 Q&A）的**自由回答**中也会自然地说 "connect you with" / "transfer" / "let me connect"。这些非模板消息同样会触发 `_ESCALATION_RE`。

### 修复（已执行）

在 SKILL.md **Step 6 Conversation Guidelines → Style** 中增加全局 **BANNED PHRASES** 规则：

> 在所有提议/建议场景（不仅限于 Step 5）中，禁止使用 `connect you with`、`transfer`、`let me connect`、`connecting you`、`please hold`、`will be right with you`。替代用语："Would you like me to arrange that?"、"Shall I set that up?"、"Would you like to speak with our team?"。触发词只允许在客户确认后的 Step 2 确认消息中使用。

### 文件变更

| File | 变更 |
|---|---|
| `.claude/skills/cinnox-demo/SKILL.md` | Step 6 Style 增加 BANNED PHRASES 全局规则 |

---

## v1.1.2: 代码级 escalation 过滤（Brainstorming 设计）

> **背景**：v1.1.1 在 SKILL.md 中增加了 BANNED PHRASES 规则，但 Round 5 测试证明 Claude **不会可靠遵守** prompt 级措辞限制。session_135557 和 session_143028 连续两次在自由回答中使用 "connect you with"，触发意外 handoff。**纯 prompt 方案已被证伪，需要代码级修复。**

### 问题

| Session | TC | 现象 |
|---------|-----|------|
| session_20260309_135557 | TC-H2 | Bot 推荐 OCC 后说 "shall I **connect you with** our sales team"，自动 handoff |
| session_20260309_143028 | TC-A4 | Bot 回答 CRM 集成后说 "shall I **connect you with** our technical team"，自动 handoff |

### 根因分析

架构层面的不匹配：`_ESCALATION_RE` 对 bot 文本做纯字符串匹配来推断意图，但它**无法区分**：

1. Bot **提议**转接（"shall I connect you with..."） → 不应触发
2. Bot **执行**转接（"Connecting you now."） → 应该触发
3. 客户直接要求人工（TC-F2） → 应该触发

SKILL.md 的 BANNED PHRASES 是"软控制"——Claude 把它当建议而非硬约束。两个连续 session 证明它不可靠。

### 方案对比（Brainstorming）

| 维度 | A: 代码级句子过滤 | B: 显式标记 `[HANDOFF]` | C: 两阶段状态机 |
|------|-------------------|------------------------|----------------|
| **原理** | 在 `_ESCALATION_RE` 匹配前，按句子拆分 bot 文本，跳过疑问句，只在陈述句中匹配 | 废弃 regex，要求 bot 在需要 handoff 时输出特殊标记 `[HANDOFF]` | regex 匹配后不立即触发，设 `escalation_proposed=True`，等下一条用户确认消息再触发 |
| **可靠性** | 高——代码级，不依赖 Claude 遵守措辞规则 | 中——Claude 可能忘记输出标记（与 BANNED PHRASES 同类问题） | 高——结构性阻止误触发 |
| **TC-F2 兼容** | ✅ "Connecting you with a human agent right away." 是陈述句 → 正常触发 | 需 SKILL.md 指示 TC-F2 时输出标记 | 需特殊处理跳过等待 |
| **Step 2 确认兼容** | ✅ "Connecting you with our billing team now." 是陈述句 → 正常触发 | 需 SKILL.md 指示确认时输出标记 | ✅ 用户确认后触发 |
| **延迟** | 无 | 无 | 增加一轮对话延迟 |
| **实现复杂度** | 低——~10 行代码，改 1 处 | 中——改 regex + SKILL.md 多处 | 高——新增状态字段 + 确认检测逻辑 |
| **SKILL.md 依赖** | 无——即使 Claude 使用触发词也不会误触发 | 高——依赖 Claude 正确输出标记 | 低 |
| **推荐** | **✅ 选择 A** | | |

### 推荐方案 A 详细设计

在 `web/server.py` 中新增辅助函数，替换原来的直接 `_ESCALATION_RE.search(bot_text)` 调用：

```python
def _should_escalate(bot_text: str) -> bool:
    """只在陈述句（非疑问句）中检测 escalation 触发词。

    疑问句中的触发词（如 "shall I connect you with..."）视为提议，不触发。
    陈述句中的触发词（如 "Connecting you now."）视为执行，触发 handoff。
    """
    for sentence in re.split(r'(?<=[.!?])\s+', bot_text):
        if sentence.strip().endswith('?'):
            continue  # 跳过疑问句
        if _ESCALATION_RE.search(sentence):
            return True
    return False
```

调用处修改（第 1247-1248 行）：

```python
# 原来
if (not session_data.get("human_agent_active")
        and _ESCALATION_RE.search(bot_text)):

# 改为
if (not session_data.get("human_agent_active")
        and _should_escalate(bot_text)):
```

### 约束验证

| 约束 | 是否满足 | 说明 |
|------|---------|------|
| TC-F2 即时触发 | ✅ | "Connecting you with a human agent right away." 以句号结尾 → 陈述句 → 触发 |
| Step 2 确认消息触发 | ✅ | "Connecting you with our billing team now." 以句号/叹号结尾 → 陈述句 → 触发 |
| 不完全禁用 `_ESCALATION_RE` | ✅ | regex 保留，只增加句子级过滤层 |
| 方案简单可靠 | ✅ | ~10 行代码，1 处调用修改，不依赖 prompt |
| 提议不误触发 | ✅ | "shall I connect you with...?" 以问号结尾 → 疑问句 → 跳过 |
| 向后兼容 support mode | ✅ | support mode 同样受益（如有提议措辞也不会误触发） |

### 边界情况

| 情况 | 处理 |
|------|------|
| Bot 在一条消息中既有提议（问句）又有执行（陈述） | 逐句检查，问句跳过，陈述句触发 → 正确 |
| Bot 用感叹号结尾的执行消息（"Connecting you now!"） | 感叹号不是问号 → 陈述句 → 触发 → 正确 |
| 中文触发词在疑问句中 | 中文问号 `？` 需加入分割和判断 → 实现时需注意 |
| Bot 在句子中间用问号（极罕见） | `re.split(r'(?<=[.!?])\s+', ...)` 按标点分割 → 正确处理 |

### 文件变更

| File | 变更 |
|---|---|
| `web/server.py` | 新增 `_should_escalate()` 函数；第 1248 行调用处改为使用新函数 |

### 验证计划

```
1. "shall I connect you with our sales team?" → _should_escalate() = False ✅
2. "Connecting you with our billing team now." → _should_escalate() = True ✅
3. "Of course! Connecting you with a human agent right away." → True ✅
4. "Would you like me to arrange that?" → False ✅（无触发词）
5. "正在为您转接客服。" → True ✅（中文陈述句）
6. "需要我帮您转接吗？" → False ✅（中文疑问句）
```
