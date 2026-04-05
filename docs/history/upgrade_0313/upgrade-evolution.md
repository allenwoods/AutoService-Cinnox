# Upgrade 演进记录

本文档记录从 upgrade-plan → upgrade-plan-2 → upgrade-plan-3 的思路演变和执行进度。细节请查阅各 plan 文档。

---

## 时间线总览

```
upgrade-plan (v1.0 → v1.1.2)
│   驱动力：KB 基础设施缺失 + UAT 暴露的运行时问题
│   核心产出：KB 切片/溯源 + subagent v1(脚本) + 4 轮 UAT 修复
│
├── 关键转折：Round 4 UAT 证明 "web/server.py 本次不动" 不可行
│   → v1.1 被迫修改 server.py（gate_cleared 门控）
│
├── 关键转折：BANNED PHRASES 纯 prompt 不可靠
│   → v1.1.2 引入代码级句子过滤（_should_escalate）
│
upgrade-plan-2 (v1.2)
│   驱动力：单 agent 架构的能力瓶颈 → 需要专职化
│   核心产出：5 个 Claude Code 原生 subagent + 动态组队 + self-challenge
│
├── 关键洞察：从"一个 agent 做所有事"到"每个 agent 做一件事"
│   → product-query / region-query / copywriting / reviewer / auditor
│
├── 关键洞察：reviewer 作为 self-challenge 机制
│   → 11 项清单，发送前拦截问题
│
upgrade-plan-3 (v1.3)
    驱动力：Leader 指出 reviewer 的"知情者盲点"
    核心产出：Red/Blue 双 agent 对抗测试

    关键洞察：self-challenge ≠ red-teaming
    → reviewer 是合规检查（知道规则，检查是否违反）
    → red-teaming 是对抗测试（不知道规则，从外部找问题）
    → 信息不对称是对抗价值的来源
```

---

## 各 Plan 执行进度

> 进度分类：
> - **已测试** = 代码已实现 + UAT 验证通过
> - **已执行未测试** = 代码/文件已实现，未经 UAT 验证
> - **已回测（有问题）** = UAT 发现问题，需要后续修复
> - **暂时搁置** = 计划中有但决定暂不执行
> - **未执行** = 尚未开始

### upgrade-plan（v1.0 → v1.1.2）

详见 [upgrade-plan.md](upgrade-plan.md)

#### Phase 0：元 Skill 改进

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 0.1 | architecture-audit Skill | 已执行未测试 | SKILL.md 已创建，未在实际项目中使用过 |
| 0.2 | autoservice-design Skill（brainstorming wrapper） | 已执行未测试 | SKILL.md 已创建 |
| 0.3 | planning-with-files 决策追踪 + 演进路线图模板 | 暂时搁置 | 模板文件存在但未增加新区块 |
| 0.4 | autoservice-skill-guide Skill（skill-creator wrapper） | 已执行未测试 | SKILL.md 已创建 |

#### Phase 1A：KB 基础设施

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 1.1 | Schema 迁移（domain/region/language/page_number） | 已测试 | ALTER TABLE 已执行，idx_kb_domain + idx_kb_region 索引已建 |
| 1.2 | PDF 语义切块 + 表格保持 | 已执行未测试 | kb_ingest.py 已修改，未单独验证切块质量 |
| 1.3 | XLSX 地区提取 | 已执行未测试 | kb_ingest.py 已修改 |
| 1.4 | 搜索增加 domain/region 过滤 | 已测试 | kb_search.py --domain/--region 参数可用，Round 4+ UAT 中使用 |
| 1.5 | Status 增加 domain/region 统计 | 已执行未测试 | kb_status.py 已修改 |
| 1.6 | Subagent 执行脚本 v1（kb_subagent.py） | 已执行未测试 | 脚本已创建，但 v1.2 后 subagent 改为 Claude Code 原生 agent，此脚本作为 fallback |
| 1.7 | KB SKILL.md 更新 | 已执行未测试 | 文档已更新 |
| — | kb_migrate.py 迁移脚本 | 已测试 | 已执行，数据已迁移 |
| — | sources.json 元数据 | 已执行未测试 | 文件已创建 |

