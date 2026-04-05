# CINNOX UAT — Round 7 Test Result (v1.2 Subagent Dispatching)

**Tester**: Chen Ruihua
**Test Date**: 2026-03-11
**Environment**: Web UI (`uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`)

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 7 |
| Passed | 1 (TC-S4) |
| Failed | 6 (TC-S1 ~ S3, S5 ~ S7) |
| Pass Rate | **14%** |
| Subagent Trace 面板出现 | **0 次** |
| 后台 `[subagent]` 日志 | **0 条** |

### 核心结论

**Claude 完全没有调度任何 subagent。** 所有产品/定价问题都走了 fallback 路径——直接用 Bash 调用 `kb_search.py`（或 `kb_subagent.py`），绕过了 Step 3.5 定义的 subagent 编排管线。

---

## 测试 Session 记录

本次测试产生了 2 个 session：

| Session | 时间 | Turn 数 | 对话内容 |
|---------|------|---------|---------|
| `session_20260311_142450` | 14:24 | 6 | WhatsApp? → US toll-free? → Germany? |
| `session_20260311_143642` | 14:36 | 6 | CINNOX cost? (gate test) → lead → plan comparison → DID? |

Lead 记录 2 条（均为 Sarah Mitchell / Austin Digital Agency）。

---

## TC Results

### TC-S1 — product-query 调度验证 ❌ FAILED

**问题**: "Does CINNOX support WhatsApp integration?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Subagent Trace 面板出现 | ❌ | 面板未出现 |
| 2 | 后台 `[subagent] dispatching:` 日志 | ❌ | 无 subagent 日志 |
| 3 | 回答基于 KB 内容 | ✅ | 回答正确，提到 360dialog/WhatsApp BSP |
| 4 | copywriting subagent 调度 | ❌ | 未调度 |
| 5 | reviewer subagent 调度 | ❌ | 未调度 |

**分析**: Claude 直接用 Bash 调 `kb_search.py` 获取结果并组织回答，功能正确但绕过了 subagent 管线。

---

### TC-S2 — region-query 调度验证 ❌ FAILED

**问题**: "How much is a US toll-free number?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板显示 region-query | ❌ | 面板未出现 |
| 2 | 后台日志显示 region-query | ❌ | 无 subagent 日志 |
| 3 | copywriting → reviewer 管线 | ❌ | 未调度 |
| 4 | 回答包含 US toll-free 费率 | ✅ | US$49/month, 费率数据正确 |

---

### TC-S3 — 上下文延续 + 路由验证 ❌ FAILED

**问题**: "What about Germany?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板显示 region-query | ❌ | 面板未出现 |
| 2 | 后台日志确认 region-query | ❌ | 无 subagent 日志 |
| 3 | 回答包含 Germany 费率 | ✅ | US$39/month, 数据正确 |

**亮点**: 上下文延续正常——Claude 理解 "What about Germany?" 指的是 toll-free number 价格。

---

### TC-S4 — gate 未通过时不调度 subagent ✅ PASSED

**问题**: "How much does CINNOX cost?"（未完成 lead collection）

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 无 Subagent Trace 面板 | ✅ | 正确：gate 未通过不应调度 |
| 2 | 无 `[subagent]` 日志 | ✅ | 正确 |
| 3 | Bot 先问客户类型 | ✅ | "are you new to CINNOX, or do you already have an account?" |

**注意**: 此 TC 通过是因为 Claude 本来就没用 subagent，gate 逻辑本身工作正常。

---

### TC-S5 — copywriting 实际工作验证 ❌ FAILED

**问题**: "Can you compare the different CINNOX plans?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板有 copywriting | ❌ | 面板未出现 |
| 2 | result_preview 有修改建议 | ❌ | N/A |
| 3 | 回复不超过 4 句话 | ❌ | 回复包含完整对比表 + 推荐 + 追问，远超 4 句 |
| 4 | 无 banned phrases | ✅ | 未发现 banned phrases |

**分析**: 回复虽内容正确，但长度不受控（无 copywriting 约束），印证了 subagent 未参与。

---

### TC-S6 — reviewer 检查验证 ❌ FAILED

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板有 reviewer | ❌ | 面板未出现 |
| 2 | result_preview 包含分数 | ❌ | N/A |
| 3 | 后台 reviewer 日志 | ❌ | 无 |

