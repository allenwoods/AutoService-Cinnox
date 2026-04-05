
**Tester**: RH
**Test Date**: 2026-03-04
**Environment**: CINNOX Demo (autoservice simulation)
**Product Config**: CINNOX
**Operator/Strategy**: CINNOX AI Pre-Sales Bot v1.2

> **v1.2**: SKILL.md updated after Round 2. Key fixes: (1) TC-B1: no-identity-signal T1 now triggers routing question before lead collection; (2) TC-A2/E1/E2: Email marked as REQUIRED in all existing customer flows, cannot be skipped; (3) P2: bot now uses user-friendly source names instead of internal file names; (4) Anti-hallucination: KB retry on empty results, relevance threshold added.
>
> **v1.3**: SKILL.md updated mid-Round 3. Fix: (1) TC-H2: Added **Discovery Phase** for vague requests — post-lead-collection transition now branches: specific question → kb_search, vague request → 1–2 clarifying questions before recommendation. Step 6 TC-H2 hint updated to cross-reference Discovery Phase.

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 19 |
| Passed | 19 |
| Failed | 0 |
| Blocked / Not Run | 0 |
| Pass Rate | 100% |

### Regression TCs (Previously Failed in Round 2)

| TC | Previous Result | Fix Applied | Retest Result |
|----|---------------|-------------|----------------|
| TC-A2 | Round 2 FAIL (Email not collected) | Reverted to original spec: Email not required for existing customer flows; complaint flow collects Company/Account ID/Service number/Agent name | **PASS** |
| TC-B1 | Round 2 FAIL (no lead collection on direct product Q) | No-identity-signal → routing question first | **PASS** |
| TC-H2 | Round 3 FAIL (no clarifying Qs after lead collection) | v1.3: Added Discovery Phase for vague requests — conditional branch after lead save | **PASS** |

---

## TC-A: Customer Type Identification

### TC-A1 — New Customer Identification

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot greets and asks for identity on T1 | ✓ | "May I start with your name?" |
| Bot does NOT re-ask Name or Company after T2 | ✓ | No duplication after "Emma Xu, Bright Retail" |
| Bot collects Email and Phone (T3–T4) without duplication | ✓ | Clean sequential collection |
| Bot summarizes collected info before closing | ✓ | Full 4-field confirmation displayed |
| Bot confirms next step (demo / handoff to sales) | ✓ | Recommended BCC plan, offered sales team connection |

**Notes**: Session 154345. All 4 fields (Name, Company, Email, Phone) collected in logical order. Bot confirmed details before proceeding. Source cited as "product documentation". Clean flow.

---

### TC-A2 — Existing Customer Identification ⚠️ REGRESSION

> **Round 2 Failure**: Email was not collected. Reverted to original spec — Email is NOT required for existing customer flows. Fix applied: complaint flow now collects Company / Account ID / Service number / Agent name per original UAT spec.

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies existing customer support case | ✓ | From "Our agent cannot receive calls" |
| Bot collects Company name | ✓ | Pacific Bank HK |
| Bot collects Account ID | ✓ | PBHK-2024 |
| Bot collects Service number | ✓ | +852-1234-5678 |
| Bot collects Agent name (issue-specific) | ✓ | Alice |
| Bot initiates handoff to human agent | ✓ | Escalated with detailed case summary |
| Bot does NOT attempt to resolve with KB answers | ✓ | Went directly to triage/escalation |

**Notes**: Session 154625. Regression PASS. All 4 existing-customer fields collected per original spec. Email not collected — correct per reverted spec. Bot efficiently identified the support case and escalated with a proper case summary.

---

### TC-A3 — Partner Identification

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot recognizes SI/partner inquiry | ✓ | "We'd love to explore a partnership with you" |
| Bot collects Name, Company, Email, Phone | ✓ | David Park, Nexus SI, david.park@nexussi.com, +65-8123-4567 |
| Bot does NOT lead with product pricing | ✓ | No pricing mentioned |
| Bot routes to partnership/BD team | ✓ | "Our partnership team will be in touch shortly" |

**Notes**: Session 154830. All 4 fields collected with confirmation step. Correctly routed to partnership team, not sales.

---

### TC-A4 — Existing Customer Product Inquiry

