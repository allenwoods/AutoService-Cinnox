"""
WebSocket handlers — generic /ws and authenticated /ws/chat.

/ws       — raw Claude Agent stream (debug terminal)
/ws/chat  — authenticated chat with dual backend routing (API vs SDK),
             escalation detection, human agent handoff, session persistence
"""

import asyncio
import json
import re
import time
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from web import auth
from web import claude_backend as backend
from web import session_persistence as sessions
from web import system_prompts as prompts
from web.plugin_kb import presearch_kb


# ── Configuration (set by app.py) ─────────────────────────────────────────
DEMO_BACKEND: str = "sdk"


def configure(demo_backend: str) -> None:
    global DEMO_BACKEND
    DEMO_BACKEND = demo_backend


# ── Generic WebSocket helper ─────────────────────────────────────────────
def _serialize(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        return {"_type": obj.__class__.__name__, **{k: _serialize(v) for k, v in vars(obj).items()}}
    return str(obj)


async def ws_generic(websocket: WebSocket):
    """Generic /ws handler — raw Claude Agent stream for debug."""
    from autoservice.claude import query as _agent_query
    from autoservice.logger import ConversationLogger

    await websocket.accept()
    logger = ConversationLogger(str(backend.ROOT))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                user_input = json.loads(data).get("content", "").strip()
            except json.JSONDecodeError:
                user_input = data.strip()
            if not user_input:
                continue
            logger.log_user_input(user_input)
            try:
                async for response in _agent_query(user_input, cwd=str(backend.ROOT)):
                    await websocket.send_json({"type": "chunk", "content": _serialize(response)})
                    logger.log_message(response)
                await websocket.send_json({"type": "done"})
            except Exception as e:
                await websocket.send_json({"type": "error", "content": str(e)})
    except WebSocketDisconnect:
        pass


# ── Authenticated chat WebSocket ──────────────────────────────────────────
async def ws_chat(websocket: WebSocket):
    """Authenticated /ws/chat handler — dual backend (API/SDK), escalation, session persistence."""
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
    from claude_agent_sdk import query as _sdk_query
    from claude_agent_sdk.types import (
        AssistantMessage,
        ResultMessage,
        StreamEvent,
        TextBlock,
        ToolUseBlock,
        UserMessage,
    )

    await websocket.accept()

    # Step 1: token authentication
    try:
        auth_data = json.loads(await websocket.receive_text())
    except (json.JSONDecodeError, WebSocketDisconnect):
        await websocket.close(code=1008)
        return

    ws_token = auth_data.get("token", "")
    if not auth.valid_token(ws_token):
        await websocket.send_json({"type": "error", "content": "Invalid or expired session. Please log in again."})
        await websocket.close(code=1008)
        return

    access_code = auth.get_code_for_token(ws_token)

    mode = auth_data.get("mode", "sales")
    if mode not in ("sales", "service"):
        mode = "sales"

    # Step 2: init web session state
    web_session_id              = sessions.new_web_session_id()
    conversation: list[dict]    = []
    api_messages: list[dict]    = []
    sdk_session_id: str | None  = None
    session_data: dict          = {
        "session_id":    web_session_id,
        "created_at":    datetime.now().isoformat(),
        "mode":          mode,
        "access_code":   access_code,
        "customer_type": "unknown",
        "resolution":    "active",
        "turn_count":    0,
        "conversation":  conversation,
        "gate_cleared":  False,
    }

    await websocket.send_json({"type": "ready", "web_session_id": web_session_id, "mode": mode})

    # Step 2b: persistent SDK client (process stays alive across turns)
    _sdk_client: ClaudeSDKClient | None = None
    _sdk_queue: asyncio.Queue = asyncio.Queue()
    _sdk_receiver_task: asyncio.Task | None = None
    _sdk_prev_model: str | None = None

    async def _sdk_connect(sd: dict):
        nonlocal _sdk_client, _sdk_receiver_task, _sdk_prev_model
        model = backend.pick_model(sd)
        sys_prompt = prompts.make_system_prompt(mode, web_session_id, sd)
        opts = ClaudeAgentOptions(
            cwd=str(backend.ROOT),
            system_prompt=sys_prompt,
            setting_sources=[],
            plugins=[],
            permission_mode="bypassPermissions",
            model=model,
            allowed_tools=["Bash"],
            max_turns=12,
            include_partial_messages=True,
            cli_path=backend.get_claude_cli(),
            env=backend.proxy_env(),
        )
        _sdk_client = ClaudeSDKClient(options=opts)
        await _sdk_client.connect()
        _sdk_prev_model = model

        async def _receiver():
            try:
                async for msg in _sdk_client.receive_messages():
                    await _sdk_queue.put(msg)
            except Exception as exc:
                await _sdk_queue.put(exc)
        _sdk_receiver_task = asyncio.create_task(_receiver())
        print(f"[sdk-client] connected (model={model})", flush=True)

    async def _sdk_ensure(sd: dict, user_text: str = ""):
        nonlocal _sdk_prev_model
        if _sdk_client is None:
            await _sdk_connect(sd)
            return
        model = backend.pick_model(sd, user_text)
        if model != _sdk_prev_model:
            await _sdk_client.set_model(model)
            _sdk_prev_model = model
            print(f"[sdk-client] model switched -> {model}", flush=True)

    async def _sdk_turn(prompt: str, sd: dict):
        await _sdk_ensure(sd, prompt)
        while not _sdk_queue.empty():
            try:
                _sdk_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        await _sdk_client.query(prompt)
        while True:
            msg = await asyncio.wait_for(_sdk_queue.get(), timeout=120)
            if isinstance(msg, Exception):
                raise msg
            yield msg
            if isinstance(msg, ResultMessage):
                return

    async def _sdk_disconnect():
        nonlocal _sdk_client, _sdk_receiver_task
        if _sdk_receiver_task and not _sdk_receiver_task.done():
            _sdk_receiver_task.cancel()
            try:
                await _sdk_receiver_task
            except (asyncio.CancelledError, Exception):
                pass
        if _sdk_client:
            try:
                await _sdk_client.disconnect()
            except Exception:
                pass
        _sdk_client = None
        _sdk_receiver_task = None

    # Step 3: conversation loop
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") == "end_session":
                session_data["resolution"] = "resolved"
                if session_data.get("customer_type", "unknown") == "unknown":
                    inferred_type, _ = sessions.infer_session_meta(conversation)
                    if inferred_type != "unknown":
                        session_data["customer_type"] = inferred_type
                sessions.save_session_data(web_session_id, session_data)
                await _sdk_disconnect()
                await websocket.send_json({"type": "session_ended"})
                break

            # Resume a previous session
            if msg.get("type") == "resume_session":
                target_id = msg.get("web_session_id", "")
                old = sessions.load_session_data(target_id, code_hint=access_code)
                can = old and (old.get("conversation") or old.get("claude_session_id"))
                if can:
                    web_session_id = target_id
                    conversation   = old.get("conversation", [])
                    api_messages   = backend.conversation_to_api_messages(conversation)
                    sdk_session_id = old.get("claude_session_id")
                    session_data   = old
                    mode           = old.get("mode", "sales")
                    await websocket.send_json({
                        "type":               "session_resumed",
                        "web_session_id":     target_id,
                        "mode":               mode,
                        "history":            conversation,
                        "turn_count":         old.get("turn_count", 0),
                        "customer_type":      old.get("customer_type", "unknown"),
                        "resolution":         old.get("resolution", "active"),
                        "human_agent_active": old.get("human_agent_active", False),
                        "human_agent_name":   old.get("human_agent_name", ""),
                        "human_agent_role":   old.get("human_agent_role", ""),
                        "escalation_turn":    old.get("escalation_turn", -1),
                    })
                else:
                    await websocket.send_json({
                        "type":    "error",
                        "content": "Session not found or cannot be resumed.",
                    })
                continue

            user_text = msg.get("content", "").strip()
            if not user_text:
                continue

            # Update idle-timeout clock
            auth.touch_token(ws_token)

            # Record user turn (original text, not augmented)
            conversation.append({"role": "user", "content": user_text})

            # Pre-search KB (API mode only -- SDK handles KB via tool calls)
            if DEMO_BACKEND == "api":
                augmented_prompt, presearch_hits = presearch_kb(
                    user_text, gate_cleared=session_data.get("gate_cleared", False)
                )
            else:
                augmented_prompt, presearch_hits = user_text, 0

            t0 = time.perf_counter()
            _turn_model = backend.pick_model(session_data, user_text)
            _gate = "Y" if session_data.get("gate_cleared") else "N"
            print(
                f"[timing] turn start -- backend={DEMO_BACKEND} model={_turn_model} gate={_gate} mode={mode}",
                flush=True,
            )

            await websocket.send_json({"type": "turn_meta", "model": _turn_model})

            try:
                if DEMO_BACKEND == "api":
                    # Direct Anthropic API path
                    api_messages.append({"role": "user", "content": augmented_prompt})
                    system_prompt = prompts.make_system_prompt(mode, web_session_id, session_data)
                    bot_text = await backend.api_chat_stream(websocket, system_prompt, api_messages)

                else:
                    # SDK persistent client path
                    bot_text = ""
                    t_first_reply: float | None = None
                    tool_uses_count = 0
                    last_tool_cmd: str = ""

                    # Background heartbeat
                    _hb_stop = asyncio.Event()
                    async def _heartbeat_loop():
                        while not _hb_stop.is_set():
                            try:
                                await asyncio.wait_for(_hb_stop.wait(), timeout=15)
                                break
                            except asyncio.TimeoutError:
                                pass
                            try:
                                await websocket.send_json({"type": "heartbeat"})
                                print(f"[ws] heartbeat sent", flush=True)
                            except Exception:
                                break
                    _hb_task = asyncio.create_task(_heartbeat_loop())

                    _streamed_text = False

                    async for message in _sdk_turn(augmented_prompt, session_data):
                        # Token-level streaming (partial messages)
                        if isinstance(message, StreamEvent):
                            evt = message.event or {}
                            if message.parent_tool_use_id:
                                continue
                            if evt.get("type") == "content_block_delta":
                                delta = evt.get("delta", {})
                                if delta.get("type") == "text_delta" and delta.get("text"):
                                    txt = delta["text"]
                                    if t_first_reply is None:
                                        t_first_reply = time.perf_counter()
                                        print(f"[timing] first token: {t_first_reply - t0:.2f}s", flush=True)
                                    bot_text += txt
                                    _streamed_text = True
                                    await websocket.send_json({"type": "bot_text_delta", "content": txt})
                            continue

                        if isinstance(message, AssistantMessage):
                            if t_first_reply is None:
                                t_first_reply = time.perf_counter()
                                print(f"[timing] first AssistantMessage: {t_first_reply - t0:.2f}s", flush=True)
                            for block in message.content:
                                if isinstance(block, TextBlock) and block.text.strip():
                                    if not _streamed_text:
                                        bot_text += block.text
                                        await websocket.send_json({"type": "bot_text_delta", "content": block.text})
                                    _streamed_text = False
                                elif isinstance(block, ToolUseBlock) and block.name == "Bash":
                                    cmd = str(block.input.get("command", ""))
                                    last_tool_cmd = cmd
                                    tool_uses_count += 1
                                    print(f"[timing] ToolUse Bash at {time.perf_counter()-t0:.2f}s: {cmd[:120]}", flush=True)
                                    if "route_query" in cmd:
                                        await websocket.send_json({"type": "thinking", "i18n_key": "thinkingAnalyze"})
                                    elif "kb_search" in cmd:
                                        m = re.search(r'[?&]query=([^&\s"\']+)', cmd)
                                        kb_q = m.group(1).replace("+", " ") if m else cmd[:60]
                                        await websocket.send_json({"type": "kb_searching", "query": kb_q})
                                        await websocket.send_json({"type": "thinking", "i18n_key": "thinkingKB"})
                                    elif "save_lead" in cmd:
                                        await websocket.send_json({"type": "thinking", "i18n_key": "thinkingSaveLead"})
                        elif isinstance(message, UserMessage) and message.tool_use_result:
                            t_result = time.perf_counter()
                            print(f"[timing] tool result at {t_result-t0:.2f}s", flush=True)
                            if "kb_search" in last_tool_cmd:
                                await websocket.send_json({"type": "thinking", "i18n_key": "thinkingOrganize"})
                            if "kb_search" in last_tool_cmd:
                                raw_out = ""
                                rd = message.tool_use_result
                                if isinstance(rd, dict):
                                    raw_out = rd.get("output", "") or rd.get("content", "") or ""
                                elif isinstance(rd, str):
                                    raw_out = rd
                                if raw_out:
                                    try:
                                        sources = json.loads(raw_out)
                                        if isinstance(sources, list) and sources:
                                            await websocket.send_json({"type": "kb_sources", "sources": [
                                                {"source_name": r.get("source_name",""), "section": r.get("section",""), "snippet": r.get("content","")[:300]}
                                                for r in sources[:5]
                                            ]})
                                    except Exception:
                                        pass
                                last_tool_cmd = ""
                        elif isinstance(message, ResultMessage):
                            sdk_session_id = message.session_id
                            session_data["claude_session_id"] = sdk_session_id
                            print(f"[timing] ResultMessage: total={time.perf_counter()-t0:.2f}s tool_uses={tool_uses_count}", flush=True)

                    # Stop heartbeat
                    _hb_stop.set()
                    _hb_task.cancel()
                    try:
                        await _hb_task
                    except (asyncio.CancelledError, Exception):
                        pass

                t_done = time.perf_counter()
                print(f"[timing] turn done: {t_done - t0:.2f}s", flush=True)
                if bot_text:
                    conversation.append({"role": "bot", "content": bot_text})
                    # Progressively update customer_type
                    if session_data.get("customer_type", "unknown") == "unknown":
                        inferred_type, _ = sessions.infer_session_meta(conversation)
                        if inferred_type != "unknown":
                            session_data["customer_type"] = inferred_type
                    # Open KB pre-fetch gate once customer type is identified
                    if session_data.get("customer_type", "unknown") != "unknown" and not session_data.get("gate_cleared"):
                        session_data["gate_cleared"] = True
                        print(f"[gate] KB pre-fetch gate cleared (customer_type={session_data['customer_type']})", flush=True)

                    # Escalation detection -> trigger human agent handoff
                    if (not session_data.get("human_agent_active")
                            and prompts.should_escalate(bot_text)):
                        agent_name = session_data.get("human_agent_name", "Agent")
                        agent_role = "Support Specialist" if mode == "service" else "Sales Account Manager"
                        session_data["human_agent_active"] = True
                        session_data["human_agent_name"]   = agent_name
                        session_data["human_agent_role"]   = agent_role
                        session_data["escalation_turn"]    = len(conversation)
                        session_data["resolution"]         = "transferred"
                        session_data["_pending_agent_join"] = {
                            "name": agent_name, "role": agent_role,
                        }

                session_data["turn_count"] = len([t for t in conversation if t["role"] == "user"])
                sessions.save_session_data(web_session_id, session_data)
                await websocket.send_json({"type": "done"})

                # Deferred agent join: send AFTER done so it's a new bubble
                _paj = session_data.pop("_pending_agent_join", None)
                if _paj:
                    agent_name = _paj["name"]
                    agent_role = _paj["role"]
                    await websocket.send_json({
                        "type": "agent_joined",
                        "agent": {"name": agent_name, "role": agent_role},
                    })
                    # Auto-generate human agent greeting
                    _ha_prompt = prompts.make_human_agent_prompt(session_data, mode)
                    _ha_greeting_q = (
                        "You just joined. Greet the customer by name, reference their issue "
                        "from the chat. Sound like a real human -- warm, casual, not robotic. "
                        "Use the SAME language the customer has been using. "
                        "2-3 short sentences max. Do NOT repeat what the AI bot already said."
                    )
                    try:
                        _ha_text = ""
                        _ha_opts = ClaudeAgentOptions(
                            cwd=str(backend.ROOT),
                            system_prompt=_ha_prompt,
                            model="haiku",
                            permission_mode="bypassPermissions",
                            allowed_tools=[],
                            max_turns=1,
                            cli_path=backend.get_claude_cli(),
                            env=backend.proxy_env(),
                        )
                        async for _ha_msg in _sdk_query(prompt=_ha_greeting_q, options=_ha_opts):
                            if isinstance(_ha_msg, AssistantMessage):
                                for _ha_blk in _ha_msg.content:
                                    if isinstance(_ha_blk, TextBlock) and _ha_blk.text.strip():
                                        _ha_text += _ha_blk.text
                        if _ha_text.strip():
                            conversation.append({"role": "bot", "content": _ha_text.strip()})
                            await websocket.send_json({"type": "bot_text_delta", "content": _ha_text.strip()})
                            await websocket.send_json({"type": "done"})
                            print(f"[human-agent] greeting: {_ha_text[:80]}", flush=True)
                    except Exception as _ha_err:
                        print(f"[human-agent] greeting failed: {_ha_err}", flush=True)

                    # End demo session after agent handoff
                    _end_msg = (
                        f"\n\n--- Demo Ended ---\n\n"
                        f"Human agent {agent_name} has joined the conversation. "
                        "In a real scenario, the agent would continue assisting the customer.\n"
                        "Thank you for trying the AI Bot demo!"
                    )
                    await asyncio.sleep(2)
                    await websocket.send_json({"type": "bot_text_delta", "content": _end_msg})
                    await websocket.send_json({"type": "done"})
                    session_data["resolution"] = "transferred"
                    if session_data.get("customer_type", "unknown") == "unknown":
                        inferred_type, _ = sessions.infer_session_meta(conversation)
                        if inferred_type != "unknown":
                            session_data["customer_type"] = inferred_type
                    sessions.save_session_data(web_session_id, session_data)
                    await websocket.send_json({"type": "session_ended"})
                    print(f"[human-agent] demo session ended after agent greeting", flush=True)

            except Exception as e:
                if '_hb_stop' in dir() and not _hb_stop.is_set():
                    _hb_stop.set()
                    _hb_task.cancel()
                await _sdk_disconnect()
                import traceback
                detail = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                print(f"[ws/chat] ERROR: {detail}", flush=True)
                await websocket.send_json({"type": "error", "content": detail})
                await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        await _sdk_disconnect()
        if session_data.get("turn_count", 0) > 0:
            if session_data.get("customer_type", "unknown") == "unknown" or \
               session_data.get("resolution", "active") == "active":
                inferred_type, inferred_res = sessions.infer_session_meta(conversation)
                if session_data.get("customer_type", "unknown") == "unknown":
                    session_data["customer_type"] = inferred_type
                if session_data.get("resolution", "active") == "active":
                    session_data["resolution"] = inferred_res
            sessions.save_session_data(web_session_id, session_data)
        else:
            code_dir = sessions.session_dir_for_code(access_code)
            f = code_dir / f"{web_session_id}.json"
            if f.exists():
                f.unlink(missing_ok=True)
