# Mock Data Templates (English)

Templates for generating realistic English mock data for sales (production environment).

**Important**: For production use, products MUST include `api_interfaces` and `operator_permissions` fields.

---

## Product Templates by Category

### CRM Systems

```json
{
  "name": "Smart CRM Cloud Platform",
  "category": "CRM Systems",
  "description": "All-in-one customer relationship management platform with sales automation, customer insights, and marketing automation",
  "features": ["Sales pipeline management", "Customer 360° view", "Intelligent lead scoring", "Mobile support", "API integrations"],
  "benefits": [
    "Boost sales productivity by 30%",
    "Increase customer conversion rates by 25%",
    "Reduce manual data entry by 50%"
  ],
  "price": "Annual subscription",
  "price_range": "$50K-$150K/year (per seat pricing)",
  "target_audience": "Mid-to-large enterprise sales teams",
  "competitors": ["Salesforce", "HubSpot", "Microsoft Dynamics"],
  "differentiators": "Flexible deployment options, deep ecosystem integrations, AI-powered sales assistant",
  "objections": {
    "Too expensive": "When you look at the ROI, most customers break even within 3 months. We also offer flexible payment plans.",
    "High migration costs": "We provide complimentary data migration services and a dedicated implementation consultant.",
    "Already have a system": "We integrate seamlessly with your existing stack. You can run both systems in parallel during the transition."
  },

  "api_interfaces": {
    "pricing_check": {
      "description": "Query product pricing and discount strategies",
      "endpoint": "/api/pricing/crm",
      "method": "GET",
      "params": ["customer_tier", "user_count"],
      "response_fields": ["base_price", "volume_discount", "special_offers", "trial_options"],
      "mock_enabled": true
    },
    "prospect_info": {
      "description": "Query prospect information and communication history",
      "endpoint": "/api/crm/prospect/{prospect_id}",
      "method": "GET",
      "params": ["prospect_id"],
      "response_fields": ["company", "contacts", "deal_stage", "interactions", "competitor_info"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["Trial<14 days", "Discount<5%", "Schedule demo", "Send collateral"],
    "requires_supervisor": ["Trial>=14 days", "Discount>=5%", "Custom quote", "POC project"],
    "requires_process": ["Annual framework agreement", "Strategic partnership", "Source code license"],
    "forbidden": ["Falsely promise features", "Disparage competitors", "Disclose other client information", "Promise unreleased features"]
  }
}
```

### AI/ML Tools

```json
{
  "name": "AI Customer Service Bot",
  "category": "AI/ML Tools",
  "description": "LLM-powered intelligent customer service solution with multi-channel support",
  "features": ["Multi-turn conversation understanding", "Automated knowledge base construction", "Human-AI collaboration", "Multi-language support", "Sentiment analysis"],
  "benefits": [
    "Reduce customer service costs by 60%",
    "24/7 service availability",
    "First contact resolution rate of 85%"
  ],
  "price": "Per conversation volume + annual fee",
  "price_range": "$80K-$300K/year",
  "target_audience": "E-commerce, financial services, telecom, and other high-volume support industries",
  "competitors": ["Intercom", "Zendesk AI", "Drift"],
  "differentiators": "On-premise deployment option, industry-specific models, deep integration with major ticketing systems",
  "objections": {
    "AI isn't smart enough": "We're built on the latest large language models and continuously learn from your data. We offer a 2-week free trial so you can see for yourself.",
    "Concerned about data security": "We support fully on-premise deployment -- your data never leaves your environment.",
    "Hard to measure results": "We provide comprehensive analytics dashboards and deliver monthly ROI reports."
  },

  "api_interfaces": {
    "pricing_check": {
      "description": "Query product pricing",
      "endpoint": "/api/pricing/ai-chatbot",
      "method": "GET",
      "params": ["deployment_type", "conversation_volume"],
      "response_fields": ["base_price", "per_conversation_price", "enterprise_discount"],
      "mock_enabled": true
    },
    "feature_availability": {
      "description": "Query feature availability",
      "endpoint": "/api/product/ai-chatbot/features",
      "method": "GET",
      "params": ["feature_name"],
      "response_fields": ["is_available", "release_date", "tier_required"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["Trial<14 days", "Discount<10%", "Technical demo", "Send case studies"],
    "requires_supervisor": ["Trial>=14 days", "Discount>=10%", "On-premise deployment quote"],
    "requires_process": ["Custom development", "Source code license", "Exclusive reseller agreement"],
    "forbidden": ["Promise accuracy guarantees", "Promise unreleased features", "Cite fabricated case studies"]
  }
}
```

