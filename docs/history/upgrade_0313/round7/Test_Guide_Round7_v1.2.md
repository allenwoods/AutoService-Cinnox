# CINNOX UAT — Round 7 Test Guide (v1.2 Subagent Dispatching)

**Tester**: _______________
**Test Date**: _______________
**Environment**: Web UI
**启动命令**: `uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`
**验证方式**: 前端 Subagent Trace 面板 + 后台终端 `[subagent]` 日志

> **Round 7 目标**: 验证 v1.2 的 subagent 是否被实际调度。
> 不测功能正确性（那是 Round 4-6 已测过的），只测**编排层是否工作**。

---

## 前置条件

- [ ] KB 已就绪（547 chunks）——用 `/knowledge-base` 确认
- [ ] Web UI 启动成功——浏览器打开 `http://localhost:8000/login`
- [ ] 5 个 subagent 定义文件存在：

```
.claude/agents/
├── product-query.md
├── region-query.md
├── copywriting.md
├── reviewer.md
└── auditor.md
```

## 实现状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `web/server.py` — `allowed_tools` | ✅ 已加 `"Agent"` | 原来只有 `["Bash"]`，现在 `["Bash", "Agent"]` |
| `web/server.py` — `max_turns` | ✅ 已改为 15 | 原来 5，不够 subagent 调度 |
| `web/server.py` — Agent 事件捕获 | ✅ 已实现 | `subagent_start` / `subagent_result` WebSocket 事件 |
| `web/server.py` — `[subagent]` 日志 | ✅ 已实现 | dispatching / result / total pipeline |
| `web/static/cinnox.html` — Trace 面板 | ✅ 已实现 | 紫色折叠面板，bot 回复下方 |
| `web/static/cinnox.html` — 实时指示器 | ✅ 已实现 | 调度中显示 ⚙️，完成显示 ✅ |
| `SKILL.md` — Step 3.5 编排规则 | ✅ 已有 | `_web_skill_text()` 保留 Step 3.5（只删 Step 1/2/7） |
| `.claude/agents/*.md` | ✅ 5 个文件就位 | product-query, region-query, copywriting, reviewer, auditor |

---

## 测试方法

每个 TC 完成后，检查两处：

1. **前端**: Bot 回复下方查看 "⚙️ Subagent Trace (N agents, X.Xs)" 面板（默认折叠，点击展开）
2. **后台**: 终端日志中搜索 `[subagent]` 前缀

后台日志格式示例：
```
[subagent] dispatching: product-query
[subagent] result from product-query: {"found":true, ...}  (3.2s)
[subagent] dispatching: copywriting
[subagent] result from copywriting: {"polished":"...", ...}  (1.8s)
[subagent] dispatching: reviewer
[subagent] result from reviewer: {"passed":true, ...}  (1.5s)
[subagent] total pipeline: 6.5s, agents=['product-query', 'copywriting', 'reviewer']
```

前端 Trace 面板示例（点击展开后）：
```
⚙️ Subagent Trace (3 agents, 6.5s)
  ✅ product-query    3.2s    found: true, 3 sources...
  ✅ copywriting      1.8s    shortened to 3 sentences...
  ✅ reviewer         1.5s    score: 11/11, passed...
```

**判断标准**: 如果 bot 回复下方没有 Subagent Trace 面板，说明编排没有生效。

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 7 |
| Passed | |
| Failed | |
| Pass Rate | |
| 平均 subagent pipeline 耗时 | |

---

## TC-S1 — product-query 调度验证

**目标**: 确认产品问题走 product-query subagent 而非直接调 kb_search.py

**步骤**:
1. 打开 Web UI (`http://localhost:8000/login`)，使用访问码登录
2. 完成 lead collection（姓名/公司/邮箱/电话）
3. 问："Does CINNOX support WhatsApp integration?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | 前端：Subagent Trace 面板出现在 bot 回复下方 | | |
| 2 | 前端：Trace 面板中有 product-query 条目 | | |
| 3 | 后台：日志有 `[subagent] dispatching:` 包含 product-query | | |
| 4 | 回答基于 KB 内容，有 source citation | | |
| 5 | Trace 面板中有 copywriting 条目 | | |
| 6 | Trace 面板中有 reviewer 条目 | | |

**记录**: Trace 面板标题显示的总耗时 = _____ s

---

## TC-S2 — region-query 调度验证

**目标**: 确认电信费率问题走 region-query subagent（而非 product-query）

**步骤**（接续 TC-S1 的 session，lead 已收集）:
1. 问："How much is a US toll-free number?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Trace 面板显示 region-query（而非 product-query） | | |
| 2 | 后台：`[subagent] dispatching:` 显示 region-query | | |
| 3 | Trace 面板显示 copywriting 和 reviewer | | |
| 4 | 回答包含 US toll-free 相关费率数据 | | |

