
**Tester**: _______________
**Test Date**: 2026-03-03
**Environment**: CINNOX Demo (autoservice simulation)
**Product Config**: CINNOX
**Operator/Strategy**: _______________

> **v1.1**: Aligned with flow.md. Total TCs: 19 (added TC-A4). TC-A2/E2 now check Email. TC-B/C/H now check lead collection before RAG.

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 19 |
| Passed | 17 |
| Failed | 2 |
| Blocked / Not Run | 0 |
| Pass Rate | 89% |

> TC-A2 was run **twice** (Run 1 before git pull, Run 2 after). Both runs recorded separately. The TC result reflects the latest run.

### Failed TCs

#### ❌ TC-A2 — 现有客户识别（Email 未收集）

**现象**：现有客户报告故障时，机器人收集了 Account ID、Agent 姓名、服务号码后直接转人工，未收集 Email。

**根因**：机器人配置文件（SKILL.md）中现有客户流程未定义 Email 字段，与 v1.1 测试标准不符。

**影响**：所有现有客户路径（投诉、技术故障）均受影响，属系统性缺口，非偶发。


#### ❌ TC-B1 — 产品咨询（首条消息无身份信号时跳过 Lead 收集）

**现象**：用户第一条消息是直接产品问题（"Does CINNOX support WhatsApp integration?"），机器人立即回答，未先识别客户身份，也未收集任何联系信息。

**根因**：此类句式不含身份信号，机器人将其识别为中性问题直接响应。对比 TC-B2（"Can you handle high volume inbound calls?"），因带有业务需求信号，机器人正确触发了新客户流程。

**影响**：直接产品提问是最常见的用户行为之一，此场景下 Lead 收集完全失效。

### No Critical Failures (TC-B3, TC-F2):
- [x] TC-B3: No hallucination ✓
- [x] TC-F2: Immediate handoff without questions ✓

---

## TC-A: Customer Type Identification

### TC-A1 — New Customer Identification

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot greets and asks for identity on T1 | ✓ | Correctly identified new customer from "looking for a contact center solution" |
| Bot does NOT re-ask Name or Company after T2 | ✓ | |
| Bot collects Email and Phone (T3–T4) without duplication | ✓ | |
| Bot summarizes collected info before closing | — | Not explicitly confirmed in session |
| Bot confirms next step (demo / handoff to sales) | ✓ | Connected to sales |

**Notes**: Emma Xu / Bright Retail / emma.xu@brightretail.com / +852-9123-4567. Customer asked about 50 seats, WhatsApp, US numbers.

---

### TC-A2 — Existing Customer Identification *(v1.1: Email added)*

#### Run 1 (before git pull)

**Result**: FAIL

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies existing customer support case | ✓ | From "Our agent cannot receive calls" |
| Bot requests Account ID + service details | ✓ | |
| Bot collects Account ID | ✓ | PBHK-2024 |
| Bot collects Company | — | Not collected separately; customer provided Account ID directly |
| Bot collects Agent name (issue-specific) | ✓ | Alice |
| Bot collects Service number | ✓ | +852-1234-5678 |
| Bot collects **Email** *(new in v1.1 per flow)* | ✗ | Not requested |
| Bot initiates handoff to human agent | ✓ | |
| Bot does NOT attempt to resolve with KB answers | ✓ | |

**Failure Detail**:

```
Email was not collected. Bot proceeded to escalation after Account ID / Agent name / Service number only.
```

**Notes**: SKILL.md does not include email in the existing customer collection flow. This is a SKILL.md gap vs. v1.1 checklist.

---

#### Run 2 (after git pull)

**Result**: FAIL

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies existing customer support case | ✓ | From "Our agent cannot receive calls" |
| Bot requests Account ID + service details | ✓ | |
| Bot collects Account ID | — | Company name (Pacific Bank HK) provided instead of Account ID |
| Bot collects Company | ✓ | Pacific Bank HK |
| Bot collects Agent name (issue-specific) | ✓ | Alice |
| Bot collects Service number | ✓ | +852-1234-5678 |
| Bot collects **Email** *(new in v1.1 per flow)* | ✗ | Not requested |
| Bot initiates handoff to human agent | ✓ | |
| Bot does NOT attempt to resolve with KB answers | ✓ | |

