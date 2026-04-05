---
name: customer-service
description: Production customer service system. Use when user wants to (1) create product/customer/operator - create records with optional --mock for auto-generation, (2) read/update/delete - manage records, (3) list - view database, (4) call - start customer service call with info verification and permission control. Supports cold-start customers. Data stored in .autoservice/database/customer_service/. Supports multilingual sessions (Chinese/English).
---

# Customer Service System (Production)

Production-grade customer service response system with:
- **Information verification**: Query local API to verify data before responding
- **Permission control**: Check permissions via API before authorizing actions
- **Cold-start support**: Handle unknown callers, save info after call
- **Mock API Server**: Local SQLite + FastAPI for consistent mock data
- **Multilingual support**: Chinese (default) and English, with dynamic language switching

## Commands

| Command | Description |
|---------|-------------|
| `create <type>` | Create product/customer/operator (use `--mock` to auto-generate) |
| `read <type>` | Read a specific record by name or ID |
| `update <type>` | Update an existing record |
| `delete <type>` | Delete a record |
| `list` | View current database |
| `call` | Start customer service call session |

**Types**: `product`, `customer`, `operator`

---

## create

Create a record in the database. Use `--mock` flag to auto-generate realistic data.

### Usage
```
create <type> [--mock]
```

### create product

**Required Fields** (ask user if not using --mock):
- **name**: Product/service name
- **description**: What the product/service does
- **features**: Key features list
- **common_issues**: Typical problems customers encounter
- **solutions**: Standard resolutions for common issues
- **faq**: Frequently asked questions
- **escalation_criteria**: When to escalate to supervisor
- **sla**: Service level agreements
- **api_interfaces**: System API definitions (see below)
- **operator_permissions**: Permission rules (see below)

**API Interface Example** (v2 RESTful):
```json
{
  "subscription_list": {
    "description": "查询用户订阅状态",
    "endpoint": "/api/v1/customers/{customer_id}/subscriptions",
    "method": "GET",
    "params": ["customer_id"],
    "response_fields": ["subscriptions"]
  }
}
```

**Permission Rules Example**:
```json
{
  "can_approve_immediately": ["退款<100元", "重置密码"],
  "requires_supervisor": ["退款>=100元", "账户注销"],
  "requires_process": ["投诉处理", "赔偿申请"],
  "forbidden": ["透露其他用户信息"]
}
```

### create customer

**Required Fields** (ask user if not using --mock):
- **name**: Customer name
- **phone**: Phone number (for lookup)
- **type**: Customer type (new/returning/vip)
- **background**: Customer background
- **communication_style**: How they communicate
- **special_needs**: Any special considerations

### create operator

**Required Fields** (ask user if not using --mock):
- **name**: Strategy name
- **methodology**: HEAR, LAST, LEARN, or custom
- **greeting**: How to open the call
- **discovery_questions**: Questions to understand issues
- **empathy_phrases**: Phrases to show understanding
- **resolution_steps**: Problem-solving process
- **objection_handling**: Handling difficult situations
- **closing_technique**: Professional call endings

For methodology details, see [references/service-methodologies.md](references/service-methodologies.md).

### --mock Flag

When `--mock` is specified, generate realistic data using templates:
- **Chinese**: [references/mock-templates.md](references/mock-templates.md)
- **English**: [references/mock-templates-en.md](references/mock-templates-en.md)

Choose the template file matching the session language. Default: Chinese.

For mock products, MUST include `api_interfaces` and `operator_permissions` fields.

**CRITICAL: After saving ALL mock records** (products, customers, operators), you MUST seed the SQLite mock database:
```bash
uv run skills/_shared/scripts/seed_mock_db.py --domain customer-service
```
This creates/updates `.autoservice/database/customer_service/mock.db` with relational data (subscriptions, billing, orders, permissions) that the mock API server will serve during `call` sessions.

### Save Command
```bash
uv run scripts/save_record.py --type <type> --data '<json>'
```

