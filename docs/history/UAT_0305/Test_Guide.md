# CINNOX UAT Test Guide

**Version**: 1.1
**Date**: 2026-03-03
**Total Test Cases**: 19
**Tester**: _______________
**Session Date**: _______________

> **v1.1 Changes**: Aligned with official conversation flow (flow.md).
> - New customer product/pricing TCs now require lead collection **before** RAG Q&A (TC-B/C/H group)
> - Existing customer complaint/technical TCs now require Email collection (TC-A2, TC-E2)
> - Added TC-A4: Existing Customer Product Inquiry (new scenario from flow)
> - TC-F2: Added note on flow gap

---

## How to Use

### Setup
1. Launch the customer service simulation:
   ```
   /cinnox-demo
   ```
2. The bot will initiate. You are now playing the customer role.

### During a Test
- Type each line in the **Tester Input** column exactly as written (you may paraphrase naturally)
- After each bot response, check the **Observation Checklist** items
- Record PASS/FAIL in `Results_Template.md`
- Note any unexpected bot behaviors verbatim

### Session Management
- Each TC that says **"New Session"** requires a fresh conversation
- TCs marked **"Continue Session"** or **"Same session"** build on the previous TC — do NOT restart

### Flow Reference
Per the official flow (flow.md):

| Customer Type | First Action | Then |
|---|---|---|
| New Customer | Collect Name / Company / Email / Phone | Product Q&A (RAG) or other |
| Existing Customer — Product Inquiry | Identify customer, query problem | RAG → if unresolved → transfer |
| Existing Customer — Billing / Complaint | Collect Name / Company / Email / Account ID | Transfer |
| Partner / Other | Collect Name / Company / Email / Phone | Transfer |

### Pass/Fail Rule
- A TC **FAILS** if ANY single Fail criterion is triggered
- Record partial passes (e.g., "2/3 checklist items passed") in the notes column

---

## TC-A: Customer Type Identification

### TC-A1: New Customer Identification

**目标**: Bot correctly identifies a new prospect, collects all 4 required fields without repeating questions, and offers next steps (demo / sales contact).

**Persona**:
| Field | Value |
|-------|-------|
| Name | Emma Xu |
| Company | Bright Retail Ltd |
| Email | emma.xu@brightretail.com |
| Phone | +852-9123-4567 |
| Account | N/A (new customer) |

**Pass Criteria**:
- Bot identifies Emma as a **new customer / prospect**
- Bot collects all 4 fields: Name, Company, Email, Phone
- Bot does NOT re-ask a field already provided
- Bot offers a clear next step (schedule demo, connect to sales, send info)

**Fail Criteria**:
- Bot treats her as an existing customer
- Bot skips any of the 4 required fields
- Bot asks for the same field twice
- Bot ends the conversation without a next step

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Hi, we are looking for a contact center solution for our team. | Opening — bot should ask who you are |
| T2 | My name is Emma Xu, and I'm from Bright Retail. | Provide Name + Company in one message |
| T3 | Sure, my email is emma.xu@brightretail.com | When bot asks for contact info |
| T4 | My phone number is +852-9123-4567 | When bot asks for phone |
| T5 | Yes, a demo would be great. | When bot offers a next step |

### Observation Checklist
- [ ] Bot greets and asks for identity on T1
- [ ] Bot does NOT re-ask for Name or Company after T2
- [ ] Bot collects Email and Phone (T3–T4) without duplication
- [ ] Bot summarizes collected info before closing
- [ ] Bot confirms a next step (demo booking, handoff to sales)

---

### TC-A2: Existing Customer Identification

**目标**: Bot correctly identifies an existing customer, collects all 5 required fields (including Email per flow), and routes to human agent.

**Persona**:
| Field | Value |
|-------|-------|
| Name | James Wong |
| Company | Pacific Bank HK |
| Email | james.wong@pacificbank.hk |
| Account ID | PBHK-2024 |
| Agent Name | Alice |
| Service Number | +852-1234-5678 |
| Issue | Agent cannot receive calls on CINNOX |

**Pass Criteria**:
- Bot identifies James as an **existing customer**
- Bot collects: Account ID, Company, **Email**, Agent name, Service number
- Bot routes to human support (does not try to solve the issue itself)

**Fail Criteria**:
- Bot treats James as a new customer
- Bot tries to troubleshoot the issue using RAG without collecting account info
- Bot does not collect Email address
- Bot does not transfer to human

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Our agent cannot receive calls on the CINNOX platform. | Existing customer issue — bot should recognize support scenario |
| T2 | Yes, I'm an existing customer. Company is Pacific Bank HK. | When bot asks about account status |
| T3 | Account ID is PBHK-2024 | When bot asks for account ID |
| T4 | The agent's name is Alice. | When bot asks for affected agent name |
| T5 | Service number is +852-1234-5678 | When bot asks for service number |
| T6 | james.wong@pacificbank.hk | When bot asks for email (required per flow) |
| T7 | Yes, please connect me to support. | When bot offers to escalate |

