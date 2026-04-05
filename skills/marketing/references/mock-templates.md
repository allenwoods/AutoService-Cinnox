# Mock Data Templates

Templates for generating realistic mock data for sales (production environment).

**Important**: For production use, products MUST include `api_interfaces` and `operator_permissions` fields.

---

## Product Templates by Category

### CRM系统

```json
{
  "name": "智能CRM云平台",
  "category": "CRM系统",
  "description": "一站式客户关系管理平台，支持销售自动化、客户洞察、营销自动化",
  "features": ["销售漏斗管理", "客户360°视图", "智能线索评分", "移动端支持", "API集成"],
  "benefits": [
    "销售效率提升30%",
    "客户转化率提升25%",
    "减少50%手工数据录入"
  ],
  "price": "年费订阅制",
  "price_range": "5-15万/年（按用户数）",
  "target_audience": "中大型企业销售团队",
  "competitors": ["Salesforce", "纷享销客", "销售易"],
  "differentiators": "本地化部署选项、深度微信生态集成、中文AI助手",
  "objections": {
    "价格太贵": "按ROI计算，3个月即可回本。我们提供分期付款方案。",
    "迁移成本高": "提供免费数据迁移服务和专属实施顾问",
    "已有系统": "支持与现有系统无缝集成，可先并行运行"
  },

  "api_interfaces": {
    "pricing_check": {
      "description": "查询产品定价和折扣策略",
      "endpoint": "/api/pricing/crm",
      "method": "GET",
      "params": ["customer_tier", "user_count"],
      "response_fields": ["base_price", "volume_discount", "special_offers", "trial_options"],
      "mock_enabled": true
    },
    "prospect_info": {
      "description": "查询潜在客户信息和历史沟通",
      "endpoint": "/api/crm/prospect/{prospect_id}",
      "method": "GET",
      "params": ["prospect_id"],
      "response_fields": ["company", "contacts", "deal_stage", "interactions", "competitor_info"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["试用<14天", "折扣<5%", "演示安排", "发送资料"],
    "requires_supervisor": ["试用>=14天", "折扣>=5%", "定制报价", "POC项目"],
    "requires_process": ["年度框架协议", "战略合作", "源码授权"],
    "forbidden": ["虚假承诺功能", "贬低竞品", "泄露其他客户信息", "承诺未发布功能"]
  }
}
```

### AI/ML工具

```json
{
  "name": "智能客服机器人",
  "category": "AI/ML工具",
  "description": "基于大语言模型的智能客服解决方案，支持多渠道接入",
  "features": ["多轮对话理解", "知识库自动构建", "人机协作", "多语言支持", "情感分析"],
  "benefits": [
    "客服成本降低60%",
    "7x24小时服务",
    "首次解决率达85%"
  ],
  "price": "按对话量+年费",
  "price_range": "8-30万/年",
  "target_audience": "电商、金融、电信等高客服量行业",
  "competitors": ["阿里小蜜", "网易七鱼", "Intercom"],
  "differentiators": "支持私有化部署、行业专属模型、与主流工单系统深度集成",
  "objections": {
    "AI不够智能": "基于最新大模型，可持续学习优化。我们提供2周免费试用。",
    "担心数据安全": "支持私有化部署，数据完全不出企业",
    "效果难衡量": "提供完整的数据看板，每月出具ROI报告"
  },

  "api_interfaces": {
    "pricing_check": {
      "description": "查询产品定价",
      "endpoint": "/api/pricing/ai-chatbot",
      "method": "GET",
      "params": ["deployment_type", "conversation_volume"],
      "response_fields": ["base_price", "per_conversation_price", "enterprise_discount"],
      "mock_enabled": true
    },
    "feature_availability": {
      "description": "查询功能可用性",
      "endpoint": "/api/product/ai-chatbot/features",
      "method": "GET",
      "params": ["feature_name"],
      "response_fields": ["is_available", "release_date", "tier_required"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["试用<14天", "折扣<10%", "技术演示", "发送案例"],
    "requires_supervisor": ["试用>=14天", "折扣>=10%", "私有化部署报价"],
    "requires_process": ["定制开发", "源码授权", "独家代理"],
    "forbidden": ["承诺准确率保证", "承诺未发布功能", "虚假案例引用"]
  }
}
```

