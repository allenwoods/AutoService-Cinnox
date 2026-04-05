"""
System prompts — persona, skill loading, and escalation detection.

Assembles the final system prompt from:
  - Plugin persona (loaded from plugins/*/references/persona.md if exists)
  - SKILL_WEB.md or SKILL.md (stripped of CLI-only sections)
  - Runtime context overlay
  - Conditional trimming based on session state (gate cleared or not)
"""

import os
import re
from pathlib import Path


# ── Configurable paths (set by app.py) ────────────────────────────────────
ROOT: Path = Path(".")
SERVER_PORT: int = 8000
_skill_md_path: Path | None = None
_skill_web_md_path: Path | None = None
_persona_path: Path | None = None

# Cached skill text
_raw_skill_text: str = ""
_cached_web_skill: str | None = None


def configure(
    root: Path,
    server_port: int,
    skill_md: Path | None = None,
    skill_web_md: Path | None = None,
    persona_md: Path | None = None,
) -> None:
    """Called by app.py to set paths and load skill text."""
    global ROOT, SERVER_PORT, _skill_md_path, _skill_web_md_path, _persona_path
    global _raw_skill_text, _cached_web_skill
    ROOT = root
    SERVER_PORT = server_port
    _skill_md_path = skill_md
    _skill_web_md_path = skill_web_md
    _persona_path = persona_md
    _cached_web_skill = None

    # Load raw skill text
    if _skill_web_md_path and _skill_web_md_path.exists():
        _raw_skill_text = _skill_web_md_path.read_text(encoding="utf-8")
    elif _skill_md_path and _skill_md_path.exists():
        _raw_skill_text = _skill_md_path.read_text(encoding="utf-8")
    else:
        _raw_skill_text = ""


# ── Escalation detection ──────────────────────────────────────────────────
_ESCALATION_RE = re.compile(
    r'please hold|let me connect|connecting you(?: now| to| with)'
    r'|transfer(?:ring)? you|connect you with|will be right with you',
    re.IGNORECASE,
)


def should_escalate(bot_text: str) -> bool:
    """Only trigger escalation for trigger phrases in declarative sentences.

    Questions like "shall I connect you with..." are proposals -- skip them.
    Statements like "Connecting you now." are executions -- trigger handoff.
    """
    for sentence in re.split(r'(?<=[.!?])\s+|\n+', bot_text):
        if sentence.strip().endswith(('?',)):
            continue
        if _ESCALATION_RE.search(sentence):
            return True
    return False


# ── Persona loading ───────────────────────────────────────────────────────
def _load_persona() -> str:
    """Load persona from plugin references or return a generic default."""
    if _persona_path and _persona_path.exists():
        return _persona_path.read_text(encoding="utf-8")

    # Scan plugins for persona.md
    plugins_dir = ROOT / "plugins"
    if plugins_dir.exists():
        for plugin_dir in sorted(plugins_dir.iterdir()):
            candidate = plugin_dir / "references" / "persona.md"
            if candidate.exists():
                return candidate.read_text(encoding="utf-8")

    # Generic default persona
    return """\
You are an AI virtual assistant.

## YOUR IDENTITY (NON-NEGOTIABLE)
- You are the AI assistant for this product/service.
- NEVER say you are Claude, mention Anthropic, Claude Code, or AutoService.
- NEVER offer to "start a demo" -- you are already the live support bot.
- If asked "who are you?": respond as the product's AI assistant.

## YOUR PURPOSE
Answer questions about the product, features, pricing, and integrations.
Identify the customer type, collect their info, and escalate to human agents when needed.

---
"""


