# CINNOX UAT — Round 7 Test Result v1.2.4

**Tester**: Chen Ruihua
**Test Date**: 2026-03-11
**Environment**: Web UI (`uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`)
**Version**: v1.2.4（`/api/kb_search` 端点阻断 + v1.2.1~v1.2.3 全部修复）

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs attempted | 5 (S1~S5) |
| Passed (功能) | 4 (S1, S2, S3, S4) |
| Failed (功能) | 0 |
| Blocked (前端冻结) | 1 (S5 后输入框不可用) |
| S6, S7 | 未测（被 S5 冻结阻断） |
| Subagent Trace 面板 | ❌ 未出现 |
| KB 回答准确性 | ✅ 全部正确 |

### Hotfix 版本演进

| 版本 | 修改 | 效果 |
|------|------|------|
| v1.2 | 初始 subagent 架构 | ❌ Claude 完全不调 subagent |
| v1.2.1 | SKILL.md 删 fallback、加 MANDATORY | ❌ Claude 用 pre-fetch 数据直接回答 |
| v1.2.2 | 禁用 pre-fetch + 重写 WEB_KB_OVERRIDE | ⚠️ Claude 调了 Agent 工具（看到 subagent 字样），但 Trace 面板不渲染 |
| v1.2.3 | `in_subagent` 过滤 subagent 内部消息 | ⚠️ 未被触发（Claude 回退到 curl） |
| v1.2.4 | 阻断 `/api/kb_search` 端点 | ✅ KB 数据正确获取，但 Trace 面板仍未出现 + 输入框冻结 bug |

---

## 测试 Session 记录

| Session | 时间 | Turn 数 | 测试 TC |
|---------|------|---------|--------|
| `session_20260311_161549` | 16:15 | 6 | TC-S1 (WhatsApp) → TC-S2 (US toll-free) → TC-S3 (Germany) |
| `session_20260311_163616` | 16:36 | 5 | TC-S4 (gate) → TC-S5 (plan comparison) → **输入框冻结** |

---

## TC Results

### TC-S1 — product-query 调度验证 ✅ PASSED (功能)

**问题**: "Does CINNOX support WhatsApp integration?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 回答基于 KB 内容 | ✅ | 提到 360dialog、WhatsApp Campaigns、WhatsApp OTP API |
| 2 | 数据准确 | ✅ | WhatsApp add-on 价格 $100/month 来自 KB |
| 3 | source citation | ⚠️ | "product documentation" 泛称，未列具体来源 |
| 4 | Trace 面板 | ❌ | 未出现 |

---

### TC-S2 — region-query 调度验证 ✅ PASSED (功能)

**问题**: "How much is a US toll-free number?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 费率数据正确 | ✅ | $49/month, $0.024/min |
| 2 | DID 对比数据 | ✅ | US DID $19/month 对比 |
| 3 | Trace 面板 | ❌ | 未出现 |

---

### TC-S3 — 上下文延续 + 路由验证 ✅ PASSED (功能)

**问题**: "what about germany"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 上下文延续 | ✅ | 正确理解为 Germany toll-free |
| 2 | 费率数据正确 | ✅ | $39/month, mobile $0.224/min, landline $0.06/min |
| 3 | Trace 面板 | ❌ | 未出现 |

---

### TC-S4 — gate 未通过时不调度 subagent ✅ PASSED

**问题**: "How much does CINNOX cost"（未完成 lead）

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | 无 Trace 面板 | ✅ | 正确 |
| 2 | Bot 先问客户类型 | ✅ | "Are you new to CINNOX, or do you already have an account?" |

---

### TC-S5 — copywriting 实际工作验证 ⚠️ BLOCKED

**问题**: "Can you compare the different CINNOX plans?"

| # | 检查 | 结果 | 备注 |
|---|------|------|------|
| 1 | Bot 回复内容 | ✅ | 详细对比表 + 推荐，数据正确 |
| 2 | 回复长度 | ❌ | 远超 4 句，copywriting 约束未生效 |
| 3 | Trace 面板 | ❌ | 未出现 |
| 4 | **输入框冻结** | 🔴 BUG | Bot 回复后输入框变为不可输入，无法继续对话 |

**BUG 详情**: Bot 成功回复了 plan comparison 内容，但之后输入框无法输入。可能原因：
- `done` WebSocket 事件未发送（SDK 异常或 max_turns 耗尽）
- `in_subagent` 状态卡在 True 导致 ResultMessage 处理异常
- 需要终端日志确认具体原因

---

### TC-S6, TC-S7 — 未测

被 TC-S5 输入框冻结阻断。

---

## 功能回归观察

| 功能 | 状态 | 说明 |
|------|------|------|
| KB 搜索准确性 | ✅ | 所有费率/功能数据正确（WhatsApp $100/mo, US TF $49/mo, DE TF $39/mo） |
| Lead collection | ✅ | 流程正确 |
| Gate 逻辑 | ✅ | 未收集 lead 时先问客户类型 |
| 上下文延续 | ✅ | "what about germany" 正确理解 |
| KB miss 处理 | N/A | 本轮未测 |
| 回复长度控制 | ❌ | plan comparison 过长 |
| Trace 面板 | ❌ | 从未出现 |
| 输入框冻结 | 🔴 BUG | 新出现的问题 |
| audit_log.jsonl | ❌ | 仍为空 |

---

## 遗留问题

### P0: 输入框冻结 BUG

Bot 回复完成后 `done` 事件可能未发送，导致 `enableInput(true)` 未执行。
需要终端日志定位：是 SDK 异常、max_turns 耗尽、还是 `in_subagent` 状态卡住。

### P0: Trace 面板从未出现

尽管 v1.2.2 测试中确认 Claude 使用了 Agent 工具（看到 subagent 字样），v1.2.4 测试中用户未再看到。可能原因：
1. Claude 在 `/api/kb_search` 被阻断后，改用 Agent 工具但 `subagent_start` 事件被 `in_subagent` 逻辑误跳
2. 或 Claude 找到了其他获取 KB 数据的路径（如直接读文件）
3. 需要终端日志确认 Claude 到底用了什么工具

### P1: audit_log.jsonl 仍为空

auditor subagent 可能从未被调度。

### P2: 回复长度不受控

copywriting subagent 的长度约束未生效。

---

## 总结

v1.2.4 的 `/api/kb_search` 端点阻断可能生效了——KB 数据通过某种路径（可能是 Agent subagent）正确获取。但**可观测性目标未达成**：Trace 面板从未渲染，无法确认 subagent 编排的具体工作方式。新增输入框冻结 BUG 阻断了进一步测试。

**下一步建议**：
1. 修复输入框冻结 BUG（最高优先级）
2. 重跑测试并保留完整终端日志，定位 Trace 面板不渲染的原因
3. 考虑简化方案：可能需要重新审视 subagent 架构在 Web UI 模式下的可行性