### 数据分析平台

```json
{
  "name": "企业数据中台",
  "category": "数据分析平台",
  "description": "一站式企业数据管理和分析平台，从数据采集到智能决策",
  "features": ["数据集成", "数据治理", "自助BI", "AI预测分析", "实时看板"],
  "benefits": [
    "数据分析效率提升10倍",
    "业务决策响应时间缩短80%",
    "数据资产统一管理"
  ],
  "price": "模块化订阅",
  "price_range": "20-100万/年",
  "target_audience": "数据驱动型中大型企业",
  "competitors": ["Tableau", "帆软", "永洪"],
  "differentiators": "端到端解决方案、低代码数据开发、内置AI模型库",
  "objections": {
    "实施周期长": "标准模块2周上线，复杂场景提供敏捷迭代方案",
    "学习成本高": "低代码设计，业务人员也能快速上手",
    "与现有系统冲突": "开放架构，支持300+数据源接入"
  }
}
```

### 云服务

```json
{
  "name": "混合云管理平台",
  "category": "云服务",
  "description": "统一管理公有云、私有云资源，实现云成本优化和安全合规",
  "features": ["多云管理", "成本优化", "安全合规", "自动化运维", "资源编排"],
  "benefits": [
    "云成本降低30%",
    "运维效率提升50%",
    "合规风险可视化"
  ],
  "price": "按管理资源量",
  "price_range": "10-50万/年",
  "target_audience": "使用多云架构的企业IT部门",
  "competitors": ["VMware", "华为云Stack", "阿里云混合云"],
  "differentiators": "厂商中立、深度FinOps能力、一键合规检查",
  "objections": {
    "已有云厂商工具": "厂商工具只管自家云，我们实现跨云统一视图",
    "担心锁定": "基于开源标准，支持自由迁移",
    "ROI不明显": "免费提供30天成本分析报告，用数据说话"
  }
}
```

### 安全产品

```json
{
  "name": "零信任安全平台",
  "category": "安全产品",
  "description": "新一代企业安全架构，基于零信任理念保护企业数字资产",
  "features": ["身份认证", "动态授权", "终端安全", "网络微隔离", "安全态势感知"],
  "benefits": [
    "安全事件减少80%",
    "远程办公安全保障",
    "满足等保2.0要求"
  ],
  "price": "按终端数",
  "price_range": "15-80万/年",
  "target_audience": "金融、政府、医疗等高安全要求行业",
  "competitors": ["Palo Alto", "奇安信", "深信服"],
  "differentiators": "国产自研、一体化方案、7x24安全运营服务",
  "objections": {
    "现有安全够用": "传统安全已无法应对新型威胁，我们提供免费安全评估",
    "部署影响业务": "渐进式部署方案，对业务零影响",
    "投入太大": "安全事故成本远高于投入，可按需选择模块"
  }
}
```

### 协作工具

```json
{
  "name": "企业协同办公平台",
  "category": "协作工具",
  "description": "一站式企业沟通协作平台，整合即时通讯、文档、会议、流程",
  "features": ["即时通讯", "在线文档", "视频会议", "审批流程", "应用集成"],
  "benefits": [
    "沟通效率提升40%",
    "减少邮件往来70%",
    "流程审批时间缩短60%"
  ],
  "price": "按用户数年费",
  "price_range": "3-20万/年",
  "target_audience": "各行业中小到大型企业",
  "competitors": ["钉钉", "企业微信", "飞书"],
  "differentiators": "开放生态、深度定制能力、私有化部署",
  "objections": {
    "员工习惯微信": "支持微信无缝接入，渐进式迁移",
    "免费版够用": "企业版提供安全管控、数据合规、高级功能",
    "切换成本": "提供迁移工具和培训服务，1个月平滑过渡"
  }
}
```

---

## Customer Persona Templates

### By Difficulty Level

#### Easy - 友好型客户

**早期采用者 (Early Adopter)**
```json
{
  "name": "王小明",
  "role": "创新部总监",
  "company": "新锐科技有限公司",
  "industry": "互联网科技",
  "company_size": "200-500人",
  "pain_points": ["急需提升团队效率", "希望引入新技术"],
  "goals": "成为行业创新标杆，愿意尝试新方案",
  "objections": ["需要看到具体案例", "预算审批流程"],
  "communication_style": "开放、好奇、喜欢深入了解",
  "decision_authority": "本部门可自主决策",
  "budget_sensitivity": "low",
  "difficulty": "easy"
}
```

