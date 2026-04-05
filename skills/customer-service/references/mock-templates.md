# Mock Data Templates

Templates for generating realistic mock data for customer service (production environment).

**Important**: For production use, products MUST include `api_interfaces` and `operator_permissions` fields.

---

## Product Templates by Category

### Electronics

```json
{
  "name": "智能手表 Pro X",
  "description": "高端智能手表，支持心率监测、GPS定位、NFC支付",
  "features": ["心率监测", "GPS定位", "NFC支付", "防水50米", "7天续航"],
  "common_issues": [
    "无法连接手机蓝牙",
    "心率监测数据不准确",
    "充电速度慢或无法充电",
    "表带断裂",
    "屏幕划痕"
  ],
  "solutions": {
    "蓝牙连接问题": "重启手表和手机，删除配对重新连接",
    "心率不准": "确保佩戴紧贴皮肤，清洁传感器",
    "充电问题": "检查充电座接触点，使用原装充电器",
    "表带断裂": "可免费更换（保修期内）",
    "屏幕划痕": "提供付费维修服务"
  },
  "faq": [
    {"q": "防水能游泳吗？", "a": "支持游泳，但不支持潜水和热水浴"},
    {"q": "能接打电话吗？", "a": "支持蓝牙通话，需配合手机使用"}
  ],
  "escalation_criteria": "客户要求退货、投诉产品质量问题、涉及人身安全",
  "sla": {"response_time": "30秒内接听", "resolution_time": "首次通话解决率80%"},

  "api_interfaces": {
    "warranty_check": {
      "description": "查询产品保修状态",
      "endpoint": "/api/warranty/{serial_number}",
      "method": "GET",
      "params": ["serial_number"],
      "response_fields": ["is_valid", "purchase_date", "expiry_date", "coverage_type"],
      "mock_enabled": true
    },
    "repair_history": {
      "description": "查询维修记录",
      "endpoint": "/api/repair/{serial_number}/history",
      "method": "GET",
      "params": ["serial_number"],
      "response_fields": ["repairs", "last_repair_date"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["免费更换表带", "软件重置指导", "退款<300元"],
    "requires_supervisor": ["退款>=300元", "免费更换主机", "延长保修"],
    "requires_process": ["产品质量投诉", "批量退货"],
    "forbidden": ["承诺未发布功能", "透露供应商信息"]
  }
}
```

### Software / SaaS

```json
{
  "name": "云存储服务 Plus",
  "description": "企业级云存储解决方案，支持文件同步、共享、备份",
  "features": ["1TB存储空间", "实时同步", "团队协作", "版本历史", "端到端加密"],
  "common_issues": [
    "同步失败或卡住",
    "文件丢失或损坏",
    "无法登录账户",
    "存储空间不足提醒",
    "分享链接失效"
  ],
  "solutions": {
    "同步问题": "检查网络连接，清除缓存，重新登录",
    "文件丢失": "检查回收站和版本历史，可恢复30天内删除文件",
    "登录问题": "重置密码，检查是否被锁定",
    "空间不足": "清理大文件或升级套餐",
    "链接失效": "检查分享设置，重新生成链接"
  },
  "faq": [
    {"q": "数据安全吗？", "a": "采用AES-256加密，通过ISO27001认证"},
    {"q": "能恢复删除的文件吗？", "a": "30天内可从回收站恢复"}
  ],
  "escalation_criteria": "数据泄露担忧、企业客户批量问题、账号被盗",
  "sla": {"response_time": "2分钟内接听", "resolution_time": "技术问题24小时内解决"},

  "api_interfaces": {
    "subscription_check": {
      "description": "查询用户订阅状态",
      "endpoint": "/api/user/{user_id}/subscription",
      "method": "GET",
      "params": ["user_id"],
      "response_fields": ["plan", "storage_limit", "used_storage", "expiry_date", "auto_renew"],
      "mock_enabled": true
    },
    "storage_usage": {
      "description": "查询存储空间使用情况",
      "endpoint": "/api/user/{user_id}/storage",
      "method": "GET",
      "params": ["user_id"],
      "response_fields": ["used_bytes", "total_bytes", "file_count", "largest_files"],
      "mock_enabled": true
    },
    "billing_history": {
      "description": "查询账单历史",
      "endpoint": "/api/user/{user_id}/billing",
      "method": "GET",
      "params": ["user_id", "months"],
      "response_fields": ["transactions", "total_charged"],
      "mock_enabled": true
    }
  },

  "operator_permissions": {
    "can_approve_immediately": ["重置密码", "恢复删除文件<30天", "临时扩容<1GB", "退款<50元"],
    "requires_supervisor": ["退款>=50元", "永久扩容", "账户解锁（异常登录）"],
    "requires_process": ["数据导出请求", "账户注销", "数据泄露调查"],
    "forbidden": ["访问用户文件内容", "绕过加密", "透露其他用户信息"]
  }
}
```

