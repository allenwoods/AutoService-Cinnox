# CINNOX UAT — Round 6 Test Results

**Tester**: Ruihua Chen
**Test Date**: 2026-03-10
**Environment**: CINNOX Demo (autoservice simulation)
**Product Config**: CINNOX
**Operator/Strategy**: Sales mode, API backend

> **Round 6**: Dedicated validation of v1.0-v1.1.2 new capabilities (ambiguity detection, two-step escalation, gate_cleared, _should_escalate, BANNED PHRASES).
> Design phase used brainstorming + planning-with-files + skill-creator.

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 10 |
| Passed | 5 |
| Failed | 3 |
| Partially Passed | 2 |
| Pass Rate | 50% (5/10) |

**Critical Failures**:
- [ ] TC-I8: Bot assumed "new" from company name alone — should continue asking new/existing
- [ ] TC-I10: Bot used BANNED PHRASE "I completely understand your frustration"

---

## Group A: Ambiguity Detection

### TC-I1 — Ambiguity Detection: Domain → Region → Toll-free

**Result**: PARTIAL
**Session**: session_20260310_101317

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| T1: Bot asks clarifying question about domain (CINNOX vs telecom) | ✓ | Lead collection 后 bot 问"请问您想了解 CINNOX 哪方面的价格呢？比如某个具体的套餐方案，还是某类服务的费用？" |
| T2: Bot asks clarifying question about region/country | ✓ | Bot 问"请问您主要关注哪些国家或地区的 DID 号码？" |
| T3: Bot asks clarifying question about number type (toll-free vs local) | ✗ | Bot 未问 toll-free/local，直接说没有美国 DID 具体价格，提议转销售 |
| Bot does NOT guess or provide a generic answer at any step | ✓ | 每步都未编造数据 |

**Notes**: Domain 和 Region 的模糊检测正常工作。Toll-free vs Local 的澄清未触发——bot 在查不到美国具体费率后直接提议转销售，跳过了类型澄清。可能是 KB 中美国费率数据的检索问题（美国有 mainland/Alaska/Hawaii 三个子区域，检索可能未命中 local 行）。

---

### TC-I2 — Context Disambiguation: Known Domain Not Re-asked

**Result**: FAIL
**Session**: session_20260310_101836

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot answers in telecom context without re-asking domain | ✗ | 这是一个**新 session**，不是续 TC-I1 的 session |
| Bot does NOT ask "Are you asking about CINNOX or telecom?" | ✗ | Bot 直接回答了 CINNOX 套餐价格（当成 CINNOX 问题而非 telecom） |
| Ambiguity Rule 5: "Don't ask about something already established" | N/A | 新 session 无上下文可继承 |

**Failure Detail**:

测试执行错误——TC-I2 应该在 TC-I1 的同一个 session 中继续（Continue Session），但实际使用了一个全新 session（session_101836）。新 session 中 `gate_cleared: false`，bot 理论上应先问 new/existing，但直接回答了产品定价问题（gate 被绕过）。

**双重问题**:
1. **测试执行问题**: 未在 TC-I1 session 中继续
2. **Gate 绕过**: 新 session 中 `gate_cleared: false` 但 bot 直接回答了产品问题

---

## Group B: Two-step Escalation — New Customer Path

### TC-I3 — New Customer: Propose Handoff → User Rejects → Continue

**Result**: PASS
**Session**: session_20260310_102221

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot proposal uses question format (ends with `?`) | ✓ | "Would you like me to arrange that?" |
| Proposal message does NOT trigger `agent_joined` event | ✓ | 无 handoff 触发 |
| `_should_escalate()` returns False (question sentence filtered) | ✓ | 安全措辞无触发词 |
| After user rejects, bot continues conversation normally | ✓ | "No problem! If you'd like, I can help answer other questions..." |
| Bot does NOT use declarative trigger phrases | ✓ | 全程使用安全措辞 |