### Observation Checklist
- [ ] Bot identifies this as an existing customer support case
- [ ] Bot requests Account ID and service details (not generic contact info)
- [ ] Bot collects all 5 fields: Account ID, Company, Agent name, Service number, **Email**
- [ ] Bot initiates handoff to human agent / support team
- [ ] Bot does NOT attempt to resolve the call issue with KB answers

---

### TC-A3: Partner Identification

**目标**: Bot correctly identifies a system integrator / partner inquiry, collects contact info, and routes to the partnerships team.

**Persona**:
| Field | Value |
|-------|-------|
| Name | David Park |
| Company | Nexus SI Singapore |
| Email | david.park@nexussi.com |
| Phone | +65-8123-4567 |
| Role | System Integrator seeking partnership |

**Pass Criteria**:
- Bot identifies David as a **partner / SI** (not a customer)
- Bot collects Name, Company, Email, Phone
- Bot routes to partnerships / business development team

**Fail Criteria**:
- Bot treats David as a regular sales prospect
- Bot pitches product features/pricing without acknowledging the partnership angle
- Bot does not route to appropriate team

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | We are a system integrator and want to explore a partnership with CINNOX. | Partnership intent — bot should recognize SI/partner type |
| T2 | My name is David Park from Nexus SI in Singapore. | When bot asks for identity |
| T3 | david.park@nexussi.com | When bot asks for email |
| T4 | +65-8123-4567 | When bot asks for phone |
| T5 | Yes, we'd like to discuss reseller opportunities. | If bot asks about partnership type |

### Observation Checklist
- [ ] Bot recognizes partnership / SI inquiry (not a customer sale)
- [ ] Bot collects Name, Company, Email, Phone
- [ ] Bot does NOT lead with product pricing or packages
- [ ] Bot routes to partnership/BD team or confirms a follow-up

---

### TC-A4: Existing Customer Product Inquiry *(New in v1.1)*

**目标**: Bot correctly identifies an existing customer asking a product question, uses RAG to answer, and escalates only if RAG cannot resolve.

> **Flow reference**: 现有客户 → 产品咨询（使用/价格）→ RAG自动回复 → 无法解答 → 转人工
> Key difference from new customer: bot proceeds to RAG **without** first collecting a new lead form (Name/Email/Phone for marketing purposes). Account identification is sufficient.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Sophie Liu |
| Company | NovaTech HK |
| Account ID | NVHK-2025 |
| Inquiry | Does CINNOX support API integration with CRM systems? |

**Pass Criteria**:
- Bot identifies Sophie as an **existing customer** (not a new prospect)
- Bot does NOT request Name/Email/Phone as a lead form
- Bot queries KB and answers the CRM/API integration question with source citation
- If KB cannot answer → bot transfers to human

**Fail Criteria**:
- Bot treats Sophie as a new customer and collects full lead info (Name/Email/Phone) before answering
- Bot answers without consulting KB (fabricates API capabilities)
- Bot neither answers nor escalates

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | We are an existing CINNOX customer. Does CINNOX support CRM integration via API? | Existing customer + product question |
| T2 | NovaTech HK, account NVHK-2025. | When bot asks to identify the account |
| T3 | We're specifically interested in Salesforce. | Follow-up — drill into specific CRM |
| T4 | OK, can we speak with a technical specialist? | If bot cannot fully answer — trigger escalation |

### Observation Checklist
- [ ] Bot identifies this as an existing customer inquiry (not new prospect)
- [ ] Bot does NOT run new customer lead collection flow
- [ ] Bot queries KB for CRM/API integration information
- [ ] Bot provides answer with source citation (if KB has relevant info)
- [ ] If KB cannot answer fully → bot transfers to human specialist
- [ ] Bot does NOT fabricate API specifications or integration capabilities

---

## TC-B: Product Inquiry / RAG

> **v1.1 Note**: Per flow.md, a new customer must provide lead information (Name / Company / Email / Phone) **before** the bot proceeds to product Q&A. Each TC-B test now includes a lead collection phase. The test focus remains on the RAG accuracy, but lead collection must be completed first.

### TC-B1: WhatsApp Integration Inquiry

**目标**: After collecting lead info, bot confirms WhatsApp support and provides accurate feature details sourced from the knowledge base.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Chris Tanaka |
| Company | Tokyo Commerce Co. |
| Email | chris@tokyocommerce.jp |
| Phone | +81-3-1234-5678 |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** answering the WhatsApp question
- Bot confirms CINNOX supports WhatsApp Business integration
- Bot mentions key capabilities: manage WhatsApp inquiries on CINNOX, WhatsApp campaigns (with 360dialog), WhatsApp Business number purchase
- Information is consistent with feature list (OCC and CXHub plans include WhatsApp; DC does not)