**有预算决策者 (Budget Owner)**
```json
{
  "name": "李总",
  "role": "副总裁",
  "company": "中型制造企业",
  "industry": "制造业",
  "company_size": "1000-2000人",
  "pain_points": ["数字化转型压力", "需要提升竞争力"],
  "goals": "年内完成核心系统升级",
  "objections": ["实施风险", "内部阻力"],
  "communication_style": "直接、注重结果、时间宝贵",
  "decision_authority": "可独立决策500万以内项目",
  "budget_sensitivity": "medium",
  "difficulty": "easy"
}
```

#### Medium - 需耐心型客户

**谨慎分析者 (Careful Analyst)**
```json
{
  "name": "张工",
  "role": "IT总监",
  "company": "国有银行省分行",
  "industry": "金融银行",
  "company_size": "5000+人",
  "pain_points": ["系统老旧需升级", "合规要求严格"],
  "goals": "找到安全可靠的解决方案",
  "objections": ["需要详细技术评估", "必须满足监管要求", "要看同行案例"],
  "communication_style": "数据驱动、严谨、需要书面材料",
  "decision_authority": "技术评估负责人，需上会决策",
  "budget_sensitivity": "medium",
  "difficulty": "medium"
}
```

**时间紧迫型 (Time-Pressed Executive)**
```json
{
  "name": "陈总监",
  "role": "运营总监",
  "company": "快速发展的电商公司",
  "industry": "零售消费",
  "company_size": "500-1000人",
  "pain_points": ["业务增长太快", "系统跟不上发展"],
  "goals": "快速解决当前瓶颈",
  "objections": ["没时间详细评估", "能否快速上线", "简单直接告诉我方案"],
  "communication_style": "简洁、高效、不喜欢技术细节",
  "decision_authority": "可快速决策，但预算有限",
  "budget_sensitivity": "high",
  "difficulty": "medium"
}
```

**价格敏感采购 (Price-Conscious Buyer)**
```json
{
  "name": "周经理",
  "role": "采购经理",
  "company": "传统制造企业",
  "industry": "制造业",
  "company_size": "2000-5000人",
  "pain_points": ["成本压力大", "需要证明采购价值"],
  "goals": "在预算内找到最优性价比方案",
  "objections": ["价格太高", "能否分期", "竞品报价更低"],
  "communication_style": "注重数字、比较细致、需要商务支持",
  "decision_authority": "采购执行，需业务部门确认需求",
  "budget_sensitivity": "high",
  "difficulty": "medium"
}
```

#### Hard - 高难度客户

**怀疑技术评估者 (Skeptical Evaluator)**
```json
{
  "name": "刘架构师",
  "role": "首席架构师",
  "company": "头部互联网公司",
  "industry": "互联网科技",
  "company_size": "10000+人",
  "pain_points": ["内部有自研能力", "外部方案难以满足定制需求"],
  "goals": "找到能真正解决问题的方案，不接受营销话术",
  "objections": ["技术深度不够", "无法满足定制需求", "我们自己也能做"],
  "communication_style": "技术导向、追问细节、挑战能力边界",
  "decision_authority": "技术否决权，重要技术采购必经",
  "budget_sensitivity": "low",
  "difficulty": "hard"
}
```

**竞品忠实用户 (Competitor Loyalist)**
```json
{
  "name": "孙部长",
  "role": "信息化部部长",
  "company": "大型央企",
  "industry": "能源",
  "company_size": "50000+人",
  "pain_points": ["现有系统用了多年", "更换风险大"],
  "goals": "维持现状，除非有足够理由更换",
  "objections": ["现有系统用得好好的", "切换成本太高", "需要向领导汇报理由"],
  "communication_style": "保守、需要充分理由、关注风险",
  "decision_authority": "有建议权，需集体决策",
  "budget_sensitivity": "medium",
  "difficulty": "hard"
}
```

