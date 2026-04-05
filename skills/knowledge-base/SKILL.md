---
name: knowledge-base
description: Knowledge base manager. Use when user wants to (1) build KB from local files and web sources, (2) search the KB, (3) check KB status. Provides RAG capability for demo and production sessions.
---

# Knowledge Base Manager

Manages the knowledge base for product data retrieval. Sources include local files (PDFs, XLSX) and web pages.

Domains and sources are configured per deployment. Check plugins/*/references/ for available data.

Data stored in `.autoservice/database/knowledge_base/`.

## Domain Slicing

The KB is organized into domains. Each domain groups related content for targeted search.

Domains, sources, and their mappings are defined in the `references/sources.json` file within each plugin. The KB system reads this file to determine what to ingest and how to tag chunks.

## Commands

| Command | Description |
|---------|-------------|
| `kb build` | Build KB from all sources (files + web) |
| `kb build --source files` | Build from local files only (faster, no network) |
| `kb build --source web` | Crawl web sources only |
| `kb search <query>` | Search the KB (for testing/debugging) |
| `kb search <query> --domain <d>` | Search within a specific domain |
| `kb search <query> --region <r>` | Search within a specific region |
| `kb status` | Show KB status and chunk counts |
| `kb migrate` | Run one-time migration to add domain/region columns |
| `kb subagent` | Run domain-filtered search as sub-agent (JSON output) |

---

## kb build

### Build from local files (recommended first step)
```bash
uv run skills/knowledge-base/scripts/kb_ingest.py --source files
```

### Build from web sources (requires internet)
```bash
uv run skills/knowledge-base/scripts/kb_ingest.py --source web
```

### Full build (files + web)
```bash
uv run skills/knowledge-base/scripts/kb_ingest.py --all
```

### Re-ingest a single file
```bash
uv run skills/knowledge-base/scripts/kb_ingest.py \
  --file "path/to/your/file.xlsx"
```

---

## kb search

### Basic search
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "Does the platform support WhatsApp integration?" \
  --top-k 5
```

### Search with source filter
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "pricing rates" \
  --top-k 3 \
  --source-filter "f1,f2,w1"
```

### Search with domain filter
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "pricing plans" \
  --domain <domain_name>
```

### Search with domain + region filter
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "rates" \
  --domain <domain_name> \
  --region US
```

Parameters:
- `--domain` / `-d`: Filter by domain (as defined in sources.json)
- `--region` / `-r`: Filter by region code (e.g., `US`, `HK`, `SG`). Uses LIKE match, so `US` matches `US/toll-free`.
- `--source-filter` / `-s`: Comma-separated source IDs (e.g., `f1,f2,w1`)
- `--raw`: Output raw JSON

---

## kb subagent

Runs a domain-filtered search and outputs structured JSON. Designed to be called by orchestrating agents.

```bash
uv run skills/knowledge-base/scripts/kb_subagent.py \
  --role region_specialist \
  --domain <domain_name> \
  --region US \
  --query "pricing" \
  --top-k 5
```

Output format:
```json
{
  "role": "region_specialist",
  "domain": "<domain_name>",
  "region": "US",
  "query": "pricing",
  "results": [...],
  "sources_consulted": ["Source Name [f1]"],
  "result_count": 3,
  "has_results": true
}
```

---

## kb migrate

One-time migration to add domain/region/language columns to an existing database and backfill values from sources.json. Safe to run multiple times.

```bash
uv run skills/knowledge-base/scripts/kb_migrate.py
```

---

## kb status

```bash
uv run skills/knowledge-base/scripts/kb_status.py
```

Now shows domain/region distribution in addition to per-source statistics.

---

## Integration: Using KB in Service Sessions

When running a session, use the KB search script **before answering any product/pricing question**:

### When to query KB
- Customer asks about features, integrations, capabilities
- Customer asks about pricing, rates, fees
- Customer asks about use cases or supported industries
- Any factual product question

### How to query
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "<customer's question>" \
  --top-k 5
```

For domain-specific questions, add `--domain`:
```bash
uv run skills/knowledge-base/scripts/kb_search.py \
  --query "<question>" --domain <domain_name>
```

### Anti-hallucination rules (CRITICAL)
1. **Only answer using content returned by kb_search.py**
2. **Always cite the source**: "According to [source name]..."
3. **If kb_search.py returns no results**: Do NOT answer from your own training knowledge. Say:
   "I don't have specific information on that in our documentation. Let me connect you with a specialist."
4. **Pricing**: Never state a price not found in KB results. For custom quotes, always transfer to human.
5. **Features**: Never confirm a feature unless it appears in KB results. If not found, say so and offer escalation.
