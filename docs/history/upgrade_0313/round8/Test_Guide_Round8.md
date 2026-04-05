# CINNOX UAT — Round 8 测试指南

**Tester**: _______________
**Test Date**: _______________
**Environment**: Web UI
**启动命令**: `uv run uvicorn web.server:app --host 0.0.0.0 --port 8000`
**版本**: v1.2.7

> **Round 8 目标**: 验证 Glossary 集成效果（查询扩展、术语快速通道）+ v1.2.7 国家/地区名修复 + Round 7 遗留问题回归。

---

## 前置条件

- [ ] KB 已就绪（547 chunks）——用 `/knowledge-base` 确认
- [ ] Web UI 启动成功——浏览器打开 `http://localhost:8000/login`
- [ ] Glossary 文件存在：

```
.claude/skills/cinnox-demo/references/
├── glossary.json        (355 条术语)
└── synonym-map.json     (37 条映射)
```

- [ ] route_query.py 已更新（含 `COUNTRY_ALIAS_MAP`、`AMBIGUOUS_COUNTRIES`、`_expand_query`、`_is_glossary_only`）
- [ ] 5 个 subagent 定义文件存在

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 15 (A 组 4 + B 组 3 + C 组 3 + D 组 2 + E 组 3) |
| A 组 — Glossary 集成 | /4 |
| B 组 — 可观测性回归 | /3 |
| C 组 — KB 准确性回归 | /3 |
| D 组 — Glossary Phase 4-5 | /2 |
| E 组 — 国家/地区名修复 (v1.2.7) | /3 |
| Pass Rate | |

---

## A 组 — Glossary 集成验证

> 验证 v1.2.4 已实现的 Glossary Phase 1-3 功能。
> **注意**: synonym-map 当前包含 37 条映射，均为**缩写展开**和**全称标准化**（如 IVR→Interactive Voice Response, DID→Direct Inward Dialing）。不包含口语词→官方术语映射（如 "group call"→"Broadcast Call Enquiry"）。测试用例基于实际数据设计。

### TC-G1 — 查询扩展验证（缩写展开）

**目标**: 确认用缩写/简称提问时，synonym-map 自动展开为官方全称，提升 KB 检索命中率。

**前置**: 完成 lead collection。

**步骤**:
1. 问："Tell me about IVR features"
   - synonym-map 应将 "ivr" 扩展为 "Interactive Voice Response (IVR)"
2. 问："What is the difference between DID and VN?"
   - synonym-map 应将 "did" 扩展为 "DID (Direct Inward Dialing)"，"vn" 扩展为 "Virtual Number (VN)"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | IVR 问题得到了关于 Interactive Voice Response 的准确回答 | | |
| 2 | 回答内容基于 KB 数据，非泛泛而谈 | | |
| 3 | DID vs VN 问题得到了基于 KB 的对比或分别说明 | | |
| 4 | 后台日志中 `expanded_query` 包含展开后的全称 | | |

---

### TC-G2 — 术语快速通道验证

**目标**: 确认纯术语定义问题（"What is X?"）跳过 subagent，直接返回 Glossary 定义。

**步骤**:
1. 问："What is DID?"
2. 问："What does IVR mean?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | "What is DID?" 得到准确的 DID 定义（Direct Inward Dialling） | | |
| 2 | 回复末尾有追问引导（如"想了解 DID 的价格或可用地区吗？"） | | |
| 3 | "What does IVR mean?" 得到准确的 IVR 定义 | | |
| 4 | 响应速度是否明显快于普通 KB 查询（主观判断） | | |

**记录**: 响应速度感受（快/一般/慢）？______

---

### TC-G3 — 复杂意图不触发快速通道

**目标**: 确认包含复杂意图的术语问题（如 pricing、comparison）不走快速通道，而是走正常 subagent 流程。

**步骤**:
1. 问："How much does DID cost in the US?"
2. 问："Compare DID and Virtual Number pricing"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | "DID cost" 问题返回了具体费率数据（非仅定义） | | |
| 2 | 费率数据准确（US DID MRC=$19/month） | | |
| 3 | "Compare" 问题提供了对比信息而非仅术语定义 | | |
| 4 | 回答内容深度超过简单定义，包含实际产品信息 | | |

---

### TC-G4 — 多缩写查询扩展

**目标**: 确认包含多个缩写的复合问题能同时扩展。

**步骤**:
1. 问："Does CINNOX support IVR with DTMF input for toll-free numbers?"
   - synonym-map 应将 "ivr" → "Interactive Voice Response (IVR)"，"dtmf" → "DTMF (Dual-tone multi-frequency signaling)"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Bot 理解了问题并给出相关回答 | | |
| 2 | 回答涉及 IVR 和 DTMF 相关功能 | | |
| 3 | 回答基于 KB 数据而非泛泛描述 | | |

**记录**: `expanded_query` 是否同时包含两个术语的展开形式？______

---

## B 组 — Subagent 可观测性回归