### Data Analytics Platform

```json
{
  "name": "Enterprise Data Platform",
  "category": "Data Analytics Platform",
  "description": "End-to-end enterprise data management and analytics platform, from data ingestion to intelligent decision-making",
  "features": ["Data integration", "Data governance", "Self-service BI", "AI-powered predictive analytics", "Real-time dashboards"],
  "benefits": [
    "10x improvement in data analysis efficiency",
    "80% reduction in business decision response time",
    "Unified data asset management"
  ],
  "price": "Modular subscription",
  "price_range": "$200K-$1M/year",
  "target_audience": "Data-driven mid-to-large enterprises",
  "competitors": ["Tableau", "Snowflake", "Databricks"],
  "differentiators": "End-to-end solution, low-code data development, built-in AI model library",
  "objections": {
    "Long implementation cycle": "Standard modules go live in 2 weeks. For complex use cases, we offer agile, iterative rollout plans.",
    "Steep learning curve": "It's designed to be low-code, so business users can get up and running quickly.",
    "Conflicts with existing systems": "Open architecture with 300+ pre-built data source connectors."
  }
}
```

### Cloud Services

```json
{
  "name": "Hybrid Cloud Management Platform",
  "category": "Cloud Services",
  "description": "Unified management for public and private cloud resources, enabling cost optimization and security compliance",
  "features": ["Multi-cloud management", "Cost optimization", "Security compliance", "Automated operations", "Resource orchestration"],
  "benefits": [
    "Reduce cloud costs by 30%",
    "Boost operational efficiency by 50%",
    "Full visibility into compliance risks"
  ],
  "price": "Based on managed resource volume",
  "price_range": "$100K-$500K/year",
  "target_audience": "Enterprise IT departments running multi-cloud architectures",
  "competitors": ["VMware", "HashiCorp", "Flexera"],
  "differentiators": "Vendor-neutral, deep FinOps capabilities, one-click compliance audits",
  "objections": {
    "Already using cloud-native tools": "Vendor tools only cover their own cloud. We give you a single pane of glass across all providers.",
    "Worried about lock-in": "We're built on open standards, so you're always free to move.",
    "ROI isn't obvious": "We'll run a free 30-day cost analysis report for you. Let the numbers do the talking."
  }
}
```

### Security Products

```json
{
  "name": "Zero Trust Security Platform",
  "category": "Security Products",
  "description": "Next-generation enterprise security architecture based on zero trust principles to protect digital assets",
  "features": ["Identity authentication", "Dynamic authorization", "Endpoint security", "Network micro-segmentation", "Security posture awareness"],
  "benefits": [
    "Reduce security incidents by 80%",
    "Secure remote workforce access",
    "Meet SOC 2, ISO 27001, and NIST compliance requirements"
  ],
  "price": "Per endpoint",
  "price_range": "$150K-$800K/year",
  "target_audience": "Financial services, government, healthcare, and other high-security industries",
  "competitors": ["Palo Alto Networks", "Zscaler", "CrowdStrike"],
  "differentiators": "Integrated platform approach, unified policy engine, 24/7 managed security operations",
  "objections": {
    "Current security is good enough": "Legacy perimeter security can't handle modern threats. We offer a free security assessment to show you the gaps.",
    "Deployment disrupts business": "We use a phased rollout approach with zero business impact.",
    "Too big an investment": "The cost of a single breach far exceeds the investment. You can also start with individual modules."
  }
}
```

