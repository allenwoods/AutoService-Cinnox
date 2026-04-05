# CINNOX UAT — Persona Quick Reference

Use this as a quick-lookup card during testing. Full dialogue scripts are in `Test_Guide.md`.

---

## Persona Cards

### P1 — Emma Xu (New Customer)
> Used in: TC-A1

| Field | Value |
|-------|-------|
| **Name** | Emma Xu |
| **Company** | Bright Retail Ltd |
| **Email** | emma.xu@brightretail.com |
| **Phone** | +852-9123-4567 |
| **Industry** | Retail |
| **Need** | Evaluating contact center solution |
| **Account** | None — new prospect |

**Opening line**: "Hi, we are looking for a contact center solution for our team."

---

### P2 — James Wong (Existing Customer — Support)
> Used in: TC-A2, TC-E2

| Field | Value |
|-------|-------|
| **Name** | James Wong |
| **Company** | Pacific Bank HK |
| **Email** | james.wong@pacificbankhk.com |
| **Phone** | +852-9876-5432 |
| **Account ID** | PBHK-2024 |
| **Agent Name** | Alice |
| **Service Number** | +852-1234-5678 |
| **Issue (A2)** | Agent cannot receive calls on CINNOX |
| **Issue (E2)** | Poor voice quality during calls |

**Opening line (A2)**: "Our agent cannot receive calls on the CINNOX platform."
**Opening line (E2)**: "Voice quality is really bad during calls on CINNOX."

---

### P3 — David Park (Partner / SI)
> Used in: TC-A3

| Field | Value |
|-------|-------|
| **Name** | David Park |
| **Company** | Nexus SI Singapore |
| **Email** | david.park@nexussi.com |
| **Phone** | +65-8123-4567 |
| **Role** | Business Development, System Integrator |
| **Need** | Explore CINNOX reseller / partnership |
| **Account** | None — potential partner |

**Opening line**: "We are a system integrator and want to explore a partnership with CINNOX."

---

### P4 — Generic New Prospect (No Identity)
> Used in: TC-B1, TC-B3, TC-C3, TC-H1, TC-H2

No specific persona. Tester plays an unnamed prospect.
- No name/company needed unless bot asks
- Can respond: "I'd prefer to stay anonymous for now" if bot asks

---

### P5 — Bank Procurement Lead (Banking Inquiry)
> Used in: TC-B2

| Field | Value |
|-------|-------|
| **Role** | IT Procurement Manager |
| **Industry** | Banking / Financial Services |
| **Company** | [Generic bank — no specific name needed] |
| **Need** | High-volume inbound call handling (~10,000/day) |
| **Account** | None — evaluating vendors |

**Opening line**: "We are a bank. Can you handle high volume inbound calls? About 10,000 per day."

---

### P6 — Kevin Han (Pricing Inquiry)
> Used in: TC-C1, TC-C2

| Field | Value |
|-------|-------|
| **Name** | Kevin Han |
| **Company** | Seoul Commerce Inc. |
| **Email** | kevin.han@seoulcommerce.com |
| **Phone** | +82-10-1234-5678 |
| **Need** | US DID number price + 50-agent volume quote |
| **Account** | None — new prospect |

**Opening line (C1)**: "How much is a US DID number per month?"
**Opening line (C2)**: "What is your pricing for 50 agents?"

---

### P7 — Emma Laurent (Demo Request)
> Used in: TC-D1, TC-D2

| Field | Value |
|-------|-------|
| **Name** | Emma Laurent |
| **Company** | Lyon Digital Agency |
| **Email** | emma@lyondigital.com |
| **Phone** | +33-6-1234-5678 |
| **Need** | Book a product demo |
| **Special (D2)** | Refuses to provide phone number |

**Opening line**: "I want to arrange a demo of CINNOX."
**Phone refusal script (D2, T3)**: "I'd rather not give my phone number."
**Second refusal (D2, T4)**: "I really don't want to share it. Please proceed without it."

---

### P8 — Tom Bradley (Billing Dispute)
> Used in: TC-E1

| Field | Value |
|-------|-------|
| **Name** | Tom Bradley |
| **Company** | Hartley Insurance UK |
| **Email** | tom@hartley.co.uk |
| **Phone** | +44-7911-123456 |
| **Account ID** | HART-UK-2023 |
| **Issue** | Believes he was overcharged last month |

**Opening line**: "I think I was overcharged on last month's bill."

---

### P9 — Security Officer (Technical Deep Dive)
> Used in: TC-F1

| Field | Value |
|-------|-------|
| **Role** | Chief Information Security Officer (CISO) |
| **Industry** | Financial Institution |
| **Company** | [Generic — no name needed] |
| **Need** | Detailed encryption / security architecture |
| **Account** | None — evaluating vendors |

**Opening line**: "Please explain your database encryption architecture in detail, including key management and at-rest encryption standards."

---

### P10 — Impatient Customer (Immediate Handoff)
> Used in: TC-F2

| Field | Value |
|-------|-------|
| **Role** | Any — withheld intentionally |
| **Identity** | Not provided |
| **Special** | Refuses any qualification questions |

**Opening line**: "I want to talk to a human representative immediately."

---

### P11 — DID Comparison Shopper
> Used in: TC-G1

| Field | Value |
|-------|-------|
| **Role** | Operations Manager comparing virtual number pricing |
| **Need** | DID number prices for UK, Germany, Hong Kong |
| **Account** | None — new prospect |

**Opening sequence**:
- T1: "How much is a UK local number?"
- T2: "What about Germany?" *(short follow-up — context test)*
- T3: "And for Hong Kong?"

---

### P12 — Typo-Prone User
> Used in: TC-H1

| Field | Value |
|-------|-------|
| **Role** | Generic prospect |
| **Special** | Types with common spelling mistakes |

**Opening line**: "Do you have whtsapp intergration?" *(intentional typos)*

---

## Summary Table

| Persona | Name | Used In | Key Differentiator |
|---------|------|---------|-------------------|
| P1 | Emma Xu | TC-A1 | New customer, all 4 fields provided |
| P2 | James Wong | TC-A2, TC-E2 | Existing customer w/ account ID + agent name |
| P3 | David Park | TC-A3 | SI/partner, not a customer |
| P4 | Generic (anon) | TC-B1, B3, C3, H1, H2 | No identity — feature/pricing questions |
| P5 | Bank Lead | TC-B2 | Banking, high volume, ACD/IVR test |
| P6 | Kevin Han | TC-C1, C2 | Pricing inquiry — DID + volume |
| P7 | Emma Laurent | TC-D1, D2 | Demo request; refuses phone on D2 |
| P8 | Tom Bradley | TC-E1 | Billing dispute, existing customer |
| P9 | CISO | TC-F1 | Security architecture deep dive |
| P10 | Impatient | TC-F2 | Demands immediate human, no questions |
| P11 | DID Shopper | TC-G1 | Context continuity — 3-country comparison |
| P12 | Typo User | TC-H1 | Spelling errors in input |
