# AutoService — Fork-Based Customer Service / Sales Bot Framework

## Overview

AutoService is a fork-based framework for building customer service and sales bots. Each customer deployment is a fork of this repo with customer-specific configuration via declarative plugins.

Two channels:
- **Feishu IM** (primary) — MCP-based, runs as `feishu/channel.py`
- **Web chat** (secondary) — FastAPI app at `web/app:app`

## Commands

- `make setup` — Create symlinks (.claude/ dirs, plugin skills), init runtime dirs
- `make run-channel` — Start Feishu IM channel (MCP server)
- `make run-web` — Start web chat (FastAPI, default port 8000)
- `make check` — Verify plugin discovery

## Directory Structure

```
feishu/              # Feishu IM channel (MCP server)
web/                 # Web chat channel (FastAPI)
autoservice/         # Core library (shared logic)
skills/              # Claude Code skills (symlinked into .claude/skills)
plugins/             # Customer-specific plugins (declarative)
commands/            # Claude Code commands (symlinked into .claude/commands)
agents/              # Claude Code agents (symlinked into .claude/agents)
hooks/               # Claude Code hooks (symlinked into .claude/hooks)
.autoservice/        # Runtime data — logs, cache, db (gitignored)
docs/                # Design docs and plans
```

## Plugin System

Each plugin lives in `plugins/<name>/` and can contain:
- `skills/` — Plugin-specific skills (auto-discovered by `make setup`)
- Config files for customer-specific API integrations

Run `make check` to verify plugin skill discovery.