### Collaboration Tools

```json
{
  "name": "Enterprise Collaboration Platform",
  "category": "Collaboration Tools",
  "description": "All-in-one enterprise communication and collaboration platform integrating messaging, documents, meetings, and workflows",
  "features": ["Instant messaging", "Online documents", "Video conferencing", "Approval workflows", "App integrations"],
  "benefits": [
    "Improve communication efficiency by 40%",
    "Reduce email volume by 70%",
    "Cut workflow approval time by 60%"
  ],
  "price": "Per user annual fee",
  "price_range": "$30K-$200K/year",
  "target_audience": "Small to large enterprises across all industries",
  "competitors": ["Slack", "Microsoft Teams", "Google Workspace"],
  "differentiators": "Open ecosystem, deep customization capabilities, on-premise deployment option",
  "objections": {
    "Everyone's used to Slack/Teams": "We integrate seamlessly with your current tools. You can migrate gradually at your own pace.",
    "Free tier is good enough": "The enterprise edition provides security controls, data compliance, and advanced admin features you won't get otherwise.",
    "Switching costs": "We provide migration tools and training. Most teams are fully transitioned within a month."
  }
}
```

---

## Customer Persona Templates

### By Difficulty Level

#### Easy - Friendly Prospects

**Early Adopter**
```json
{
  "name": "Michael Wang",
  "role": "Director of Innovation",
  "company": "Vanguard Technologies Inc.",
  "industry": "Technology",
  "company_size": "200-500 employees",
  "pain_points": ["Urgently needs to improve team productivity", "Eager to adopt new technology"],
  "goals": "Become an industry innovation leader, willing to try new solutions",
  "objections": ["Need to see concrete case studies", "Budget approval process"],
  "communication_style": "Open, curious, likes to dig into details",
  "decision_authority": "Can make independent decisions for their department",
  "budget_sensitivity": "low",
  "difficulty": "easy"
}
```

**Budget Owner**
```json
{
  "name": "Sarah Johnson",
  "role": "Vice President",
  "company": "Midwest Manufacturing Corp.",
  "industry": "Manufacturing",
  "company_size": "1,000-2,000 employees",
  "pain_points": ["Digital transformation pressure", "Need to improve competitiveness"],
  "goals": "Complete core system upgrades within the year",
  "objections": ["Implementation risk", "Internal resistance to change"],
  "communication_style": "Direct, results-oriented, values their time",
  "decision_authority": "Can independently approve projects up to $500K",
  "budget_sensitivity": "medium",
  "difficulty": "easy"
}
```

#### Medium - Requires Patience

**Careful Analyst**
```json
{
  "name": "Robert Zhang",
  "role": "IT Director",
  "company": "National Federal Credit Union",
  "industry": "Financial Services",
  "company_size": "5,000+ employees",
  "pain_points": ["Legacy systems need upgrading", "Strict regulatory requirements"],
  "goals": "Find a secure and reliable solution",
  "objections": ["Need a thorough technical evaluation", "Must meet regulatory requirements", "Want to see peer references"],
  "communication_style": "Data-driven, rigorous, requires written documentation",
  "decision_authority": "Leads technical evaluation, final decision requires committee approval",
  "budget_sensitivity": "medium",
  "difficulty": "medium"
}
```

**Time-Pressed Executive**
```json
{
  "name": "Jennifer Chen",
  "role": "Director of Operations",
  "company": "FastGrowth E-Commerce LLC",
  "industry": "Retail & E-Commerce",
  "company_size": "500-1,000 employees",
  "pain_points": ["Business growing too fast", "Systems can't keep up with growth"],
  "goals": "Quickly resolve current bottlenecks",
  "objections": ["No time for lengthy evaluations", "How fast can we go live?", "Just give me the bottom line"],
  "communication_style": "Concise, efficient, doesn't want technical details",
  "decision_authority": "Can make quick decisions but budget is limited",
  "budget_sensitivity": "high",
  "difficulty": "medium"
}
```

