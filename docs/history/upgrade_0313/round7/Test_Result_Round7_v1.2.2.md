# CINNOX UAT — Round 7 Test Result v1.2.2 (Subagent Dispatching)

**Tester**: Chen Ruihua
**Test Date**: 2026-03-11
**Environment**: Web UI (`uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`)
**Version**: v1.2.2（SKILL.md 修复 + WEB_KB_OVERRIDE 修复 + pre-fetch 禁用）

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 7 |
| Passed | 1 (TC-S4) |
| Partially Passed | 3 (TC-S1, S2, S3) |
| Failed | 3 (TC-S5, S6, S7) |
| Pass Rate | **14% full pass, 57% partial** |
| Subagent 调度 | ✅ **确认发生**（前端看到 subagent 字样） |
| Subagent Trace 面板 | ❌ 未出现（前端 bug） |
| 后台 `[subagent] dispatching:` 日志 | ✅ 出现 |
| auditor audit_log.jsonl | ❌ 仍为空 |

### 关键进展（对比 v1.2 Round 7 首测）

| 指标 | v1.2 首测 | v1.2.2 |
|------|----------|--------|
| Claude 调度 subagent | ❌ 完全没有 | ✅ 确认调度了 |
| 前端 subagent_start 事件 | ❌ 无 | ✅ 看到 "subagent" 字样 |
| 前端 Trace 面板 | ❌ 无 | ❌ 未渲染（前端 bug） |
| KB 回答正确性 | ✅ | ✅ |

### 核心结论

**Subagent 编排已生效。** v1.2.1 的 SKILL.md 修复 + v1.2.2 的 pre-fetch 禁用成功让 Claude 使用 Agent 工具调度 subagent。但 Trace 面板未渲染，需调查 `subagent_result` 事件是否到达前端。

---

## 测试 Session 记录

| Session | 时间 | Turn 数 | 测试 TC |
|---------|------|---------|--------|
| `session_20260311_151437` | 15:14 | 5 | TC-S1 (WhatsApp) → TC-S2 (US toll-free) → TC-S3 (Germany) |
| `session_20260311_153649` | 15:36 | 6 | TC-S4 (gate) → TC-S5 (plan comparison) → TC-S6/S7 (hologram = KB miss) |

---

## TC Results

### TC-S1 — product-query 调度验证 ⚠️ PARTIAL

**问题**: "Does CINNOX support WhatsApp integration?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Subagent 被调度 | ✅ | 前端显示 subagent 字样 |
| 2 | Trace 面板可展开 | ❌ | 面板未渲染 |
| 3 | 回答基于 KB 内容 | ✅ | 提到 360dialog、WhatsApp BSP、Campaigns |
| 4 | source citation | ⚠️ | 说 "product documentation" 但无具体来源名 |

**回答质量**: 完整准确，提到 WhatsApp Business connectivity、WhatsApp Campaigns、WhatsApp Reporting。

---

### TC-S2 — region-query 调度验证 ⚠️ PARTIAL

**问题**: "How much is a US toll-free number?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Subagent 被调度 | ✅ | 前端显示 subagent 字样 |
| 2 | Trace 面板可展开 | ❌ | 面板未渲染 |
| 3 | 费率数据正确 | ✅ | US$49/month, $0.024/min |

---

### TC-S3 — 上下文延续 + 路由验证 ⚠️ PARTIAL

**问题**: "What about Germany?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Subagent 被调度 | ✅ | 前端显示 subagent 字样 |
| 2 | Trace 面板可展开 | ❌ | 面板未渲染 |
| 3 | 上下文延续正确 | ✅ | 理解为 Germany toll-free |
| 4 | 费率数据正确 | ✅ | US$39/month, $0.224/min mobile |

---

### TC-S4 — gate 未通过时不调度 subagent ✅ PASSED

**问题**: "How much does CINNOX cost?"（未完成 lead collection）

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 无 Subagent Trace 面板 | ✅ | 正确 |
| 2 | 无 subagent 字样 | ✅ | 正确 |
| 3 | Bot 先问客户类型 | ✅ | "Are you new to CINNOX, or do you already have an account?" |

---

### TC-S5 — copywriting 实际工作验证 ❌ FAILED (未验证)

**问题**: "Can you compare the different CINNOX plans?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板有 copywriting | ❌ | 面板未渲染，无法确认 |
| 2 | 回复不超过 4 句话 | ❌ | 回复包含完整对比表 + 推荐 + 追问 |
| 3 | 无 banned phrases | ✅ | |

**注意**: 回复很长，但无法确认是否经过 copywriting——Trace 面板不可用。

---

### TC-S6 — reviewer 检查验证 ❌ FAILED (未验证)

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板有 reviewer | ❌ | 面板未渲染 |
| 2 | result_preview 包含分数 | ❌ | 无法确认 |

---

### TC-S7 — auditor fire-and-forget 验证 ❌ FAILED

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Trace 面板显示 auditor | ❌ | 面板未渲染 |
| 2 | audit_log.jsonl 有记录 | ❌ | 文件仍为空 |

---

## 功能回归观察

| 功能 | 状态 | 说明 |
|------|------|------|
| Subagent 调度 | ✅ | 前端看到 subagent 字样，确认 Agent 工具被使用 |
| Lead collection | ✅ | 流程正常 |
| Gate 逻辑 | ✅ | 未收集 lead 时先问客户类型 |
| KB 搜索准确性 | ✅ | WhatsApp、US/DE 费率数据正确 |
| 上下文延续 | ✅ | "What about Germany?" 正确理解 |
| KB miss 处理 | ✅ | "hologram video call" → 正确回答不支持 |
| 回复长度控制 | ❌ | 部分回复仍然过长 |
| Trace 面板渲染 | ❌ | subagent_start 到达前端但面板未出现 |

---

## 遗留问题

### P0: Trace 面板未渲染

**现象**: `subagent_start` WebSocket 事件到达前端（显示 "subagent" 字样），但 `done` 时 Trace 面板未出现。

**可能原因**:
1. `subagent_result` 事件未发送——Agent 工具的 `UserMessage.tool_use_result` 可能为 None（结果在 `content` blocks 中）
2. `done` 事件的 `subagent_trace` 为空数组
3. 前端 `pendingSubagentTrace` 没被填充

**下一步**: 已添加 `[debug]` 日志，重启后重测一次，查看 SDK 消息格式。

### P1: audit_log.jsonl 为空

auditor subagent 可能未被调度，或调度了但写入失败。需 Trace 面板或后台日志确认。

### P2: 回复长度

copywriting subagent 的长度约束可能未生效。需确认 copywriting 是否真的被调度。