> 验证 Round 7 遗留的前端展示问题。如相关 bug 尚未修复，标记为 N/A。

### TC-O1 — Trace 面板渲染验证

**目标**: 确认 subagent 被调度后，前端 Subagent Trace 面板正确渲染。

**前置**: 完成 lead collection。

**步骤**:
1. 问任意产品问题（如 "Does CINNOX support WhatsApp?"）
2. 检查 bot 回复下方是否出现 Subagent Trace 面板

**检查项**:

| # | 检查 | 通过/失败/N/A | 备注 |
|---|------|-------------|------|
| 1 | Trace 面板出现在 bot 回复下方 | | |
| 2 | 面板显示 subagent 名称和耗时 | | |
| 3 | 后台日志有 `[subagent]` 记录 | | |

**如果 Trace 面板未出现**：检查后台日志中 Claude 使用的工具是什么（Agent / Bash / 其他），记录在备注中。

---

### TC-O2 — 输入框冻结回归测试

**目标**: 确认 Round 7 发现的输入框冻结 bug 是否已修复。

**步骤**:
1. 在一个 session 中连续问 3 个以上产品问题
2. 每次回复后检查输入框是否可用

**检查项**:

| # | 检查 | 通过/失败/N/A | 备注 |
|---|------|-------------|------|
| 1 | 连续 3 次问答后输入框仍可输入 | | |
| 2 | 无需刷新页面即可继续对话 | | |
| 3 | 后台日志无 `done` 事件缺失警告 | | |

**如果冻结复现**：记录在第几轮问答后冻结，以及当时的问题内容。

---

### TC-O3 — audit_log.jsonl 写入验证

**目标**: 确认 auditor subagent 被调度并写入了审计日志。

**步骤**:
1. 完成至少 1 个产品问答
2. 检查审计日志文件：

```bash
cat .claude/agent-memory/auditor/audit_log.jsonl
```

**检查项**:

| # | 检查 | 通过/失败/N/A | 备注 |
|---|------|-------------|------|
| 1 | audit_log.jsonl 中有新记录 | | |
| 2 | 记录包含 customer_type, domain, subagents_invoked 字段 | | |
| 3 | 记录不包含 PII（无姓名/邮箱/电话） | | |

---

## C 组 — KB 准确性回归

> 确保 Glossary 集成不影响已有 KB 回答质量。

### TC-K1 — 产品功能问答准确性

**前置**: 完成 lead collection。

**步骤**:
1. 问："Does CINNOX support WhatsApp integration?"
2. 问："What video conferencing features does CINNOX have?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | WhatsApp 回答包含具体功能（360dialog, Campaigns, OTP API） | | |
| 2 | WhatsApp add-on 价格 $100/month（Round 7 已验证数据） | | |
| 3 | Video 回答基于 KB 数据，提及 CINNOX 实际功能 | | |

---

### TC-K2 — 区域费率问答准确性

**步骤**:
1. 问："How much is a US toll-free number?"
2. 问："What about Germany?"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | US toll-free: $49/month, $0.024/min | | |
| 2 | Germany toll-free: $39/month | | |
| 3 | 上下文延续正确（"What about Germany" 理解为费率切换） | | |

---

### TC-K3 — KB miss 场景处理

**目标**: 确认 bot 对 KB 中没有的内容不会幻觉回答。

**步骤**:
1. 问："Does CINNOX integrate with Salesforce?"（KB 中可能无此信息）
2. 问："What is the SLA for CINNOX uptime?"（KB 中可能无此信息）

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | Bot 承认不确定 / 无相关信息，不编造 | | |
| 2 | Bot 提议升级到人工获取更多信息（使用安全措辞） | | |
| 3 | 无幻觉数据（虚假功能/价格/集成） | | |

---

## D 组 — Glossary Phase 4-5 验证

> 如 Phase 4（copywriting 术语纠正）和 Phase 5（reviewer 第 12 项检查）尚未实施，标记为 N/A。

### TC-T1 — Copywriting 术语纠正

**目标**: 确认 copywriting subagent 将回复中的口语词替换为官方术语。

**步骤**:
1. 问一个容易引出口语词回复的问题，如 "Tell me about your ticket system"
2. 检查 bot 回复中是否使用了 "Enquiry" / "Enquiry Centre" 而非 "ticket"

**检查项**:

| # | 检查 | 通过/失败/N/A | 备注 |
|---|------|-------------|------|
| 1 | Bot 回复中使用官方术语而非口语词 | | |
| 2 | Trace 面板 copywriting 条目显示术语纠正记录 | | |

---

### TC-T2 — Reviewer 第 12 项术语准确性检查

**目标**: 确认 reviewer 清单新增了术语准确性检查项。

**步骤**:
1. 完成任意产品问答
2. 检查 reviewer 输出是否包含第 12 项检查结果

**检查项**:

| # | 检查 | 通过/失败/N/A | 备注 |
|---|------|-------------|------|
| 1 | Reviewer 结果中包含 Terminology Accuracy 检查 | | |
| 2 | 检查级别为 minor（不阻塞发送） | | |

---

## E 组 — 国家/地区名修复验证 (v1.2.7)

> 验证 v1.2.7 修复的三个核心问题：FTS5 短词丢弃、国家名扩展、歧义国名澄清。

### TC-R1 — 国家别名扩展 + FTS5 短词保留

**目标**: 确认 "US"、"UK" 等短缩写不再被 FTS5 丢弃，且 expanded_query 包含 xlsx 精确国名。

**前置**: 完成 lead collection。

**步骤**:
1. 问："How much does DID cost in the US?"
   - expanded_query 应包含 "United States"
   - 预期返回 US DID MRC=$19/month
2. 问："UK toll-free rates"
   - expanded_query 应包含 "United Kingdom"
3. 问："UAE DID pricing"
   - expanded_query 应包含 "United Arab Emirates"

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | US DID 返回 $19/month（而非 "I don't have specific pricing"） | | |
| 2 | UK toll-free 返回具体费率 | | |
| 3 | UAE DID 返回具体费率（MRC=$150） | | |
| 4 | 三次查询都基于 KB 数据，无幻觉 | | |

---

### TC-R2 — 歧义国名主动澄清

**目标**: 确认用户使用歧义国名时，bot 主动 clarify 而非猜测。

**步骤**:
1. 问："What's the DID price in America?"
   - 预期 bot 澄清：United States or American Samoa?
2. 回答："United States"
   - 预期 bot 继续澄清 toll-free vs local，或返回相应费率
3. 开新 session，问："Guinea number rates"
   - 预期 bot 澄清：Guinea, Equatorial Guinea, Guinea Bissau, or Papua New Guinea?

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | "America" 触发澄清（US vs American Samoa），而非直接返回 US 数据 | | |
| 2 | 澄清后 re-route：用户回答 "United States" 后继续正确处理 | | |
| 3 | "Guinea" 触发澄清（列出 4 个 Guinea 选项） | | |
| 4 | Bot 不猜测、不假设，先确认再搜索 | | |

---

### TC-R3 — 精确国名不触发歧义

**目标**: 确认用户使用精确国名时，不会被误判为歧义。

**步骤**:
1. 问："American Samoa call rates"
   - 不应触发 America 歧义澄清，应直接搜索 American Samoa
2. 问："South Korea DID pricing"
   - 不应触发 Korea 歧义澄清，应直接搜索 South Korea

**检查项**:

| # | 检查 | 通过/失败 | 备注 |
|---|------|----------|------|
| 1 | "American Samoa" 不触发澄清，直接返回费率 | | |
| 2 | "South Korea" 不触发澄清，直接返回费率 | | |
| 3 | 结果准确，基于 KB 数据 | | |

---

## 关键观察点

测试过程中注意以下信号，即使 TC 通过也要记录：

| 观察点 | 说明 | 记录 |
|--------|------|------|
| 查询扩展是否生效 | 后台日志是否可见术语/国名扩展痕迹 | |
| 快速通道响应速度 | TC-G2 是否明显快于普通查询 | |
| 国家名扩展 | expanded_query 是否包含 xlsx 精确国名 | |
| 歧义澄清 | 歧义国名是否触发 clarify，精确国名是否跳过 | |
| Trace 面板状态 | 是否出现 / 内容是否正确 | |
| 输入框状态 | 每次回复后是否仍可输入 | |
| 总 pipeline 耗时 | 目标 <30s | |
| Claude 的工具选择 | 使用 Agent / Bash / 直接回答 | |

---

## 故障排查

### 如果查询扩展未生效

1. 检查 `synonym-map.json` 是否存在且内容正确（当前 37 条，均为缩写/全称映射）
2. 检查 `route_query.py` 是否包含 `_expand_query` 函数
3. 后台日志搜索 `expanded_query` 字样
4. 确认问题中的缩写在 synonym-map 中有映射（如 IVR、DID、VN、DTMF）

### 如果术语快速通道未触发

1. 确认问题格式为纯术语定义（"What is X?"、"define X"）
2. 确认 X 在 glossary.json 中存在
3. 确认问题不包含复杂意图关键词（pricing、compare、how many 等）
4. 检查 `route_query.py` 的 `_is_glossary_only` 函数逻辑

### 如果国家名修复未生效

1. 确认 server 已重启（`_skill_text` 在模块加载时缓存）
2. 检查 `route_query.py` 是否包含 `COUNTRY_ALIAS_MAP` 和 `AMBIGUOUS_COUNTRIES`
3. 运行测试：`uv run .autoservice/.claude/skills/cinnox-demo/scripts/route_query.py --query "US DID pricing"` 确认 expanded_query 包含 "United States"
4. 检查 `kb_search.py` 的 `build_fts_query()` 是否保留 2 字符大写缩写

### 通用排查

参见 Round 7 测试指南的故障排查章节。