**Price-Conscious Buyer**
```json
{
  "name": "David Zhou",
  "role": "Procurement Manager",
  "company": "Heritage Manufacturing Group",
  "industry": "Manufacturing",
  "company_size": "2,000-5,000 employees",
  "pain_points": ["Under heavy cost pressure", "Needs to justify procurement value"],
  "goals": "Find the best value-for-money solution within budget",
  "objections": ["Price is too high", "Can we do installments?", "Competitor quoted lower"],
  "communication_style": "Numbers-focused, detail-oriented, needs commercial support",
  "decision_authority": "Executes procurement, needs business unit sign-off on requirements",
  "budget_sensitivity": "high",
  "difficulty": "medium"
}
```

#### Hard - Challenging Prospects

**Skeptical Evaluator**
```json
{
  "name": "Andrew Liu",
  "role": "Chief Architect",
  "company": "Apex Digital Corp.",
  "industry": "Technology",
  "company_size": "10,000+ employees",
  "pain_points": ["Strong internal engineering capability", "External solutions rarely meet custom requirements"],
  "goals": "Find a solution that genuinely solves the problem -- no tolerance for marketing fluff",
  "objections": ["Not technically deep enough", "Can't meet our customization needs", "We could build this ourselves"],
  "communication_style": "Technically oriented, probes for details, tests your limits",
  "decision_authority": "Technical veto power, must sign off on all major tech purchases",
  "budget_sensitivity": "low",
  "difficulty": "hard"
}
```

**Competitor Loyalist**
```json
{
  "name": "William Sun",
  "role": "Head of IT Infrastructure",
  "company": "Continental Energy Holdings",
  "industry": "Energy",
  "company_size": "50,000+ employees",
  "pain_points": ["Current system has been in place for years", "High switching risk"],
  "goals": "Maintain the status quo unless there's a compelling reason to change",
  "objections": ["Current system works just fine", "Switching costs are too high", "Need to justify the change to leadership"],
  "communication_style": "Conservative, needs thorough justification, risk-averse",
  "decision_authority": "Advisory role, requires collective decision-making",
  "budget_sensitivity": "medium",
  "difficulty": "hard"
}
```

**Committee Decision**
```json
{
  "name": "Patricia Zheng",
  "role": "CIO",
  "company": "Summit Group International",
  "industry": "Conglomerate",
  "company_size": "20,000+ employees",
  "pain_points": ["High bar for group-wide standards", "Different subsidiaries have different needs"],
  "goals": "Find an enterprise-wide solution that works across the group",
  "objections": ["Needs multi-department evaluation", "Long decision cycle", "Requires a comprehensive proposal"],
  "communication_style": "Big-picture thinker, focused on coordination, expects executive-level engagement",
  "decision_authority": "Leads the initiative but requires collective sign-off",
  "budget_sensitivity": "low",
  "difficulty": "hard"
}
```

---

## Operator Templates by Methodology

> **Language style note**: Templates use natural English phone sales style. When generating mock data, all opening, key_phrases, objection_handling must use natural spoken English, avoiding corporate jargon or overly scripted language.

### SPIN Selling

