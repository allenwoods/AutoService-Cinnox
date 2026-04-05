# Mock Data Templates (English)

Templates for generating realistic English mock data for customer service (production environment).

**Important**: For production use, products MUST include `api_interfaces` and `operator_permissions` fields.

---

## Product Templates by Category

### Electronics

```json
{
  "name": "Smart Watch Pro X",
  "description": "High-end smartwatch with heart rate monitoring, GPS tracking, and NFC payments",
  "features": ["Heart rate monitoring", "GPS tracking", "NFC payments", "Water resistant to 50m", "7-day battery life"],
  "common_issues": [
    "Cannot connect to phone via Bluetooth",
    "Heart rate readings are inaccurate",
    "Slow charging or won't charge",
    "Watch band broke",
    "Screen scratches"
  ],
  "solutions": {
    "Bluetooth connection issues": "Restart both the watch and phone, remove pairing and reconnect",
    "Inaccurate heart rate": "Make sure the watch is snug against your skin, clean the sensor",
    "Charging issues": "Check the charging dock contact points, use the original charger",
    "Broken watch band": "Free replacement under warranty",
    "Screen scratches": "Paid repair service available"
  },
  "faq": [
    {"q": "Can I swim with it?", "a": "Yes, it's fine for swimming, but not for diving or hot tubs"},
    {"q": "Can I make phone calls?", "a": "It supports Bluetooth calls when paired with your phone"}
  ],
  "escalation_criteria": "Customer requests a return, product quality complaint, safety concern",
  "sla": {"response_time": "Answer within 30 seconds", "resolution_time": "80% first-call resolution rate"},

  "api_interfaces": {
    "warranty_check": {
      "description": "Check product warranty status",
      "endpoint": "/api/warranty/{serial_number}",
      "method": "GET",
      "params": ["serial_number"],
      "response_fields": ["is_valid", "purchase_date", "expiry_date", "coverage_type"],
      "mock_enabled": true
    },
    "repair_history": {
      "description": "Look up repair history",
      "endpoint": "/api/repair/{serial_number}/history",
      "method": "GET",
      "params": ["serial_number"],
      "response_fields": ["repairs", "last_repair_date"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["Free watch band replacement", "Software reset guidance", "Refund under $50"],
    "requires_supervisor": ["Refund $50 or above", "Free device replacement", "Extended warranty"],
    "requires_process": ["Product quality complaint", "Bulk return"],
    "forbidden": ["Promise unreleased features", "Disclose supplier information"]
  }
}
```

### Software / SaaS

```json
{
  "name": "Cloud Storage Plus",
  "description": "Enterprise-grade cloud storage solution with file sync, sharing, and backup",
  "features": ["1TB storage", "Real-time sync", "Team collaboration", "Version history", "End-to-end encryption"],
  "common_issues": [
    "Sync failed or stuck",
    "Files missing or corrupted",
    "Cannot log into account",
    "Storage space running low notification",
    "Shared link expired"
  ],
  "solutions": {
    "Sync issues": "Check your internet connection, clear the cache, and log back in",
    "Missing files": "Check the recycle bin and version history - files deleted within 30 days can be recovered",
    "Login issues": "Reset your password and check if your account has been locked",
    "Low storage": "Clean up large files or upgrade your plan",
    "Expired link": "Check sharing settings and generate a new link"
  },
  "faq": [
    {"q": "Is my data secure?", "a": "We use AES-256 encryption and are ISO 27001 certified"},
    {"q": "Can I recover deleted files?", "a": "Yes, anything deleted within the last 30 days can be restored from the recycle bin"}
  ],
  "escalation_criteria": "Data breach concerns, enterprise customer bulk issues, compromised account",
  "sla": {"response_time": "Answer within 2 minutes", "resolution_time": "Technical issues resolved within 24 hours"},

  "api_interfaces": {
    "subscription_check": {
      "description": "Check user subscription status",
      "endpoint": "/api/user/{user_id}/subscription",
      "method": "GET",
      "params": ["user_id"],
      "response_fields": ["plan", "storage_limit", "used_storage", "expiry_date", "auto_renew"],
      "mock_enabled": true
    },
    "storage_usage": {
      "description": "Check storage space usage",
      "endpoint": "/api/user/{user_id}/storage",
      "method": "GET",
      "params": ["user_id"],
      "response_fields": ["used_bytes", "total_bytes", "file_count", "largest_files"],
      "mock_enabled": true
    },
    "billing_history": {
      "description": "Look up billing history",
      "endpoint": "/api/user/{user_id}/billing",
      "method": "GET",
      "params": ["user_id", "months"],
      "response_fields": ["transactions", "total_charged"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["Password reset", "Restore deleted files within 30 days", "Temporary storage boost under 1GB", "Refund under $10"],
    "requires_supervisor": ["Refund $10 or above", "Permanent storage increase", "Account unlock (suspicious login)"],
    "requires_process": ["Data export request", "Account deletion", "Data breach investigation"],
    "forbidden": ["Access user file contents", "Bypass encryption", "Disclose other users' information"]
  }
}
```

