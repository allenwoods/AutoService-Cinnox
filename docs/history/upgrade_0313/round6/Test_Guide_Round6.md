# CINNOX UAT — Round 6 Test Guide (New Capability Validation)

**Tester**: _______________
**Test Date**: _______________
**Environment**: CINNOX Demo (autoservice simulation)
**Product Config**: CINNOX
**Operator/Strategy**: Sales mode + Support mode, API backend

> **Round 6**: Dedicated validation of v1.0-v1.1.2 new capabilities. These TCs supplement the original 19 TCs (TC-A through TC-H) which achieved 100% pass in Round 5.
>
> **Scope**: Domain/region ambiguity detection, two-step escalation (new + existing customer paths), `gate_cleared` state machine, `_should_escalate()` sentence filter, BANNED PHRASES.
>
> **Reference**: See original `Test_Guide.md` for environment setup, session management, and severity definitions.

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 10 |
| Passed | |
| Failed | |
| Blocked / Not Run | |
| Pass Rate | |

---

## Group A: Ambiguity Detection (Prompt-level)

> **Note**: These TCs test prompt-guided behavior (SKILL.md ambiguity rules), not code-level logic. Pass criteria allow flexible wording — any clarifying question counts as a pass.

### TC-I1 — Ambiguity Detection: Domain → Region → Toll-free

**Result**: ___
**Session**: _______________

**Pre-condition**: New customer with lead collection completed (reuse TC-A1 persona or complete lead collection first).

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "价格多少？" | Bot asks: CINNOX plan or telecom rate? (domain clarification) |
| T2 | User | "telecom rates" then "DID rates?" | Bot asks: which country/region? (region clarification) |
| T3 | User | "US" | Bot asks: toll-free or local number? (type clarification) |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| T1: Bot asks clarifying question about domain (CINNOX vs telecom) | | |
| T2: Bot asks clarifying question about region/country | | |
| T3: Bot asks clarifying question about number type (toll-free vs local) | | |
| Bot does NOT guess or provide a generic answer at any step | | |

**Notes**:

---

### TC-I2 — Context Disambiguation: Known Domain Not Re-asked

**Result**: ___
**Session**: _______________ (Continue from TC-I1)

**Pre-condition**: TC-I1 completed — conversation context has established "telecom rates" as the domain.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "What about monthly fees?" | Bot answers within telecom context, does NOT re-ask "CINNOX or telecom?" |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot answers in telecom context without re-asking domain | | |
| Bot does NOT ask "Are you asking about CINNOX or telecom?" | | |
| Ambiguity Rule 5: "Don't ask about something already established" | | |

**Notes**:

---

## Group B: Two-step Escalation — New Customer Path

> **Code reference**: `_should_escalate()` at `web/server.py:692-703` — splits bot text by sentence, skips sentences ending with `?`, only triggers on declarative sentences matching `_ESCALATION_RE`.

### TC-I3 — New Customer: Propose Handoff → User Rejects → Continue

**Result**: ___
**Session**: _______________

**Pre-condition**: New session, sales mode.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1-T4 | User | Complete lead collection (name, company, email, phone) | Bot collects info normally |
| T5 | User | "What's CINNOX's SLA for 99.99% uptime in APAC region?" | Bot attempts KB search, finds insufficient answer |
| T6 | Bot | (auto) | Bot proposes handoff using **question format** (e.g., "Would you like me to connect you with...?") |
| T7 | User | "No, not yet" | Bot acknowledges and continues conversation |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot proposal uses question format (ends with `?`) | | |
| Proposal message does NOT trigger `agent_joined` event | | |
| `_should_escalate()` returns False (question sentence filtered) | | |
| After user rejects, bot continues conversation normally | | |
| Bot does NOT use declarative trigger phrases ("Connecting you with...") | | |

**Notes**:

---

### TC-I4 — New Customer: Propose Handoff → User Confirms → Handoff Triggers

**Result**: ___
**Session**: _______________ (Continue from TC-I3)

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "Actually, can you tell me about CINNOX's disaster recovery setup?" | Bot finds insufficient KB answer |
| T2 | Bot | (auto) | Bot proposes handoff again (question format) |
| T3 | User | "Yes, please" | Bot confirms and uses declarative trigger |
| T4 | Bot | (auto) | "Connecting you with our sales team." (declarative) → handoff triggers |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| After user confirms, bot uses **declarative** trigger phrase | | |
| Trigger phrase matches `_ESCALATION_RE` pattern | | |
| `_should_escalate()` returns True (declarative sentence) | | |
| Frontend receives `agent_joined` WebSocket event | | |
| Agent name is "Michael Liu" (sales mode) | | |

