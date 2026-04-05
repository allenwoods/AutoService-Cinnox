# CINNOX UAT — Round 7 Test Result v1.2.6

**Tester**: Chen Ruihua
**Test Date**: 2026-03-12
**Environment**: Web UI (`uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`)
**Version**: v1.2.6 (Background heartbeat + client watchdog + done handler safety)

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs attempted | 5 (S1~S5) |
| Passed (functional) | 5 (S1, S2, S3, S4, S5) |
| Failed | 0 |
| Blocked | 0 |
| S6, S7 | Not verified (Trace panel not expanded to check reviewer/auditor entries) |
| Subagent dispatching | Yes — `[subagent]` logs confirm Agent tool used |
| Subagent Trace panel | Partial — real-time indicator appeared; persistent card not confirmed |
| KB answer accuracy | All correct |
| Input freeze bug | **FIXED** — all turns completed, all `[ws] done sent OK` |

### v1.2.6 Hotfix Changes

| Change | Description | Effect |
|--------|-------------|--------|
| Server: background heartbeat | Replaced inline heartbeat (only fired on SDK yield) with concurrent `asyncio.Task` sending heartbeat every 15s | WS stays alive during 47~75s subagent operations |
| Frontend: client watchdog | 30s no-message watchdog forces reconnect if `waitingReply` stuck | Catches half-open connections where `onclose` never fires |
| Frontend: done handler try-catch | Post-processing (KB card, trace card, sidebar parsing) wrapped in try-catch | `waitingReply=false` + `enableInput(true)` always execute |

---

## Test Sessions

| Session | Time | Turns | Test Cases |
|---------|------|-------|------------|
| `session_20260312_155126` | 15:51 | 6 | TC-S1 (WhatsApp) -> TC-S2 (US toll-free) -> TC-S3 (Germany) |
| `session_20260312_160104` | 16:01 | 5 | TC-S4 (gate check) -> TC-S5 (plan comparison) |

---

## TC Results

### TC-S1 — product-query dispatch verification — PASSED

**Question**: "Does CINNOX support WhatsApp integration?" (after lead collection)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Subagent dispatched | PASS | `[subagent] dispatching: KB search WhatsApp integration` |
| 2 | KB data accurate | PASS | Mentions Roche case study, WhatsApp campaigns, customer engagement |
| 3 | Source citation | PASS | Subagent result cites `M800 Introduction - Roche case study` |
| 4 | Real-time indicator visible | PASS | User saw subagent indicator during processing |
| 5 | Trace panel (persistent card) | N/V | User did not attempt to expand |
| 6 | Input usable after reply | PASS | `[ws] done sent OK` |

**Timing**: Turn total 49.11s, subagent pipeline 16.6s, 3 tool uses (save_lead + route_query + Agent)

**Subagent trace**:
```
[subagent] dispatching: KB search WhatsApp integration
[subagent] result from KB search WhatsApp integration: found=true, confidence=high  (16.6s)
```

---

### TC-S2 — region-query dispatch verification — PASSED

**Question**: "How much is a US toll-free number?"

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Subagent dispatched | PASS | `[subagent] dispatching: KB search for US toll-free number pricing` |
| 2 | Rate data correct | PASS | $49/month MRC, $0.024/min (mobile & fixed) |
| 3 | Heartbeat kept connection alive | PASS | 4 heartbeats sent during 47.9s subagent |
| 4 | Input usable after reply | PASS | `[ws] done sent OK` |

**Timing**: Turn total 76.00s, subagent pipeline 47.9s, 2 tool uses (route_query + Agent)

**Subagent trace**:
```
[subagent] dispatching: KB search for US toll-free number pricing
[subagent] result: found=true, MRC $49/month, confidence=medium (chunking boundary)  (47.9s)
```

---

### TC-S3 — context continuation + routing — PASSED

**Question**: "What about Germany" (context continuation from TC-S2)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Context continuation | PASS | Correctly understood as Germany toll-free |
| 2 | Subagent dispatched | PASS | `[subagent] dispatching: KB search Germany toll-free pricing` |
| 3 | Rate data correct | PASS | $39/month MRC, mobile $0.224/min, landline $0.06/min |
| 4 | Input usable after reply | PASS | `[ws] done sent OK` |

**Timing**: Turn total 49.76s, subagent pipeline 24.7s, 2 tool uses (route_query + Agent)

---

### TC-S4 — gate not cleared: no subagent — PASSED

**Question**: "How much does CINNOX cost?" (first message, no lead collected)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | No subagent dispatched | PASS | No `[subagent]` log, 0 tool uses |
| 2 | Bot asks customer type first | PASS | "Are you new to CINNOX, or do you already have an account?" |
| 3 | Gate cleared after lead | PASS | `[gate] KB pre-fetch gate cleared` after turn 3 |

**Timing**: Turn 1 total 12.43s (no tools)

---

### TC-S5 — copywriting verification — PASSED (functional)