#### Phase 1B：元 Skill 升级

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 1.8 | autoservice-design Skill | 已执行未测试 | 同 0.2 |
| 1.9 | planning-with-files 修改 | 暂时搁置 | 同 0.3 |
| 1.10 | autoservice-skill-guide Skill | 已执行未测试 | 同 0.4 |

#### Phase 2：cinnox-demo 重建

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 2.1 | 两层架构重构 | 已测试 | SKILL.md 重写，Round 4-6 UAT 验证 |
| 2.2 | Query 路由逻辑 | 已回测（有问题） | Round 6 测试 5/10 通过；TC-I8 客户类型误判仍存在 |
| 2.3 | route_query.py 路由脚本 | 已测试 | 脚本可用，关键词覆盖有限（见 plan-3 Glossary 分析） |
| 2.4 | 溯源增强 | 已执行未测试 | SKILL.md 中定义了 source citation 规则，未单独验证 |
| 2.5 | 模糊处理 v1（纯 Prompt） | 已回测（有问题） | Round 6 部分场景通过，部分场景 bot 仍跳过澄清直接猜测 |

#### v1.1 ~ v1.1.2：UAT 驱动修复

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| v1.1 | gate_cleared 门控 + 两步 escalation | 已测试 | server.py 已实现，Round 5 验证通过 (19/19) |
| v1.1.1 | BANNED PHRASES 全局规则 | 已测试 | SKILL.md 已更新，但纯 prompt 不够可靠，由 v1.1.2 兜底 |
| v1.1.2 | _should_escalate() 代码级过滤 | 已测试 | server.py 已实现，Round 5 验证通过 (19/19) |

#### Round 汇总

| Round | 版本 | 结果 | 说明 |
|-------|------|------|------|
| Round 4 | v1.0 | 失败 | 发现 3 个结构性问题 → 催生 v1.1 |
| Round 5 | v1.1.2 | 19/19 通过 | gate + escalation + banned phrases 全部修复 |
| Round 6 | v1.1.2 | 5/10 通过 | 新能力验证（ambiguity、edge case），暴露客户类型误判等问题 |

---

### upgrade-plan-2（v1.2）

详见 [upgrade-plan-2.md](upgrade-plan-2.md)

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 1 | product-query subagent | 已执行未测试 | `.claude/agents/product-query.md` 已创建 |
| 2 | region-query subagent | 已执行未测试 | `.claude/agents/region-query.md` 已创建 |
| 3 | copywriting subagent | 已执行未测试 | `.claude/agents/copywriting.md` 已创建 |
| 4 | reviewer subagent（11 项清单） | 已执行未测试 | `.claude/agents/reviewer.md` 已创建 |
| 5 | auditor subagent（fire-and-forget） | 已执行未测试 | `.claude/agents/auditor.md` 已创建 |
| 6 | SKILL.md 编排层（Step 3.5 动态组队） | 已执行未测试 | SKILL.md 已写入编排逻辑，未经 UAT 验证 subagent 实际调度 |
| 7 | Context 隔离规则 | 已执行未测试 | 隔离矩阵已定义在 SKILL.md 中 |
| 8 | Audit 存储（audit_log.jsonl + strategy_summary） | 未执行 | 目录和文件尚未创建 |

**整体状态**：5 个 subagent 的 agent .md 文件已全部创建，SKILL.md 编排逻辑已写入，但**尚未进行任何 UAT 验证**。不确定 subagent 在实际对话中是否被正确调度。

---

### upgrade-plan-3（v1.3）

详见 [upgrade-plan-3.md](upgrade-plan-3.md)

| # | 任务 | 进度 | 说明 |
|---|------|------|------|
| 1 | red-agent.md 定义 | 未执行 | |
| 2 | blue-agent.md 定义 | 未执行 | |
| 3 | SKILL.md 增加 red-teaming 条件触发 | 未执行 | |
| 4 | Context 抽取脱敏规则 | 未执行 | 方案已设计（见 plan-3），待实施 |
| 5 | auditor.md 增加 redteam 字段 | 未执行 | |
| 6 | Glossary 数据预处理（synonym-map.json） | 已执行未测试 | `build_glossary.py` 已创建，生成 `glossary.json`（355 条）+ `synonym-map.json`（38 条映射） |
| 7 | product-query Query Expansion | 已执行未测试 | 由 `route_query.py` 的 `_expand_query()` 统一处理，subagent 收到的 query 已是扩展后的版本 |
| 8 | region-query Query Expansion | 已执行未测试 | 同 #7，由 `route_query.py` 统一处理 |
| 9 | route_query.py 关键词扩展 | 已测试 | `_expand_query()` + `_is_glossary_only()` 已实现，SKILL.md 已增加 Glossary Fast-Track 分支。术语查询直接走 glossary 不走 subagent，已验证生效 |
| 10 | copywriting 术语校正 | 未执行 | Phase 4 待实施 |
| 11 | reviewer 第 12 项检查 | 未执行 | Phase 5 待实施 |