**Notes**:

---

## Group C: Two-step Escalation — Existing Customer Path

> **Code reference**: Existing customers follow the same two-step escalation as new customers (proposal → confirmation → handoff). The key difference is that existing customers reach the escalation point immediately after identity verification (no KB query needed for billing/fault issues). The risk is trigger words leaking into verification-phase responses.

### TC-I5 — Existing Customer: No Trigger Words During Verification

**Result**: ___
**Session**: _______________

**Pre-condition**: New session, sales mode (or support mode if available).

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "I'm an existing customer, I have a billing issue" | Bot identifies as existing customer |
| T2 | Bot | (auto) | Bot requests identity verification (Name + Company + Email + Account ID) |
| T3 | User | "My name is James Wong" | Bot acknowledges, asks for remaining info |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot correctly identifies existing customer | | |
| Bot requests verification (Name + Company + Email + Account ID) | | |
| Bot's verification-phase responses contain NO trigger words from `_ESCALATION_RE` | | |
| Specifically: no "connect you with", "transfer", "let me connect", "转接" in bot text | | |
| No `agent_joined` event during verification phase | | |
| Bot does NOT use BANNED PHRASES ("I sincerely apologize", "I understand your frustration", "Rest assured") | | |

**Notes**:

---

### TC-I6 — Existing Customer: Two-step Handoff After Verification for Billing

**Result**: ___
**Session**: _______________ (Continue from TC-I5)

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "James Wong, Pacific Bank HK, james@pb.hk, ACC-2024" | Bot receives all 4 verification fields |
| T2 | Bot | (auto) | Bot confirms identity, recognizes billing issue |
| T3 | Bot | (auto) | Bot proposes escalation: "This is something our billing team can best assist with. Would you like me to arrange that?" (safe wording, no trigger) |
| T4 | User | "Yes, please" | Customer confirms |
| T5 | Bot | (auto) | Bot sends trigger: "Connecting you with our billing team now." (declarative) → handoff triggers |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot confirms identity without asking more questions | | |
| Bot uses **safe proposal wording** first (no trigger words in T3) | | |
| Proposal does NOT trigger `agent_joined` event | | |
| After customer confirms, bot uses **declarative** trigger phrase (T5) | | |
| `_should_escalate()` returns True on T5 | | |
| Frontend receives `agent_joined` WebSocket event after T5 | | |
| **Key difference from TC-I3/I4**: Escalation happens immediately after verification — no KB query failure needed to trigger proposal | | |

**Notes**:

---

## Group D: Gate Control + Sentence Filter

### TC-I7 — Gate Not Cleared: Product Question Blocked Before Identification

**Result**: ___
**Session**: _______________

**Pre-condition**: New session, sales mode. First message is a product question.

> **Code reference**: `gate_cleared` initialized as `False` at `server.py:1113`. `_presearch_kb()` at L85-94 skips KB injection when `gate_cleared=False`.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "Does CINNOX support WhatsApp?" | Bot does NOT answer the product question |
| T2 | Bot | (auto) | Bot asks: new or existing customer? |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT answer the WhatsApp question directly | | |
| Bot asks for customer identification (new/existing) first | | |
| `gate_cleared` remains `False` (verify via server log: no `[gate]` message) | | |
| No KB search results injected into the prompt | | |

**Difference from TC-B1**: TC-B1 verifies bot CAN answer after lead collection; TC-I7 verifies bot CANNOT answer before identification.

**Notes**:

---

### TC-I8 — Gate Boundary: Partial Info Does Not Open Gate

**Result**: ___
**Session**: _______________ (Continue from TC-I7)

> **Code reference**: `_infer_session_meta()` at L317-362 scans user messages for type keywords. "I'm from Acme Corp" contains no type keyword → returns `unknown` → gate stays closed.
>
> **Edge case**: If bot asks for email in response, the fallback at L354-360 may infer `new_customer` on the NEXT turn. This TC tests the state IMMEDIATELY after user provides only company name.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "I'm from Acme Corp" | Bot continues asking for customer type |
| T2 | Bot | (auto) | Bot asks: are you a new customer or existing customer? |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT answer the WhatsApp question (from TC-I7 T1) | | |
| Bot continues customer identification flow | | |
| `gate_cleared` remains `False` after this turn | | |
| `_infer_session_meta()` returns `customer_type = "unknown"` (company name alone is not a type keyword) | | |
| No `[gate] KB pre-fetch gate cleared` in server log | | |