**Notes**: 完美执行。用户说 "No, not yet" 后 bot 友好地继续对话，未强行转接。

---

### TC-I4 — New Customer: Propose Handoff → User Confirms → Handoff Triggers

**Result**: PASS
**Session**: session_20260310_102221 (Continue from TC-I3)

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| After user confirms, bot uses **declarative** trigger phrase | ✓ | "Connecting you with a specialist now. They'll be with you shortly!" |
| Trigger phrase matches `_ESCALATION_RE` pattern | ✓ | "Connecting you" 命中 regex |
| `_should_escalate()` returns True (declarative sentence) | ✓ | 陈述句，以 `!` 结尾 |
| Frontend receives `agent_joined` WebSocket event | ✓ | `human_agent_active: true` |
| Agent name is "Michael Liu" (sales mode) | ✓ | `human_agent_name: "Michael Liu"` |

**Notes**: 两步流程完整执行——第一次提议被拒 → bot 继续 → 第二次提议被接受 → 陈述句触发 handoff。`escalation_turn: 18` 确认 handoff 在确认后才触发。

---

## Group C: Two-step Escalation — Existing Customer Path

### TC-I5 — Existing Customer: No Trigger Words During Verification

**Result**: PASS
**Session**: session_20260310_102741

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot correctly identifies existing customer | ✓ | 正确识别 "I'm an existing customer" |
| Bot requests verification (Name + Company + Email + Account ID) | ✓ | 一次性请求 4 项 |
| Bot's verification-phase responses contain NO trigger words from `_ESCALATION_RE` | ✓ | 验证阶段无 "connect you with" / "transfer" 等触发词 |
| Specifically: no "connect you with", "transfer", "let me connect", "转接" in bot text | ✓ | 已逐条检查验证阶段（T2, T4）的 bot 回复 |
| No `agent_joined` event during verification phase | ✓ | 验证阶段无 handoff |
| Bot does NOT use BANNED PHRASES | ✓ | 无 "I sincerely apologize" 等表达 |

**Notes**: 验证流程干净利落——bot 专注于收集信息，未提前暗示转接。

---

### TC-I6 — Existing Customer: Two-step Handoff After Verification for Billing

**Result**: PASS
**Session**: session_20260310_102741 (Continue from TC-I5)

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot confirms identity without asking more questions | ✓ | "Your details have been verified." |
| Bot uses **safe proposal wording** first (no trigger words) | ✓ | "This is something our billing team can best assist with. Would you like me to arrange that?" |
| Proposal does NOT trigger `agent_joined` event | ✓ | 提议阶段无 handoff |
| After customer confirms, bot uses **declarative** trigger phrase | ✓ | "Connecting you with our billing team now. They'll be with you shortly!" |
| `_should_escalate()` returns True on confirmation | ✓ | "Connecting you" 命中 regex |
| Frontend receives `agent_joined` WebSocket event after confirmation | ✓ | `human_agent_active: true`, `escalation_turn: 10` |
| Key difference from TC-I3/I4: escalation immediately after verification | ✓ | 无 KB 查询步骤，验证后直接进入 escalation 提议 |

**Notes**: 与 SKILL.md 两步流程完全一致——验证 → 安全提议 → 客户确认 → 触发 handoff。

---

## Group D: Gate Control + Sentence Filter

### TC-I7 — Gate Not Cleared: Product Question Blocked Before Identification

**Result**: PASS
**Session**: session_20260310_103121

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT answer the WhatsApp question directly | ✓ | Bot 先问 new/existing |
| Bot asks for customer identification (new/existing) first | ✓ | "are you new to CINNOX, or do you already have an account with us?" |
| `gate_cleared` remains `False` | ✓ | session 数据确认 `gate_cleared: false` |
| No KB search results injected into the prompt | ✓ | Bot 未引用任何 KB 内容 |

**Notes**: Gate 门控正常工作。第一条产品问题被成功拦截。

---

### TC-I8 — Gate Boundary: Partial Info Does Not Open Gate