### E-commerce

```json
{
  "name": "在线购物平台订单",
  "description": "综合电商平台，销售电子产品、服装、家居用品等",
  "features": ["次日达配送", "7天无理由退换", "正品保证", "价格保护"],
  "common_issues": [
    "订单状态查询",
    "物流延迟或丢失",
    "收到错误/损坏商品",
    "退款未到账",
    "优惠券无法使用"
  ],
  "solutions": {
    "订单查询": "提供订单号查询实时状态",
    "物流问题": "联系快递公司，必要时补发",
    "商品问题": "拍照上传，安排退换货",
    "退款延迟": "核实退款状态，一般3-5个工作日到账",
    "优惠券问题": "检查使用条件和有效期"
  },
  "faq": [
    {"q": "退货运费谁承担？", "a": "质量问题我们承担，无理由退换客户承担"},
    {"q": "发票怎么开？", "a": "订单详情页可申请电子发票"}
  ],
  "escalation_criteria": "大额订单问题、多次退换货、投诉态度",
  "sla": {"response_time": "20秒内接听", "resolution_time": "退换货48小时内处理"}
}
```

### Finance / Banking

```json
{
  "name": "信用卡服务",
  "description": "银行信用卡产品，包括消费、还款、积分兑换",
  "features": ["免年费", "消费返现", "积分兑换", "分期付款", "境外消费免货币转换费"],
  "common_issues": [
    "账单金额疑问",
    "还款未到账",
    "卡片挂失/解冻",
    "额度调整申请",
    "积分查询/兑换"
  ],
  "solutions": {
    "账单疑问": "核对交易明细，可申请账单复核",
    "还款问题": "确认还款渠道和到账时间（跨行1-2天）",
    "挂失解冻": "身份验证后即时处理",
    "额度调整": "需提交申请，3个工作日审批",
    "积分问题": "可通过APP实时查询和兑换"
  },
  "faq": [
    {"q": "最低还款会影响信用吗？", "a": "不影响信用记录，但会产生利息"},
    {"q": "境外消费手续费？", "a": "本卡境外消费免货币转换费"}
  ],
  "escalation_criteria": "欺诈交易、大额纠纷、投诉服务态度、监管投诉",
  "sla": {"response_time": "15秒内接听", "resolution_time": "紧急挂失即时处理"}
}
```

### Telecom

```json
{
  "name": "移动通信套餐",
  "description": "手机通信服务，包括通话、流量、增值服务",
  "features": ["全国通话", "5G流量", "国际漫游", "家庭共享", "视频会员"],
  "common_issues": [
    "话费账单查询",
    "流量用超/限速",
    "信号差/无法通话",
    "套餐变更",
    "携号转网咨询"
  ],
  "solutions": {
    "账单查询": "可通过APP或短信查询明细",
    "流量问题": "购买加油包或升级套餐",
    "信号问题": "确认位置，必要时报修基站",
    "套餐变更": "次月生效，可线上办理",
    "携号转网": "需满足条件，提供转网流程"
  },
  "faq": [
    {"q": "套餐能降级吗？", "a": "可以，但需等当前合约到期"},
    {"q": "流量不够用怎么办？", "a": "可购买流量包或升级套餐"}
  ],
  "escalation_criteria": "扣费争议、长期信号问题、携号转网受阻",
  "sla": {"response_time": "30秒内接听", "resolution_time": "业务办理即时生效"}
}
```

