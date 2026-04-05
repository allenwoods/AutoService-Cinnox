# CINNOX UAT — Test Results Record

**Tester**: _______________
**Test Date**: _______________
**Environment**: CINNOX Demo (autoservice simulation)
**Product Config**: CINNOX
**Operator/Strategy**: _______________

> **v1.1**: Aligned with flow.md. Total TCs: 19 (added TC-A4). TC-A2/E2 now check Email. TC-B/C/H now check lead collection before RAG.

---

## Overall Summary

| Metric | Value |
|--------|-------|
| Total TCs | 19 |
| Passed | ___ |
| Failed | ___ |
| Blocked / Not Run | ___ |
| Pass Rate | ___% |

**Critical Failures** (TC-B3, TC-F2 — showstoppers):
- [ ] TC-B3: No hallucination ✓/✗
- [ ] TC-F2: Immediate handoff without questions ✓/✗

---

## TC-A: Customer Type Identification

### TC-A1 — New Customer Identification

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot greets and asks for identity on T1 | | |
| Bot does NOT re-ask Name or Company after T2 | | |
| Bot collects Email and Phone (T3–T4) without duplication | | |
| Bot summarizes collected info before closing | | |
| Bot confirms next step (demo / handoff to sales) | | |

**Failure Detail** (if FAIL):

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-A2 — Existing Customer Identification *(v1.1: Email added)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies existing customer support case | | |
| Bot requests Account ID + service details | | |
| Bot collects Account ID | | |
| Bot collects Company | | |
| Bot collects Agent name (issue-specific) | | |
| Bot collects Service number | | |
| Bot collects **Email** *(new in v1.1 per flow)* | | |
| Bot initiates handoff to human agent | | |
| Bot does NOT attempt to resolve with KB answers | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-A3 — Partner Identification

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot recognizes SI/partner inquiry | | |
| Bot collects Name, Company, Email, Phone | | |
| Bot does NOT lead with product pricing | | |
| Bot routes to partnership/BD team | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-A4 — Existing Customer Product Inquiry *(New in v1.1)*

**Result**: PASS / FAIL / BLOCKED

> **Flow reference**: 现有客户 → 产品咨询 → RAG回复 → 无法解答 → 转人工
> Bot should NOT run the new-customer lead form for existing customers.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies this as existing customer inquiry (not new prospect) | | |
| Bot does NOT collect Name/Email/Phone as a new lead form | | |
| Bot queries KB for CRM/API integration information | | |
| Bot provides answer with source citation (if KB has info) | | |
| If KB cannot answer → bot transfers to human specialist | | |
| Bot does NOT fabricate API specs or integration capabilities | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-B: Product Inquiry / RAG

> **v1.1**: All TC-B tests now require bot to collect lead info (Name/Company/Email/Phone) **before** answering product questions. Each checklist includes a lead collection verification row.

### TC-B1 — WhatsApp Integration *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT answer WhatsApp question immediately)** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot returns to answer the WhatsApp question after lead collection | | |
| Bot confirms WhatsApp Business support | | |
| Bot mentions OCC/CXHub availability (not DC) | | |
| Bot correctly describes campaign capability | | |
| Bot mentions WhatsApp number purchase (or defers to sales) | | |
| No fabricated features | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-B2 — High Volume Banking *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately pitch product)** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot returns to address the high-volume banking question | | |
| Bot mentions ACD routing modes (≥2) | | |
| Bot confirms IVR menu support | | |
| Bot recommends OCC or CXHub | | |
| Bot avoids fabricated throughput guarantees | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-B3 — Non-Existent Feature ⚠️ CRITICAL *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

> **Note**: A FAIL on hallucination is a showstopper. Lead collection before Q&A is secondary — focus is on no fabrication.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot clearly denies hologram video calling after lead collection | | |
| Bot maintains denial under pressure | | |
| Bot describes real video features | | |
| **CRITICAL**: No fabrication at any point | | |

**Failure Detail**:

```
[CRITICAL: Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-C: Pricing Accuracy

> **v1.1**: All TC-C tests now require lead collection before pricing Q&A.

### TC-C1 — DID Number Price *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot gives specific price OR correctly defers to pricing page | | |
| Price given is consistent with knowledge base | | |
| Bot mentions DID is an add-on | | |
| Bot mentions KYC/verification requirement | | |
| Bot correctly states plan eligibility for DID | | |

**Price given by bot**: _______________

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-C2 — Volume Pricing (50 Agents) *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 before pricing answer** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot explains per-agent license model | | |
| Bot mentions annual vs. monthly pricing | | |
| Bot mentions volume discounts via sales | | |
| Bot recommends OCC or CXHub for 50 agents | | |
| Bot routes to sales for formal quote | | |
| Bot does NOT fabricate a specific total price | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-C3 — Incorrect Price Correction *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot collects all 4 lead fields before pricing discussion** | | |
| Bot explicitly says $5/minute per agent is NOT correct | | |
| Bot maintains correction under pressure | | |
| Bot correctly explains license-based model | | |
| Bot provides accurate tier pricing or defers to pricing page | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-D: Data Collection

### TC-D1 — Demo Request (All Fields)

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot requests all 4 fields in logical order | | |
| Bot does NOT re-ask fields already provided | | |
| Bot confirms demo request receipt after all 4 fields | | |
| Bot provides next step | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-D2 — Phone Number Refused

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot explains reason for phone on T3 | | |
| Bot does NOT demand phone after T4 | | |
| Bot offers alternative or human handoff on T4 | | |
| Bot routes to human after second refusal | | |
| Conversation continues (not terminated) | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-E: Existing Customer Routing

### TC-E1 — Billing Issue

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot identifies billing issue on T1 | | |
| Bot collects Name | | |
| Bot collects Company | | |
| Bot collects **Email** | | |
| Bot collects Account ID | | |
| Bot does NOT explain billing rates | | |
| Bot routes to billing/support team | | |
| Bot confirms handoff with next step | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-E2 — Technical Issue (Voice Quality) *(v1.1: Email added)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot acknowledges technical issue on T1 | | |
| Bot requests account info (not new-customer lead form) | | |
| Bot collects Name | | |
| Bot collects Company | | |
| Bot collects **Email** *(new in v1.1 per flow)* | | |
| Bot collects Account ID | | |
| Bot collects Service Number | | |
| Bot does NOT give >2 troubleshooting steps before routing | | |
| Bot routes to technical support | | |
| Bot confirms technician follow-up | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-F: Human Handoff

### TC-F1 — Knowledge Boundary

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot shares known security info on T2/T3 | | |
| Bot does NOT fabricate DB encryption architecture on T1 | | |
| Bot acknowledges knowledge limits for T1 | | |
| Bot offers/accepts escalation to technical team | | |
| No hallucinated technical specs | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-F2 — Immediate Human Request ⚠️ CRITICAL

**Result**: PASS / FAIL / BLOCKED

> **Note**: Any qualifying question = FAIL.
> **Flow Gap Note**: The official flow.md does not have a direct human request branch. Bot's correct behavior here (immediate routing) should be added to the flow.

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot does NOT ask qualifying question after T1 | | |
| Bot acknowledges and confirms handoff in same response | | |
| **CRITICAL**: No qualification questions before routing | | |

**Failure Detail**:

```
[CRITICAL: Paste exact bot response — including any questions asked]
```

**Notes**:

---

## TC-G: Context Continuity

### TC-G1 — Multi-Turn DID Pricing

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| Bot provides UK DID pricing on T1 | | |
| Bot correctly interprets T2 as Germany DID (not re-explains product) | | |
| Bot answers T3 as HK DID pricing | | |
| Bot does NOT re-explain DID on T2/T3 | | |
| Prices are consistent with knowledge base | | |

**UK price given**: _______________
**Germany price given**: _______________
**HK price given**: _______________

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## TC-H: Error Tolerance

### TC-H1 — Spelling Errors *(v1.1: lead collection first)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot asks for lead info after T1 (does NOT immediately answer typo question)** | | |
| **Bot collects all 4 fields: Name, Company, Email, Phone** | | |
| Bot returns to answer original typo question at T6 (no clarification request about spelling) | | |
| Bot correctly interprets "whtsapp intergration" as WhatsApp integration | | |
| Bot provides accurate WhatsApp answer | | |
| Bot handles T7 follow-up correctly (campaign capabilities) | | |
| No error messages or confusion at any point | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

### TC-H2 — Vague Request *(v1.1: lead collection first, then clarifying questions)*

**Result**: PASS / FAIL / BLOCKED

| Checklist Item | ✓/✗ | Notes |
|---------------|-----|-------|
| **Bot collects all 4 lead fields (T2–T5) before handling the vague inquiry** | | |
| Bot asks clarifying question(s) at T6 — NOT a product pitch | | |
| Bot builds on T7 context and asks relevant follow-up | | |
| Bot synthesizes T8 context (phone + WhatsApp → OCC/CXHub) | | |
| Bot makes concrete recommendation on T9 with reasoning | | |
| Bot does NOT quote prices before T9 | | |

**Failure Detail**:

```
[Paste exact bot response that triggered failure]
```

**Notes**:

---

## Final Results Table

| TC | Category | Title | Result | Notes |
|----|----------|-------|--------|-------|
| TC-A1 | Customer Type | New Customer Identification | PASS / FAIL | |
| TC-A2 | Customer Type | Existing Customer Identification | PASS / FAIL | |
| TC-A3 | Customer Type | Partner Identification | PASS / FAIL | |
| TC-A4 *(new)* | Customer Type | Existing Customer Product Inquiry | PASS / FAIL | |
| TC-B1 | Product / RAG | WhatsApp Integration | PASS / FAIL | |
| TC-B2 | Product / RAG | High Volume Banking | PASS / FAIL | |
| TC-B3 ⚠️ | Product / RAG | Non-Existent Feature | PASS / FAIL | |
| TC-C1 | Pricing | DID Number Price | PASS / FAIL | |
| TC-C2 | Pricing | 50-Agent Volume Quote | PASS / FAIL | |
| TC-C3 | Pricing | False Price Correction | PASS / FAIL | |
| TC-D1 | Data Collection | Demo Request — All Fields | PASS / FAIL | |
| TC-D2 | Data Collection | Phone Number Refused | PASS / FAIL | |
| TC-E1 | Existing Customer | Billing Issue Routing | PASS / FAIL | |
| TC-E2 | Existing Customer | Technical Issue Routing | PASS / FAIL | |
| TC-F1 | Human Handoff | Knowledge Boundary | PASS / FAIL | |
| TC-F2 ⚠️ | Human Handoff | Immediate Human Request | PASS / FAIL | |
| TC-G1 | Context | Multi-Turn DID Pricing | PASS / FAIL | |
| TC-H1 | Error Tolerance | Spelling Errors | PASS / FAIL | |
| TC-H2 | Error Tolerance | Vague Request | PASS / FAIL | |

---

## Issues Log

| # | TC | Severity | Description | Bot Response (verbatim) |
|---|----|----------|-------------|------------------------|
| 1 | | | | |

**Severity Guide**:
- **Critical**: Hallucination, wrong routing on immediate handoff request (TC-B3, TC-F2)
- **High**: Wrong pricing, failed to collect required fields, wrong customer type identification, answered product question before collecting lead info
- **Medium**: Suboptimal phrasing, minor routing delay, missing one checklist item (e.g., forgot email)
- **Low**: Style/tone issue, cosmetic, KB retrieval gap with no hallucination

---

## Flow Compliance Summary *(v1.1)*

| Flow Branch | Tested By | Status |
|-------------|-----------|--------|
| 新客户 → 收集信息 → 产品咨询/RAG | TC-B1/B2/B3, TC-C1/C2/C3, TC-H1/H2 | |
| 新客户 → 收集信息 → 其他问题 → 转人工 | TC-D2 | |
| 现有客户 → 产品咨询 → RAG → 转人工 | TC-A4 | |
| 现有客户 → 套餐计费 → 收集信息 → 转人工 | TC-E1 | |
| 现有客户 → 投诉 → 收集信息 → 转人工 | TC-A2, TC-E2 | |
| 其他（合作伙伴）→ 收集信息 → 转人工 | TC-A3 | |
| 直接要求转人工（flow gap）| TC-F2 | |

---

## Sign-Off

| | Name | Signature | Date |
|--|------|-----------|------|
| **Tester** | | | |
| **Reviewer** | | | |