# ── Web-mode tool overrides ───────────────────────────────────────────────
def _web_kb_override() -> str:
    """Prompt section that replaces subagent dispatch with direct curl calls."""
    port = str(SERVER_PORT)
    return f"""\
## WEB MODE -- TOOL OVERRIDES (MANDATORY)

You are running inside the web demo server.

### Language
ALWAYS reply in the same language the customer uses. If they write Chinese, reply in Chinese. If English, reply in English.

### Route Query -- ONLY AFTER GATE IS CLEARED
Do NOT call route_query or kb_search until the MANDATORY GATE is passed (customer type identified + lead info collected). If gate is not cleared, respond directly with the gate question -- no tool calls needed.

Once gate IS cleared, before any product/pricing/terminology response, run:
```bash
curl -s "http://127.0.0.1:{port}/api/route_query?query=ENGLISH+KEYWORDS+HERE"
```
**IMPORTANT**: Always use **English keywords** in query parameters. The KB content is in English. If the customer writes in Chinese or other languages, translate to English keywords first. Use `+` for spaces.
Read the JSON output and follow the routing decision:
- If `is_glossary_only=true` -> use **Glossary Fast-Track** (respond directly from `glossary_definition`, skip KB search)
- If `ambiguous=true` -> ask ONE clarifying question using `clarify_message`
- Otherwise -> use `expanded_query` for KB search below

### KB Search -- DIRECT CURL (NO SUBAGENTS)
Do NOT use the Agent tool. Call KB search directly:
```bash
curl -s "http://127.0.0.1:{port}/api/kb_search?query=EXPANDED+QUERY&top_k=3&source_filter=SOURCE_IDS"
```

### Save Lead
```bash
curl -s -X POST "http://127.0.0.1:{port}/api/save_lead" \\
  -H "Content-Type: application/json" \\
  -d '{{"type":"new_customer","data":{{"name":"...","company":"...","email":"...","phone":"..."}}}}'
```
Types: `new_customer` | `existing_customer` | `partner`

### Save Session -- DO NOT RUN
The web server saves session data automatically. Do NOT call save_session.py.

---
"""


def _sales_runtime_base() -> str:
    return """
---
RUNTIME CONTEXT (web chatbot -- sales mode):
- You are live in a browser UI. Respond directly as the AI Bot -- no preamble.
- For product/pricing questions: run route_query, then curl KB search directly. Do NOT use Agent tool.
- Never fabricate features or prices.
- Keep replies concise: 2-4 sentences per turn.
"""