**整体状态**：Glossary Phase 1-3（#6~#9）已实施，#9 已测试验证术语直查生效。Phase 4-5（#10~#11）和 Red-teaming（#1~#5）未执行。

---

## 全局进度一览

```
                    已测试    已执行未测试   已回测(有问题)   暂时搁置   未执行
                    ──────    ──────────   ────────────   ────────   ──────
upgrade-plan        8 项       10 项         2 项          2 项       0 项
  (v1.0-v1.1.2)

upgrade-plan-2      0 项        7 项         0 项          0 项       1 项
  (v1.2)

upgrade-plan-3      1 项        3 项         0 项          0 项       7 项
  (v1.3)
```

**当前最大风险**：upgrade-plan-2 的 7 个 subagent 相关任务"已执行未测试"——Round 7 验证了 KB 数据准确性，但 Trace 面板和 audit_log 可观测性未达标。plan-3 的 Glossary #9（route_query.py 关键词扩展）已测试验证。

**建议下一步**：Round 8 UAT 验证 Glossary 集成 + Trace 面板验证。

---

### v1.2.6 Hotfix — 输入框冻结 bug（2026-03-12）

**问题**：subagent 调用完成并回答客户问题后，session 未结束，但输入框不可点击/发送。

**根本原因**：双层问题。

| 层 | 位置 | 问题 |
|----|------|------|
| ① WebSocket 超时断连 | `web/server.py` 消息循环 | subagent 执行期间（81s+），服务端跳过内部消息不向前端发送任何数据，WebSocket 因静默超时被断开 |
| ② 前端状态未重置 | `web/static/cinnox.html` | `done` 消息未送达（连接已断），前端重连后 `waitingReply` 仍为 `true`，`send()` 静默拒绝发送 |

**修改方案**：

| 文件 | 变更 |
|------|------|
| `web/static/cinnox.html` 'ready' handler | 新增 `removeTyping()` + `waitingReply = false` |
| `web/static/cinnox.html` 'session_resumed' handler | 新增 `waitingReply = false` |
| `web/static/cinnox.html` handleMsg switch | 新增 `heartbeat` case（忽略，保持连接） |
| `web/server.py` SDK 消息循环 | 新增 `last_ws_send_t` 追踪 + subagent 期间每 15s 发送 heartbeat 防断连 |

---

## 跨 Plan 的持续主题

### 1. Prompt 不够，代码兜底

- Plan 1：BANNED PHRASES 纯 prompt → 失败 → `_should_escalate()` 代码级过滤
- Plan 2：reviewer 的 11 项清单仍是 prompt 级 → 通过 context 隔离做结构性保障
- Plan 3：Red Agent 的 5 个维度是 prompt 级 → 但通过 Blue Agent 的 KB 证据做事实性兜底

教训：**关键安全行为不能只靠 prompt。每一层都需要结构性保障。**

### 2. Context 隔离越来越重要

- Plan 1：无隔离，所有信息在一个 context 中
- Plan 2：每个 subagent 只拿必要信息（PII 隔离、KB 隔离）
- Plan 3：**信息不对称成为核心机制**——Red Agent 的价值恰恰来自它"不知道"规则

隔离不仅是安全措施，更是**功能设计**。

### 3. 从线性到对抗

- Plan 1：线性流程（输入 → 处理 → 输出）
- Plan 2：线性 + 检查点（输入 → 处理 → reviewer 检查 → 输出）
- Plan 3：对抗（输入 → 处理 → 检查 → Red 攻击 → Blue 辩护 → 裁决 → 输出）

系统的"免疫力"在增强——从没有免疫、到被动免疫（清单检查）、到主动免疫（对抗测试）。
