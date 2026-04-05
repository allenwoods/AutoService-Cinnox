#!/usr/bin/env python3
"""
Knowledge Base Search Script

Searches the knowledge base using SQLite FTS5 (BM25 ranking).

Usage:
    uv run skills/knowledge-base/scripts/kb_search.py \
        --query "Does the platform support WhatsApp integration?" \
        --top-k 5

    uv run skills/knowledge-base/scripts/kb_search.py \
        --query "US DID number price" \
        --top-k 3 \
        --source-filter "f5,f7,w4"
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows (avoids GBK emoji errors)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path.cwd()
KB_DIR = PROJECT_ROOT / ".autoservice" / "database" / "knowledge_base"
KB_DB = KB_DIR / "kb.db"

STARS = ["", "★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"]


def build_fts_query(query: str) -> str:
    """Convert a natural-language query to an FTS5 query expression.

    Proper-noun phrases (consecutive Title-Case words, e.g. "United States",
    "United Kingdom") are kept as FTS5 phrase matches so they rank above chunks
    that happen to contain "united" and "states" in unrelated positions.
    """
    clean = re.sub(r'["\(\)\*\:\^]', " ", query)
    tokens = clean.split()

    terms = []
    def is_proper(word: str) -> bool:
        """Title-Case word (not ALL-CAPS acronym like DID/MRC)."""
        return bool(word) and word[0].isupper() and not word.isupper()

    i = 0
    while i < len(tokens):
        # Collect up to 2 consecutive Title-Case words as a phrase (bigram only)
        # e.g. "United States", "United Kingdom", "Hong Kong" — but NOT 3+ word chains
        if is_proper(tokens[i]) and i + 1 < len(tokens) and is_proper(tokens[i + 1]):
            terms.append(f'"{tokens[i]} {tokens[i + 1]}"')  # phrase match
            i += 2
            continue
        # Single word: keep if 3+ chars, or 2-char uppercase (country codes: US, UK, HK)
        if len(tokens[i]) >= 3 or (len(tokens[i]) == 2 and tokens[i].isupper()):
            terms.append(f'"{tokens[i]}"')
        i += 1

    if not terms:
        return f'"{query}"'
    return " OR ".join(terms)


def build_fts_countries(countries: list[str], extra_terms: list[str] | None = None) -> str:
    """Build FTS5 query for a list of country names.

    Each country name is wrapped as an exact phrase, joined by OR.
    Extra terms (e.g. "DID", "toll-free") are appended as OR terms.
    """
    terms = [f'"{c}"' for c in countries if c]
    if extra_terms:
        for t in extra_terms:
            t = t.strip()
            if t and len(t) >= 2:
                terms.append(f'"{t}"')
    return " OR ".join(terms) if terms else ""


def search(query: str, top_k: int = 5, source_filter: list[str] | None = None,
           countries: list[str] | None = None) -> list[dict]:
    """Return top-k matching chunks from the knowledge base.

    If `countries` is provided, builds a phrase-based FTS5 query where each
    country name is an exact phrase match, avoiding false merges like
    "Germany France" being treated as a single phrase.
    """
    if not KB_DB.exists():
        return []

    conn = sqlite3.connect(str(KB_DB))
    conn.row_factory = sqlite3.Row

    if countries:
        # Extract non-country keywords from query for extra relevance
        extra = [w for w in re.sub(r'["\(\)\*\:\^]', " ", query).split()
                 if w.isupper() and len(w) >= 2]  # e.g. DID, MRC
        fts_query = build_fts_countries(countries, extra)
    else:
        fts_query = build_fts_query(query)

    try:
        if source_filter:
            placeholders = ",".join("?" * len(source_filter))
            sql = f"""
                SELECT c.id, c.source_id, c.source_type, c.source_name,
                       c.source_url, c.file_path, c.section, c.content,
                       rank AS score
                FROM kb_fts f
                JOIN kb_chunks c ON c.rowid = f.rowid
                WHERE kb_fts MATCH ? AND c.source_id IN ({placeholders})
                ORDER BY rank
                LIMIT ?
            """
            rows = conn.execute(sql, [fts_query] + source_filter + [top_k]).fetchall()
        else:
            rows = conn.execute(
                """SELECT c.id, c.source_id, c.source_type, c.source_name,
                          c.source_url, c.file_path, c.section, c.content,
                          rank AS score
                   FROM kb_fts f
                   JOIN kb_chunks c ON c.rowid = f.rowid
                   WHERE kb_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                [fts_query, top_k],
            ).fetchall()
        return [dict(r) for r in rows]

    except sqlite3.OperationalError:
        # Fallback: simpler single-term query
        try:
            first_word = [w for w in query.split() if len(w) >= 4]
            if not first_word:
                return []
            rows = conn.execute(
                """SELECT c.id, c.source_id, c.source_type, c.source_name,
                          c.source_url, c.file_path, c.section, c.content,
                          rank AS score
                   FROM kb_fts f
                   JOIN kb_chunks c ON c.rowid = f.rowid
                   WHERE kb_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                [f'"{first_word[0]}"', top_k],
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
    finally:
        conn.close()


def score_to_stars(score: float, all_scores: list[float]) -> int:
    """Map BM25 score (negative; lower = better match) to 1–5 stars."""
    if len(all_scores) < 2:
        return 4
    best, worst = min(all_scores), max(all_scores)
    if best == worst:
        return 4
    norm = (score - worst) / (best - worst)  # 0 = worst, 1 = best
    return max(1, min(5, round(1 + norm * 4)))


def source_ref(result: dict) -> str:
    """Format a human-readable source reference string."""
    if result["source_type"] == "web":
        url = result.get("source_url") or ""
        return f"{result['source_name']}" + (f" | {url}" if url else "")
    fname = Path(result.get("file_path") or "").name
    return result["source_name"] + (f" [{fname}]" if fname else "")


def main():
    parser = argparse.ArgumentParser(description="Search the knowledge base")
    parser.add_argument("--query", "-q", required=True, help="Natural-language search query")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument(
        "--source-filter", "-s",
        help="Comma-separated source IDs to restrict search (e.g., f4,f5,w1)",
    )
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if not KB_DB.exists():
        if args.raw:
            print(json.dumps({"error": "KB not initialised", "results": []}))
        else:
            print("【知识库检索结果】")
            print("⚠️  知识库未初始化。请先运行:")
            print("   uv run skills/knowledge-base/scripts/kb_ingest.py --source files")
        sys.exit(1)

    source_filter = (
        [s.strip() for s in args.source_filter.split(",")]
        if args.source_filter
        else None
    )
    results = search(args.query, top_k=args.top_k, source_filter=source_filter)

    if args.raw:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("【知识库检索结果】")
    print(f"查询: {args.query}")

    if not results:
        print("\n❌ 未找到相关内容")
        print("\n⚠️  知识库无结果，禁止自行回答，应回复:")
        print('   "I don\'t have specific information on that in our documentation.')
        print('    Let me connect you with a specialist who can help."')
        return

    all_scores = [r["score"] for r in results]
    print(f"检索到 {len(results)} 条相关内容:\n")

    # Collect searchable terms for snippet highlighting
    query_words = [w.strip('"') for w in re.findall(r'"[^"]+"|\S+', build_fts_query(args.query))
                   if w not in ('OR', 'AND', 'NOT')]

    for i, r in enumerate(results, 1):
        stars = score_to_stars(r["score"], all_scores)
        section = r.get("section") or ""
        ref = source_ref(r)

        print(f"[{i}] 来源: {ref}" + (f"  |  {section}" if section else ""))

        content = r["content"]
        # Show snippet around first query term match instead of always showing from start
        snippet_start = 0
        for term in query_words:
            idx = content.lower().find(term.lower())
            if idx > 100:  # Only shift if match is far from start
                snippet_start = max(0, idx - 80)
                break
        snippet = content[snippet_start:snippet_start + 900]
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_start + 900 < len(content):
            snippet = snippet + "..."
        print(f"    {snippet}")
        print(f"    相关度: {STARS[stars]}")
        print()

    print("─" * 60)
    print("⚠️  回答时必须引用以上来源，禁止添加知识库以外的内容。")


if __name__ == "__main__":
    main()
