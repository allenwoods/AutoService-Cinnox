# /discussion 指令设计文档

> 日期: 2026-04-12
> 作者: Allen Woods
> 状态: Draft

## 1. 目标

在飞书 IM 中新增 `/discussion` 指令，支持子命令分发，能够动态映射到已有的 Claude Code skill。用户在飞书群聊中发送 `/discussion create` 等子命令时，系统自动切换到对应 runtime_mode 并调用对应 skill。

## 2. 现有架构分析

### 2.1 当前指令分发流程

```
飞书用户消息
  ↓
channel_server.py: on_message()
  ↓ (文本匹配 /improve, /production 等)
  ├─ 管理群: _handle_admin_message() → /help, /status, /inject, /explain
  └─ 普通群: mode switching → 设置 _chat_modes[chat_id]
       ↓
  channel_server.py: route_message()
       ↓
  channel.py: inject_message() → MCP notification
       ↓
  Claude Code: 读 channel-instructions.md → 按 runtime_mode 路由到 skill
```

### 2.2 现有模式与 skill 映射

| runtime_mode | business_mode | 调用的 Skill |
|---|---|---|
| production | sales | /cinnox-demo 或 /sales-demo |
| production | support | /customer-service |
| improve | * | /improve |
| explain | * | /explain |

### 2.3 现有子命令模式 (skill 内部)

以 `/evaluate` 为例:
- skill 自身在 SKILL.md 中声明 Command Routing 表
- Claude Code 根据 skill description 中的 trigger 条件匹配
- 子命令在 skill 内部解析 (pattern matching table)

## 3. 设计方案

### 3.1 核心思路

`/discussion` 不是一个独立 skill，而是一个**指令路由器**——在 channel_server.py 层面拦截 `/discussion <subcmd>` 消息，将其转换为对应的 runtime_mode + 附加 metadata，然后交给已有的 skill 处理。

这与 `/explain` 的实现模式一致: channel_server 拦截指令 → 构造特殊 message → route 到对应 instance。

### 3.2 子命令定义

| 子命令 | 映射的 runtime_mode | 映射的 Skill | 说明 |
|---|---|---|---|
| `/discussion create <topic>` | discussion | project-discussion-autoservice | 创建一个讨论主题，初始化讨论上下文 |
| `/discussion eval @<path>` | discussion | evaluate | 快捷入口：发起对文档的评审讨论 |
| `/discussion improve` | improve | improve | 快捷切换到改进模式 |
| `/discussion explain <query>` | explain | explain | 快捷切换到 explain 模式 |
| `/discussion status` | — | (内置) | 显示当前讨论状态/活跃主题 |
| `/discussion list` | — | (内置) | 列出所有讨论记录 |
| `/discussion help` | — | (内置) | 显示帮助信息 |

### 3.3 架构层次

```
┌─────────────────────────────────────────────────┐
│ Layer 1: channel_server.py (指令拦截与路由)       │
│   - 拦截 /discussion <subcmd> 消息               │
│   - 解析子命令 + 参数                             │
│   - 构造带 runtime_mode + discussion_meta 的 msg │
│   - 内置子命令 (status/list/help) 直接回复        │
└───────────────────────┬─────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: channel-instructions.md (路由规则)       │
│   - 新增 discussion mode 路由规则                 │
│   - 根据 discussion_meta.subcmd 分发到对应 skill  │
└───────────────────────┬─────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: 已有 Skills (执行层)                     │
│   - project-discussion-autoservice               │
│   - evaluate                                     │
│   - improve                                      │
│   - explain                                      │
└─────────────────────────────────────────────────┘
```

## 4. 详细设计

### 4.1 channel_server.py 改动

在 `on_message()` 的 mode switching 区域（当前 `/improve` 和 `/production` 之后），新增 `/discussion` 拦截:

```python
# --- /discussion command routing ---
elif text_stripped.startswith("/discussion"):
    parts = text.strip().split(None, 2)  # ["/discussion", subcmd, args?]
    subcmd = parts[1].lower() if len(parts) > 1 else "help"
    args = parts[2] if len(parts) > 2 else ""

    # 内置子命令：不进入 Claude Code，直接回复
    if subcmd == "help":
        threading.Thread(
            target=self._send_feishu_text,
            args=(chat_id, DISCUSSION_HELP_TEXT),
            daemon=True
        ).start()
        return
    
    if subcmd == "status":
        # 查询当前讨论状态（从 _discussion_state 读取）
        status = self._discussion_status(chat_id)
        threading.Thread(
            target=self._send_feishu_text,
            args=(chat_id, status),
            daemon=True
        ).start()
        return

    # 路由子命令：进入 Claude Code 处理
    self._chat_modes[chat_id] = "discussion"
    threading.Thread(
        target=self._send_reaction, args=(msg_id, "DONE"),
        daemon=True
    ).start()
    
    msg = {
        "type": "message",
        "text": text,  # 保留原始文本，让 skill 解析细节
        "chat_id": chat_id,
        "message_id": msg_id,
        "user": display_name,
        "user_id": sender_id,
        "runtime_mode": "discussion",
        "business_mode": "customer_service",
        "discussion_meta": {
            "subcmd": subcmd,
            "args": args,
        },
        "ts": ts,
    }
    loop.call_soon_threadsafe(queue.put_nowait, msg)
    return
```