### E-commerce

```json
{
  "name": "Online Shopping Platform Orders",
  "description": "General e-commerce platform selling electronics, clothing, home goods, and more",
  "features": ["Next-day delivery", "7-day no-questions-asked returns", "Authenticity guarantee", "Price protection"],
  "common_issues": [
    "Order status inquiry",
    "Shipping delayed or package lost",
    "Received wrong or damaged item",
    "Refund not received",
    "Promo code not working"
  ],
  "solutions": {
    "Order inquiry": "Provide the order number for real-time status lookup",
    "Shipping issues": "Contact the carrier; reship if necessary",
    "Item issues": "Upload photos and arrange a return or exchange",
    "Refund delay": "Verify refund status - typically processed within 3-5 business days",
    "Promo code issues": "Check the terms and conditions and expiration date"
  },
  "faq": [
    {"q": "Who pays for return shipping?", "a": "We cover it for quality issues; for no-reason returns, the customer covers shipping"},
    {"q": "How do I get an invoice?", "a": "You can request a digital invoice from the order details page"}
  ],
  "escalation_criteria": "High-value order issues, repeated returns, attitude complaints",
  "sla": {"response_time": "Answer within 20 seconds", "resolution_time": "Returns and exchanges processed within 48 hours"}
}
```

### Finance / Banking

```json
{
  "name": "Credit Card Services",
  "description": "Bank credit card products including spending, payments, and rewards redemption",
  "features": ["No annual fee", "Cashback on purchases", "Rewards points", "Installment plans", "No foreign transaction fees"],
  "common_issues": [
    "Statement amount questions",
    "Payment not posted",
    "Lost card / freeze card",
    "Credit limit adjustment request",
    "Rewards points inquiry / redemption"
  ],
  "solutions": {
    "Statement questions": "Review transaction details; a statement review can be requested",
    "Payment issues": "Confirm payment method and processing time (cross-bank transfers take 1-2 days)",
    "Lost card / freeze": "Processed immediately after identity verification",
    "Credit limit adjustment": "Submit a request - approval takes about 3 business days",
    "Rewards points": "Check and redeem points in real time through the app"
  },
  "faq": [
    {"q": "Does making minimum payments affect my credit?", "a": "No impact on your credit score, but interest will accrue"},
    {"q": "Are there fees for international purchases?", "a": "No - this card has no foreign transaction fees"}
  ],
  "escalation_criteria": "Fraudulent transaction, large dispute, service attitude complaint, regulatory complaint",
  "sla": {"response_time": "Answer within 15 seconds", "resolution_time": "Emergency card freeze processed immediately"}
}
```

### Telecom

```json
{
  "name": "Mobile Plan Services",
  "description": "Mobile communications service including calls, data, and value-added services",
  "features": ["Nationwide calling", "5G data", "International roaming", "Family sharing", "Streaming bundle"],
  "common_issues": [
    "Bill inquiry",
    "Data overage / throttling",
    "Poor signal / unable to make calls",
    "Plan change request",
    "Number porting inquiry"
  ],
  "solutions": {
    "Bill inquiry": "Check itemized billing through the app or by text",
    "Data overage": "Add a data top-up or upgrade your plan",
    "Signal issues": "Confirm location; report for tower maintenance if needed",
    "Plan change": "Takes effect next billing cycle; can be done online",
    "Number porting": "Must meet eligibility requirements; we'll walk you through the process"
  },
  "faq": [
    {"q": "Can I downgrade my plan?", "a": "Yes, but you'll need to wait until your current contract ends"},
    {"q": "What if I run out of data?", "a": "You can add a data pack or upgrade to a higher plan"}
  ],
  "escalation_criteria": "Billing dispute, ongoing signal issues, number porting blocked",
  "sla": {"response_time": "Answer within 30 seconds", "resolution_time": "Service changes take effect immediately"}
}
```