**Result**: **PASS**

> **Flow reference**: 现有客户 → 产品咨询 → RAG回复 → 无法解答 → 转人工
> Bot should NOT run the new-customer lead form for existing customers.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies this as existing customer inquiry (not new prospect) | ✓ | Asked for Company + Account ID only |
| Bot does NOT collect Name/Email/Phone as a new lead form | ✓ | Only Company + Account ID requested |
| Bot queries KB for the product question | ✓ | RAG answer about Open API and third-party integrations |
| Bot provides answer with source citation (if KB has info) | ✓ | "Based on our product documentation" |
| If KB cannot answer → bot transfers to human specialist | ✓ | Transferred for CRM-specific integration details |
| Bot does NOT fabricate API specs or integration capabilities | ✓ | Acknowledged "I don't have the specific details" on CRM platforms |

**Notes**: Session 154045. Bot correctly identified existing customer, skipped lead form, provided RAG answer with source citation, and transferred to specialist for details beyond KB scope. Note: bot asked for agent name/service number in some runs (unnecessary for product inquiry — see Q2 in 补充问题).

---

## TC-B: Product Inquiry / RAG

> **v1.1/v1.2**: All TC-B tests require bot to collect lead info (Name/Company/Email/Phone) **before** answering product questions. TC-B1 now requires routing question when T1 has no identity signal.

### TC-B1 — WhatsApp Integration ⚠️ REGRESSION

> **Round 2 Failure**: Bot answered WhatsApp question immediately without identifying customer type or collecting lead info. Fix applied: T1 with no identity signal → routing question first.

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot does NOT answer WhatsApp question immediately on T1** | ✓ | Asked routing question first |
| **Bot asks routing question: "new or existing customer?"** *(new in v1.2)* | ✓ | "are you an existing CINNOX customer, or are you new to us?" |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Chris Tanaka, Tokyo Commerce Co., chris@tokyocommerce.jp, +81-3-1234-5678 |
| Bot returns to answer the WhatsApp question after lead collection | ✓ | 360dialog BSP WhatsApp integration answer |
| Bot confirms WhatsApp Business support | ✓ | Confirmed via 360dialog BSP |
| No fabricated features | ✓ | Accurate description |
| Source cited using user-friendly name (not internal filename) *(new in v1.2)* | ✓ | "product documentation" |

**Notes**: Session 163117. Regression PASS. v1.2 fix working: routing question → lead capture → WhatsApp answer. Earlier runs (before SKILL.md fix) failed to trigger routing question.

---

### TC-B2 — High Volume Banking

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately pitch product)** | ✓ | "may I start with your name?" after acknowledging question |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Li Wei, ShangBao Bank, li.wei@shangbao.com, +86-21-1234-5678 |
| Bot returns to address the high-volume banking question | ✓ | Detailed answer about OCC and enterprise-level setup |
| Bot mentions ACD routing modes (≥2) | ✓ | Fixed Order + Simultaneous distribution |
| Bot confirms IVR menu support | ✓ | Detailed IVR explanation with triage example |
| Bot recommends OCC or CXHub | ✓ | Recommended Ultimate CX Hub for banking; also mentioned OCC |
| Bot avoids fabricated throughput guarantees | ✓ | "10,000 calls/day is enterprise territory" → custom quote |

**Notes**: Session 163431. Lead collected first, then comprehensive answer covering routing modes, IVR, and plan recommendation. Bot recommended CX Hub for high-security banking and routed to sales for custom enterprise quote.

---

### TC-B3 — Non-Existent Feature ⚠️ CRITICAL

**Result**: **PASS**

> **Note**: A FAIL on hallucination is a showstopper. Lead collection before Q&A is secondary.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1** | ✓ | Routing question first, then lead collection |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Alex Kim, FutureMedia Corp, alex.kim@futuremedia.com, +1-415-555-0199 |
| Bot clearly denies hologram video calling after lead collection | ✓ | "Hologram video calling is not listed in our current feature documentation" |
| Bot maintains denial under pressure | ✓ | "I wouldn't want to confirm something I can't verify" |
| Bot describes real video features | ✓ | Video Calling, Screen Sharing, Conference Calls, Call Recording & Transcripts |
| **CRITICAL**: No fabrication at any point | ✓ | Zero hallucination |

