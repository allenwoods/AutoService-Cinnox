# Round 5 UAT Issues

**Date**: 2026-03-09
**Testing scope**: TC-A1 ~ TC-H2 (19 TCs, post v1.1 + v1.1.1 fix)
**Environment**: `uv run uvicorn web.server:app --host 0.0.0.0 --port 8000` (sales mode)
**Changes since Round 4**:
- v1.1: `_presearch_kb()` gate_cleared 门控 + SKILL.md 两步转人工
- v1.1.1: SKILL.md 全局 BANNED PHRASES 规则（防止自由回答触发 handoff）

---

## Issue Summary

| # | Session | TC | Severity | Description |
|---|---------|-----|----------|-------------|
| | | | | *(no issues yet)* |

---

## Issue Detail

*(Record issues as they are discovered during testing)*