### Healthcare

```json
{
  "name": "在线问诊服务",
  "description": "互联网医疗平台，提供在线问诊、开药、健康咨询",
  "features": ["24小时问诊", "专家预约", "处方开具", "药品配送", "健康档案"],
  "common_issues": [
    "问诊等待时间长",
    "无法预约特定医生",
    "处方药配送延迟",
    "退款申请",
    "报告解读"
  ],
  "solutions": {
    "等待时间": "高峰期可能延长，可预约定时问诊",
    "预约问题": "专家号源有限，建议提前预约",
    "配送延迟": "联系物流，加急处理",
    "退款": "未问诊可全额退款，已问诊按规则处理",
    "报告解读": "可付费咨询专业医生"
  },
  "faq": [
    {"q": "能开处方药吗？", "a": "需医生问诊后开具，部分管制药品除外"},
    {"q": "医保能报销吗？", "a": "部分城市支持在线医保结算"}
  ],
  "escalation_criteria": "医疗纠纷、药品不良反应、紧急情况",
  "sla": {"response_time": "60秒内接听", "resolution_time": "医疗问题需转专业处理"}
}
```

### Travel

```json
{
  "name": "机票预订服务",
  "description": "在线机票预订平台，提供国内外航班预订、改签、退票",
  "features": ["比价搜索", "在线值机", "行程管理", "航班动态", "保险服务"],
  "common_issues": [
    "航班取消/延误",
    "退改签政策咨询",
    "行李额度查询",
    "无法在线值机",
    "发票开具"
  ],
  "solutions": {
    "航班变动": "提供改签或全额退款",
    "退改签": "根据票价规则执行，提供具体费用",
    "行李问题": "不同航司政策不同，可查询具体规定",
    "值机问题": "确认航班时间和证件信息",
    "发票": "行程结束后可申请电子行程单"
  },
  "faq": [
    {"q": "特价票能退吗？", "a": "根据票价规则，可能收取手续费"},
    {"q": "婴儿票怎么买？", "a": "需致电客服添加，出示出生证明"}
  ],
  "escalation_criteria": "航班取消赔偿、大额退款、投诉航司服务",
  "sla": {"response_time": "45秒内接听", "resolution_time": "退款7个工作日内处理"}
}
```

### Food Delivery

```json
{
  "name": "外卖配送服务",
  "description": "餐饮外卖平台，提供餐厅搜索、下单、配送服务",
  "features": ["准时送达", "超时赔付", "食品安全", "多种支付", "会员优惠"],
  "common_issues": [
    "订单超时/未送达",
    "餐品撒漏/错送",
    "食品质量问题",
    "退款申请",
    "配送员态度"
  ],
  "solutions": {
    "超时": "自动赔付优惠券，可申请退款",
    "撒漏错送": "拍照反馈，安排补送或退款",
    "质量问题": "保留证据，可全额退款",
    "退款": "根据订单状态处理，即时到账",
    "服务态度": "记录投诉，反馈配送站点"
  },
  "faq": [
    {"q": "超时多久可以退款？", "a": "超过预计时间30分钟可申请"},
    {"q": "餐品不合口味能退吗？", "a": "口味问题不支持退款，质量问题可退"}
  ],
  "escalation_criteria": "食品安全事故、多次配送失败、恶意投诉",
  "sla": {"response_time": "20秒内接听", "resolution_time": "退款即时处理"}
}
```

---

## Customer Persona Templates

### By Difficulty Level

#### Easy - 平和型客户