```json
{
  "name": "SPIN Consultative Selling",
  "methodology": "SPIN",
  "approach": "Guide prospects to discover their own problems and needs through systematic questioning",
  "target_scenario": "Complex B2B sales, solution selling, high-value products",
  "opening": [
    "Thanks for making the time today. Before we get into anything, I'd love to hear a bit about what's going on at your end...",
    "Let's not jump into the product just yet -- I'd rather understand what challenges you're facing first."
  ],
  "discovery_questions": {
    "situation": [
      "What system or process are you currently using to handle this?",
      "Roughly how big is the team involved?",
      "Can you walk me through how the current workflow looks?"
    ],
    "problem": [
      "What's the biggest challenge you're running into with this process?",
      "How often does this issue come up?",
      "What's the team's feedback on the current setup?"
    ],
    "implication": [
      "If this keeps going unchecked, what kind of impact would it have on the business?",
      "Have you been able to put a number on what this problem costs you each year?",
      "How does this affect your personal KPIs or targets?"
    ],
    "need_payoff": [
      "If we could fix this, what would be the biggest win for you?",
      "What would the ideal solution look like in your mind?",
      "If you could boost efficiency by 30%, what would that mean for your team?"
    ]
  },
  "value_proposition": "Based on what you've shared, we can help you tackle [specific problem] and deliver roughly [quantified value]",
  "objection_handling": {
    "Price": "I totally get that price is a big factor. Let's walk through the ROI together...",
    "Timing": "I understand the timing might feel off. But given the impact of [problem], the sooner we address it...",
    "Competition": "Great that you've done your homework. Where we really stand out is..."
  },
  "closing_technique": [
    "Based on what we've discussed today, would it make sense to set up a technical evaluation as a next step?",
    "How about I schedule a demo for next week so your team can see it in action?"
  ],
  "key_phrases": [
    "I hear what you're saying",
    "That's a real concern worth taking seriously",
    "Let's figure this out together",
    "You're right, that's a critical point"
  ],
  "pitfalls_to_avoid": [
    "Jumping into a product demo too early",
    "Not fully exploring the business impact of the problem",
    "Asking only Situation questions without digging into Problems",
    "Answering the Need-Payoff questions yourself instead of letting the prospect"
  ]
}
```

### Challenger Sales

```json
{
  "name": "Challenger Sales Method",
  "methodology": "Challenger",
  "approach": "Create value by delivering insights and challenging the prospect's existing assumptions",
  "target_scenario": "Industry disruption periods, markets requiring customer education, innovative product sales",
  "opening": [
    "I've been talking to a lot of folks in your space lately, and there's an interesting trend I wanted to share with you...",
    "The industry's been shifting pretty quickly -- I think it ties into some of the things you're probably planning for..."
  ],
  "discovery_questions": {
    "teaching": [
      "How do you see [industry trend] impacting your business?",
      "In your view, what's going to be the biggest change in the industry over the next three years?"
    ],
    "tailoring": [
      "What's your company's roadmap in this area?",
      "What are the unique challenges you're dealing with?"
    ],
    "control": [
      "If you don't take action, how big is the risk in your view?",
      "Who else needs to be involved in this decision?"
    ]
  },
  "value_proposition": "We're seeing [trend] reshape the industry, and the leading companies are already [action]. We can help you [value]",
  "objection_handling": {
    "Don't agree with the trend": "I respect your perspective. But if you look at [data/case study]...",
    "We're different": "You're absolutely right -- every company has its own context. Let's look at how we can tailor this...",
    "Internal resistance": "Change is always tough. We can work with you on a rollout strategy that brings people along..."
  },
  "closing_technique": [
    "Since you agree this trend is important, I'd suggest we take the next step and...",
    "Want me to help you put together a briefing for your leadership team?"
  ],
  "key_phrases": [
    "The leading companies in your space are already...",
    "The data shows...",
    "This might change how you think about it",
    "Let me share a different perspective on this"
  ],
  "pitfalls_to_avoid": [
    "Challenging turns into offending",
    "Not having enough data to back up your point of view",
    "Teaching without listening",
    "Being too aggressive and losing trust"
  ]
}
```

### Solution Selling