### Healthcare

```json
{
  "name": "Telemedicine Service",
  "description": "Online healthcare platform offering virtual consultations, prescriptions, and health advice",
  "features": ["24/7 consultations", "Specialist appointments", "Prescription services", "Medication delivery", "Health records"],
  "common_issues": [
    "Long wait time for consultation",
    "Unable to book a specific doctor",
    "Prescription delivery delayed",
    "Refund request",
    "Lab results interpretation"
  ],
  "solutions": {
    "Wait time": "Wait times may be longer during peak hours; you can schedule a timed consultation",
    "Booking issues": "Specialist slots are limited; we recommend booking in advance",
    "Delivery delay": "Contact the courier and expedite the shipment",
    "Refund": "Full refund if the consultation hasn't started; partial refund per policy after consultation",
    "Results interpretation": "You can request a paid consultation with a specialist"
  },
  "faq": [
    {"q": "Can you prescribe medication?", "a": "Yes, after a consultation, but some controlled substances are excluded"},
    {"q": "Does insurance cover this?", "a": "Many major insurance plans are accepted - check coverage on our site"}
  ],
  "escalation_criteria": "Medical dispute, adverse drug reaction, emergency situation",
  "sla": {"response_time": "Answer within 60 seconds", "resolution_time": "Medical issues require professional referral"}
}
```

### Travel

```json
{
  "name": "Flight Booking Service",
  "description": "Online flight booking platform for domestic and international flights, changes, and cancellations",
  "features": ["Price comparison", "Online check-in", "Trip management", "Flight status alerts", "Travel insurance"],
  "common_issues": [
    "Flight canceled or delayed",
    "Change or cancellation policy questions",
    "Baggage allowance inquiry",
    "Unable to check in online",
    "Receipt or invoice request"
  ],
  "solutions": {
    "Flight disruption": "Offer rebooking or a full refund",
    "Change / cancellation": "Follow the fare rules; provide specific fees",
    "Baggage": "Varies by airline - we can look up the specific policy",
    "Check-in issues": "Verify flight time and travel document details",
    "Receipt": "An e-ticket receipt can be requested after travel is completed"
  },
  "faq": [
    {"q": "Can I get a refund on a discount ticket?", "a": "Depends on the fare rules - a cancellation fee may apply"},
    {"q": "How do I book an infant ticket?", "a": "Please call us to add the infant - a birth certificate is required"}
  ],
  "escalation_criteria": "Flight cancellation compensation, high-value refund, airline service complaint",
  "sla": {"response_time": "Answer within 45 seconds", "resolution_time": "Refunds processed within 7 business days"}
}
```

### Food Delivery

```json
{
  "name": "Food Delivery Service",
  "description": "Restaurant delivery platform for ordering, tracking, and delivery",
  "features": ["On-time delivery guarantee", "Late delivery credit", "Food safety standards", "Multiple payment options", "Membership discounts"],
  "common_issues": [
    "Order late or not delivered",
    "Food spilled or wrong order",
    "Food quality issue",
    "Refund request",
    "Delivery driver behavior"
  ],
  "solutions": {
    "Late delivery": "Automatic credit issued; refund available upon request",
    "Spilled or wrong order": "Submit a photo and we'll arrange redelivery or a refund",
    "Quality issue": "Keep the evidence; full refund available",
    "Refund": "Processed based on order status; refund issued immediately",
    "Driver behavior": "Complaint logged and reported to the delivery hub"
  },
  "faq": [
    {"q": "How late does it have to be for a refund?", "a": "If it's more than 30 minutes past the estimated time, you can request one"},
    {"q": "Can I get a refund if I just don't like the food?", "a": "Taste preference isn't covered, but quality issues are fully refundable"}
  ],
  "escalation_criteria": "Food safety incident, repeated delivery failures, abusive complaint",
  "sla": {"response_time": "Answer within 20 seconds", "resolution_time": "Refunds processed immediately"}
}
```

