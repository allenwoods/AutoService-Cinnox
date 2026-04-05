# CINNOX AI Bot 升级进度报告


## 一、项目进度总览

| 痛点 | 解决方案 | 状态 | 相关文档 |
|------|---------|------|---------|
| **知识库内容混杂，搜索结果不精准**。例：客户问"US DID号码价格"，bot 把 CINNOX 套餐价格和电信费率混在一起返回 | KB 分域切片——按产品线（Contact Center / AI Sales Bot / Global Telecom）和地区建立索引，搜索时自动过滤 | ✅ 已测试通过 | upgrade-plan Phase 1A; Round 5 |
| **PDF/Excel 切割方式粗糙，表格和段落被拆散**。例：费率表被从中间切开，bot 读到半张表给出错误价格 | PDF 语义分段 + 表格结构保持；Excel 费率表行级地区提取 | ✅ 已实现 | upgrade-plan 1.2/1.3 |
| **Bot 转人工时不等客户确认，直接触发转接**。例：bot 说"要不要帮你转接专员？"这句话本身就触发了转接 | 两步 escalation（先提议→等确认→再执行）+ 代码级句子过滤（疑问句中的触发词不生效） | ✅ 已测试通过 (19/19) | upgrade-plan v1.1~v1.1.2; Round 5 |
| **单个 agent 能力瓶颈——又要查资料、又要写话术、又要自检，质量不稳定** | 5 个专职 subagent 动态协作：product-query（产品查询）、region-query（地区费率）、copywriting（话术优化）、reviewer（质量自检 11 项）、auditor（审计记录） | ⚠️ 已实现，UAT 验证中 | upgrade-plan-2; Round 7 |
| **客户用口语词提问，bot 搜不到知识库内容**。例：客户说"group call"，知识库里叫"Broadcast Call Enquiry"，搜索完全匹配不上 | Glossary 术语表集成——自动将口语词替换为官方术语后再搜索（详见第三章） | ⚠️ 已实现，待 Round 8 验证 | upgrade-plan-2 Glossary; Round 8 |
| **纯术语定义问题（"DID 是什么？"）也要走完整搜索流程，慢且不必要** | 术语快速通道——纯定义问题直接从 Glossary 返回，跳过搜索流程，100% 准确 | ⚠️ 已实现，待 Round 8 验证 | upgrade-plan-2 Glossary Phase 3; Round 8 |
| **Bot 回复中使用非官方术语（如把"Enquiry"说成"ticket"），品牌不一致** | Copywriting 术语纠正——回复发出前自动替换为官方术语 | 🔲 待实施 | upgrade-plan-2 Glossary Phase 4 |


---


| 其他技术优化或Minor问题 | 解决方案 | 状态 | 相关文档 |
|------|---------|------|---------|
| **Reviewer 自检清单缺少术语准确性维度** | Reviewer 新增第 12 项检查：术语准确性（对照 Glossary） | 🔲 待实施 | upgrade-plan-2 Glossary Phase 5 |
| **Reviewer 的"知情者盲点"——它知道所有规则，只能查合规，发现不了客户体验问题** | Red-Teaming 对抗测试——两个 agent 信息不对称对抗：Red（不知规则，从客户角度找问题）vs Blue（知道规则，用证据辩护） | 🔲 待实施 | upgrade-plan-3 |
| **客户还没说是谁，bot 就直接回答产品问题**。例：新客户第一条消息问价格，bot 跳过身份识别直接给报价 | Gate 门控机制——客户身份确认前，禁止注入知识库内容 | ✅ 已测试通过 | upgrade-plan v1.1; Round 4/5 |
| **Bot 在自由回答中意外触发转人工**。例：bot 推荐方案后说"shall I connect you with our sales team"，被系统误判为转接指令 | BANNED PHRASES 全局规则 + `_should_escalate()` 代码级过滤——只有陈述句中的触发词才生效 | ✅ 已测试通过 (19/19) | upgrade-plan v1.1.1~v1.1.2; Round 5 |


> **图例**: ✅ 已测试通过 · ⚠️ 已实现待验证 · 🔲 待实施 · 🔴 待修复

---

## 二、术语表 (Glossary) 的价值 — 重点

### 1. 问题：术语不匹配导致搜索失败

客户使用口语词提问，KB 使用 CINNOX 官方术语，BM25 全文搜索因术语不匹配导致检索失败：