---

### TC-S7 — auditor fire-and-forget 验证 ❌ FAILED

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板显示 auditor | ❌ | 面板未出现 |
| 2 | audit_log.jsonl 有记录 | ❌ | 文件存在但为空 |
| 3 | 记录包含必要字段 | ❌ | N/A |
| 4 | 记录不含 PII | ❌ | N/A |

---

## Root Cause Analysis

### 根本原因：SKILL.md 中的 fallback 路径被优先选择

SKILL.md 第 438 行：

```
> **Fallback**: If subagents are unavailable (e.g., running outside Claude Code),
> you may call kb_search.py directly:
```

Claude 选择了这条 fallback 路径，直接用 Bash 调 `kb_search.py`，而不是通过 Agent 工具调度 subagent。

### 原因分析

1. **SKILL.md 中 `kb_subagent.py` 被提及 10 次**（在 Step 3 的各分支中），而 Step 3.5 的 subagent 编排规则只是作为"追加步骤"存在。Claude 在读到 Step 3 的 "run kb_subagent.py" 指令时就已经决定了执行路径，没有走到 Step 3.5。

2. **fallback 门槛太低** — "If subagents are unavailable" 的判断标准模糊。Claude 可能认为在 Web UI 模式下 subagent 不可用，或者认为 Bash 方式更简单直接。

3. **Step 编号造成歧义** — Step 3 说 "run kb_subagent.py"，Step 3.5 说 "dispatch to subagent via Agent tool"，两者描述的是同一个动作的两种实现方式，Claude 选了更直接的那个。

4. **Agent 工具虽已启用（`allowed_tools=["Bash", "Agent"]`），但 Claude 从未尝试使用它** — 说明问题不在权限层，而在 prompt 层。

### 非根本原因（已排除）

| 排除项 | 状态 |
|--------|------|
| `allowed_tools` 缺少 Agent | ✅ 已加，不是原因 |
| `max_turns` 不够 | ✅ 已改为 15，不是原因 |
| Agent 事件捕获代码 | ✅ 代码正确，只是没触发 |
| 前端 Trace 面板代码 | ✅ 代码正确，只是没数据 |
| `.claude/agents/*.md` 文件 | ✅ 5 个文件都在 |

---

## 功能回归观察

虽然 subagent 未调度，但核心功能仍然正常：

| 功能 | 状态 | 说明 |
|------|------|------|
| Lead collection | ✅ | Name → Company → Email → Phone 顺序正确 |
| Gate 逻辑 | ✅ | 未收集 lead 时先问客户类型 |
| KB 搜索 | ✅ | 产品/费率数据正确 |
| 上下文延续 | ✅ | "What about Germany?" 正确理解为 toll-free |
| 费率数据准确性 | ✅ | US $49/month, DE $39/month 与 KB 一致 |
| Source citation | ⚠️ | 提到 "product documentation" / "rate sheet" 但未列具体来源 |
| 回复长度控制 | ❌ | 无 copywriting 约束，部分回复过长 |

---

## 修复建议

### 优先级 P0：修改 SKILL.md，消除 fallback 歧义

1. **将 Step 3 中所有 `run kb_subagent.py` 替换为指向 Step 3.5 的明确指令**：
   ```
   # 原来
   → run kb_subagent.py

   # 改为
   → proceed to Step 3.5 (Subagent Orchestration) to dispatch the query
   ```

2. **删除或严格限制 fallback 路径**（第 438 行）：
   ```
   # 原来
   > **Fallback**: If subagents are unavailable (e.g., running outside Claude Code),
   > you may call kb_search.py directly

   # 改为（删除 fallback，或改为）
   > **NOTE**: Do NOT call kb_search.py directly. ALWAYS use the Agent tool
   > to dispatch to subagents as defined in Step 3.5.
   ```

3. **在 Step 3.5 开头加强制语气**：
   ```
   > **MANDATORY**: When answering any product/pricing question, you MUST
   > use the Agent tool to dispatch to subagents. Do NOT call kb_search.py
   > or kb_subagent.py via Bash directly.
   ```

### 优先级 P1：验证修复后重跑 Round 7

修改 SKILL.md 后重启 Web UI，重跑所有 7 个 TC。