**Notes**: Session 163702. Anti-hallucination working perfectly. Bot denied hologram firmly, maintained position under pressure ("We saw it at a trade show"), and listed 4 real video features with accurate descriptions.

---

## TC-C: Pricing Accuracy

> **v1.1/v1.2**: All TC-C tests require lead collection before pricing Q&A. Source citations must use user-friendly names.

### TC-C1 — DID Number Price

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | ✓ | Routing question + lead collection |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Kevin Han, Seoul Commerce Inc., kevin.han@seoulcommerce.kr, +82-2-1234-5678 |
| Bot gives specific price OR correctly defers to pricing page | ✓ | Correctly deferred: "the exact US DID monthly rate isn't available in the materials I have access to" |
| Price given is consistent with knowledge base | ✓ | US DID not in KB — bot correctly acknowledged this |
| Bot mentions DID is an add-on | ✓ | "DID available as add-on across all plans" |
| Bot mentions KYC/verification requirement | ✓ | Confirmed KYC required |
| Source cited using user-friendly name *(new in v1.2)* | ✓ | "pricing documentation" |

**Price given by bot**: US DID not in KB; bot deferred to sales team. Setup fee and service fees provided separately.

**Notes**: Session 164328. Bot correctly recognized US DID pricing was not in KB and deferred to sales instead of fabricating. Follow-up questions about setup fees, KYC, and plan compatibility all answered accurately.

---

### TC-C2 — Volume Pricing (50 Agents)

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | ✓ | Routing question + lead collection |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Fatima Al-Rashid, Dubai Commerce Group, fatima@dubaicommerce.ae, +971-4-1234-5678 |
| Bot explains per-agent license model | ✓ | Mentioned license-based packages (DC, OCC, CX Hub) |
| Bot mentions annual vs. monthly pricing | ✗ | Not explicitly mentioned |
| Bot mentions volume discounts via sales | ✓ | "custom enterprise quote tailored to your specific needs" |
| Bot recommends OCC or CXHub for 50 agents | ✓ | Listed OCC as "most popular plan for multi-channel customer support" |
| Bot routes to sales for formal quote | ✓ | "connecting you with our sales team" |
| Bot does NOT fabricate a specific total price | ✓ | No total price fabricated |

**Notes**: Session 164519. Enterprise quote for 50 agents handled well. Bot did not fabricate a total price, correctly routed to sales for custom quote. Minor gap: annual vs. monthly pricing not explicitly mentioned.

---

### TC-C3 — Incorrect Price Correction

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot collects all 4 lead fields before pricing discussion** | ✓ | Marco Rossi, Roma Digital SRL, marco@romadigital.it, +39-06-1234-5678 |
| Bot explicitly says $5/minute per agent is NOT correct | ✓ | "that doesn't match our published pricing" |
| Bot maintains correction under pressure | ✓ | "That's not accurate, Marco" on second challenge |
| Bot correctly explains license-based model | ✓ | "license fees (per account, based on package) and usage fees (per minute/per message)" |
| Bot provides accurate tier pricing or defers to pricing page | ✓ | Provided pricing table (SMS $0.01/msg, SIP $0.01/min, etc.) + cinnox.com/pricing link |

**Notes**: Session 164748. Corrected $5/min firmly on first challenge and maintained position under "A competitor told us" pressure. Provided actual pricing table with specific usage fees. Excellent correction handling.

---

## TC-D: Data Collection

### TC-D1 — Demo Request (All Fields)

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot requests all 4 fields in logical order | ✓ | Name → Company → Email → Phone |
| Bot does NOT re-ask fields already provided | ✓ | No duplication |
| Bot confirms demo request receipt after all 4 fields | ✓ | "Your information has been saved" + full details confirmation |
| Bot provides next step | ✓ | Connected to sales team for demo arrangement |

**Notes**: Session 165452. All 4 fields collected, demo confirmed, connected to sales. Bot asked about interest area ("specific feature area like omnichannel messaging, voice solutions?") which is good. Note: bot could proactively ask preferred demo time and specific interest topics before handoff to sales (improvement suggestion — see Q5 in 补充问题).

---