**委员会决策型 (Committee Decision)**
```json
{
  "name": "郑总",
  "role": "CIO",
  "company": "上市集团公司",
  "industry": "综合",
  "company_size": "20000+人",
  "pain_points": ["集团统一要求高", "各子公司需求不一"],
  "goals": "找到集团级解决方案",
  "objections": ["需要多部门评估", "决策周期长", "需要全面方案"],
  "communication_style": "全局视角、注重协调、需要高层对接",
  "decision_authority": "牵头但需集体决策",
  "budget_sensitivity": "low",
  "difficulty": "hard"
}
```

---

## Operator Templates by Methodology

> **语言风格提示**：以下模板中的话术均为电话口语风格。生成 mock 数据时，所有 opening、key_phrases、objection_handling 等文案必须保持口语化，避免书面翻译腔。参考 SKILL.md 中"语言风格"部分的详细规范。

### SPIN销售法

```json
{
  "name": "SPIN顾问式销售",
  "methodology": "SPIN",
  "approach": "通过系统性提问引导客户发现问题和需求",
  "target_scenario": "复杂B2B销售、解决方案销售、高客单价产品",
  "opening": [
    "谢谢您抽空聊聊。我先了解一下你们现在的情况哈...",
    "咱们先不急聊产品，我想先听听您这边目前碰到什么问题？"
  ],
  "discovery_questions": {
    "situation": [
      "目前贵公司使用什么系统/方案处理这个业务？",
      "团队规模大概有多少人？",
      "现有流程是怎样的？"
    ],
    "problem": [
      "在这个过程中，您遇到最大的挑战是什么？",
      "这个问题多久发生一次？",
      "团队对现状有什么反馈？"
    ],
    "implication": [
      "这个问题如果持续下去，会对业务造成什么影响？",
      "您估算过这个问题每年造成的成本吗？",
      "这对您个人的KPI有什么影响？"
    ],
    "need_payoff": [
      "如果能解决这个问题，您觉得最大的收益是什么？",
      "理想的解决方案应该是什么样的？",
      "如果效率提升30%，对您意味着什么？"
    ]
  },
  "value_proposition": "根据您刚才说的情况，我们这边可以帮您解决[具体问题]，效果上大概能做到[量化的价值]",
  "objection_handling": {
    "价格": "我理解价格是重要考量。让我们算一下ROI...",
    "时机": "理解现在可能不是最佳时机。不过考虑到[影响]，早一天解决...",
    "竞品": "很高兴您做了充分调研。我们的差异化在于..."
  },
  "closing_technique": [
    "基于我们今天的讨论，您觉得下一步安排一个技术评估如何？",
    "我可以下周安排一个演示，让您的团队也看看实际效果？"
  ],
  "key_phrases": [
    "我理解您的意思",
    "这个问题的影响确实值得重视",
    "让我们一起来看看如何解决",
    "您说得对，这确实是个关键点"
  ],
  "pitfalls_to_avoid": [
    "过早进入产品演示",
    "没有充分挖掘问题影响",
    "只问Situation不深入Problem",
    "自己回答Need-Payoff问题"
  ]
}
```

### 挑战者销售法

```json
{
  "name": "挑战者销售法",
  "methodology": "Challenger",
  "approach": "通过提供洞察和挑战客户现有认知来创造价值",
  "target_scenario": "行业变革期、客户需要教育的市场、创新产品销售",
  "opening": [
    "跟不少同行聊下来，我发现一个挺有意思的趋势，跟您分享一下...",
    "最近行业变化挺大的，可能跟你们的规划也有关系..."
  ],
  "discovery_questions": {
    "teaching": [
      "您怎么看待[行业趋势]对贵公司的影响？",
      "在您看来，行业未来3年最大的变化会是什么？"
    ],
    "tailoring": [
      "贵公司在这方面的规划是怎样的？",
      "您面临的独特挑战是什么？"
    ],
    "control": [
      "如果不采取行动，您觉得风险有多大？",
      "决策过程中还有哪些关键人需要参与？"
    ]
  },
  "value_proposition": "我们看到行业正在发生[趋势]，领先企业已经在[行动]。我们可以帮助您[价值]",
  "objection_handling": {
    "不认同趋势": "我理解您的观点。不过[数据/案例]表明...",
    "我们不一样": "您说得对，每家企业情况不同。让我们看看具体怎么适配...",
    "内部阻力": "变革确实需要克服阻力。我们可以一起制定推进策略..."
  },
  "closing_technique": [
    "既然您也认同这个趋势的重要性，我建议我们下一步...",
    "让我帮您准备一份给管理层的汇报材料？"
  ],
  "key_phrases": [
    "行业领先企业已经在...",
    "数据显示...",
    "这可能会改变您的看法",
    "让我分享一个不同的视角"
  ],
  "pitfalls_to_avoid": [
    "挑战变成冒犯",
    "没有足够的数据支撑观点",
    "只顾教育忘了倾听",
    "过于激进失去信任"
  ]
}
```

