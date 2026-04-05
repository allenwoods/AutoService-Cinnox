# Round 4 UAT Issues — Root Cause Analysis

**Date**: 2026-03-09
**Testing scope**: TC-A1 ~ TC-B3 (测试暂停，发现 3 个结构性问题)
**Environment**: `uv run uvicorn web.server:app --host 0.0.0.0 --port 8000` (sales mode)

---

## Issue Summary

| # | Session | TC | Severity | Description |
|---|---------|-----|----------|-------------|
| 1 | session_20260309_112339 | TC-B2 | High | Bot 回答完问题后直接转人工，未等客户确认 |
| 1b | session_20260309_111337 | TC-A4 | Medium | 同上：推荐转人工后应等客户确认 |
| 2 | session_20260309_111916 | TC-B1 | Critical | 没有识别客户身份/收集信息就直接回答产品问题 |
| 3 | session_20260309_112738 | TC-B3 | High | 没有收集客户信息就提议转人工 |

---

## Issue 1: 转人工不等客户确认

### 现象

session_112339（TC-B2 高流量银行）：Bot 在回答完"高流量呼叫"问题后，最后一句直接说：
> "I'm connecting you with our sales team now — they'll be able to walk you through capacity planning and pricing for your volume. They'll be with you shortly!"

没有问客户是否需要转人工，直接触发了 human agent handoff。

session_111337（TC-A4 现有客户产品咨询）：Bot 回答了 CRM/API 集成问题后，问"Would you like me to connect you with a specialist?"——但这条消息触发了 `_ESCALATION_RE` 正则，自动切换到了 human agent。

### 根因

**双重问题**：

1. **SKILL.md 缺失**：当前 SKILL.md 的升级规则是"recommend 转人工 → 直接转"，没有"等客户确认"的步骤。这是**新需求**（用户反馈：浪费人工资源）。

2. **server.py `_ESCALATION_RE` 自动触发**（第 681-684 行）：
   ```python
   _ESCALATION_RE = re.compile(
       r'please hold|let me connect|connecting you|transfer|connect you with|will be right with you'
       ...
   )
   ```
   只要 bot 回复中包含这些短语，server.py **立即**触发 human agent 接管。即使 SKILL.md 改成"先问客户"，bot 说"Would you like me to **connect you with** a specialist?"也会被 regex 匹配并自动转人工。

### 影响范围

所有通过 web 测试的 session 都受影响：TC-B2, TC-C2 (volume pricing), TC-E1, TC-E2, TC-F1, TC-F2。

---

## Issue 2: 跳过客户识别直接回答（pre-fetched KB 短路门控）

### 现象

session_111916（TC-B1 WhatsApp）：用户第一条消息"Does CINNOX support WhatsApp integration?"，bot 直接回答了 WhatsApp 功能——完全跳过了：
1. 客户类型识别（新客户/老客户？）
2. Lead 信息收集（Name/Company/Email/Phone）
3. MANDATORY GATE 检查

### 根因

`web/server.py` 第 85-113 行的 `_presearch_kb()` 函数：

```python
def _presearch_kb(user_text: str, top_k: int = 3):
    # Skip injection for very short inputs (greetings, single words)
    if len(user_text.strip()) < 12:
        return user_text, 0
    # ... search KB ...
    augmented = f"{user_text}\n\n---\n🔍 KB Context (pre-fetched):\n{injected}\n---"
    return augmented, len(results)
```

**每条用户消息（>12 字符）都会自动搜索 KB 并注入结果到 prompt 中。** Claude 看到消息里已经有 KB 答案，倾向于直接使用——即使 SKILL.md 的 MANDATORY GATE 明确要求"先收集客户信息再查 KB"。

这是 **prompt 竞争**：SKILL.md 说"不许查 KB"，但 KB 结果已经出现在 prompt 中了。结果 = SKILL.md 的门控规则被短路。

### 影响范围

所有新 session 的第一条产品/定价问题都受影响。这是 TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 失败的根因。

---

## Issue 3: 跳过信息收集直接转人工

### 现象

session_112738（TC-B3 不存在功能）：用户问"Do you support hologram video calling?"，bot 回复说功能不在文档中并提议转人工——完全跳过了客户识别和信息收集。

### 根因

与 Issue 2 相同：`_presearch_kb()` 在第一条消息就搜索了 KB，没有命中结果。Claude 按反幻觉规则（正确）说"not in our documentation"，但跳过了客户识别门控——因为 pre-fetch 已经把它带入了"KB 回答"流程。

---

## 根因汇总

```
┌─────────────────────────────────────────────┐
│          用户发送第一条消息                      │
└──────────────┬──────────────────────────────┘
               │
        ┌──────▼──────┐
        │ _presearch_ │  ← server.py 自动执行
        │   kb()      │    不管是否过了 MANDATORY GATE
        └──────┬──────┘
               │ KB 结果注入到 user message
        ┌──────▼──────┐
        │  Claude     │  ← 看到 KB 结果已在眼前
        │  跳过门控   │    直接使用结果回答
        └──────┬──────┘
               │
        ┌──────▼──────────────┐
        │ _ESCALATION_RE      │  ← 如果回复中有"connect"
        │ 自动触发 human agent │    不等客户确认
        └─────────────────────┘
```

**核心矛盾**：upgrade-plan.md 说"web/server.py 本次不动"，但 server.py 的 pre-fetch 机制和 escalation regex 直接导致了 SKILL.md 门控失效。**不修改 server.py 就无法通过 TC**。

---

## 关联 Session 文件

| Session | TC | 问题 |
|---------|-----|------|
| [session_20260309_111337.json](../../../.autoservice/database/knowledge_base/sessions/session_20260309_111337.json) | TC-A4 | Issue 1 |
| [session_20260309_111916.json](../../../.autoservice/database/knowledge_base/sessions/session_20260309_111916.json) | TC-B1 | Issue 2 |
| [session_20260309_112339.json](../../../.autoservice/database/knowledge_base/sessions/session_20260309_112339.json) | TC-B2 | Issue 1 |
| [session_20260309_112738.json](../../../.autoservice/database/knowledge_base/sessions/session_20260309_112738.json) | TC-B3 | Issue 3 |