| 客户可能说 | CINNOX 官方术语 | BM25 能匹配吗 |
|-----------|----------------|--------------|
| "group call" | Broadcast Call Enquiry | ❌ 完全不同 |
| "phone number for my company" | DID (Direct Inward Dialing) | ❌ 模糊 |
| "AI chatbot" | CINNOX Bot / CINNOX Q&A Bot / Claire.AI | ❌ 不同名称 |
| "CRM integration" | Zapier / Zaps | ❌ 完全不同 |
| "ticket system" | Enquiry Centre | ❌ 完全不同 |
| "free number" | TF (Toll-free) / Toll-free Number | ⚠️ "free" 模糊 |
| "auto reply" | Auto-reply messages / Auto-welcome message | ⚠️ 部分匹配 |
| "forward a call" | Call Transfer / Call Forwarding | ⚠️ 部分匹配 |
| "smart routing" | Automatic Enquiry Distribution / Sticky Routing | ❌ 不同概念 |
| "noise cancel" | Noise Reduction | ⚠️ 部分匹配 |
| "screen share" | Share Screen | ✅ 基本匹配 |
| "IVR menu" | Interactive Voice Response (IVR) / IVR Menu | ✅ 匹配 |
| "voicemail" | Voicemail | ✅ 匹配 |

> 以上 13 个案例中，**5 个完全无法匹配，4 个仅部分匹配**——超过 2/3 的常见口语词无法正确检索。

### 2. CX 提供的术语表

CX 提供的 `CINNOX Glossary.csv` 包含 **355 个官方术语**，每个术语含：
- 术语名称
- 完整描述/定义
- 关联术语（Related Glossary）

我们将其处理为两个索引文件：
- **glossary.json** — 完整术语定义表（355 条），用于术语快速通道和 reviewer 校验
- **synonym-map.json** — 口语词→官方术语映射（38 条），用于查询扩展

### 3. 集成方式：五个阶段

```
CSV → build_glossary.py → glossary.json + synonym-map.json
                                ↓
客户提问 → route_query.py (术语扩展) → subagent (精准搜索)
              ↓ (纯术语问题)
         直接返回 glossary 定义，跳过搜索（100% 准确）
```

| 阶段 | 用户价值 | 状态 |
|------|---------|------|
| **Phase 1：术语表预处理** | 将 CX 提供的 355 条术语 CSV 转为系统可用的结构化数据，是后续所有优化的基础 | ✅ 已完成 |
| **Phase 2：查询扩展** | **客户不需要记住官方术语就能得到准确回答。** 例如客户说"group call"，系统自动翻译为"Broadcast Call Enquiry"再去搜索，大幅提升搜索命中率 | ✅ 已完成，待测试 |
| **Phase 3：术语快速通道** | **客户问"DID 是什么"等纯定义问题时，秒级响应，且准确率 100%。** 不走搜索流程，直接从官方术语表返回权威定义，同时引导客户深入了解（"想了解 DID 的价格吗？"） | ✅ 已完成，待测试 |
| **Phase 4：回复术语纠正** | **确保 bot 回复中统一使用 CINNOX 官方术语，维护品牌专业形象。** 例如 bot 不会说"ticket"，而是说"Enquiry"——让客户从第一次接触就熟悉 CINNOX 的产品体系 | 🔲 待实施 |
| **Phase 5：术语准确性自检** | **双重保障——即使前面遗漏了非官方术语，发送前的质量检查也能捕获。** 降低人工审核负担，提高一致性 | 🔲 待实施 |

### 4. 效果

Round 7 v1.2.4 测试结果显示，**所有 KB 回答数据准确**：

| 问题 | 回答 | 数据来源 | 准确性 |
|------|------|---------|--------|
| "Does CINNOX support WhatsApp?" | WhatsApp add-on $100/month, 360dialog, Campaigns, OTP API | KB | ✅ |
| "How much is a US toll-free number?" | $49/month, $0.024/min, DID 对比 $19/month | KB | ✅ |
| "What about Germany?" | $39/month, mobile $0.224/min, landline $0.06/min | KB | ✅ |

术语扩展确保了即使客户使用口语词，也能通过同义词映射找到正确的 KB 内容。

### 5. 当前 synonym-map 覆盖范围

当前 38 条映射主要覆盖高频术语，但仍有大量客户常用词未覆盖。提供更多真实客户用语数据，可以让我们进一步扩展映射表。

---

## 三、接下来可以升级优化的方向

### 一、让 bot 回答更专业、更像专业的销售人员

**目标效果**：bot 不仅能回答"CINNOX 有什么功能"，还能像资深销售一样处理客户异议、推荐合适套餐、引导升级。