```json
{
  "name": "Solution Selling",
  "methodology": "Solution Selling",
  "approach": "Deeply understand customer pain points and deliver tailored solutions",
  "target_scenario": "Complex project sales, prospects with clear pain points, requires integrated solutions",
  "opening": [
    "I heard your team's been dealing with [business challenge] -- I'd love to learn more about that...",
    "We've helped quite a few companies work through [problem], and I wanted to see if we could do the same for you..."
  ],
  "discovery_questions": {
    "pain": [
      "What's the biggest headache on the business side right now?",
      "How long has this been going on?",
      "What have you tried so far to fix it?"
    ],
    "power": [
      "Beyond yourself, who else cares about solving this?",
      "What does the budget and timeline look like for this project?",
      "How does the decision-making process work?"
    ],
    "vision": [
      "What would the ideal solution look like for you?",
      "How would you define success?",
      "When do you need to see results by?"
    ]
  },
  "value_proposition": "Based on the pain points you've described, we can deliver [tailored solution] to help you achieve [vision]",
  "objection_handling": {
    "Solution isn't customized enough": "Let's dive deeper into your specific requirements and see how we can adjust the approach...",
    "Too risky": "We can phase the rollout so you can validate with a smaller group first...",
    "Takes too long": "Let's see which parts we can run in parallel to speed things up..."
  },
  "closing_technique": [
    "Based on what we've mapped out, how about I put together a detailed implementation plan?",
    "Shall we schedule a solution review session next week with the broader team?"
  ],
  "key_phrases": [
    "Your situation is pretty unique",
    "Let's design something that works specifically for you",
    "Phased implementation helps manage the risk",
    "We've successfully helped [similar company] with this"
  ],
  "pitfalls_to_avoid": [
    "Proposing a solution before fully understanding the needs",
    "Ignoring other key stakeholders in the decision chain",
    "Offering a cookie-cutter solution that doesn't feel customized",
    "Not defining clear success criteria upfront"
  ]
}
```

### Value Selling

```json
{
  "name": "Value Selling",
  "methodology": "Value Selling",
  "approach": "Focus on quantifying business value and let the ROI speak for itself",
  "target_scenario": "High-value projects, ROI-focused buyers, competitive situations requiring differentiation",
  "opening": [
    "Quick question to start -- what are the key metrics your team is measured on in [business area]?",
    "Our customers are seeing an average of [quantified value] -- I wanted to explore whether we can do the same for you..."
  ],
  "discovery_questions": {
    "discover": [
      "What are the critical KPIs for this part of the business?",
      "Where are you tracking against those targets right now?",
      "What does best-in-class look like in your industry?"
    ],
    "diagnose": [
      "What's the main thing holding you back from hitting those numbers?",
      "Have you been able to estimate what that gap is costing you?",
      "Where do you see the biggest room for improvement?"
    ],
    "design": [
      "If you could improve that KPI by X%, what would that mean for the business?",
      "What level of investment would that improvement justify?",
      "What kind of payback period would make sense for you?"
    ]
  },
  "value_proposition": "Based on our analysis, this solution can deliver [quantified value] with a payback period of [timeframe]",
  "objection_handling": {
    "Can't quantify the value": "Let's work through a detailed value analysis together...",
    "Promises seem too good": "These figures are based on averages from our existing customers. We're happy to set more conservative targets...",
    "Hidden costs": "Let me walk you through the full TCO so there are no surprises..."
  },
  "closing_technique": [
    "Since the ROI is clearly positive, shall we move forward with nailing down the implementation plan?",
    "How about I put together a detailed value analysis report for your leadership team?"
  ],
  "key_phrases": [
    "Let's put some numbers around the value",
    "The payback period is X months",
    "That translates to roughly $X in annual savings",
    "Customers in your industry are averaging..."
  ],
  "pitfalls_to_avoid": [
    "Making overly aggressive value claims",
    "Talking only about features instead of value",
    "Ignoring how the customer calculates value internally",
    "Not benchmarking against industry standards"
  ]
}
```