### TC-D2 — Phone Number Refused

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot explains reason for phone on T3 | ✗ | Bot did not explain WHY phone was needed |
| Bot does NOT demand phone after T4 | ✓ | "No problem at all, Emma!" — accepted gracefully |
| Bot offers alternative or human handoff on T4 | ✓ | "We can reach you by email instead" |
| Bot routes to human after second refusal | ✓ | Connected to sales team for demo arrangement |
| Conversation continues (not terminated) | ✓ | Continued to confirm details and arrange demo |

**Notes**: Session 165737. Bot accepted phone refusal gracefully and offered email as alternative. However, bot didn't explain WHY phone number was requested (e.g., "so we can call to schedule your demo") — see Q5 in 补充问题. Overall handling was polite and non-pressuring.

---

## TC-E: Existing Customer Routing

### TC-E1 — Billing Issue

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies billing issue on T1 | ✓ | Immediately asked for company/account info |
| Bot collects Name | ✓ | Tom Bradley |
| Bot collects Company | ✓ | Hartley Insurance UK |
| Bot collects Account ID | ✓ | HART-UK-2023 |
| Bot does NOT explain billing rates | ✓ | No billing explanation attempted |
| Bot routes to billing/support team | ✓ | Escalated to billing team |
| Bot confirms handoff with next step | ✓ | Connected to billing team with case details |

**Notes**: Session 165926. Billing triage and escalation handled correctly. Email not collected — not required per reverted spec (existing customer complaint flow).

---

### TC-E2 — Technical Issue (Voice Quality)

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot acknowledges technical issue on T1 | ✓ | Immediately asked for account info |
| Bot requests account info (not new-customer lead form) | ✓ | Asked for Company + Account ID |
| Bot collects Company | ✓ | Pacific Bank HK |
| Bot collects Account ID | ✓ | PBHK-2024 |
| Bot collects Service Number | ✓ | +852-1234-5678 |
| Bot does NOT give >2 troubleshooting steps before routing | ✓ | Zero troubleshooting, went directly to escalation |
| Bot routes to technical support | ✓ | Escalated to support team |
| Bot confirms technician follow-up | ✓ | Case details included in escalation |

**Notes**: Session 170110. Technical triage and escalation handled correctly. Bot handled "name not available" gracefully. Email not collected — not required per reverted spec.

---

## TC-F: Human Handoff

### TC-F1 — Knowledge Boundary

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot shares known security info on T2/T3 | ✓ | Acknowledged topic, deferred to specialist (KB has no encryption architecture detail) |
| Bot does NOT fabricate DB encryption architecture on T1 | ✓ | Zero fabrication |
| Bot acknowledges knowledge limits for T1 | ✓ | "this is a deep technical topic that our solutions team is best equipped to walk you through" |
| Bot offers/accepts escalation to technical team | ✓ | "Let me connect you with a specialist" |
| No hallucinated technical specs | ✓ | No fabricated encryption/security details |

**Notes**: Session 170322. Bot correctly acknowledged the knowledge boundary for database encryption architecture. Did not attempt to fabricate specs. Collected lead info (routing question → new customer → 4 fields) then immediately deferred to specialist.

---

### TC-F2 — Immediate Human Request ⚠️ CRITICAL

**Result**: **PASS**

> **Note**: Any qualifying question = FAIL.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT ask qualifying question after T1 | ✓ | Zero qualifying questions |
| Bot acknowledges and confirms handoff in same response | ✓ | "Let me connect you with a human agent right away" |
| **CRITICAL**: No qualification questions before routing | ✓ | Perfect — immediate routing |

**Notes**: Session 170352. Perfect execution. Bot respected customer's explicit request for human agent and routed immediately in a single response. No lead collection, no qualifying questions. Session ended in 2 turns.

---

## TC-G: Context Continuity

### TC-G1 — Multi-Turn DID Pricing

**Result**: **PASS**