### 4.2 channel-instructions.md 改动

在 `## Mode Routing` 下新增:

```markdown
### discussion mode
Route by `discussion_meta.subcmd`:
- **create** → use /project-discussion-autoservice skill. 
  The `discussion_meta.args` contains the topic. Create a new discussion context.
- **eval** → use /evaluate skill. 
  The `discussion_meta.args` contains the document path. Equivalent to `/evaluate @path`.
- **improve** → use /improve skill. Full permissions.
- **explain** → use /explain skill. 
  The `discussion_meta.args` contains the query.
- **list** → (handled by channel_server, should not reach here)

After any discussion subcommand completes, remain in discussion mode until user sends `/production`.
```

### 4.3 讨论状态管理

在 channel_server.py 中维护轻量级讨论状态:

```python
# 新增实例变量
self._discussion_state: dict[str, dict] = {}
# 结构: { chat_id: { "topic": str, "subcmd": str, "started_at": str, "user": str } }
```

`/discussion create <topic>` 时记录:
```python
self._discussion_state[chat_id] = {
    "topic": args,
    "subcmd": "create",
    "started_at": ts,
    "user": display_name,
}
```

`/discussion status` 时从 `_discussion_state[chat_id]` 读取并格式化返回。

### 4.4 子命令映射配置 (可选扩展)

为了支持未来动态添加子命令→skill 映射，可以用声明式配置:

```yaml
# .autoservice/discussion-commands.yaml
commands:
  create:
    skill: project-discussion-autoservice
    runtime_mode: discussion
    description: "创建讨论主题"
  eval:
    skill: evaluate
    runtime_mode: discussion
    description: "评审文档"
  improve:
    skill: improve
    runtime_mode: improve
    description: "改进模式"
  explain:
    skill: explain
    runtime_mode: explain
    description: "流程分析"
```

**当前阶段不实现此配置文件**，先硬编码在 channel_server.py 中。等子命令稳定后再抽取。

## 5. 管理群支持

管理群 (`admin_chat_id`) 中也支持 `/discussion`，需要在 `_handle_admin_message()` 中新增:

```python
if text.startswith("/discussion"):
    # 解析子命令，构造 msg 并 route
    # 复用与 on_message 相同的逻辑
    ...
```

建议抽取一个 `_parse_discussion_command(text, chat_id, msg_id, display_name, sender_id, ts)` 方法，供 `on_message()` 和 `_handle_admin_message()` 共用。

## 6. 消息流示例

### 用户发送 `/discussion create 客服流程优化`

```
1. on_message() 捕获文本 "/discussion create 客服流程优化"
2. 解析: subcmd="create", args="客服流程优化"
3. 设置 _chat_modes[chat_id] = "discussion"
4. 记录 _discussion_state[chat_id] = { topic: "客服流程优化", ... }
5. 构造 msg: runtime_mode="discussion", discussion_meta={subcmd:"create", args:"客服流程优化"}
6. route_message() → channel.py → inject_message() → MCP notification
7. Claude Code 读 channel-instructions.md → discussion mode → create → 触发 /project-discussion-autoservice
8. Skill 初始化讨论上下文，回复确认
```

### 用户发送 `/discussion eval docs/plans/xxx.md`

```
1. 解析: subcmd="eval", args="docs/plans/xxx.md"
2. 构造 msg: runtime_mode="discussion", discussion_meta={subcmd:"eval", args:"docs/plans/xxx.md"}
3. Claude Code → discussion mode → eval → 触发 /evaluate @docs/plans/xxx.md
4. evaluate skill 正常执行评审流程
```

## 7. 帮助文本

```
/discussion — 讨论指令

子命令:
  /discussion create <topic>      创建讨论主题
  /discussion eval @<path>        评审文档
  /discussion improve             切换到改进模式
  /discussion explain <query>     分析业务流程
  /discussion status              当前讨论状态
  /discussion list                讨论记录列表
  /discussion help                显示此帮助

示例:
  /discussion create 客服流程优化
  /discussion eval docs/plans/2026-04-09-three-layer-architecture.md
```

## 8. 实现计划

| 步骤 | 文件 | 改动 |
|---|---|---|
| 1 | `feishu/channel_server.py` | 新增 `/discussion` 拦截逻辑、`_discussion_state`、`_parse_discussion_command()` |
| 2 | `feishu/channel-instructions.md` | 新增 discussion mode 路由规则 |
| 3 | `feishu/channel_server.py` | 更新 `help_text()` 加入 `/discussion` |
| 4 | 测试 | 在管理群中测试各子命令 |

## 9. 开放问题

1. **讨论持久化**: 当前 `_discussion_state` 是内存态，重启丢失。是否需要持久化到 `.autoservice/database/` ?
2. **多主题并发**: 同一个 chat_id 是否允许同时有多个讨论主题？当前设计为单主题覆盖。
3. **退出讨论**: 是否需要 `/discussion end` 子命令，还是沿用 `/production` 切回？
4. **权限控制**: `/discussion` 是否需要限制为管理群或特定用户？当前设计为所有群可用。