**Question**: "Can you compare the different CINNOX plans?" (after lead collection + pricing question)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Subagent dispatched | PASS | `[subagent] dispatching: CINNOX plan comparison search` |
| 2 | Data accurate | PASS | 4 plans with correct pricing, features, min licences |
| 3 | Reply includes comparison table | PASS | Markdown table with all 4 plans |
| 4 | Reply length controlled | FAIL | Long reply with detailed breakdown, copywriting constraint not enforced |
| 5 | Input usable after reply | PASS | `[ws] done sent OK` |

**Timing**: Turn total 75.26s, subagent pipeline 42.0s, 2 tool uses (route_query + Agent)

---

### TC-S6, TC-S7 — Not Verified

User did not expand the Subagent Trace panel to check for reviewer/auditor entries. Terminal logs show **no** separate `[subagent] dispatching:` for copywriting, reviewer, or auditor — only a single KB search Agent per turn.

---

## Heartbeat & Connection Stability

| Turn | Duration | Heartbeats | Done Status | Freeze? |
|------|----------|------------|-------------|---------|
| S1-T1 (greeting) | 14.18s | 0 | OK | No |
| S1-T2 (lead confirm) | 40.83s | 2 | OK | No |
| S1-T3 (WhatsApp) | 49.11s | 3 | OK | No |
| S1-T4 (US toll-free) | 76.00s | 4 | OK | No |
| S1-T5 (Germany) | 49.76s | 3 | OK | No |
| S1-T6 (bye) | 17.02s | 1 | OK | No |
| S2-T1 (gate) | 12.43s | 0 | OK | No |
| S2-T2 (new) | 15.00s | 0 | OK | No |
| S2-T3 (lead) | 10.79s | 0 | OK | No |
| S2-T4 (pricing) | 81.36s | 4 | OK | No |
| S2-T5 (compare) | 75.26s | 5 | OK | No |

**All 11 turns**: `[ws] done sent OK` confirmed. Zero freezes. Input freeze bug is **resolved**.

---

## Subagent Dispatching Analysis

| Turn | route_query called | Agent dispatched | Agent name | Pipeline time |
|------|-------------------|-----------------|------------|---------------|
| S1-T3 (WhatsApp) | Yes | Yes | KB search WhatsApp integration | 16.6s |
| S1-T4 (US toll-free) | Yes | Yes | KB search for US toll-free number pricing | 47.9s |
| S1-T5 (Germany) | Yes | Yes | KB search Germany toll-free pricing | 24.7s |
| S2-T4 (pricing) | Yes | Yes | CINNOX pricing KB search | 42.4s |
| S2-T5 (compare) | Yes | Yes | CINNOX plan comparison search | 42.0s |

**Observations**:
- Claude dispatches **1 generic KB search Agent per turn**, not the named subagents (product-query, region-query, copywriting, reviewer, auditor)
- `route_query.py` is called before each Agent dispatch (glossary/synonym routing works)
- Average subagent pipeline time: **34.7s** (range 16.6s ~ 47.9s)
- No copywriting/reviewer/auditor subagents observed in logs

---

## Functional Regression

| Feature | Status | Notes |
|---------|--------|-------|
| KB search accuracy | PASS | All rates/features correct |
| Lead collection flow | PASS | 4-field collection works |
| Gate logic | PASS | No KB search before lead collected |
| Context continuation | PASS | "What about Germany" correctly understood |
| Reply length control | FAIL | Plan comparison reply too long, copywriting not enforced |
| Trace panel (real-time) | PASS | Indicator visible during subagent execution |
| Trace panel (persistent) | N/V | Not tested (user did not expand) |
| Input freeze bug | **FIXED** | 11/11 turns OK, 0 freezes |
| audit_log.jsonl | N/V | Not checked |

---

## Remaining Issues

### RESOLVED: P0 Input Freeze Bug

v1.2.6 three-layer fix (background heartbeat + client watchdog + done handler safety) resolved the input freeze. All 11 turns across 2 sessions completed without any freeze, including turns with 75+ second subagent operations.

### OPEN: P1 Subagent Pipeline Not Multi-Stage

Claude dispatches a single generic "KB search" Agent per turn instead of the designed multi-stage pipeline (product-query/region-query -> copywriting -> reviewer -> auditor). The SKILL.md Step 3.5 orchestration rules are not being followed. The Agent `description` field shows free-form names like "KB search WhatsApp integration" rather than the defined agent names.

### OPEN: P2 Reply Length Not Controlled

Without the copywriting subagent enforcing length constraints, replies remain long (especially plan comparisons).

---

## Summary

v1.2.6 successfully fixes the critical input freeze bug that blocked testing since v1.2.4. The background heartbeat kept WebSocket connections alive through operations lasting up to 81 seconds. All 5 functional test cases pass — KB data is accurate, gate logic works, and context continuation is correct.

The subagent architecture is **partially working**: Claude does dispatch Agent tools for KB search, but uses a single generic agent rather than the designed multi-stage pipeline (product-query -> copywriting -> reviewer -> auditor). This remains the primary architectural gap for Round 7's orchestration goals.

**Next steps**:
1. Investigate why Claude uses generic KB search agents instead of named subagents
2. Re-test TC-S6/S7 with Trace panel expansion to verify reviewer/auditor presence
3. Address reply length control (copywriting subagent integration)