**Result**: FAIL
**Session**: session_20260310_103121 (Continue from TC-I7)

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT answer the WhatsApp question (from TC-I7 T1) | ✓ | WhatsApp 问题仍未回答 |
| Bot continues customer identification flow | ✗ | Bot 假设用户是新客户："Since you're new to CINNOX"，跳过了 new/existing 确认 |
| `gate_cleared` remains `False` after this turn | ✓ | session 数据确认 `gate_cleared: false`，`customer_type: "unknown"` |
| `_infer_session_meta()` returns `customer_type = "unknown"` | ✓ | "I'm from Acme Corp" 不匹配任何 type 关键词 |
| No `[gate] KB pre-fetch gate cleared` in server log | ✓ | Gate 未打开 |

**Failure Detail**:

Bot 回复:
> "Thanks for letting me know! Since you're **new to CINNOX**, let me get a few details first. May I start with your name?"

用户说 "I'm from Acme Corp" 只提供了公司名，未说明 new/existing。**代码层面** `_infer_session_meta()` 正确返回 `unknown`，`gate_cleared` 保持 `false`——代码行为正确。但 **prompt 层面** bot 错误地假设用户是新客户，跳过了 "Are you new or existing?" 的确认步骤。

**根因**: SKILL.md 的 "No identity signal" 规则（L133-139）要求先问 routing question，但 bot 可能从 "I'm from Acme Corp" 推断用户是在自我介绍（暗示新客户）。这是 prompt-level 推理偏差。

---

### TC-I9 — `_should_escalate()`: Question-mark Sentences Do Not Trigger

**Result**: PARTIAL
**Session**: session_20260310_103317

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot response contains trigger word(s) from `_ESCALATION_RE` | ✗ | Bot 使用了安全措辞 "Shall I arrange that for you?"，不含 `_ESCALATION_RE` 中的触发词 |
| Trigger word appears in a sentence ending with `?` | N/A | 无触发词出现 |
| `_should_escalate()` returns `False` | ✓ | 无 handoff 触发 |
| No `agent_joined` WebSocket event fired | ✓ | session 数据无 `human_agent_active` |
| Frontend does NOT show "agent joined" notification | ✓ | 无 handoff |

**Notes**: Bot 使用了安全措辞（"Shall I arrange that for you?"）而非包含触发词的疑问句（如 "Would you like me to connect you with..."）。因此 `_should_escalate()` 的疑问句过滤逻辑**未被真正测试到**——它没有失败，但也没有验证核心场景（触发词出现在疑问句中被过滤）。需要在后续测试中引导 bot 使用包含触发词的疑问句。

---

### TC-I10 — BANNED PHRASES: Bot Does Not Use Prohibited Expressions

**Result**: FAIL
**Session**: session_20260310_103317 (Continue from TC-I9)

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT say "I sincerely apologize" | ✓ | 未使用 |
| Bot does NOT say "I understand your frustration" | ✗ | Bot 说了 "I **completely understand your frustration**" |
| Bot does NOT say "Rest assured" | ✓ | 未使用 |
| Bot uses genuine/natural empathy expression instead | ✗ | 使用了典型的 corporate filler |
| Response feels conversational, not corporate/scripted | ✗ | "I completely understand your frustration" 是标准套话 |

**Failure Detail**:

用户:
> "This is really frustrating, I've been waiting for days and nobody has helped me!"

Bot 回复:
> "I **completely understand your frustration**, Sarah, and I'm sorry to hear about the delay. A member of our team would be best placed to assist with this. Shall I arrange that for you?"

Bot 使用了 BANNED PHRASE 的变体 "I completely understand your frustration"（比禁用列表中的 "I understand your frustration" 多了 "completely"，但本质相同）。