**Failure Detail**:

```
Email was not collected in either run. SKILL.md existing customer flow only collects Account ID / Agent name / Service number.
```

**Notes**: Same root cause as Run 1. SKILL.md needs to be updated to include email collection for existing customer flow.

---

### TC-A3 — Partner Identification

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot recognizes SI/partner inquiry | ✓ | From "system integrator and want to explore a partnership" |
| Bot collects Name, Company, Email, Phone | ✓ | David Park / Nexus SI Singapore / david.park@nexussi.com / +65-8123-4567 |
| Bot does NOT lead with product pricing | ✓ | |
| Bot routes to partnership/BD team | ✓ | |

**Notes**: Clean pass.

---

### TC-A4 — Existing Customer Product Inquiry *(New in v1.1)*

**Result**: PASS

> **Flow reference**: 现有客户 → 产品咨询 → RAG回复 → 无法解答 → 转人工
> Bot should NOT run the new-customer lead form for existing customers.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies this as existing customer inquiry (not new prospect) | ✓ | "We are an existing CINNOX customer" |
| Bot does NOT collect Name/Email/Phone as a new lead form | ✓ | Correctly skipped new-customer lead form |
| Bot queries KB for CRM/API integration information | ✓ | |
| Bot provides answer with source citation (if KB has info) | ✓ | |
| If KB cannot answer → bot transfers to human specialist | ✓ | Escalated to tech specialist |
| Bot does NOT fabricate API specs or integration capabilities | ✓ | |

**Notes**: Sophie Liu / NVHK-2025. Bot correctly differentiated existing customer product inquiry from new prospect flow.

---

## TC-B: Product Inquiry / RAG

> **v1.1**: All TC-B tests now require bot to collect lead info (Name/Company/Email/Phone) **before** answering product questions. Each checklist includes a lead collection verification row.

### TC-B1 — WhatsApp Integration *(v1.1: lead collection first)*

**Result**: FAIL

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT answer WhatsApp question immediately)** | ✗ | Bot answered WhatsApp question immediately |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✗ | Never collected |
| Bot returns to answer the WhatsApp question after lead collection | — | N/A (question answered immediately) |
| Bot confirms WhatsApp Business support | ✓ | Answered correctly |
| Bot mentions OCC/CXHub availability (not DC) | — | Not confirmed |
| Bot correctly describes campaign capability | — | Not confirmed |
| Bot mentions WhatsApp number purchase (or defers to sales) | — | Not confirmed |
| No fabricated features | ✓ | |

**Failure Detail**:

```
T1: "Does CINNOX support WhatsApp integration?"
Bot answered the product question immediately without asking customer type or collecting lead info.
After answering, bot asked "Is there anything specific about the WhatsApp integration you'd like to know more about?" — no lead collection attempted.
```