**冷静专业人士 (Calm Professional)**
```json
{
  "name": "黄玲",
  "type": "returning",
  "background": "IT经理，代表团队报告问题，已做好详细记录",
  "issue_type": "系统bug报告",
  "emotional_state": "calm",
  "communication_style": "technical",
  "expectations": "专业确认、明确时间线、后续跟进",
  "difficulty": "easy",
  "special_needs": "偏好邮件跟进并提供工单号"
}
```

**好奇新手 (Curious First-Timer)**
```json
{
  "name": "刘小明",
  "type": "new",
  "background": "研究人员，考虑购买，想了解详细信息",
  "issue_type": "售前咨询",
  "emotional_state": "neutral",
  "communication_style": "verbose",
  "expectations": "详尽解答所有问题，不希望被推销",
  "difficulty": "easy",
  "special_needs": "无"
}
```

#### Medium - 需耐心型客户

**困惑的老年用户 (Confused Senior)**
```json
{
  "name": "王阿姨",
  "type": "returning",
  "background": "65岁，老客户，不太懂技术",
  "issue_type": "使用问题 - 不会用新功能",
  "emotional_state": "confused",
  "communication_style": "non-technical",
  "expectations": "耐心的分步指导，不要居高临下",
  "difficulty": "medium",
  "special_needs": "需要放慢节奏、使用简单语言、可能需要重复说明"
}
```

**忙碌的多任务者 (Busy Multitasker)**
```json
{
  "name": "孙磊",
  "type": "returning",
  "background": "忙碌的职场人，边打电话边做其他事",
  "issue_type": "账单问题 - 扣费不对",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "快速解决，等太久可能挂断",
  "difficulty": "medium",
  "special_needs": "需要简洁沟通，可能会打断"
}
```

**技术用户 (Technical User)**
```json
{
  "name": "张伟",
  "type": "returning",
  "background": "软件开发者，使用产品6个月，对最近更新不满",
  "issue_type": "技术问题 - 更新后软件故障",
  "emotional_state": "frustrated",
  "communication_style": "technical",
  "expectations": "快速解决，技术层面的解释",
  "difficulty": "medium",
  "special_needs": "无"
}
```

#### Hard - 高难度客户

**愤怒的首次购买者 (Angry First-Timer)**
```json
{
  "name": "李明",
  "type": "new",
  "background": "第一次购买就收到次品，邮件投诉没人理",
  "issue_type": "产品质量 - 收到次品",
  "emotional_state": "angry",
  "communication_style": "verbose",
  "expectations": "立即换货或退款，承认服务失误",
  "difficulty": "hard",
  "special_needs": "无"
}
```

**反复投诉者 (Repeat Complainer)**
```json
{
  "name": "赵杰",
  "type": "returning",
  "background": "同一问题打过3次电话，每次都没彻底解决",
  "issue_type": "反复出现的问题",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "彻底解决、升级到主管、考虑补偿",
  "difficulty": "hard",
  "special_needs": "需要承认之前的处理不到位"
}
```

**VIP高管 (VIP Executive)**
```json
{
  "name": "陈总",
  "type": "vip",
  "background": "大客户公司CEO，高级会员，时间紧迫的问题",
  "issue_type": "服务中断 - 影响业务运营",
  "emotional_state": "frustrated",
  "communication_style": "brief",
  "expectations": "必要时立即升级，快速解决，直接沟通",
  "difficulty": "hard",
  "special_needs": "期望优先处理，必要时联系决策者"
}
```

---

## Operator Templates by Methodology

> **语言风格提示**：以下模板中的话术均为电话口语风格。生成 mock 数据时，所有 greeting、empathy_phrases、objection_handling 等文案必须保持口语化，避免书面翻译腔。参考 SKILL.md 中"语言风格"部分的详细规范。

### HEAR Method