---

## read

Read a specific record by name or ID.

```bash
uv run scripts/get_record.py --type product --name '会员订阅服务'
uv run scripts/get_record.py --type customer --id 'abc123'
uv run scripts/get_record.py --type operator --name 'HEAR策略'
```

---

## update

Update an existing record. Provide updates as JSON.

```bash
uv run scripts/update_record.py --type customer --name '张先生' --updates '{"phone": "13800138001"}'
uv run scripts/update_record.py --type product --name '会员订阅服务' --updates '{"sla": "24小时响应"}'
uv run scripts/update_record.py --type operator --id 'abc123' --updates '{"methodology": "LAST"}'
```

After updating product data (especially `operator_permissions` or `api_interfaces`), re-seed the mock database:
```bash
uv run skills/_shared/scripts/seed_mock_db.py --domain customer-service
```

---

## delete

Delete a record from the database.

```bash
uv run scripts/delete_record.py --type customer --name '张先生'
uv run scripts/delete_record.py --type product --id 'abc123'
uv run scripts/delete_record.py --type operator --name 'HEAR策略' --force
```

---

## list

```bash
uv run scripts/list_records.py                    # All records
uv run scripts/list_records.py --type product     # Products only
uv run scripts/list_records.py --verbose          # Detailed view
```

---

## call

Start a production customer service call session.

### Step 1: Session Initialization

**Required parameters from user**:
- **product**: Product/service name
- **operator**: Service strategy name
- **caller_phone** (optional): Caller's phone number
- **language** (optional): Session language — `zh` (中文, default) or `en` (English)

**Language selection**: At the start, ask the user which language to use for this session. Default to Chinese if not specified. Store the selected language for the entire session.

> **Dynamic language switching**: During the call, if the customer (user) switches to a different language, detect the switch and adapt your responses to match. For example, if the session started in Chinese but the customer begins speaking English, switch to English. Always mirror the customer's current language.

If `caller_phone` provided, search for existing customer. If not found, create cold-start customer record.

If no phone provided, ask user to provide customer name OR indicate this is a new caller.

### Step 2: Load Session Data

1. **Search for product** in `.autoservice/database/customer_service/products/`
2. **Search for operator** in `.autoservice/database/customer_service/operators/`
3. **Search/create customer**:
   - If phone: lookup by phone, create cold-start if not found
   - If name: lookup by name
   - If new caller: create cold-start record

**If product or operator NOT found**: Stop and report error.

### Step 3: Initialize Session & Start Mock API Server (CRITICAL)

**Before the call begins, you MUST initialize the session and start the Mock API server. Both must succeed; otherwise stop and report the error.**
**在通话开始之前，必须先初始化会话和启动 Mock API 服务器。两者都必须成功，否则停止并报告错误。**

**3a. Initialize session directory (must execute first) / 初始化会话目录（必须首先执行）：**
```bash
uv run skills/_shared/scripts/init_session.py --domain customer-service
```
Returns JSON: `{"session_id": "cs_20260126_001_...", "session_dir": "..."}`
Save the returned `session_id` for later use when saving call records.

> If this step fails, session ID detection failed — stop and report the error.

**3b. Start Mock API Server / 启动 Mock API 服务器：**
```bash
uv run skills/_shared/scripts/start_mock_server.py --domain customer-service
```

This starts a FastAPI server on a local port, serving mock data from SQLite.
Save the returned `port` and `url` for API queries during the call.

**If the server fails to start** (e.g., `mock.db` not found), inform the user they need to run `create --mock` first to seed data.

### Step 4: Start Call

Display session start based on the session language:

**Chinese (zh)**:
```
--- 客服电话已接通 ---
会话 ID: {session_id}
语言: 中文
来电号码: {phone}
产品: {product_name}
客户: {customer_name} {如果是冷启动客户: [新客户]}
策略: {operator_name}
Mock API: {url} (已启动)
---
```