**Fail Criteria**:
- Bot answers the WhatsApp question **before** collecting lead info
- Bot says CINNOX does NOT support WhatsApp
- Bot provides information that contradicts the feature list
- Bot fabricates WhatsApp features not in the knowledge base

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Does CINNOX support WhatsApp integration? | Direct feature question — bot should ask for identity first (new customer) |
| T2 | Chris Tanaka | When bot asks for name |
| T3 | Tokyo Commerce Co. | When bot asks for company |
| T4 | chris@tokyocommerce.jp | When bot asks for email |
| T5 | +81-3-1234-5678 | When bot asks for phone |
| T6 | *(bot now answers the WhatsApp question)* | Bot should return to answer T1 after lead collection |
| T7 | Which pricing plan includes WhatsApp? | Follow-up on plan availability |
| T8 | Can we run WhatsApp marketing campaigns? | Deeper feature question |

### Observation Checklist
- [ ] Bot asks for lead info after T1 (does NOT answer WhatsApp question immediately)
- [ ] Bot collects all 4 fields: Name, Company, Email, Phone (T2–T5)
- [ ] Bot returns to answer the WhatsApp question after lead collection
- [ ] Bot confirms WhatsApp Business support
- [ ] Bot mentions it's available on OCC and/or CXHub (NOT on DC plan)
- [ ] Bot correctly describes campaign capability (requires 360dialog)
- [ ] Bot mentions WhatsApp number purchase option (or defers to sales for pricing)
- [ ] No fabricated features

---

### TC-B2: High Volume Inbound Calls — Banking Scenario

**目标**: After collecting lead info, bot explains ACD/IVR/routing capabilities relevant to high-volume call center use.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Li Wei |
| Company | ShangBao Bank |
| Email | li.wei@shangbao.com |
| Phone | +86-21-1234-5678 |
| Context | Procurement lead, evaluating CCaaS for 10,000 calls/day |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** answering the banking question
- Bot addresses the high-volume use case meaningfully
- Bot mentions ACD routing modes: Simultaneous, Round Robin, Most Idle, or Fixed Order (at least 2)
- Bot mentions IVR menu for call routing
- Bot recommends OCC or CXHub for this scale
- Bot does NOT claim specific call volume capacity numbers not in the knowledge base

**Fail Criteria**:
- Bot answers the banking question **before** completing lead collection
- Bot gives vague or generic answer without mentioning ACD/IVR
- Bot fabricates specific SLA or capacity numbers (e.g., "handles 50,000 calls/hour")
- Bot recommends DC plan for a high-volume bank

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | We are a bank. Can you handle high volume inbound calls? About 10,000 per day. | Volume + industry context — bot should ask for identity first |
| T2 | Li Wei | When bot asks for name |
| T3 | ShangBao Bank | When bot asks for company |
| T4 | li.wei@shangbao.com | When bot asks for email |
| T5 | +86-21-1234-5678 | When bot asks for phone |
| T6 | *(bot now answers the banking question)* | Bot should return to address T1 |
| T7 | How do you route calls to the right agents? | ACD/routing follow-up |
| T8 | Do you have IVR capabilities? | Specific IVR question |
| T9 | What plan would you recommend for our size? | Package recommendation |

### Observation Checklist
- [ ] Bot asks for lead info after T1 (does NOT immediately pitch product)
- [ ] Bot collects all 4 fields: Name, Company, Email, Phone (T2–T5)
- [ ] Bot returns to address the high-volume banking question after lead collection
- [ ] Bot mentions ACD routing modes (at least 2 of: Simultaneous, Round Robin, Most Idle, Fixed Order)
- [ ] Bot confirms IVR menu support
- [ ] Bot recommends OCC or CXHub (not DC or BCC)
- [ ] Bot avoids stating specific throughput/capacity guarantees not in the KB

---

### TC-B3: Non-Existent Feature — Hallucination Test

**目标**: After collecting lead info, bot clearly states that CINNOX does NOT support hologram video calling, without fabricating or speculating.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Alex Kim |
| Company | FutureMedia Corp |
| Email | alex.kim@futuremedia.com |
| Phone | +1-415-555-0199 |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** answering the hologram question
- Bot clearly states the feature is not supported
- Bot does NOT make up technical explanations for how it could work
- Bot may pivot to real video/collaboration features that exist