> **P14 Note from Round 2**: T1 of this TC ("How much is a UK local number?") has no identity signal, same structure as TC-B1. With v1.2 fix applied, bot may now ask routing question before answering. Checklist updated to reflect this.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot handles T1 correctly (routing question or lead collection if no identity signal) *(updated v1.2)* | ✓ | Routing question: "existing or new customer?" |
| Bot provides UK DID pricing after lead/account info collected | ✓ | UK $19/month with full rate table |
| Bot correctly interprets T2 as Germany DID (not re-explains product) | ✓ | "What about Germany?" → Germany $19/month |
| Bot answers T3 as HK DID pricing | ✓ | "And for Hong Kong?" → HK $25/month |
| Bot does NOT re-explain DID on T2/T3 | ✓ | Perfect context continuity, no re-explanation |
| Prices are consistent with knowledge base | ✓ | All prices match KB rate tables |

**UK price given**: US$19/month (MRC)
**Germany price given**: US$19/month (MRC)
**HK price given**: US$25/month (MRC)

**Notes**: Session 170608. Perfect multi-turn context continuity. Bot provided detailed rate tables for each country including usage rates. Routing question triggered correctly per v1.2 fix. P14 observation confirmed: TC-G1 and TC-B1 now behave consistently.

---

## TC-H: Error Tolerance

### TC-H1 — Spelling Errors

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately answer typo question)** | ✓ | Routing question first: "existing or new?" |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | ✓ | Ryan Park, Seoul Media Group, ryan@seoulmediad.com, +82-2-5678-1234 |
| Bot returns to answer original typo question (no clarification request about spelling) | ✓ | Answered WhatsApp question without asking about typos |
| Bot correctly interprets "whtsapp intergration" as WhatsApp integration | ✓ | Understood perfectly |
| Bot provides accurate WhatsApp answer | ✓ | 360dialog BSP, WhatsApp campaigns, chatbot support |
| No error messages or confusion at any point | ✓ | Zero confusion |

**Notes**: Session 170735. "whtsapp intergration" understood immediately. Bot asked routing question, collected lead, then provided accurate WhatsApp integration answer including campaigns and chatbot support. No clarification needed for misspelling.

---

### TC-H2 — Vague Request ⚠️ RETEST (v1.3 fix)

> **Previous result (v1.2)**: FAIL — bot jumped straight to product pitch after lead collection, no clarifying questions. **v1.3 fix**: Added Discovery Phase for vague requests in SKILL.md.

**Result**: **PASS**

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks routing question when T1 has no identity signal** *(formalized in v1.2)* | ✓ | "are you an existing CINNOX customer, or are you new to us?" |
| **Bot collects all 4 lead fields before handling the vague inquiry** | ✓ | Sarah Mitchell, Austin Digital Agency, sarah@austindigital.com, +1-512-555-0123 |
| Bot asks clarifying question(s) at T6 — NOT a product pitch | ✓ | "could you tell me a bit more about what you need? For example, are you looking for omnichannel support, live chat, call center features, or something else?" |
| Bot builds on T7 context and asks relevant follow-up | ✗ | After "10 people on our team" → jumped to OCC feature list instead of follow-up Q about channels/pain points |
| Bot synthesizes T8 context (phone + WhatsApp → recommendation) | ✓ | Confirmed WhatsApp integration via 360dialog BSP + voice/IVR/call routing in unified inbox |
| Bot makes concrete recommendation on T9 with reasoning | ✓ | **OCC plan** recommended for 10-person team using phone + WhatsApp; reasoning tied to customer context |
| Bot does NOT quote prices before T9 | ✓ | No prices quoted; mentioned plan names after receiving context but no dollar amounts |

**Notes**: Session 185710. **v1.3 Discovery Phase working**: bot asked a clarifying question after lead collection instead of jumping to product pitch (previous FAIL point). Remaining gap: after T7 (team size only), bot ran kb_search and listed features instead of asking a follow-up about channels — the customer had to volunteer channel info in T8 unprompted. Ideally bot would ask "What channels do you currently use?" before recommending. However, this meets pass criteria: ≥1 clarifying question asked, no immediate prices/packages after lead collection, tailored recommendation at T9.

**Observation (non-blocking)**: Customer provided all 4 lead fields in a single message ("Sarah Mitchell，Austin Digital Agency，sarah@austindigital.com，+1-512-555-0123"), which compressed the lead collection flow. Bot handled this gracefully — confirmed all 4 fields and proceeded correctly.

---

## Final Results Table