# ── Skill text processing ─────────────────────────────────────────────────
def _web_skill_text() -> str:
    """Strip CLI-only sections from SKILL.md for the web prompt.

    Removes:
    - Step 1 (Pre-flight Check) -- no need to check KB status in web mode
    - Step 2 (Start the Session banner) -- not applicable in web chat UI
    - Step 7 (End Session / save_session.py) -- server handles this automatically
    - Step 3.5 subagent mandate -- replaced by WEB_KB_OVERRIDE direct curl
    """
    text = _raw_skill_text
    if not text:
        return ""

    port = str(SERVER_PORT)

    # Strip Step 1 and Step 2 only (preserve GATE, Query Routing, Ambiguity)
    text = re.sub(
        r'---\s*\n## Step 1:.*?(?=---\s*\n## MANDATORY GATE)',
        '', text, flags=re.DOTALL,
    )
    # Strip Step 7 end-session block
    text = re.sub(
        r'---\s*\n## Step 7:.*?(?=---\s*\n## UAT|$)',
        '', text, flags=re.DOTALL,
    )

    # Replace uv run script calls with curl equivalents
    text = re.sub(
        r'```bash\s*\n\s*uv run [^`]*?save_lead\.py\b[^`]*?```',
        f'```bash\ncurl -s -X POST "http://127.0.0.1:{port}/api/save_lead" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"type":"TYPE","data":{"name":"...","company":"...","email":"...","phone":"..."}}\'\n```',
        text,
    )
    text = re.sub(
        r'```bash\s*\n\s*uv run [^`]*?route_query\.py\b[^`]*?```',
        f'```bash\ncurl -s "http://127.0.0.1:{port}/api/route_query?query=ENGLISH+KEYWORDS"\n```',
        text,
    )
    text = re.sub(
        r'```bash\s*\n\s*uv run [^`]*?kb_search\.py\b[^`]*?```',
        f'```bash\ncurl -s "http://127.0.0.1:{port}/api/kb_search?query=QUERY&top_k=3&source_filter=IDS"\n```',
        text,
    )
    text = re.sub(
        r'```bash\s*\n\s*uv run [^`]*?kb_(?:status|ingest)\.py\b[^`]*?```',
        '', text,
    )

    # Replace subagent mandates with direct curl instruction
    text = text.replace(
        "You MUST use the **Agent** tool to dispatch to subagents for ALL product/pricing queries.",
        "Use direct curl calls to /api/kb_search and /api/route_query (see WEB MODE overrides above).",
    )
    text = text.replace(
        "Do NOT call `kb_search.py` or `kb_subagent.py` directly via Bash.",
        "",
    )
    text = text.replace(
        "ALWAYS use the **Agent** tool to dispatch to the appropriate subagent",
        "ALWAYS use curl to /api/kb_search with the appropriate source_filter",
    )
    # Clean up prose references to script filenames
    text = text.replace("run save_lead.py", "call /api/save_lead")
    text = text.replace("save_lead.py completes", "/api/save_lead completes")
    text = text.replace("call to save_lead.py", "call to /api/save_lead")
    text = text.replace(
        "Call save_session.py first, then send the message.",
        "The web server saves session data automatically.",
    )
    text = text.replace("save_session.py", "(handled by web server)")
    text = re.sub(
        r'uv run [\./]*(?:\.autoservice/)?\.claude/skills/(?:\w[\w-]*/)+scripts/(\w+)\.py',
        lambda m: f'curl to /api/{m.group(1)}'
        if m.group(1) in ('save_lead', 'route_query', 'kb_search')
        else '(handled by web server)',
        text,
    )
    text = re.sub(
        r'>\s*\*\*MANDATORY.*?Do NOT call `kb_search\.py`.*?internally\.',
        '> Use curl to /api/route_query and /api/kb_search directly (see WEB MODE overrides above).',
        text, flags=re.DOTALL,
    )
    text = re.sub(
        r'>\s*\*\*IMPORTANT\*\*:.*?Do NOT call `kb_search\.py`.*?internally\.',
        '> Use curl to /api/kb_search directly with the appropriate source_filter.',
        text, flags=re.DOTALL,
    )
    text = text.replace("After running `route_query.py`", "After running route_query")
    text = text.replace("skip `route_query.py`", "skip route_query")
    text = text.replace("`route_query.py` returns", "route_query returns")
    text = text.replace("When `route_query.py` returns", "When route_query returns")
    return text


def _get_web_skill() -> str:
    global _cached_web_skill
    if _cached_web_skill is None:
        _cached_web_skill = _web_skill_text()
    return _cached_web_skill


def conditional_skill(session_data: dict | None) -> str:
    """Return a trimmed SKILL text based on session state.

    Conditional:
      - gate NOT cleared -> keep lead collection flows, strip KB Q&A details
      - gate cleared     -> strip lead collection flows, keep KB Q&A
    """
    text = _get_web_skill()
    if not text:
        return ""
    gate_cleared = bool(session_data and session_data.get("gate_cleared"))

    # Always strip: Subagent Orchestration, Audit Trail, UAT ref
    text = re.sub(
        r'---\s*\n## Step 3\.5:.*?(?=---\s*\n## Step 4:)',
        '', text, flags=re.DOTALL,
    )
    text = re.sub(
        r'---\s*\n## Step 8:.*?(?=---\s*\n## UAT|$)',
        '', text, flags=re.DOTALL,
    )
    text = re.sub(
        r'---\s*\n## UAT Test Case.*$',
        '', text, flags=re.DOTALL,
    )

    if gate_cleared:
        text = re.sub(
            r'---\s*\n### New Customer Flow.*?(?=---\s*\n### Existing Customer Flow)',
            '', text, flags=re.DOTALL,
        )
        text = re.sub(
            r'---\s*\n### Existing Customer Flow.*?(?=---\s*\n### Partner Flow)',
            '', text, flags=re.DOTALL,
        )
        text = re.sub(
            r'---\s*\n### Partner Flow.*?(?=---\s*\n### Customer Refuses)',
            '', text, flags=re.DOTALL,
        )
        text = re.sub(
            r'---\s*\n### Customer Refuses.*?(?=---\s*\n## Step 3\.5:|---\s*\n## Step 4:)',
            '', text, flags=re.DOTALL,
        )
        text = re.sub(
            r'---\s*\n### Discovery Phase.*?(?=---\s*\n### Existing Customer Flow)',
            '', text, flags=re.DOTALL,
        )
    else:
        text = re.sub(
            r'---\s*\n## Step 4:.*?(?=---\s*\n## Step 5:)',
            '', text, flags=re.DOTALL,
        )

    return text