**Notes**:

---

### TC-I9 — `_should_escalate()`: Question-mark Sentences Do Not Trigger

**Result**: ___
**Session**: _______________

**Pre-condition**: New session, new customer with lead collection completed.

> **Code reference**: `_should_escalate()` at L698-701 — `if sentence.strip().endswith(('?', '？')): continue` — skips question sentences even if they contain trigger words.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1-T4 | User | Complete lead collection | Normal |
| T5 | User | Ask a question KB can partially answer (e.g., "What integrations does CINNOX support with enterprise CRM systems?") | Bot answers from KB with partial info |
| T6 | Bot | (auto) | Bot's response includes a question like "Would you like me to connect you with our team for more details?" |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot response contains trigger word(s) from `_ESCALATION_RE` (e.g., "connect you with") | | |
| Trigger word appears in a sentence ending with `?` | | |
| `_should_escalate()` returns `False` | | |
| No `agent_joined` WebSocket event fired | | |
| Frontend does NOT show "agent joined" notification | | |

**Notes**:

---

### TC-I10 — BANNED PHRASES: Bot Does Not Use Prohibited Expressions

**Result**: ___
**Session**: _______________ (Continue from TC-I9, or new session in support mode)

> **Code reference**: BANNED PHRASES defined in server.py support mode prompt at L599:
> `❌ Say "I sincerely apologize", "I understand your frustration", "Rest assured"`

**Pre-condition**: Trigger an empathy scenario — user expresses dissatisfaction or frustration.

**Dialogue Script**:

| Turn | Actor | Message | Expected Bot Behavior |
|------|-------|---------|----------------------|
| T1 | User | "This is really frustrating, I've been waiting for days and nobody has helped me!" | Bot responds with genuine empathy |
| T2 | Bot | (auto) | Bot uses natural empathy (e.g., "That's not right at all" / "Yeah, that sounds frustrating") |

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT say "I sincerely apologize" | | |
| Bot does NOT say "I understand your frustration" | | |
| Bot does NOT say "Rest assured" | | |
| Bot uses genuine/natural empathy expression instead | | |
| Response feels conversational, not corporate/scripted | | |

**Notes**:

---

## Session Dependency Diagram

```
Group A: [TC-I1] → [TC-I2]              (1 session, sales mode)
Group B: [TC-I3] → [TC-I4]              (1 session, sales mode)
Group C: [TC-I5] → [TC-I6]              (1 session, sales/support mode)
Group D: [TC-I7] → [TC-I8]              (1 session, sales mode)
         [TC-I9] → [TC-I10]             (1 session, sales → support trigger)
```

**Total**: 5 sessions, 10 TCs. Groups are independent — can be tested in parallel.

---

## Final Results Table

| TC | Title | Result | Notes |
|----|-------|--------|-------|
| TC-I1 | Ambiguity Detection: Domain→Region→Toll-free | | |
| TC-I2 | Context Disambiguation | | |
| TC-I3 | New Customer: Propose → Reject | | |
| TC-I4 | New Customer: Propose → Confirm → Handoff | | |
| TC-I5 | Existing Customer: No Trigger During Verification | | |
| TC-I6 | Existing Customer: Two-step Handoff After Verification | | |
| TC-I7 | Gate Not Cleared: Product Q Blocked | | |
| TC-I8 | Gate Boundary: Partial Info | | |
| TC-I9 | `_should_escalate()` Question Filter | | |
| TC-I10 | BANNED PHRASES | | |

---

## Issues Log

| # | TC | Severity | Description | Root Cause | Status |
|---|-----|----------|-------------|------------|--------|
| | | | | | |

**Severity Guide**:
- **Critical**: Handoff false positive/negative, gate bypass, hallucination
- **High**: Escalation timing wrong, verification flow broken
- **Medium**: Ambiguity detection inconsistent, empathy tone off
- **Low**: Wording style, minor formatting

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Tester | | |
| Reviewer | | |