**记录**: 总耗时 = _____ s

---

## TC-S3 — 上下文延续 + 路由验证

**目标**: 确认跟进问题能正确路由到同类 subagent

**步骤**（接续 TC-S2 的 session）:
1. 问："What about Germany?"（上下文延续）

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Trace 面板显示 region-query（正确路由，非 product-query） | | |
| 2 | 后台日志确认调度了 region-query | | |
| 3 | 回答包含 Germany/DE 相关费率数据 | | |

---

## TC-S4 — gate 未通过时不调度 subagent

**目标**: 确认 gate_cleared=false 时不派任何 KB subagent

**步骤**:
1. 开启新 session（新标签页或点 New Chat，重新登录）
2. 第一条消息直接问产品问题："How much does CINNOX cost?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Bot 回复下方 **没有** Subagent Trace 面板 | | |
| 2 | 后台日志 **没有** `[subagent]` 记录 | | |
| 3 | Bot 先问客户类型（新客户还是老客户） | | |

---

## TC-S5 — copywriting 实际工作验证

**目标**: 确认 copywriting subagent 确实对回复进行了润色

**步骤**（在 TC-S4 session 中，完成 lead collection 后）:
1. 问："Can you compare the different CINNOX plans?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Trace 面板中有 copywriting 条目 | | |
| 2 | copywriting 的 result_preview 显示有修改建议 | | |
| 3 | 最终回复不超过 4 句话（copywriting 的长度约束） | | |
| 4 | 回复不包含 banned phrases（如 "I understand your frustration"） | | |

---

## TC-S6 — reviewer 检查验证

**目标**: 确认 reviewer subagent 执行了质量检查并返回分数

**步骤**（接续任意已完成 lead 的 session）:
1. 问任意产品问题，等回答后
2. 展开 Subagent Trace 面板，查看 reviewer 条目

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Trace 面板中 reviewer 条目存在 | | |
| 2 | reviewer 的 result_preview 包含分数（如 N/11）或 pass/fail | | |
| 3 | 后台 `[subagent] result from reviewer:` 有完整检查结果 | | |

---

## TC-S7 — auditor fire-and-forget 验证

**目标**: 确认 auditor 被调度且写入了审计日志

**步骤**:
1. 完成以上任意一个产品问答后
2. 检查 Trace 面板是否有 auditor 条目
3. 在终端检查文件：

```bash
cat .claude/agent-memory/auditor/audit_log.jsonl
```

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Trace 面板显示 auditor 被调度 | | |
| 2 | audit_log.jsonl 中有新记录 | | |
| 3 | 记录包含 customer_type, domain, subagents_invoked 字段 | | |
| 4 | 记录不包含 PII（无姓名/邮箱/电话） | | |

---

## 关键观察点

测试过程中注意以下信号，即使 TC 通过也要记录：

| 观察点 | 说明 | 记录 |
|--------|------|------|
| 单个 subagent 耗时 | Trace 面板每个条目的秒数 | |
| 总 pipeline 耗时 | Trace 面板标题的总耗时（目标 <30s） | |
| 实时指示器 | 调度中是否看到 "⚙️ Subagent: xxx..." 提示 | |
| Claude 是否跳过 subagent | 有无应调度但未出现 Trace 面板的情况 | |
| max_turns 截断 | 后台日志是否有 turns 超限警告 | |
| 路径报错 | 后台日志有无 kb_search.py FileNotFoundError | |

---

## 故障排查

### 如果 Subagent Trace 面板未出现

按以下顺序检查：

1. **后台日志有无 Agent ToolUseBlock？**
   - 搜索 `[subagent] dispatching:` — 如果有日志但前端没面板，是前端 WebSocket 问题
   - 如果后台也没有，说明 Claude 没有调度 subagent

2. **Claude 为什么没调度 subagent？**
   - **SKILL.md 太长，Claude 跳过了 Step 3.5** — 最常见原因
   - **Claude 走了 fallback 路径** — SKILL.md 中有 "如果 subagent 不可用可直接调 kb_search.py"
   - **Agent 工具名称不匹配** — 检查 ToolUseBlock 的 `block.name` 是否真的是 `"Agent"`

3. **max_turns 是否足够？**
   - 当前设为 15。每个 Agent 调用 + 每个 Bash 调用各算 1 turn
   - 如果日志显示 ResultMessage 来得很早（只有 1-2 个 tool use），可能是 turns 被截断

4. **subagent 定义文件是否被识别？**
   ```bash
   ls -la .claude/agents/
   ```
   应有 5 个 .md 文件

5. **kb_search.py 路径问题？**
   - subagent 中使用 `uv run .autoservice/.claude/skills/knowledge-base/scripts/kb_search.py`
   - cwd 应为项目根目录——检查 server.py 的 `cwd=str(ROOT)`

记录失败原因和排查结果，作为修复依据。