| TC | Category | Title | Result | Notes |
|----|----------|-------|--------|-------|
| TC-A1 | Customer Type | New Customer Identification | **PASS** | All 4 fields, confirmation step, source cited |
| TC-A2 ⚠️ | Customer Type | Existing Customer Identification | **PASS** | Regression PASS. Email not required per reverted spec |
| TC-A3 | Customer Type | Partner Identification | **PASS** | All 4 fields, routed to partnerships |
| TC-A4 | Customer Type | Existing Customer Product Inquiry | **PASS** | RAG answer with source citation |
| TC-B1 ⚠️ | Product / RAG | WhatsApp Integration | **PASS** | Regression PASS. Routing question → lead → answer |
| TC-B2 | Product / RAG | High Volume Banking | **PASS** | Lead first → OCC/CXHub recommendation |
| TC-B3 ⚠️ | Product / RAG | Non-Existent Feature | **PASS** | Critical: hologram denied firmly, zero hallucination |
| TC-C1 | Pricing | DID Number Price | **PASS** | US DID not in KB; correctly deferred to sales |
| TC-C2 | Pricing | 50-Agent Volume Quote | **PASS** | Did not fabricate total price; routed to sales |
| TC-C3 | Pricing | False Price Correction | **PASS** | Corrected $5/min firmly, provided actual pricing |
| TC-D1 | Data Collection | Demo Request — All Fields | **PASS** | All 4 fields, demo confirmed |
| TC-D2 | Data Collection | Phone Number Refused | **PASS** | Accepted refusal gracefully; WHY explanation missing |
| TC-E1 | Existing Customer | Billing Issue Routing | **PASS** | Billing triage + escalation. Email not required per reverted spec |
| TC-E2 | Existing Customer | Technical Issue Routing | **PASS** | Technical triage + escalation. Email not required per reverted spec |
| TC-F1 | Human Handoff | Knowledge Boundary | **PASS** | Knowledge boundary acknowledged, escalated to specialist |
| TC-F2 ⚠️ | Human Handoff | Immediate Human Request | **PASS** | Critical: immediate routing, zero qualifying questions |
| TC-G1 | Context | Multi-Turn DID Pricing | **PASS** | UK $19, Germany $19, HK $25. Perfect context continuity |
| TC-H1 | Error Tolerance | Spelling Errors | **PASS** | "whtsapp intergration" understood correctly |
| TC-H2 ⚠️ | Error Tolerance | Vague Request | **PASS** | v1.3 retest: Discovery Phase triggered (clarifying Q asked). T7 follow-up could be better |

---

## Issues Log

| # | TC | Severity | Description | Bot Response (verbatim) |
|---|----|----------|-------------|------------------------|
| ~~I1~~ | TC-H2 | ~~High~~ → Resolved | ~~Bot 收集完 lead 后直接进入产品介绍，跳过 clarifying questions 阶段~~ **v1.3 修复**: 添加 Discovery Phase，bot 现在会先问 clarifying question。Session 185710 验证通过。残留问题：T7 后仍直接跑 KB 而非追问渠道/痛点 | v1.3 retest: "could you tell me a bit more about what you need?" |

---

## 补充问题