| Bot 能做什么 | 说明 | 需要的资料 |
|-------------|------|-----------|
| Bot 的回答与 CX 销售团队口径一致，避免"bot 说的和销售说的不一样" | 针对常见问题的官方推荐回答（例如"CINNOX 和竞品有什么区别？"） | **标准回复话术** |
| Bot 能专业地应对价格异议和竞品比较，而非简单说"请联系销售"，提升转化率 | 客户说"太贵了"、"我们已经在用 Zendesk"等场景的应对方式 | **异议处理话术** |
| Bot 能快速准确地定位客户需求对应的套餐，缩短销售周期 | 每个套餐（BCC/DC/OCC/CXHub）的 1-2 句亮点介绍 | **产品亮点话术** |
| Bot 能在客户了解基础套餐后自然引导升级，增加客单价 | 从低套餐引导至高套餐的话术模板 | **追加销售话术** |
| 客户常问"和 Zendesk/Intercom 比怎么样"，bot 能专业应对而非回避 | 主要竞品清单、差异化优势、功能/价格对比 | **竞品对比资料** |

### 二、让 bot 回答更深入、能解决具体问题

**目标效果**：bot 不仅能说"有这个功能"，还能回答"这个功能怎么用？适合我们行业吗？安全吗？"

| Bot 能做什么 | 说明 | 需要的资料 |
|-------------|------|-----------|
| Bot 能回答"这个功能具体怎么用？"类深度问题 | 每个功能的使用场景、限制条件、配置方式 | **功能详细说明** |
| Bot 能回答"我们是做电商的，CINNOX 能帮什么？"——从功能介绍升级为场景化推荐 | 按行业（金融/电商/物流等）说明 CINNOX 如何解决客户问题 | **行业场景文档**（如有） |
| 客户问"数据存在哪？安全吗？"时 bot 能给出权威回答，而非含糊其辞或转人工 | 安全合规、数据中心分布、SLA 等（非深度技术文档） | **技术架构概述** |
| 作为自动化测试基准，每次升级后可自动验证 bot 回答是否偏离标准 | 问题+官方标准答案 | **带标准答案的 QA 对** |
| 定义 bot 能力边界——哪些该回答、哪些该转人工，避免错误回答损害信任 | 客户可能问的刁钻问题（如"你们安全合规吗？"、"支持哪些国家？"） | **边界/刁钻问题** |

### 三、让 bot 支持多语言客户

**目标效果**：bot 能用客户的母语（如泰语、中文等）准确沟通，术语翻译一致，不出现歧义。

| Bot 能做什么 | 说明 | 需要的资料 |
|-------------|------|-----------|
| Bot 能准确对应各语言术语，例如"DID"在泰语中的标准翻译，避免机器翻译的歧义 | 基于现有 355 条 Glossary，提供中文/泰语等目标语言的对应术语 | **多语言术语对照表** |
| Bot 回答的语气和用词符合当地客户习惯，而非生硬的机器翻译 | 各目标语言的常见问题及标准回答 | **多语言常见问答模板** |
| 不同市场的客户异议点不同（如泰国客户可能更关心本地支付方式），bot 能针对性应对 | 各目标语言的销售话术和异议处理方式 | **多语言话术/异议处理** |
| 确定开发顺序，优先覆盖最重要的市场 | 需要支持哪些语言、优先级排序 | **目标语言优先级** |

---

## 五、下一步计划预览

### 近期（Round 7-8 验证）

- **Glossary 集成 UAT 验证** — 验证查询扩展、术语快速通道、多术语复合问题
- **Round 7 遗留问题回归** — Trace 面板渲染、输入框冻结 bug 修复验证
- **KB 准确性回归** — 确保新功能不影响已有回答质量

### 中期

- **Glossary Phase 4-5** — copywriting 术语纠正 + reviewer 第 12 项检查
- **Trace 面板 + 输入框冻结 bug 修复** — 恢复 subagent 可观测性
- **audit_log.jsonl 写入修复** — 实现跨会话审计能力

### 远期（v1.3）

- **Red-Teaming 对抗测试架构** — Red/Blue 双 agent 对抗模型
  - Red Agent：只拿到客户问题和 bot 回复（信息不对称），从外部视角找问题
  - Blue Agent：拿到完整 context，用规则和 KB 数据为回复辩护
  - 价值：发现 reviewer 合规检查无法触及的"知情者盲点"（客户体验缺陷、信息泄漏、隐蔽幻觉、规则漏洞）
  - 触发策略：pricing / escalation 高风险场景条件触发 + 离线全量扫描