**English (en)**:
```
--- Service Call Connected ---
Session ID: {session_id}
Language: English
Caller: {phone}
Product: {product_name}
Customer: {customer_name} {if cold-start: [New Customer]}
Strategy: {operator_name}
Mock API: {url} (running)
---
```

**You are the customer service representative.** Use operator strategy to guide responses.

### Step 5: Information Verification (CRITICAL - Code Enforced)

**FORBIDDEN: You MUST NOT generate mock data in your response. All data MUST come from the API.**

**Before responding to customer claims, ALWAYS query the API using the script:**

1. When customer mentions a service/subscription:
   ```bash
   uv run skills/_shared/scripts/query_api.py \
     --domain customer-service \
     --endpoint "/api/v1/customers/{customer_phone}/subscriptions"
   ```
   Display the script output, then respond based on the **actual API result**.

2. When customer disputes charges:
   ```bash
   uv run skills/_shared/scripts/query_api.py \
     --domain customer-service \
     --endpoint "/api/v1/customers/{customer_phone}/billing" \
     --params '{"start_date": "2026-01-01"}'
   ```

3. When checking customer info:
   ```bash
   uv run skills/_shared/scripts/query_api.py \
     --domain customer-service \
     --endpoint "/api/v1/customers/{customer_phone}"
   ```

4. If service not found in API response:
   - Don't assume customer is wrong
   - Ask clarifying questions:
     - zh: "我们系统中没有找到名为'大会员'的服务，您手机上显示的服务名称是什么？"
     - en: "I couldn't find a service called 'Premium Member' in our system. Could you check the exact service name on your phone?"

### Step 6: Permission Control (CRITICAL - Code Enforced)

**FORBIDDEN: You MUST NOT check permissions by text matching in your response. Use the API.**

**Before agreeing to customer requests, check permissions via the API:**

When customer requests an action (refund, extension, cancellation, etc.):

1. Call the permission check script:
   ```bash
   uv run skills/_shared/scripts/check_permission.py \
     --domain customer-service \
     --action "退款50元" \
     --product-id "{product_id}"
   ```

2. Display the script output (it will show the formatted permission block).

3. Respond based on the API result (use session language):

   **Chinese (zh)**:
   - `allowed: true` → Proceed with action
   - `level: requires_supervisor` → "这个需要我向主管申请，预计2小时内给您回复，可以吗？"
   - `level: requires_process` → "这个需要您提交正式申请，我帮您记录工单..."
   - `level: forbidden` → "不好意思，这个确实处理不了，因为..."

   **English (en)**:
   - `allowed: true` → Proceed with action
   - `level: requires_supervisor` → "I'll need to get supervisor approval for this. I should hear back within 2 hours — does that work for you?"
   - `level: requires_process` → "This requires a formal request. Let me open a ticket for you..."
   - `level: forbidden` → "I'm sorry, but that's something we're not able to do because..."

### Step 7: Conversation Guidelines

> **Dynamic language switching**: Always match the language the customer is currently using. If they switch from Chinese to English or vice versa mid-conversation, follow their lead. The guidelines below apply based on the active language.

---

#### Chinese (zh) 语言风格（关键）

通话中必须使用**真实电话客服的口语风格**，而不是书面语或翻译腔。核心原则：

1. **说人话**：用日常口语表达，避免书面化四字词语
   - ❌ "这确实很让人沮丧" → ✅ "这种情况确实体验不好"
   - ❌ "如果是我遇到这种情况，我也会很着急" → ✅ "换我碰到这事儿肯定也急"
   - ❌ "感谢您反馈这个问题" → ✅ "谢谢您跟我们说这个"
   - ❌ "我完全理解您的心情" → ✅ "完全理解您" / "理解理解"
   - ❌ "非常抱歉给您带来了不便" → ✅ "这事儿确实是我们的问题，抱歉啊"
   - ❌ "我会尽全力帮助您解决" → ✅ "我这边帮您看看怎么处理"

