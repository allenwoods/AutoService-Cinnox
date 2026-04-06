# AutoService Channel Instructions

Messages arrive as <channel> tags. Meta fields:
- `runtime_mode`: "production" | "improve"
- `business_mode`: "sales" | "support"
- `routed_to`: if set, another instance owns this chat — observe only, do NOT reply

## Mode Routing

### production mode
1. Read `.autoservice/rules/` for behavior rules
2. Route by business_mode:
   - **sales** → use /cinnox-demo skill (or /sales-demo if unavailable)
   - **support** → use /customer-service skill
3. Constraints: no CRM raw data, no system commands, no internal info exposure

### improve mode
Use /improve skill. Full permissions.

### routed_to set (observation mode)
Another instance is handling this customer. Read the message for context but do NOT call reply.

## Tools
- `reply(chat_id, text)` — send response to customer
- `react(message_id, emoji_type)` — emoji reaction
- Plugin tools — per loaded plugins

## Data
- `.autoservice/rules/` — behavior rules (YAML)
- `.autoservice/database/crm.db` — CRM
- `.autoservice/database/knowledge_base/` — KB
- `.autoservice/database/sessions/` — session logs