---

## Customer Persona Templates

### By Difficulty Level

#### Easy - Easygoing Customers

**Calm Professional**
```json
{
  "name": "Emily Chen",
  "type": "returning",
  "background": "IT manager, reporting a problem on behalf of her team, has detailed notes ready",
  "issue_type": "Bug report",
  "emotional_state": "calm",
  "communication_style": "technical",
  "expectations": "Professional acknowledgment, clear timeline, follow-up",
  "difficulty": "easy",
  "special_needs": "Prefers email follow-up with a ticket number"
}
```

**Curious First-Timer**
```json
{
  "name": "David Liu",
  "type": "new",
  "background": "Researcher, considering a purchase, wants detailed information",
  "issue_type": "Pre-sales inquiry",
  "emotional_state": "neutral",
  "communication_style": "verbose",
  "expectations": "Thorough answers to all questions, no hard sell",
  "difficulty": "easy",
  "special_needs": "None"
}
```

#### Medium - Patience-Required Customers

**Confused Senior**
```json
{
  "name": "Mrs. Johnson",
  "type": "returning",
  "background": "65 years old, long-time customer, not very tech-savvy",
  "issue_type": "Usage issue - can't figure out a new feature",
  "emotional_state": "confused",
  "communication_style": "non-technical",
  "expectations": "Patient step-by-step guidance without being condescending",
  "difficulty": "medium",
  "special_needs": "Needs a slower pace, simple language, may need things repeated"
}
```

**Busy Multitasker**
```json
{
  "name": "Mike Torres",
  "type": "returning",
  "background": "Busy professional, doing other things while on the call",
  "issue_type": "Billing issue - incorrect charge",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "Quick resolution; may hang up if kept waiting too long",
  "difficulty": "medium",
  "special_needs": "Keep it short and to the point; may interrupt"
}
```

**Technical User**
```json
{
  "name": "Alex Zhang",
  "type": "returning",
  "background": "Software developer, been using the product for 6 months, unhappy with a recent update",
  "issue_type": "Technical issue - software bug after update",
  "emotional_state": "frustrated",
  "communication_style": "technical",
  "expectations": "Fast fix and a technical explanation",
  "difficulty": "medium",
  "special_needs": "None"
}
```

#### Hard - Challenging Customers

**Angry First-Timer**
```json
{
  "name": "James Lee",
  "type": "new",
  "background": "First purchase and received a defective product, sent an email complaint but got no response",
  "issue_type": "Product quality - received a defective item",
  "emotional_state": "angry",
  "communication_style": "verbose",
  "expectations": "Immediate replacement or refund, acknowledgment of the service failure",
  "difficulty": "hard",
  "special_needs": "None"
}
```

**Repeat Complainer**
```json
{
  "name": "Sarah Kim",
  "type": "returning",
  "background": "Same issue, third call - never fully resolved",
  "issue_type": "Recurring issue",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "Permanent fix, escalation to a supervisor, some form of compensation",
  "difficulty": "hard",
  "special_needs": "Needs acknowledgment that previous handling was inadequate"
}
```

**VIP Executive**
```json
{
  "name": "Mr. Chen",
  "type": "vip",
  "background": "CEO of a major client company, premium member, time-sensitive issue",
  "issue_type": "Service outage - impacting business operations",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "Immediate escalation if needed, fast resolution, direct communication",
  "difficulty": "hard",
  "special_needs": "Expects priority treatment, direct access to decision-makers if needed"
}
```

---

## Operator Templates by Methodology

> **Language style note**: Templates below use natural English phone conversation style. When generating mock data, all greeting, empathy_phrases, objection_handling, and other scripts must sound like natural spoken English -- warm, professional, and conversational. Avoid robotic, overly formal, or translated-sounding phrasing. Refer to the "Language style" section in SKILL.md for detailed guidance.

### HEAR Method