**Fail Criteria** (**Critical — any failure here is a showstopper**):
- Bot answers the hologram question **before** collecting lead info *(minor — focus is on hallucination)*
- Bot claims CINNOX supports hologram video calling
- Bot says "it might be possible" or gives a vague answer that could be interpreted as confirmation
- Bot describes how the feature works as if it exists

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Do you support hologram video calling? We saw it at a trade show. | Fabricated feature test — bot should ask for identity first |
| T2 | Alex Kim | When bot asks for name |
| T3 | FutureMedia Corp | When bot asks for company |
| T4 | alex.kim@futuremedia.com | When bot asks for email |
| T5 | +1-415-555-0199 | When bot asks for phone |
| T6 | *(bot now answers the hologram question)* | CRITICAL: bot must deny hologram video calling |
| T7 | Are you sure? We specifically saw the CINNOX name on the booth. | Pressure test — bot should not capitulate |
| T8 | What video features do you actually support? | Pivot to real features |

### Observation Checklist
- [ ] Bot asks for lead info after T1 before answering product question
- [ ] Bot collects all 4 fields (T2–T5)
- [ ] Bot clearly denies hologram video calling on T6
- [ ] Bot maintains denial under pressure on T7 (does NOT change answer)
- [ ] Bot describes real video features on T8 (1-1 video call, screen sharing, video conference)
- [ ] **CRITICAL**: No fabrication at any point

---

## TC-C: Pricing Accuracy

> **v1.1 Note**: Per flow.md, new customers must provide lead information before pricing Q&A. Each TC-C test now includes a lead collection phase at the start.

### TC-C1: DID Number Price Inquiry

**目标**: After collecting lead info, bot provides accurate DID number pricing or correctly defers to pricing page/sales.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Kevin Han |
| Company | Seoul Commerce Inc. |
| Email | kevin.han@seoulcommerce.kr |
| Phone | +82-2-1234-5678 |
| Inquiry | US DID number monthly fee |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** answering the DID question
- Bot provides a specific price for US DID (or says it varies and directs to pricing page/sales)
- If bot gives a price, it must match the configured pricing data
- Bot mentions DID numbers are an add-on fee (not included in base license)
- Bot mentions KYC/verification requirement for virtual numbers

**Fail Criteria**:
- Bot answers the pricing question **before** completing lead collection
- Bot gives a fabricated price with false confidence
- Bot says $5/minute or any clearly wrong per-minute rate when asked about monthly DID fee
- Bot claims DID numbers are included in the base plan at no extra cost

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | How much is a US DID number per month? | Direct pricing question — bot should ask for identity first |
| T2 | Kevin Han | When bot asks for name |
| T3 | Seoul Commerce Inc. | When bot asks for company |
| T4 | kevin.han@seoulcommerce.kr | When bot asks for email |
| T5 | +82-2-1234-5678 | When bot asks for phone |
| T6 | *(bot now answers the DID price question)* | Bot should return to address T1 |
| T7 | Is there a setup fee? | Follow-up on one-time fees |
| T8 | Do we need to verify anything to get a number? | KYC requirement |
| T9 | Which plan do we need to be on to use DID numbers? | Plan eligibility |

### Observation Checklist
- [ ] Bot asks for lead info after T1 before pricing answer
- [ ] Bot collects all 4 fields: Name, Company, Email, Phone (T2–T5)
- [ ] Bot gives a specific price OR correctly says "depends on region, contact sales / check pricing page"
- [ ] If a price is given, it's consistent with the knowledge base
- [ ] Bot mentions DID is an add-on (not base license included)
- [ ] Bot mentions KYC/verification requirement
- [ ] Bot correctly states plan eligibility for DID

---

### TC-C2: Multi-Agent Volume Pricing

**目标**: After collecting lead info, bot explains the per-agent license model, mentions volume considerations, and routes to sales for custom quotes.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Fatima Al-Rashid |
| Company | Dubai Commerce Group |
| Email | fatima@dubaicommerce.ae |
| Phone | +971-4-1234-5678 |
| Inquiry | Pricing for 50 agents |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** answering the pricing question
- Bot explains per-agent (per-license) billing model
- Bot mentions monthly vs. annual pricing difference
- Bot suggests custom/enterprise quote for 50 agents via sales
- Bot does NOT calculate and state a specific total (e.g., "$2,950/month") with false confidence

**Fail Criteria**:
- Bot answers the pricing question **before** collecting lead info
- Bot invents a total price for 50 agents without caveat
- Bot fails to mention volume discounts or annual pricing option

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | What is your pricing for 50 agents? | Volume pricing question — bot should ask for identity first |
| T2 | Fatima Al-Rashid | When bot asks for name |
| T3 | Dubai Commerce Group | When bot asks for company |
| T4 | fatima@dubaicommerce.ae | When bot asks for email |
| T5 | +971-4-1234-5678 | When bot asks for phone |
| T6 | *(bot now answers the pricing question)* | Bot returns to address T1 |
| T7 | Is there a discount for larger teams? | Volume discount probe |
| T8 | What if we pay annually instead of monthly? | Annual vs monthly |
| T9 | Can you give us a formal quote? | Escalation to sales |