**Notes**: Two issues logged (#1, #2 in Issues Log). Root cause: first message is a direct product question with no identity signal — bot cannot distinguish customer type and defaults to answering. SKILL.md does not handle this edge case.

---

### TC-B2 — High Volume Banking *(v1.1: lead collection first)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately pitch product)** | ✓ | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Li Wei / ShangBao Bank / li.wei@shangbao.com / +86-21-1234-5678 |
| Bot returns to address the high-volume banking question | ✓ | |
| Bot mentions ACD routing modes (≥2) | ✓ | ACD distribution method and routing rules mentioned |
| Bot confirms IVR menu support | ✓ | |
| Bot recommends OCC or CXHub | ✓ | Recommended CXHub |
| Bot avoids fabricated throughput guarantees | ✓ | |

**Notes**: Clean pass. Bot correctly deferred product question until after lead collection.

---

### TC-B3 — Non-Existent Feature ⚠️ CRITICAL *(v1.1: lead collection first)*

**Result**: PASS

> **Note**: A FAIL on hallucination is a showstopper. Lead collection before Q&A is secondary — focus is on no fabrication.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1** | ✓ | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Alex Kim / FutureMedia Corp / alex.kim@futuremedia.com / +1-415-555-0199 |
| Bot clearly denies hologram video calling after lead collection | ✓ | |
| Bot maintains denial under pressure | ✓ | Maintained denial twice under pushback |
| Bot describes real video features | ✓ | Video calling features cited from KB |
| **CRITICAL**: No fabrication at any point | ✓ | |

**Notes**: Critical test passed. Bot held firm under "We specifically saw the CINNOX name on the booth" pressure. Immediately escalated when customer requested human (TC-F2 within same session).

---

## TC-C: Pricing Accuracy

> **v1.1**: All TC-C tests now require lead collection before pricing Q&A.

### TC-C1 — DID Number Price *(v1.1: lead collection first)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | ✓ | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Kevin Han / Seoul Commerce Inc. / kevin.han@seoulcommerce.kr / +82-2-1234-5678 |
| Bot gives specific price OR correctly defers to pricing page | ✓ | USD 19/month MRC |
| Price given is consistent with knowledge base | ✓ | |
| Bot mentions DID is an add-on | — | Not explicitly confirmed |
| Bot mentions KYC/verification requirement | ✓ | |
| Bot correctly states plan eligibility for DID | ✓ | |

**Price given by bot**: USD 19/month MRC (US DID)

**Notes**: Follow-up questions on setup fee and KYC also handled correctly.

---

### TC-C2 — Volume Pricing (50 Agents) *(v1.1: lead collection first)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | ✓ | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Fatima Al-Rashid / Dubai Commerce Group / fatima@dubaicommerce.ae / +971-4-1234-5678 |
| Bot explains per-agent license model | ✓ | Per-account model explained |
| Bot mentions annual vs. monthly pricing | ✓ | OCC $59/$50, DC $29/$20 |
| Bot mentions volume discounts via sales | ✓ | |
| Bot recommends OCC or CXHub for 50 agents | ✓ | OCC recommended |
| Bot routes to sales for formal quote | ✓ | |
| Bot does NOT fabricate a specific total price | ✓ | |

**Notes**: Annual vs monthly pricing comparison provided correctly from KB.

---

### TC-C3 — Incorrect Price Correction *(v1.1: lead collection first)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot collects all 4 lead fields before pricing discussion** | ✓ | Marco Rossi / Roma Digital SRL / marco@romadigital.it / +39-06-1234-5678 |
| Bot explicitly says $5/minute per agent is NOT correct | ✓ | |
| Bot maintains correction under pressure | ✓ | Maintained x2 ("industry standard" / "I don't believe that") |
| Bot correctly explains license-based model | ✓ | |
| Bot provides accurate tier pricing or defers to pricing page | ✓ | Provided OCC/DC rates from KB |

**Notes**: Strong performance under repeated pushback. Cited KB source for correction.

---

## TC-D: Data Collection

### TC-D1 — Demo Request (All Fields)

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot requests all 4 fields in logical order | ✓ | |
| Bot does NOT re-ask fields already provided | ✓ | |
| Bot confirms demo request receipt after all 4 fields | ✓ | |
| Bot provides next step | ✓ | |

**Notes**: Emma Laurent / Lyon Digital Agency / emma@lyondigital.com / +33-6-1234-5678. Customer noted weekday afternoon preference and demo focus (DID + volume discounts) — bot acknowledged.

---

### TC-D2 — Phone Number Refused

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot explains reason for phone on T3 | ✓ | |
| Bot does NOT demand phone after T4 | ✓ | |
| Bot offers alternative or human handoff on T4 | ✓ | |
| Bot routes to human after second refusal | ✓ | |
| Conversation continues (not terminated) | ✓ | |

**Notes**: Same persona as TC-D1 (Emma Laurent). Bot handled refusal gracefully without pressuring.

---

## TC-E: Existing Customer Routing

### TC-E1 — Billing Issue

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies billing issue on T1 | ✓ | "I think I was overcharged on last month's bill" |
| Bot collects Name | ✓ | Tom Bradley |
| Bot collects Company | ✓ | Hartley Insurance UK |
| Bot collects **Email** | — | Not confirmed collected in session |
| Bot collects Account ID | ✓ | HART-UK-2023 |
| Bot does NOT explain billing rates | ✓ | |
| Bot routes to billing/support team | ✓ | |
| Bot confirms handoff with next step | ✓ | |

**Notes**: Email collection not confirmed. May be a gap consistent with TC-A2 finding (SKILL.md does not include email for existing customer flows).

---

### TC-E2 — Technical Issue (Voice Quality) *(v1.1: Email added)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot acknowledges technical issue on T1 | ✓ | "Voice quality is really bad" |
| Bot requests account info (not new-customer lead form) | ✓ | |
| Bot collects Name | ✓ | James Wong |
| Bot collects Company | — | Not confirmed separately |
| Bot collects **Email** *(new in v1.1 per flow)* | — | Not confirmed collected |
| Bot collects Account ID | ✓ | PBHK-2024 |
| Bot collects Service Number | ✓ | +852-1234-5678 |
| Bot does NOT give >2 troubleshooting steps before routing | ✓ | |
| Bot routes to technical support | ✓ | |
| Bot confirms technician follow-up | ✓ | |

**Notes**: Email and company not confirmed collected — same SKILL.md gap as TC-A2/E1.

---

## TC-F: Human Handoff

### TC-F1 — Knowledge Boundary

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot shares known security info on T2/T3 | ✓ | GDPR compliance, TLS 1.2+ confirmed from KB |
| Bot does NOT fabricate DB encryption architecture on T1 | ✓ | Acknowledged knowledge limits |
| Bot acknowledges knowledge limits for T1 | ✓ | |
| Bot offers/accepts escalation to technical team | ✓ | |
| No hallucinated technical specs | ✓ | SOC2 denied (not in KB) |

**Notes**: Bot correctly denied SOC2 compliance (not found in KB) rather than inventing an answer.

---

### TC-F2 — Immediate Human Request ⚠️ CRITICAL

**Result**: PASS

> **Note**: Any qualifying question = FAIL.
> **Flow Gap Note**: The official flow.md does not have a direct human request branch. Bot's correct behavior here (immediate routing) should be added to the flow.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT ask qualifying question after T1 | ✓ | |
| Bot acknowledges and confirms handoff in same response | ✓ | |
| **CRITICAL**: No qualification questions before routing | ✓ | |

**Notes**: Critical test passed. Bot responded with immediate escalation — "Of course! Let me connect you with a human agent right away."

---

## TC-G: Context Continuity

### TC-G1 — Multi-Turn DID Pricing

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot provides UK DID pricing on T1 | ✓ | USD 19/month |
| Bot correctly interprets T2 as Germany DID (not re-explains product) | ✓ | Correctly inferred DID context |
| Bot answers T3 as HK DID pricing | ✓ | USD 25/month |
| Bot does NOT re-explain DID on T2/T3 | ✓ | |
| Prices are consistent with knowledge base | ✓ | |

**UK price given**: USD 19/month MRC
**Germany price given**: USD 19/month MRC
**HK price given**: USD 25/month MRC

**Notes**: Customer (James Wong / PBHK-2024) initially refused to provide lead info before pricing. Bot explained the reason once, customer then provided Account ID. Context maintained correctly across all three follow-up questions.

---

## TC-H: Error Tolerance

### TC-H1 — Spelling Errors *(v1.1: lead collection first)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately answer typo question)** | ✓ | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Ryan Park / Seoul Media Group / ryan@seoulmediad.com / +82-2-5678-1234 |
| Bot returns to answer original typo question at T6 (no clarification request about spelling) | ✓ | |
| Bot correctly interprets "whtsapp intergration" as WhatsApp integration | ✓ | No clarification asked |
| Bot provides accurate WhatsApp answer | ✓ | 360dialog BSP cited |
| Bot handles T7 follow-up correctly (campaign capabilities) | ✓ | Confirmed campaigns supported, cited CINNOX Docs |
| No error messages or confusion at any point | ✓ | |

**Notes**: Seamless handling of both typos. Campaign follow-up also answered correctly from KB.

---

### TC-H2 — Vague Request *(v1.1: lead collection first, then clarifying questions)*

**Result**: PASS

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot collects all 4 lead fields before handling the vague inquiry** | ✓ | 见下方流程说明 |
| Bot asks clarifying question(s) — NOT a product pitch | ✓ | 路由问题在前，需求澄清在 lead 收集之后 |
| Bot builds on context and asks relevant follow-up | ✓ | |
| Bot synthesizes context (phone + WhatsApp → OCC/CXHub) | ✓ | |
| Bot makes concrete recommendation with reasoning | ✓ | Recommended OCC with reasoning |
| Bot does NOT quote prices before recommendation | ✓ | |

**Flow Deviation Note** *(与元流程不同，但行为正确)*:

```
元流程预设顺序：
  T1: 模糊输入 → T2–T5: 收集 lead → T6: 澄清需求

实际执行顺序：
  T1: "I want something for customer service."
  Bot → [路由问题] "Are you a new customer or existing?"   ← 元流程未定义此步
  T2: "we don't have existing account"
  T3–T6: 收集 Name / Company / Email / Phone
  T7: 澄清需求 ("mostly phone calls, but also WhatsApp")
  T8+: 推荐 OCC
```

**偏差原因**：T1 消息无任何身份信号，Bot 无法在不确认身份的情况下启动正确的收集流程（新客户表单 vs 现有客户账户信息）。Bot 先问「新/现有客户？」是必要的路由步骤，不是提前澄清产品需求。lead 收集仍在需求回答之前完成，核心流程逻辑正确。

**建议**：元流程应补充「首条消息无身份信号时，先做单次路由确认，再进入对应收集流程」的分支。

**Notes**: Sarah Mitchell / Austin Digital Agency / sarah@austindigital.com / +1-512-555-0123.

---

## Final Results Table

| TC | Category | Title | Result | Notes |
|----|----------|-------|--------|-------|
| TC-A1 | Customer Type | New Customer Identification | PASS | |
| TC-A2 (Run 1) | Customer Type | Existing Customer Identification | FAIL | Email not collected; before git pull |
| TC-A2 (Run 2) | Customer Type | Existing Customer Identification | FAIL | Email not collected; same root cause |
| TC-A3 | Customer Type | Partner Identification | PASS | |
| TC-A4 *(new)* | Customer Type | Existing Customer Product Inquiry | PASS | |
| TC-B1 | Product / RAG | WhatsApp Integration | FAIL | No lead collection; direct product answer |
| TC-B2 | Product / RAG | High Volume Banking | PASS | |
| TC-B3 ⚠️ | Product / RAG | Non-Existent Feature | PASS | Critical: no hallucination ✓ |
| TC-C1 | Pricing | DID Number Price | PASS | US DID: USD 19/month |
| TC-C2 | Pricing | 50-Agent Volume Quote | PASS | |
| TC-C3 | Pricing | False Price Correction | PASS | Corrected $5/min x2 under pressure |
| TC-D1 | Data Collection | Demo Request — All Fields | PASS | |
| TC-D2 | Data Collection | Phone Number Refused | PASS | |
| TC-E1 | Existing Customer | Billing Issue Routing | PASS | Email not confirmed (SKILL.md gap) |
| TC-E2 | Existing Customer | Technical Issue Routing | PASS | Email not confirmed (SKILL.md gap) |
| TC-F1 | Human Handoff | Knowledge Boundary | PASS | SOC2 correctly denied |
| TC-F2 ⚠️ | Human Handoff | Immediate Human Request | PASS | Critical: immediate routing ✓ |
| TC-G1 | Context | Multi-Turn DID Pricing | PASS | UK/DE $19, HK $25 |
| TC-H1 | Error Tolerance | Spelling Errors | PASS | |
| TC-H2 | Error Tolerance | Vague Request | PASS | 路由问题先于 lead 收集，属元流程未覆盖分支，行为正确 |

---

## Issues Log

| # | TC | Severity | Description | Bot Response (verbatim) |
|---|----|----------|-------------|------------------------|
| 1 | TC-B1 | High | 当客户第一条消息为直接产品提问（无身份信号）时，Bot 无法从首条输入辨认客户身份（新客户 / 现有客户 / 合作伙伴），直接回答问题而跳过身份识别流程 | Bot answered WhatsApp question immediately without asking customer type or collecting lead info |
| 2 | TC-B1 | High | Bot 回答产品问题后未尝试收集用户信息（Name / Company / Email / Phone），未完成 lead 表单，对话即结束 | After answering, bot asked "Is there anything specific about the WhatsApp integration you'd like to know more about?" — no lead collection attempted |
| 3 | TC-A2 | High | v1.1 要求收集 Email，但 SKILL.md 现有客户流程未包含 Email 字段，两次运行均未收集 Email | Bot escalated to human without requesting email address |
| 4 | TC-H2 | Low *(流程建议)* | 元流程未定义「首条消息无身份信号」分支。Bot 先做路由确认（新/现有客户？）再收集 lead，行为正确但超出元流程覆盖范围。建议元流程补充此分支。 | — *(非 Bot 错误，为流程设计补充建议)* |
| 5 | TC-E1/E2 | Medium | 现有客户投诉/技术问题流程中 Email 字段未被收集（与 #3 同根因，SKILL.md 未定义） | Bot proceeded to escalation without requesting email |
| 6 | TC-B1 | High | 当首条消息为纯功能查询句（"Does X support Y?"）时，Bot 不触发 lead 收集流程。根因：此类句式不含任何身份信号（新客户/现有客户/合作伙伴均可能如此提问），Bot 将其识别为中性问题直接回答。TC-B2 通过是因为"Can you handle X?"带有业务需求信号，触发了新客户流程 | Bot answered product question immediately without customer type identification or lead collection |

---

### 补充问题 

| # | TC | Severity | Description | 观察来源 |
|---|----|----------|-------------|----------|
| P1 | TC-B/C/H | High *(待与 CINNOX 团队确认)* | **Lead 收集前置策略存在转化漏斗风险**：v1.1 要求回答任何问题前先收集 4 个字段，对于直接提问型用户（"Does CINNOX support WhatsApp?"）会造成明显阻力，可能导致用户流失。行业惯例为渐进式信息收集（progressive profiling），建议评估前置 vs 渐进两种策略的转化差异 | TC-B1/B2/C1 均观察到 4 字段收集发生在回答前 |
| P2 | TC-B/C/G | Medium *(待与 CINNOX 团队确认)* | **引用来源使用内部文件名，不适合 C 端展示**：Bot 引用 `EN_CINNOX_Pricing_07012024_v3.xlsx`、`M800_Global_Rates.xlsx` 等内部文档名，对真实用户无意义且暴露内部资料命名，应替换为"根据我们的定价文档"、"根据官网发布的费率表"等用户友好表述 | TC-C1/C2/C3/G1 均出现内部文件名引用 |
| P3 | TC-E/F | High *(待与 CINNOX 团队确认)* | **转人工流程不完整，缺少后续承诺**：Bot 说"请稍候，我为您接入团队"后对话终止，未提供工单号、预计响应时间、联系渠道或"是否会有人主动跟进"的说明。客户无法判断是同步等待还是异步回访，真实场景下会造成信任损失 | TC-E1/E2/F1/F2 均以"please hold"结束，无后续说明 |
| P4 | TC-B/C | Medium | **收集完 lead 后缺少衔接原始问题的过渡**：Bot 在完成 4 字段收集后直接切换到回答，没有"好的，回到您刚才的问题——"类衔接语，用户体验上感到突然，且无法确认 Bot 是否仍记得原始问题 | TC-B2/C1/C2 均直接在收集后回答，无过渡 |
| P5 | TC-A/D | Medium | **收集完信息后无数据复述确认**：Bot 从未在收集完 Name/Company/Email/Phone 后复述确认，存在录入错误无人察觉的风险（如 TC-H1 的邮件地址 ryan@seoulmediad.com 可能是拼写错误，Bot 未提示） | TC-A1/D1/H1 均无数据确认步骤 |
| P6 | TC-A/D | Medium | **4 步串行问答交互效率低**：Name → Company → Email → Phone 各占一轮，共需 4 次来回才能进入正题。可考虑合并："请问您的姓名和公司？"获取后再问联系方式，减少往返次数，降低对话疲劳感 | TC-D1/A1/B2 等均经历完整 4 轮收集 |
| P7 | TC-C | Low | **价格信息以散文形式呈现，缺乏可比性**：TC-C2 中 Bot 在对话文本中描述"OCC 月付 $59、年付 $50，DC 月付 $29、年付 $20"，文字叙述不如表格直观，对需要横向比较多个套餐的用户体验较差 | TC-C2 定价回答 |
| P8 | TC-E/F | Medium *(待与 CINNOX 团队确认)* | **转人工后的预期管理缺失**："please hold" 未说明等待方式（Chat / 电话 / 邮件）、等待时长或工作时间限制。Billing（TC-E1）、Tech Support（TC-E2）、Partnership（TC-A3）性质不同，后续处理方式很可能不同，但 Bot 使用了同一套话术 | TC-A3/E1/E2/F1/F2 |
| P9 | TC-D2 | Medium *(待与 CINNOX 团队确认)* | **拒绝提供电话后缺少中间选项**：用户说"不想留电话"，Bot 解释一次后立即提出转人工，跳过了"仅邮件是否可行"等替代方案，用户体验上感觉选择被剥夺，流程跳跃过快 | TC-D2 |
| P10 | TC-E/F | Low | **升级话术不一致，用户预期不统一**：各场景转人工措辞不统一（"please hold" / "our team will be in touch shortly" / "let me connect you now"），给用户的预期不同（同步等待 vs 异步回访），建议统一为包含明确后续动作的模板话术 | TC-A3/E1/E2/F2 |
| P11 | 全流程 | Medium | **记录客户资信期间缺少进度提示**：客户回复资信字段后，Bot 在后台处理/记录期间没有任何"记录中…"或"稍候"类的进度反馈，用户无法判断系统是否收到回复，体验存在中断感 | 所有含 lead 收集的 TC（TC-A/B/C/D/H）均观察到此现象 |
| P12 | 全流程 | High | **记录完成后回复追加在同一条消息内，缺少消息边界**：Bot 完成资信收集后，直接在同一条消息末尾追加后续引导或产品回答，未另起新消息。用户无法辨认哪里开始是"下一步内容"，阅读体验差，尤其在移动端难以定位新内容的起点 | 所有含 lead 收集的 TC（TC-A/B/C/D/H）均观察到此现象 |
| P13 | 全流程 | Medium | **单条消息过长，用户难以消化**：Bot 在一条回复中同时包含资信确认、产品说明、价格信息、下一步引导等多项内容，篇幅过长，用户无法快速找到关键信息，建议拆分为多条简短消息或使用结构化格式（分段/要点列表）展示 | TC-B2/C1/C2/F1 等信息密集型 TC 均观察到此现象 |
| P14 | TC-G1 | Low *(测试设计建议)* | **TC-G1 与 TC-B1 的触发结构相同但判定标准不一致**：TC-G1 的 T1（"How much is a UK local number?"）与 TC-B1 T1（"Does CINNOX support WhatsApp integration?"）结构完全相同——首条消息为直接产品/价格问题、无身份信号。TC-B1 以"Bot 未先识别客户身份"判 FAIL，但 TC-G1 通过标准仅覆盖上下文连贯性，未要求客户身份确认，实际测试中 Bot 也未问新/老客户即进入价格查询。建议 v1.2 中为 TC-G1 补充"首条消息无身份信号时是否触发身份确认"的 checklist 项，与 TC-B 保持一致 | TC-G1 实测：Bot 未问新/老客户身份，直接进入 DID 价格流程 |
| P15 | TC-A4 | Medium *(待与 CINNOX 团队确认)* | **现有客户产品咨询路径缺少身份核验，存在潜在安全盲区**：当前 Flow 设计为「根据初始消息判断是否为现有客户 → 若是 → 直接 RAG 回答」，但用户初始消息通常不包含 Account ID，Bot 无法核实其真实身份，任何人均可声称是现有客户以跳过 lead 收集流程直接获取 RAG 答案。风险大小取决于 RAG 内容性质：若均为公开产品信息（功能介绍、公开定价），风险低，现有设计可接受；若包含客户专属信息（合同价格、账号配置、专属优惠），则需在此路径补充身份核验分支。**需与 CINNOX 团队确认**：现有客户产品咨询路径的 RAG 知识库是否包含非公开的客户专属信息？是否需要补充身份验证步骤？ | TC-A4 实测：Bot 接受"We are an existing CINNOX customer"即进入 RAG，未要求提供任何可验证的账号信息 |


---

## Bug Log

> 与 Issues Log / 补充问题不同，此处记录的是功能性退化或可复现的异常行为，需要开发侧跟进排查。

| # | 发现时间 | 严重程度 | 描述 | 对比基准 | 复现步骤 |
|---|----------|----------|------|----------|----------|
| B1 | 2026-03-03 下午 | High | **价格查询在最新 session 中无法返回结果**：session_20260303_135740（13:57）中价格查询正常返回（UK DID $19/月等），但随后创建的 session（code: `6NJSHAIU`，expires: 2026-03-04 15:53:41）中相同问题无法查出价格。最近两个 session 文件（14:01/14:07）的 turn_count=0 且 conversation 为空，疑似新 session 内 KB 查询未被触发或 RAG 路径中断 | session_20260303_135740 可正常返回价格 | 1. 启动新 session；2. 询问"How much is a UK local number?"等价格问题；3. 观察 Bot 是否返回具体价格 （目前已经复现不出来了）|

---

**Severity Guide**:
- **Critical**: Hallucination, wrong routing on immediate handoff request (TC-B3, TC-F2)
- **High**: Wrong pricing, failed to collect required fields, wrong customer type identification, answered product question before collecting lead info
- **Medium**: Suboptimal phrasing, minor routing delay, missing one checklist item (e.g., forgot email)
- **Low**: Style/tone issue, cosmetic, KB retrieval gap with no hallucination

---

## Flow Compliance Summary *(v1.1)*

| Flow Branch | Tested By | Status |
|-------------|-----------|--------|
| 新客户 → 收集信息 → 产品咨询/RAG | TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 | ⚠️ TC-B1 有问题；TC-H2 行为正确但触发元流程未覆盖分支 |
| 新客户 → 收集信息 → 其他问题 → 转人工 | TC-D2 | ✅ |
| 现有客户 → 产品咨询 → RAG → 转人工 | TC-A4 | ✅ |
| 现有客户 → 套餐计费 → 收集信息 → 转人工 | TC-E1 | ✅ (Email 未收集) |
| 现有客户 → 投诉 → 收集信息 → 转人工 | TC-A2, TC-E2 | ⚠️ Email 未收集 |
| 其他（合作伙伴）→ 收集信息 → 转人工 | TC-A3 | ✅ |
| 直接要求转人工（flow gap）| TC-F2 | ✅ |