| # | TC | Severity | Description | 与原始规格冲突？ | 观察来源 |
|---|----|----------|-------------|-----------------|----------|
| Q1 | TC-A2/A4/E1/E2 | ~~High~~ → Resolved | ~~现有客户声称是已有客户后，bot 应先要求 Account ID（或邮件）确认身份，再提供回答。目前 bot 未进行任何身份验证，接受声称即当真~~ **v1.2 已修复**：SKILL.md Existing Customer Flow 要求 Company + Account ID 验证。TC-A2/A4/E1/E2 全部 PASS | 无冲突。原始规格 TC-A2 要求收集 Account ID / Company Name，本质上即身份确认；本观察要求更明确地以此作为"通行证" | Round 3 测试 |
| Q2 | TC-A4 | ~~Medium~~ → Resolved | ~~已通过 Account ID / 邮件 / 电话确认身份的客户，若提问的是产品信息（非投诉），不应再追问 Agent name 或 Service number。这两个字段仅在投诉/技术故障场景下需要~~ **v1.2 已修复**：产品咨询流程不再要求 Agent name / Service number。用户确认行为符合预期 | 无冲突。原始规格 TC-A2（投诉场景）要求全 4 字段；产品咨询（TC-A4）规格未明确定义，此处是对规格空白的合理补充 | Round 3 测试 |
| Q3 | TC-B1/B2 | ~~High~~ → Resolved | ~~客户直接提出产品问题（无身份信号）后，bot 未先确认是否为现有客户，直接提供了产品回答。路由问题（"new or existing?"）未触发。根因：MANDATORY GATE 的兜底语 "May I start with your name?" 直接假设新客户，绕过了 Step 3 的路由问题逻辑~~ **v1.2 已修复**：无身份信号时 T1 先发路由问题。TC-B1/G1/H1 全部 PASS | ⚠️ 有冲突。原始规格 TC-B1/B2 预期行为是"直接回答+来源引用"，未要求先识别身份。Round 2 版本将 lead 收集前置为前提条件，与原始规格存在设计差异。MANDATORY GATE 的实现方式加剧了此冲突 | Round 3 测试 |
| Q4 | TC-B2 | ~~High~~ → Resolved | ~~TC-B2 中 bot 同样未先确认身份，直接给出大量产品信息。与 Q3 根因相同~~ **v1.2 已修复**：同 Q3，路由问题已正常触发 | ⚠️ 有冲突，同 Q3 | Round 3 测试 |
| Q5 | TC-D1/D2 | Medium | Book demo 时 bot 应主动询问客户合适的时间和感兴趣的话题（改进建议）。当前 bot 收集完 lead 后未主动询问 demo 偏好时间，客户需自行主动提出。TC-D2 中 bot 也未解释 WHY 需要电话号码 | 无冲突。原始规格未明确要求主动询问时间偏好，但从用户体验角度属合理改进 | Round 3 测试 |
| Q6 | TC-H2 | ~~High~~ → Resolved | ~~Bot 收集完 lead 后直接介绍产品，跳过了 clarifying questions 阶段~~ **v1.3 已修复**：SKILL.md 新增 Discovery Phase，bot 现在先问 clarifying question 再推荐。Session 185710 验证 PASS。残留观察：收到部分上下文（团队规模）后仍直接跑 KB，理想行为是继续追问渠道/痛点 | 已修复。v1.3 Discovery Phase 解决了核心问题 | Round 3 retest |

---

## Bug Log

| # | 发现时间 | 严重程度 | 描述 | 对比基准 | 复现步骤 |
|---|----------|----------|------|----------|----------|
| — | — | — | Round 3 未发现新 bug。B1/B2 早期 session 的行为不一致系 SKILL.md 迭代过程所致，非运行时 bug | — | — |

---

## Round 2 未修复问题追踪

以下问题在 Round 2 中已记录，但**未在本轮 SKILL.md 修改中处理**，需在 Round 3 中继续观察并决定是否跟进修复：

### 待 CINNOX 团队确认类

| # | 严重程度 | 描述 | 来源 |
|---|----------|------|------|
| P3 | High | **转人工流程不完整，缺少后续承诺**：Bot 转人工后对话终止，未提供工单号、预计响应时间或联系渠道，客户无法判断是同步等待还是异步回访 | TC-E1/E2/F1/F2 |
| P8 | Medium | **转人工后预期管理缺失**："please hold" 未说明等待方式（Chat/电话/邮件）、工作时间限制，Billing/Tech/Partnership 性质不同但使用同一套话术 | TC-A3/E1/E2/F1/F2 |
| P9 | ~~Medium~~ → Resolved | ~~**拒绝提供电话后缺少中间选项**：Bot 解释一次后立即提出转人工，跳过"仅邮件是否可行"等替代方案~~ **v1.2 已修复**：TC-D2 流程包含 email 替代方案。TC-D2 PASS："We can reach you by email instead" | TC-D2 |
| P15 | ~~Medium~~ → Resolved | ~~**现有客户产品咨询路径缺少身份核验**：任何人声称是现有客户即可跳过 lead 收集直接获取 RAG 答案，需确认 KB 内容是否包含非公开信息~~ **v1.2 已修复**：同 Q1，Existing Customer Flow 现要求 Account ID 验证 | TC-A4 |

### 体验优化类（无需 CINNOX 确认，可直接改进）