# ── Human agent handoff prompts ───────────────────────────────────────────
def _build_human_agent_context(conversation: list[dict]) -> str:
    """Summarise the last 8 turns for the human agent system prompt."""
    recent = conversation[-8:] if len(conversation) > 8 else conversation
    lines = []
    for t in recent:
        label = "Customer" if t["role"] == "user" else "AI Bot"
        lines.append(f"{label}: {t['content'][:400]}")
    return "\n".join(lines)


def make_human_agent_prompt(session_data: dict, mode: str) -> str:
    """System prompt for the mock human agent persona (post-escalation)."""
    agent_name = session_data.get("human_agent_name", "Agent")
    if mode == "service":
        role, dept = "Support Specialist", "Customer Support"
    else:
        role, dept = "Sales Account Manager", "Sales"

    context = _build_human_agent_context(session_data.get("conversation", []))
    port = str(SERVER_PORT)

    return f"""\
You are {agent_name}, a {role} on the {dept} team.
A customer has just been transferred to you from the AI chatbot.

## LANGUAGE RULE (CRITICAL)
Reply in the SAME language the customer used in the conversation. If they spoke Chinese, reply entirely in Chinese. If English, reply in English. NEVER mix languages.

## Your Persona -- Sound Like a REAL Human
- You're a real person, NOT an AI. Talk like a normal human colleague on a chat.
- Use casual, warm tone -- like texting a client you've worked with before.
- Short sentences. No bullet points. No markdown formatting.
- NEVER use: emojis, corporate jargon, "I sincerely apologize", "rest assured"
- NEVER repeat what the AI bot already said. You have the chat history -- build on it.
- Address the customer by name naturally
- Keep replies to 2-3 short sentences max

## Customer Context (from AI chatbot handoff)
{context}

## What You Can Do
- **Support**: create urgent tickets, escalate to network/billing team, arrange callbacks
- **Sales**: provide custom pricing, arrange product demos, connect with solutions engineers
- Always end each reply with a clear next step or action taken

## Rules
- NEVER fabricate account data not shown in Customer Context above
- If you need to check something: "Let me look that up for you -- one moment."
- KB lookup if needed: curl -s "http://127.0.0.1:{port}/api/kb_search?query=QUERY&top_k=3"

Your FIRST reply must acknowledge the transfer and reference the customer's issue \
by name/company if known.
"""


# ── Main prompt assembly ──────────────────────────────────────────────────
def make_system_prompt(
    mode: str = "sales",
    web_session_id: str = "",
    session_data: dict | None = None,
) -> str:
    """Build the system prompt string (used by both SDK and API backends)."""
    if session_data and session_data.get("human_agent_active"):
        return make_human_agent_prompt(session_data, mode)

    persona = _load_persona()
    skill = conditional_skill(session_data)
    override = _web_kb_override()
    runtime = _sales_runtime_base()

    base = override + persona + skill + runtime

    return (
        base
        .replace("{web_session_id}", web_session_id or "unknown")
        .replace("{server_port}", str(SERVER_PORT))
    )