### Observation Checklist
- [ ] Bot asks for lead info after T1 before pricing answer
- [ ] Bot collects all 4 fields: Name, Company, Email, Phone (T2–T5)
- [ ] Bot explains per-agent license model
- [ ] Bot mentions annual pricing option (annual saves vs monthly)
- [ ] Bot mentions volume discounts / enterprise pricing require sales contact
- [ ] Bot recommends OCC or CXHub for 50-agent scale
- [ ] Bot routes to sales for formal quote
- [ ] Bot does NOT fabricate a specific total price

---

### TC-C3: Incorrect Price Correction

**目标**: After collecting lead info, bot corrects a customer's false price assumption without agreeing with it.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Marco Rossi |
| Company | Roma Digital SRL |
| Email | marco@romadigital.it |
| Phone | +39-06-1234-5678 |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** the false pricing discussion
- Bot explicitly corrects the false assumption ("$5/minute" is not CINNOX's pricing model)
- Bot explains correct billing logic (per-agent license, not per-minute for agents)
- Bot does NOT validate the wrong price

**Fail Criteria**:
- Bot starts correcting the price **before** collecting lead info *(minor — focus is on correction accuracy)*
- Bot agrees with or does not contradict "$5 per minute"
- Bot gives a vague non-answer that leaves the wrong impression intact

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Hi, I'm interested in CINNOX. | Opening — bot should ask for identity |
| T2 | Marco Rossi | When bot asks for name |
| T3 | Roma Digital SRL | When bot asks for company |
| T4 | marco@romadigital.it | When bot asks for email |
| T5 | +39-06-1234-5678 | When bot asks for phone |
| T6 | I heard the price is $5 USD per minute for agents, is that right? | Introduce false pricing claim after lead collection |
| T7 | Really? A competitor told us that was the industry standard. | Pressure test |
| T8 | So what IS the correct pricing then? | Let bot explain correctly |

### Observation Checklist
- [ ] Bot collects all 4 lead fields (T2–T5) before pricing discussion
- [ ] Bot explicitly says $5/minute per agent is NOT correct on T6
- [ ] Bot maintains correction under pressure on T7
- [ ] Bot correctly explains the license-based model on T8
- [ ] Bot provides accurate tier pricing (DC / OCC / CXHub) or defers to pricing page

---

## TC-D: Data Collection

### TC-D1: Demo Request — Complete Data Collection

**目标**: Bot collects all 4 required fields (Name, Company, Email, Phone) when a prospect requests a demo.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Emma Laurent |
| Company | Lyon Digital Agency |
| Email | emma@lyondigital.com |
| Phone | +33-6-1234-5678 |

**Pass Criteria**:
- Bot collects all 4 fields: Name, Company, Email, Phone
- Bot confirms receipt of all info
- Bot confirms next step (demo will be arranged)

**Fail Criteria**:
- Bot skips any field
- Bot collects info but does not confirm or provide next step
- Bot asks for the same field twice

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | I want to arrange a demo of CINNOX. | Demo request trigger |
| T2 | Emma Laurent | When bot asks for name |
| T3 | Lyon Digital Agency | When bot asks for company |
| T4 | emma@lyondigital.com | When bot asks for email |
| T5 | +33-6-1234-5678 | When bot asks for phone |
| T6 | Yes, any weekday afternoon works for me. | When bot asks about availability/timing |

### Observation Checklist
- [ ] Bot requests all 4 fields in logical order
- [ ] Bot does NOT re-ask fields already provided
- [ ] Bot confirms demo request receipt after all 4 fields collected
- [ ] Bot provides estimated timeline or next step

---

### TC-D2: Data Collection — Phone Number Refused

**目标**: Bot handles phone refusal gracefully — explains why it's needed, accepts refusal, and routes to human without abandoning the customer.

**Session**: Continue from TC-D1 — same session (same persona: Emma Laurent)

**Scenario**: Restart session as Emma Laurent but this time refuse to provide phone number.

**Pass Criteria**:
- Bot explains why phone number is needed
- If still refused after explanation, bot routes to human agent (does not force)
- Bot does NOT abandon the conversation or end service
- Bot does NOT keep asking after second refusal

**Fail Criteria**:
- Bot accepts refusal silently without explanation
- Bot asks for phone 3+ times (harassment)
- Bot ends conversation or says it cannot proceed without phone
- Bot routes to human without informing Emma

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | I want to arrange a demo of CINNOX. | Re-trigger demo request |
| T2 | Emma Laurent, Lyon Digital Agency, emma@lyondigital.com | Provide 3 fields at once |
| T3 | I'd rather not give my phone number. | First refusal — when bot asks for phone |
| T4 | I really don't want to share it. Please proceed without it. | Second refusal — firm |
| T5 | Okay, please connect me with someone. | Accept handoff when offered |

### Observation Checklist
- [ ] Bot explains reason for needing phone number on T3
- [ ] Bot does NOT demand phone after T4 (accepts refusal)
- [ ] Bot offers alternative (email-only follow-up or human handoff) on T4
- [ ] Bot routes to human after second refusal
- [ ] Conversation continues — service not terminated

---

## TC-E: Existing Customer Routing

### TC-E1: Billing Issue — Correct Routing

**目标**: Bot identifies a billing dispute, collects all 5 required fields (including Email per flow), and routes to billing team.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | Tom Bradley |
| Company | Hartley Insurance UK |
| Email | tom@hartley.co.uk |
| Account | HART-UK-2023 |
| Issue | Believes he was overcharged last month |

**Pass Criteria**:
- Bot identifies this as a billing issue
- Bot collects: Name, Company, **Email**, Service Account ID
- Bot routes to billing / support team
- Bot does NOT try to explain or justify the charge

**Fail Criteria**:
- Bot starts explaining billing rates or invoice items
- Bot does not collect Account ID or Email
- Bot routes to wrong team (e.g., sales)
- Bot says it cannot help without trying to route

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | I think I was overcharged on last month's bill. | Billing dispute opener |
| T2 | Tom Bradley, Hartley Insurance UK | When bot asks for identity |
| T3 | tom@hartley.co.uk | When bot asks for email |
| T4 | Account number is HART-UK-2023 | When bot asks for account/service ID |
| T5 | Yes, please escalate this. | Confirm handoff |

### Observation Checklist
- [ ] Bot identifies billing issue on T1
- [ ] Bot collects all fields: Name, Company, **Email**, Account ID
- [ ] Bot does NOT explain billing rates or justify charges
- [ ] Bot routes to billing/support team
- [ ] Bot confirms handoff with estimated response time or next step

---

### TC-E2: Technical Issue — Voice Quality

**目标**: Bot identifies a technical issue, collects all required fields including Email, and routes to technical support.

**Session**: New session

**Persona**:
| Field | Value |
|-------|-------|
| Name | James Wong |
| Company | Pacific Bank HK |
| Email | james.wong@pacificbank.hk |
| Account ID | PBHK-2024 |
| Service Number | +852-1234-5678 |
| Issue | Bad voice quality during calls |

**Pass Criteria**:
- Bot identifies this as a technical support issue
- Bot collects: Name, Company, **Email**, Account ID, Service Number
- Bot routes to technical support team
- Bot does NOT go through a multi-step troubleshooting script using KB answers

**Fail Criteria**:
- Bot provides lengthy troubleshooting steps (check network, restart app, etc.) before routing
- Bot fails to collect Email
- Bot routes to sales team instead of support

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Voice quality is really bad during calls on CINNOX. | Technical complaint |
| T2 | Yes, I'm an existing customer. James Wong, Pacific Bank HK. | When bot asks for identity |
| T3 | james.wong@pacificbank.hk | When bot asks for email |
| T4 | Account ID is PBHK-2024 | When bot requests account details |
| T5 | +852-1234-5678 is our service number | Additional account info |
| T6 | Yes, please get a technician to contact me. | Confirm handoff |

### Observation Checklist
- [ ] Bot acknowledges technical issue (voice quality) on T1
- [ ] Bot requests account info (not generic new-customer contact info)
- [ ] Bot collects: Name, Company, **Email**, Account ID, Service Number
- [ ] Bot does NOT provide more than 1–2 quick self-help steps before routing
- [ ] Bot routes to technical support
- [ ] Bot confirms a technician will follow up

---

## TC-F: Human Handoff

### TC-F1: Knowledge Boundary — Security Architecture

**目标**: Bot answers known security information, acknowledges limits, and routes to a technical specialist rather than fabricating architecture details.

**Session**: New session

**Persona**: Security officer at a financial institution

**Pass Criteria**:
- Bot shares known security info (data encryption, 2FA, SOC2/compliance if in KB, Audit Logs)
- Bot explicitly states it cannot provide full database encryption architecture details
- Bot offers to connect to a technical specialist
- Bot does NOT fabricate key management or at-rest encryption specifications

**Fail Criteria**:
- Bot describes specific encryption algorithms (AES-256, RSA-2048, etc.) not in the knowledge base
- Bot describes key management systems that are not in the knowledge base
- Bot does not offer human escalation for the out-of-scope questions

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Please explain your database encryption architecture in detail, including key management and at-rest encryption standards. | Highly technical — likely out of KB scope |
| T2 | Are you SOC2 compliant? What about GDPR? | Known compliance question |
| T3 | What encryption is used for data in transit? | May be in KB |
| T4 | Can we speak to a technical security specialist? | Request escalation |

### Observation Checklist
- [ ] Bot shares known security info on T2/T3 (certifications, TLS in transit, 2FA)
- [ ] Bot does NOT fabricate database encryption architecture on T1
- [ ] Bot acknowledges the limits of its knowledge for T1
- [ ] Bot proactively offers or accepts T4 escalation to technical team
- [ ] No hallucinated technical specifications

---

### TC-F2: Immediate Human Request

**目标**: Bot immediately routes to human without asking any qualifying questions.

> **Flow Note (v1.1)**: The official flow (flow.md) does not contain an explicit branch for direct human requests. This TC tests a critical edge case. Expected behavior — immediate routing without qualification — should be considered for addition to the official flow document.

**Session**: New session

**Persona**: Any — identity intentionally withheld to test bot behavior

**Pass Criteria**:
- Bot immediately acknowledges the request
- Bot initiates handoff within 1–2 exchanges at most
- Bot does NOT ask qualifying questions before routing

**Fail Criteria** (**Critical**):
- Bot asks ANY question before routing (e.g., "May I ask what this is regarding?", "What is your name?")
- Bot says "Let me first understand your issue" before routing
- Bot fails to route to human

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | I want to talk to a human representative immediately. | Direct human request — bot should route NOW |
| T2 | Please don't ask me any questions, just connect me. | If bot asks anything — reinforce |

### Observation Checklist
- [ ] Bot does NOT ask any qualifying question after T1
- [ ] Bot acknowledges the request and confirms handoff in the same response
- [ ] **CRITICAL**: No qualification questions before routing

---

## TC-G: Context Continuity

### TC-G1: Multi-Turn Context — DID Pricing Follow-Up

**目标**: Bot correctly interprets "What about Germany?" as a follow-up to a UK DID price question, without losing context or re-explaining the product.

**Session**: New session

**Persona**: Generic prospect comparing DID number pricing across regions

**Pass Criteria**:
- Bot correctly understands T2 ("What about Germany?") as a Germany DID price question
- Bot provides Germany DID pricing (or states it needs to check / refers to pricing page)
- Bot does NOT re-explain what a DID number is on T2
- Bot does NOT ask for clarification that treats T2 as an unrelated question

**Fail Criteria**:
- Bot answers T2 with product explanation instead of Germany pricing
- Bot asks "What do you mean by Germany?" or similar loss-of-context response
- Bot provides pricing for UK instead of Germany on T2

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | How much is a UK local number? | Establish context: DID pricing |
| T2 | What about Germany? | Short follow-up — bot MUST infer "Germany DID number price" |
| T3 | And for Hong Kong? | Second follow-up to reinforce context test |

### Observation Checklist
- [ ] Bot provides UK DID pricing on T1
- [ ] Bot correctly interprets T2 as Germany DID pricing (not product question)
- [ ] Bot answers T3 as HK DID pricing
- [ ] Bot does NOT re-explain DID numbers or ask clarifying product questions on T2 or T3
- [ ] Prices given are consistent with knowledge base

---

## TC-H: Error Tolerance

### TC-H1: Spelling Errors — WhatsApp

**目标**: Bot collects lead info first, then correctly understands the original typo message and responds accurately.

**Session**: New session

> **v1.1 Note**: Per flow, bot must collect lead info before answering product questions. The typo ("whtsapp intergration") is the customer's first message; the bot should ask for lead info, then revisit and correctly interpret the original question. This also tests that the bot **remembers and correctly interprets** the typo message after lead collection.

**Persona**:
| Field | Value |
|-------|-------|
| Name | Ryan Park |
| Company | Seoul Media Group |
| Email | ryan@seoulmediad.com |
| Phone | +82-2-5678-1234 |

**Pass Criteria**:
- Bot asks for lead info after receiving the typo message (does not answer immediately)
- After lead collection, bot **returns to answer the original typo question** — correctly interpreting "whtsapp intergration" as "WhatsApp integration"
- Bot provides accurate WhatsApp integration information
- Bot does NOT return an error, ask for clarification about the spelling, or say it doesn't understand

**Fail Criteria**:
- Bot says it doesn't understand the typo question
- Bot asks user to rephrase
- Bot forgets the original question after lead collection and doesn't address it
- Bot gives wrong WhatsApp information

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | Do you have whtsapp intergration? | Intentional typos: "whtsapp" + "intergration" — bot should ask for lead info first |
| T2 | Ryan Park | When bot asks for name |
| T3 | Seoul Media Group | When bot asks for company |
| T4 | ryan@seoulmediad.com | When bot asks for email |
| T5 | +82-2-5678-1234 | When bot asks for phone |
| T6 | *(bot returns to answer the WhatsApp question)* | Bot must correctly interpret the original typo |
| T7 | Does it support WhatsApp campaigns too? | Follow-up with correct spelling to confirm context |

### Observation Checklist
- [ ] Bot asks for lead info after T1 (does not answer immediately)
- [ ] Bot collects all 4 fields (T2–T5)
- [ ] Bot returns to answer the original typo question at T6 (without asking for clarification)
- [ ] Bot correctly interprets "whtsapp intergration" as WhatsApp integration
- [ ] Bot provides accurate WhatsApp answer
- [ ] Bot handles T7 follow-up correctly (campaign capabilities)
- [ ] No error messages or confusion indicators at any point

---

### TC-H2: Vague Request — Needs Clarification

**目标**: Bot collects lead info first, then asks clarifying questions (rather than immediately pitching products), and ultimately guides toward an appropriate solution.

**Session**: New session

> **v1.1 Note**: Per flow, bot collects lead info for new customers first, then handles their inquiry. The clarifying questions in this TC should come **after** lead collection — this tests that the bot does not immediately pitch a product when the need is unclear, even after already knowing who the customer is.

**Persona**:
| Field | Value |
|-------|-------|
| Name | Sarah Mitchell |
| Company | Austin Digital Agency |
| Email | sarah@austindigital.com |
| Phone | +1-512-555-0123 |

**Pass Criteria**:
- Bot collects all 4 lead fields **before** addressing the vague inquiry
- After lead collection, bot asks at least 1–2 clarifying questions to understand the need
- Bot does NOT immediately quote prices or package names after lead collection
- Bot eventually guides toward an appropriate solution after clarification

**Fail Criteria**:
- Bot skips lead collection
- Bot immediately says "Our OCC plan is $59/month" after lead collection without understanding the need
- Bot provides a generic product brochure response without any clarifying questions
- Bot asks more than 3–4 clarifying questions (over-qualifying)

### Dialogue Script

| # | Tester Input | Notes |
|---|-------------|-------|
| T1 | I want something for customer service. | Intentionally vague — bot should ask for identity first |
| T2 | Sarah Mitchell | When bot asks for name |
| T3 | Austin Digital Agency | When bot asks for company |
| T4 | sarah@austindigital.com | When bot asks for email |
| T5 | +1-512-555-0123 | When bot asks for phone |
| T6 | *(bot asks clarifying question about the need)* | Bot should NOT immediately pitch a product |
| T7 | We have about 10 people on our team. | Partial context — bot should ask more |
| T8 | Mostly phone calls, but we also use WhatsApp with some customers. | More context — bot should now guide to a solution |
| T9 | What would you recommend? | Request for recommendation |

### Observation Checklist
- [ ] Bot collects all 4 lead fields (T2–T5) before addressing the inquiry
- [ ] Bot asks clarifying question(s) at T6 — NOT a product pitch
- [ ] Bot builds on T7 context and asks a relevant follow-up
- [ ] Bot synthesizes T8 context (phone + WhatsApp → OCC or CXHub recommendation)
- [ ] Bot makes a concrete recommendation on T9 with reasoning
- [ ] Bot does NOT quote prices before T9

---

## Summary Reference

| TC | Category | Title | Session | v1.1 Change |
|----|----------|-------|---------|-------------|
| TC-A1 | Customer Type | New Customer Identification | New | — |
| TC-A2 | Customer Type | Existing Customer Identification | New | Added Email field |
| TC-A3 | Customer Type | Partner Identification | New | — |
| TC-A4 *(new)* | Customer Type | Existing Customer Product Inquiry | New | New TC |
| TC-B1 | Product / RAG | WhatsApp Integration | New | Lead collection first |
| TC-B2 | Product / RAG | High Volume Banking | New | Lead collection first |
| TC-B3 | Product / RAG | Non-Existent Feature (Hallucination) | New | Lead collection first |
| TC-C1 | Pricing | DID Number Price | New | Lead collection first |
| TC-C2 | Pricing | 50-Agent Volume Quote | New | Lead collection first |
| TC-C3 | Pricing | False Price Correction | New | Lead collection first |
| TC-D1 | Data Collection | Demo Request — All Fields | New | — |
| TC-D2 | Data Collection | Phone Number Refused | Continue from D1 | — |
| TC-E1 | Existing Customer | Billing Issue Routing | New | — |
| TC-E2 | Existing Customer | Technical Issue Routing | New | Added Email field |
| TC-F1 | Human Handoff | Knowledge Boundary | New | — |
| TC-F2 | Human Handoff | Immediate Human Request | New | Added flow gap note |
| TC-G1 | Context | Multi-Turn DID Pricing | New | — |
| TC-H1 | Error Tolerance | Spelling Errors | New | Lead collection first |
| TC-H2 | Error Tolerance | Vague Request | New | Lead collection first |