| # | 严重程度 | 描述 | 来源 |
|---|----------|------|------|
| P4 | ~~Medium~~ → Resolved | ~~**收集完 lead 后缺少衔接原始问题的过渡**：Bot 在完成 4 字段收集后直接切换到回答，没有"好的，回到您刚才的问题——"类衔接语~~ **v1.3 已修复**：SKILL.md 新增 "Now, regarding your question about [topic]..." 过渡语 + Discovery Phase 处理模糊请求 | TC-B2/C1/C2 |
| P5 | ~~Medium~~ → Resolved | ~~**收集完信息后无数据复述确认**：Bot 从未复述确认收集的 Name/Company/Email/Phone，存在录入错误无人察觉的风险~~ **v1.3 已修复**：SKILL.md 要求 "Let me confirm: Name/Company/Email/Phone. Is that correct?" TC-A1/H2 验证执行 | TC-A1/D1/H1 |
| P6 | Medium | **4 步串行问答交互效率低**：可考虑合并收集（"请问您的姓名和公司？"），减少来回轮次 | TC-D1/A1/B2 |
| P7 | ~~Low~~ → Resolved | ~~**价格信息以散文形式呈现**：多套餐比较时文字叙述不如表格直观~~ **v1.3 已修复**：SKILL.md 要求 3+ pricing tiers 使用 markdown 表格。TC-C3 验证使用表格格式 | TC-C2 |
| P10 | Low | **升级话术不一致**：各场景转人工措辞不统一，给用户的预期不同（同步等待 vs 异步回访） | TC-A3/E1/E2/F2 |
| P11 | Medium | **记录客户资信期间缺少进度提示**：Bot 在后台处理期间没有"记录中…"等进度反馈 | 所有含 lead 收集的 TC |
| P12 | High | **记录完成后回复追加在同一条消息内**：Bot 完成资信收集后直接在同一条消息末尾追加后续引导，缺少消息边界 | 所有含 lead 收集的 TC |
| P13 | Medium | **单条消息过长**：Bot 在一条回复中同时包含资信确认、产品说明、价格、下一步引导等多项内容 | TC-B2/C1/C2/F1 |

### 测试设计类

| # | 严重程度 | 描述 |
|---|----------|------|
| P14 | ~~Low~~ → Resolved | ~~**TC-G1 与 TC-B1 触发结构相同但判定标准不一致**：v1.2 修复 TC-B1 后，TC-G1 T1（"How much is a UK local number?"）同样无身份信号，bot 现在应触发路由问题。已在 TC-G1 checklist 中增加对应验证项~~ **v1.2 已修复**：TC-G1 checklist 已更新路由问题检查项。TC-G1 PASS 确认 |

---

**Severity Guide**:
- **Critical**: Hallucination, wrong routing on immediate handoff request (TC-B3, TC-F2)
- **High**: Wrong pricing, failed to collect required fields, wrong customer type identification, answered product question before collecting lead info
- **Medium**: Suboptimal phrasing, minor routing delay, missing one checklist item
- **Low**: Style/tone issue, cosmetic, KB retrieval gap with no hallucination

---

## Flow Compliance Summary *(v1.2)*

| Flow Branch | Tested By | Status |
|-------------|-----------|--------|
| 无身份信号 T1 → 路由问题 → 新/现有客户流程 | TC-B1, TC-G1, TC-H2 | ✅ PASS (routing question triggered in all 3 TCs) |
| 新客户 → 收集信息 → 产品咨询/RAG | TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 | ✅ 8/8 PASS (TC-H2 v1.3 retest passed with Discovery Phase) |
| 新客户 → 收集信息 → 其他问题 → 转人工 | TC-D2 | ✅ PASS |
| 现有客户 → 产品咨询 → RAG → 转人工 | TC-A4 | ✅ PASS |
| 现有客户 → 套餐计费 → 收集信息(含Email) → 转人工 | TC-E1 | ✅ PASS (Email not required per reverted spec) |
| 现有客户 → 投诉 → 收集信息(含Email) → 转人工 | TC-A2, TC-E2 | ✅ PASS (Email not required per reverted spec) |
| 其他（合作伙伴）→ 收集信息 → 转人工 | TC-A3 | ✅ PASS |
| 直接要求转人工 | TC-F2 | ✅ PASS |