```json
{
  "name": "HEAR方法",
  "methodology": "HEAR",
  "greeting": "您好，感谢您致电客服中心。我是[姓名]，请问有什么可以帮您？",
  "discovery_questions": [
    "能详细描述一下您遇到的问题吗？",
    "这个问题是什么时候开始出现的？",
    "您之前有尝试过什么解决方法吗？"
  ],
  "empathy_phrases": [
    "完全理解您",
    "这种情况确实体验不好",
    "换我碰到这事儿肯定也着急"
  ],
  "resolution_steps": [
    "确认问题：复述客户问题确保理解正确",
    "提供方案：给出1-2个解决选项",
    "执行：获得客户同意后立即处理",
    "确认：处理完成后确认客户满意"
  ],
  "objection_handling": {
    "要求退款": "理解您的想法。我先帮您看看能不能解决，实在不行咱们再说退款的事，您看行吗？",
    "要求主管": "可以的，我帮您转。不过您先跟我说一下具体情况，这样转过去处理也快一些。",
    "威胁差评": "您的反馈我们很重视。您给我个机会，我帮您把这事儿解决了。"
  },
  "closing_technique": "好的，那还有别的需要帮忙的吗？没有的话祝您生活愉快！",
  "follow_up": "重要问题24小时内电话回访确认"
}
```

### LAST Method

```json
{
  "name": "LAST方法",
  "methodology": "LAST",
  "greeting": "您好，欢迎致电[公司名称]，我是[姓名]，今天我能为您做些什么？",
  "discovery_questions": [
    "请问您遇到了什么问题？",
    "方便告诉我订单号/账号吗？",
    "这个问题对您造成了什么影响？"
  ],
  "empathy_phrases": [
    "这事儿确实是我们的问题，抱歉啊",
    "理解，碰到这种情况肯定闹心",
    "谢谢您跟我们说这个"
  ],
  "resolution_steps": [
    "倾听：让客户完整表达，不打断",
    "致歉：真诚道歉，承担责任",
    "解决：提供明确的解决方案",
    "感谢：感谢客户的反馈和耐心"
  ],
  "objection_handling": {
    "不满意方案": "理解，这个方案可能不是最好的。我再看看还有没有别的办法。",
    "时间紧迫": "好的，您时间紧我理解，我尽快帮您处理。",
    "质疑能力": "您放心，这个问题我一定帮您跟到底。需要的话我请专业团队一起来处理。"
  },
  "closing_technique": "好的，谢谢您来电。后面有问题随时联系我们，祝您一切顺利！",
  "follow_up": "发送满意度调查短信"
}
```

### LEARN Method

```json
{
  "name": "LEARN方法",
  "methodology": "LEARN",
  "greeting": "您好，[公司名称]客服，我是[姓名]。请问有什么可以帮您的？",
  "discovery_questions": [
    "请问能详细说一下发生了什么吗？",
    "这个问题最早是什么时候出现的？",
    "您希望我们如何帮您解决这个问题？",
    "除了这个问题，还有其他困扰您的地方吗？"
  ],
  "empathy_phrases": [
    "您说的这个情况我了解了，确实得重视",
    "换位想想，碰到这种事确实不放心",
    "谢谢您说得这么详细，这样我好帮您处理"
  ],
  "resolution_steps": [
    "倾听：全神贯注听客户讲述",
    "共情：表达理解和关心",
    "询问：通过提问确认细节",
    "解决：采取行动解决问题",
    "通知：确认问题已解决并跟进"
  ],
  "objection_handling": {
    "不信任": "理解您的顾虑。我跟您说一下我们的处理流程，您心里也有个数。",
    "比较竞品": "谢谢您说这个。我们也一直在改进。今天先帮您把眼前的问题解决了。",
    "情绪激动": "您别着急，我理解。您给我一点时间，我一定帮您处理好。"
  },
  "closing_technique": "好的，我已经帮您[具体处理内容]了。还有别的需要帮忙的吗？谢谢您来电，祝您今天愉快！",
  "follow_up": "48小时内邮件确认处理结果，一周后电话回访"
}
```