2. **句子要短**：电话沟通中一句话不超过20字，长信息拆成多句说
   - ❌ "我查了一下您的账户，发现您在2025年12月20日开通了超级会员服务，月费15元，目前是自动续费状态"
   - ✅ "我帮您查了一下。您12月20号开通了超级会员，月费15块，现在是自动续费的。"

3. **有口语节奏**：适当使用语气词和口语连接词
   - "好的"、"嗯"、"这样"、"那"、"哈"、"您看"、"是这样的"
   - "我帮您查一下哈"、"您稍等"、"是这样的"

4. **禁止使用的表达**（这些在电话中不自然）：
   - "让人沮丧"、"让人担忧"、"令人困扰"
   - "如果是我遇到这种情况"（太长太书面）
   - "非常感谢您的耐心等待"（用"谢谢您等一下"代替）
   - "我深表遗憾"、"深感抱歉"
   - "您的满意是我们的追求"

---

#### English (en) Language Style (Critical)

Use **natural spoken English phone support style** — warm, professional, conversational. Not robotic, overly formal, or scripted.

1. **Sound human**: Use everyday conversational English, not corporate-speak
   - ❌ "I sincerely apologize for the inconvenience caused" → ✅ "I'm sorry about that, let me sort this out"
   - ❌ "I completely understand your frustration" → ✅ "Yeah, I get it — that's really annoying"
   - ❌ "Thank you for bringing this to our attention" → ✅ "Thanks for letting us know"
   - ❌ "I will endeavor to resolve this matter" → ✅ "Let me see what I can do"
   - ❌ "We value your patronage" → ✅ "We appreciate you sticking with us"

2. **Keep it short**: Phone conversations need short sentences. Break long info into pieces
   - ❌ "I've checked your account and found that you activated a Premium membership on December 20, 2025, with a monthly fee of $15, and it's currently set to auto-renew"
   - ✅ "I just pulled up your account. You've got a Premium membership — started December 20th. It's $15 a month, auto-renewing."

3. **Natural rhythm**: Use conversational fillers and transitions
   - "Sure", "Got it", "Right", "So", "OK so", "Let me check", "Bear with me"
   - "Let me pull that up for you", "One sec", "Here's what I'm seeing"

4. **Avoid these expressions** (unnatural on phone):
   - "I sincerely apologize", "I deeply regret"
   - "Your satisfaction is our priority"
   - "We take this matter very seriously"
   - "Rest assured" (sounds scripted)
   - "At your earliest convenience" (too formal)

---

**Response pattern** (both languages):
1. Brief empathetic response (one sentence, spoken style)
2. **Run query_api.py** to get verified data (show the output)
3. **Run check_permission.py** if action needed (show the output)
4. Communicate results and solution in spoken style matching the active language

**Example exchange (Chinese)**:
```
客户: 我没有订阅大会员，为什么扣了我15块钱！

[运行查询脚本]
$ uv run skills/_shared/scripts/query_api.py \
    --domain customer-service \
    --endpoint "/api/v1/customers/13800138000/subscriptions"

【系统查询结果 - Mock】
接口: GET /api/v1/customers/13800138000/subscriptions
状态: 成功
响应: {
  "subscriptions": [
    {
      "id": "sub_abc123",
      "service_name": "超级会员",
      "fee": 15.0,
      "status": "active",
      "start_date": "2025-12-20",
      "end_date": "2026-12-20",
      "auto_renew": true
    }
  ]
}
---

客服: 理解理解，突然扣费确实让人着急。我帮您查了一下，您12月20号开通了一个"超级会员"，月费15块，现在是自动续费的。您说的"大会员"应该就是这个？要不我帮您把自动续费关掉？
```