### 解决方案销售

```json
{
  "name": "解决方案销售",
  "methodology": "Solution Selling",
  "approach": "深入理解客户痛点，提供定制化解决方案",
  "target_scenario": "复杂项目销售、客户有明确痛点、需要整合方案",
  "opening": [
    "听说你们这边在处理[业务挑战]，我想多了解一下...",
    "之前帮不少类似的企业解决过[问题]，想看看能不能也帮到你们..."
  ],
  "discovery_questions": {
    "pain": [
      "目前最让您头疼的业务问题是什么？",
      "这个问题存在多久了？",
      "之前尝试过什么方案？"
    ],
    "power": [
      "除了您之外，还有谁关心这个问题？",
      "这个项目的预算和时间线是怎样的？",
      "决策流程是怎样的？"
    ],
    "vision": [
      "理想的解决方案应该是什么样的？",
      "成功的标准是什么？",
      "您希望在什么时间看到效果？"
    ]
  },
  "value_proposition": "针对您提到的[痛点]，我们可以提供[定制方案]，帮助您实现[愿景]",
  "objection_handling": {
    "方案不够定制": "让我们深入讨论您的具体需求，看如何调整方案...",
    "风险太大": "我们可以分阶段实施，先用小范围验证...",
    "周期太长": "让我们看看哪些部分可以并行，加速实施..."
  },
  "closing_technique": [
    "基于我们讨论的方案，我准备一份详细的实施计划？",
    "要不我们下周约一次方案评审会？"
  ],
  "key_phrases": [
    "您的情况比较独特",
    "让我们一起设计一个适合您的方案",
    "分阶段实施可以控制风险",
    "我们成功帮助过[类似企业]"
  ],
  "pitfalls_to_avoid": [
    "过早提出方案没有充分理解需求",
    "忽视决策链其他关键人",
    "方案过于标准化不够定制",
    "没有明确成功标准"
  ]
}
```

### 价值销售

```json
{
  "name": "价值销售",
  "methodology": "Value Selling",
  "approach": "聚焦量化业务价值，用ROI说话",
  "target_scenario": "高价值项目、客户注重ROI、竞争激烈需差异化",
  "opening": [
    "想先问一下，你们这边[业务领域]最看重的指标是什么？",
    "我们客户平均做到了[量化价值]，想看看能不能也帮到你们..."
  ],
  "discovery_questions": {
    "discover": [
      "目前这个业务的关键KPI是什么？",
      "当前的达成情况如何？",
      "行业标杆水平是多少？"
    ],
    "diagnose": [
      "影响KPI达成的主要因素是什么？",
      "您估算过这个差距的成本吗？",
      "哪些改进空间最大？"
    ],
    "design": [
      "如果KPI提升X%，对业务意味着什么？",
      "您愿意为这个提升投入多少？",
      "怎样的回报周期是可接受的？"
    ]
  },
  "value_proposition": "根据我们的计算，这个方案可以帮您实现[量化价值]，投资回报期为[时间]",
  "objection_handling": {
    "价值算不清": "让我们一起做一个详细的价值分析...",
    "承诺太大": "这是基于我们过去案例的平均值，我们可以约定保守一点的目标...",
    "隐性成本": "让我把TCO完整算给您看..."
  },
  "closing_technique": [
    "既然ROI是正的，我们下一步落实实施计划？",
    "我准备一份详细的价值分析报告给您的管理层？"
  ],
  "key_phrases": [
    "让我们量化一下价值",
    "投资回报期是X个月",
    "这相当于每年节省X万",
    "同行业客户平均实现了..."
  ],
  "pitfalls_to_avoid": [
    "价值承诺过于激进",
    "只谈功能不谈价值",
    "忽视客户的价值计算方式",
    "没有对标行业标杆"
  ]
}
```