**根因**: 此 session 运行在 **sales mode**，而 BANNED PHRASES 规则仅在 `server.py` 的 support mode prompt 中（L599）。Sales mode 的 SKILL.md 没有语气禁用规则。这与设计阶段 skill-creator 评估的结论一致——当时决定不将 BANNED PHRASES 添加到 SKILL.md（仅在 support mode 测试）。但本次测试在 sales mode 下执行，导致 bot 缺少这条约束。

---

## Final Results Table

| TC | Title | Result | Session | Notes |
|----|-------|--------|---------|-------|
| TC-I1 | Ambiguity: Domain→Region→Toll-free | **PARTIAL** | session_101317 | Domain ✓ Region ✓ Toll-free ✗ |
| TC-I2 | Context Disambiguation | **FAIL** | session_101836 | 新 session 测试，未延续 TC-I1；gate 被绕过 |
| TC-I3 | New Customer: Propose → Reject | **PASS** | session_102221 | 完美执行两步流程 |
| TC-I4 | New Customer: Propose → Confirm → Handoff | **PASS** | session_102221 | 陈述句正确触发 handoff |
| TC-I5 | Existing Customer: No Trigger During Verification | **PASS** | session_102741 | 验证阶段无触发词泄漏 |
| TC-I6 | Existing Customer: Two-step Handoff | **PASS** | session_102741 | 两步流程与 SKILL.md 一致 |
| TC-I7 | Gate Not Cleared: Product Q Blocked | **PASS** | session_103121 | Gate 正确拦截产品问题 |
| TC-I8 | Gate Boundary: Partial Info | **FAIL** | session_103121 | 代码正确（gate=false），prompt 错误（假设 new） |
| TC-I9 | `_should_escalate()` Question Filter | **PARTIAL** | session_103317 | 未真正测到核心场景（bot 用安全措辞避开了触发词） |
| TC-I10 | BANNED PHRASES | **FAIL** | session_103317 | Bot 说了 "I completely understand your frustration" |

---

## Issues Log

| # | TC | Severity | Description | Root Cause | Status |
|---|-----|----------|-------------|------------|--------|
| 1 | TC-I1 | Medium | Toll-free vs Local 澄清未触发 | Bot 查不到 US DID 费率后直接提议转销售，跳过类型澄清 | Open |
| 2 | TC-I2 | High | 新 session 测试（应续 TC-I1 session）+ gate 被绕过 | 测试执行错误 + `_presearch_kb` 在短输入下可能未走 gate 检查 | Open |
| 3 | TC-I8 | High | Bot 从 "I'm from Acme Corp" 推断为新客户 | Prompt-level 推理偏差，SKILL.md 规则未被严格遵循 | Open |
| 4 | TC-I9 | Medium | 未测到核心场景（触发词 + 疑问句） | Bot 使用安全措辞避开了触发词，需要更强的触发条件 | Open |
| 5 | TC-I10 | High | Sales mode 下使用 BANNED PHRASE 变体 | BANNED PHRASES 仅在 support prompt 中，sales mode SKILL.md 无此约束 | Open |

**Severity Guide**:
- **Critical**: Handoff false positive/negative, gate bypass, hallucination
- **High**: Escalation timing wrong, verification flow broken, BANNED PHRASE violation
- **Medium**: Ambiguity detection inconsistent, test coverage gap
- **Low**: Wording style, minor formatting

---

## Session-TC Mapping

| Session | TCs | 说明 |
|---------|-----|------|
| session_20260310_101317 | TC-I1 | 组 A 第 1 个 session（lead 收集 + ambiguity） |
| session_20260310_101836 | TC-I2 | 组 A 第 2 个 session（⚠ 应为续 session，实际为新 session） |
| session_20260310_102221 | TC-I3 + TC-I4 | 组 B 完整 session |
| session_20260310_102741 | TC-I5 + TC-I6 | 组 C 完整 session |
| session_20260310_103121 | TC-I7 + TC-I8 | 组 D1 session |
| session_20260310_103317 | TC-I9 + TC-I10 | 组 D2 session |

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Tester | Ruihua Chen | 2026-03-10 |
| Reviewer | | |