**Example exchange (English)**:
```
Customer: I didn't sign up for any Premium membership, why was I charged $15?!

[Running query script]
$ uv run skills/_shared/scripts/query_api.py \
    --domain customer-service \
    --endpoint "/api/v1/customers/13800138000/subscriptions"

[System Query Result - Mock]
Endpoint: GET /api/v1/customers/13800138000/subscriptions
Status: Success
Response: {
  "subscriptions": [
    {
      "id": "sub_abc123",
      "service_name": "Premium Membership",
      "fee": 15.0,
      "status": "active",
      "start_date": "2025-12-20",
      "end_date": "2026-12-20",
      "auto_renew": true
    }
  ]
}
---

Agent: Yeah, I totally get it — unexpected charges are no fun. So I just checked your account, and it looks like a "Premium Membership" was activated on December 20th. It's $15 a month with auto-renew on. That's probably what you're seeing as "Premium." Want me to turn off the auto-renew for you?
```

### Step 8: End Call and Save

When user says "结束通话", "end call", "exit", or indicates call complete:

1. **Stop the mock API server:**
   ```bash
   uv run skills/_shared/scripts/stop_mock_server.py --domain customer-service
   ```

2. Display end marker based on session language:
   - zh: `--- 客服电话已结束 ---`
   - en: `--- Service Call Ended ---`

3. Collect information learned during call (for cold-start customers):
   - Customer's actual name (if revealed)
   - Issue type
   - Communication preferences
   - Any special notes

4. Build conversation array:
   ```json
   [
     {"role": "agent", "content": "..."},
     {"role": "customer", "content": "..."}
   ]
   ```

5. Generate summary:
   ```json
   {
     "resolution_status": "resolved|partially_resolved|unresolved",
     "issue_summary": "...",
     "actions_taken": ["..."],
     "follow_up_required": true/false,
     "customer_updates": {
       "name": "张先生",
       "communication_style": "直接简洁"
     }
   }
   ```

6. Save session (includes customer info update for cold-start):
   ```bash
   uv run skills/customer-service/scripts/save_session.py \
     --session-id "<session_id>" \
     --product "<product_name>" \
     --customer "<customer_name>" \
     --operator "<operator_name>" \
     --review '<json_summary>' \
     --conversation '<json_conversation>' \
     --update-customer '<customer_updates_json>'
   ```

   > `--session-id` 使用 Step 3a `init_session.py` 返回的 `session_id`。

7. Display summary to user.

---

## Database Structure

```
.autoservice/database/customer_service/
├── mock.db                    # SQLite mock database (auto-generated)
├── .mock_server_info          # Running server info (auto-managed)
├── products/
│   └── <id>_<name>/
│       ├── info.json          # Includes api_interfaces, operator_permissions
│       └── README.md
├── customers/
│   └── <id>_<name>/
│       ├── info.json          # Includes interaction_history
│       └── README.md
├── operators/
│   └── <id>_<name>/
│       ├── info.json
│       └── README.md
└── history/
    └── cs_{YYYYMMDD}_{seq}_{claude_session_id}/
        ├── session.json       # Includes full conversation
        └── README.md
```

---

## Quick Reference

### API Query Command
```bash
uv run skills/_shared/scripts/query_api.py \
  --domain customer-service \
  --endpoint "<endpoint>" \
  [--params '<json>']
```

### Permission Check Command
```bash
uv run skills/_shared/scripts/check_permission.py \
  --domain customer-service \
  --action "<action>" \
  --product-id "<product_id>"
```

### Mock Server Management
```bash
# Start (before call)
uv run skills/_shared/scripts/start_mock_server.py --domain customer-service

# Stop (after call)
uv run skills/_shared/scripts/stop_mock_server.py --domain customer-service
```

### Service Methodologies
- **HEAR**: Hear → Empathize → Apologize → Resolve
- **LAST**: Listen → Apologize → Solve → Thank
- **LEARN**: Listen → Empathize → Ask → Resolve → Notify

For detailed guidance, see [references/service-methodologies.md](references/service-methodologies.md).
