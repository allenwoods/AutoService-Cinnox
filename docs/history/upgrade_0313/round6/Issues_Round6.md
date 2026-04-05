# Round 6 Issues — Design Review

**Date**: 2026-03-10
**Scope**: Round 6 TC 设计阶段（TC-I1 ~ TC-I10），使用 brainstorming + planning-with-files + skill-creator 三个元能力完善计划
**Status**: 设计完成，尚未执行 UAT

---

## Issue Summary

| # | 来源 | Severity | TC 影响 | Description |
|---|------|----------|---------|-------------|
| 1 | 设计审查 | Medium | TC-I1 (Toll-free vs Local) | 美国地区在费率表中分 3 个子区域，TC-I1 的 toll-free/local 澄清可能还需要子区域澄清 |
| 2 | 设计审查 | Low | TC-I10 | BANNED PHRASES 的来源依据需要记录 |

---

## Issue 1: 美国地区应进一步细分子区域

### 现象

TC-I1 第 3 步测试用户回答 "US" 后 bot 应问 "toll-free or local?"。但实际上 KB 中美国费率分为 **3 个子区域**，费率不同：

| 子区域 | 来源 |
|--------|------|
| United States (mainland) | M800 VN, Call and SMS Rates.xlsx — Sheet1 |
| United States (Alaska) | M800 VN, Call and SMS Rates.xlsx — Sheet1 |
| United States (Hawaii) | M800 VN, Call and SMS Rates.xlsx — Sheet1 |

### 影响

TC-I1 的 toll-free/local 澄清之后，如果用户选了 local number，bot 理论上还应该问是 mainland/Alaska/Hawaii——但这取决于费率是否真的不同。

### 参考文档

费率数据来源：`docs/resource/OneSyn/M800 VN, Call and SMS Rates.xlsx` — Sheet1，搜索 "United States"。

### 建议

- 暂不修改 TC-I1（当前测试目标是 ambiguity detection 能力，不是费率精度）
- 记录为已知限制：如果 Round 6 测试中 bot 追问了 US 子区域，视为 **bonus behavior** 而非失败

---

## Issue 2: BANNED PHRASES 的依据来源

### 问题

TC-I10 测试 bot 不使用 "I sincerely apologize"、"I understand your frustration"、"Rest assured" 三个表达。为什么要禁止这些表达？

### 依据

BANNED PHRASES 来自两个层面的设计决策：

#### 1. 业务层面 — 真实客服对话分析

项目 `docs/resource/OneSyn/CINNOX Enquiries & Chat History 202512-20260212/` 中包含真实的客服聊天记录。其中投诉类对话（`3_historyFiles_complaint/`）显示，真实客服频繁使用这些套话：

> "We're sorry that... Rest assured, we will do our best to follow up and expedite the matter. We apologize for any inconvenience caused."
> — `Chat_History_INQ-002E7F.csv`, Turn 49

这类回复是典型的 **"empathy theater"（表演式共情）**——听起来很专业，但客户实际感受是"你在走流程，不是真的在帮我"。

#### 2. 产品设计层面 — AI bot 差异化

v1.0 upgrade-plan 的核心理念是：AI bot 不应模仿传统客服的套话模式。如果 AI bot 也说 "I sincerely apologize for the inconvenience caused"，用户无法区分是在和 AI 还是在和一个照本宣科的人工客服对话。

禁用这些表达，强制 bot 使用自然、具体的回应（如 "That's not right at all" / "Yeah, that sounds frustrating"），让对话更真实。

#### 3. 代码实现位置

- `web/server.py` L599（support mode prompt）: `❌ Say "I sincerely apologize", "I understand your frustration", "Rest assured"`
- `.claude/skills/customer-service/SKILL.md` L367-386: 完整的自然语言对照表（❌ corporate-speak → ✅ natural expression）
- `.claude/skills/marketing/SKILL.md` L385-389: 同样的禁用列表

### 结论

BANNED PHRASES 不是随意设定的——它来自真实对话数据分析 + 产品差异化策略。TC-I10 测试的是 AI bot 能否避免传统客服的套话模式，展现更自然的沟通风格。