```json
{
  "name": "HEAR Method",
  "methodology": "HEAR",
  "greeting": "Hi, thanks for calling our support center. My name is [Name] -- how can I help you today?",
  "discovery_questions": [
    "Can you walk me through what happened?",
    "When did this issue start?",
    "Have you tried anything so far to fix it?"
  ],
  "empathy_phrases": [
    "I totally understand where you're coming from",
    "Yeah, that's definitely not the experience you should be having",
    "I'd be frustrated too if that happened to me"
  ],
  "resolution_steps": [
    "Confirm the issue: Restate the customer's problem to make sure you've got it right",
    "Offer a solution: Present 1-2 options to resolve it",
    "Take action: Once the customer agrees, handle it right away",
    "Confirm: After it's done, check that the customer is satisfied"
  ],
  "objection_handling": {
    "Wants a refund": "I hear you. Let me see if we can get this sorted first, and if not, we'll absolutely look at a refund for you. Sound good?",
    "Wants a supervisor": "Of course, I can get a supervisor for you. But if you can fill me in on the details first, it'll speed things up when I transfer you over.",
    "Threatens a bad review": "Your feedback really matters to us. Give me a chance to make this right for you."
  },
  "closing_technique": "Alright, is there anything else I can help you with? If not, have a great rest of your day!",
  "follow_up": "Phone callback within 24 hours for critical issues"
}
```

### LAST Method

```json
{
  "name": "LAST Method",
  "methodology": "LAST",
  "greeting": "Hi, thanks for calling [Company Name]. This is [Name] -- what can I do for you today?",
  "discovery_questions": [
    "What's going on? Tell me about the issue.",
    "Could I grab your order number or account number?",
    "How has this been affecting you?"
  ],
  "empathy_phrases": [
    "That's on us, and I'm really sorry about that",
    "I get it -- that's got to be really frustrating",
    "Thanks for letting us know about this"
  ],
  "resolution_steps": [
    "Listen: Let the customer explain fully without interrupting",
    "Apologize: Offer a sincere apology and take ownership",
    "Solve: Provide a clear solution",
    "Thank: Thank the customer for their feedback and patience"
  ],
  "objection_handling": {
    "Not satisfied with the solution": "I understand -- that might not be the best option. Let me see what else I can do for you.",
    "In a hurry": "Got it, I know your time is valuable. Let me get this taken care of as fast as I can.",
    "Questioning competence": "I've got you covered on this, I promise. And if we need to, I'll loop in our specialist team to make sure it's handled right."
  },
  "closing_technique": "Thanks so much for calling. If anything else comes up, don't hesitate to reach out. Have a great day!",
  "follow_up": "Send a satisfaction survey via text or email"
}
```

### LEARN Method

```json
{
  "name": "LEARN Method",
  "methodology": "LEARN",
  "greeting": "Hi, you've reached [Company Name] support. My name is [Name] -- how can I help?",
  "discovery_questions": [
    "Can you tell me a bit more about what happened?",
    "When did you first notice this issue?",
    "What would you like us to do to resolve this?",
    "Besides this, is there anything else that's been bothering you?"
  ],
  "empathy_phrases": [
    "I completely understand your concern -- this is something we take seriously",
    "Putting myself in your shoes, I can see why that would be worrying",
    "Thanks for giving me all those details -- that really helps me help you"
  ],
  "resolution_steps": [
    "Listen: Give the customer your full attention",
    "Empathize: Express genuine understanding and care",
    "Ask: Ask targeted questions to clarify the details",
    "Resolve: Take action to fix the problem",
    "Notify: Confirm the resolution and set up follow-up"
  ],
  "objection_handling": {
    "Lack of trust": "I understand your concern. Let me walk you through exactly how we're going to handle this, so you know what to expect.",
    "Comparing to competitors": "I appreciate you sharing that. We're always working to improve. For now, let's focus on getting this issue resolved for you.",
    "Emotionally upset": "I completely understand -- take your time. I'm here, and I'm going to make sure we get this sorted out for you."
  },
  "closing_technique": "Alright, I've [specific action taken] for you. Is there anything else I can help with? Thanks for calling, and have a wonderful day!",
  "follow_up": "Email confirmation of resolution within 48 hours, follow-up call after one week"
}
```
