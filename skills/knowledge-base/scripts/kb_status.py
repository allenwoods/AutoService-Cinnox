#!/usr/bin/env python3
"""
Knowledge Base Status Script

Shows the current state of the knowledge base.

Usage:
    uv run skills/knowledge-base/scripts/kb_status.py
"""

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

DOMAIN_LABELS = {
    "ai_sales_bot": "AI Sales Bot",
    "contact_center": "Contact Center",
    "global_telecom": "Global Telecom",
}


def main():
    print("【知识库状态】")
    print(f"数据库路径: {KB_DB}")

    if not KB_DB.exists():
        print("状态: ❌ 未初始化\n")
        print("请运行以下命令构建知识库:")
        print("  uv run skills/knowledge-base/scripts/kb_ingest.py --source files")
        print("  uv run skills/knowledge-base/scripts/kb_ingest.py --source web  # 需要网络")
        sys.exit(1)

    conn = sqlite3.connect(str(KB_DB))
    total = conn.execute("SELECT COUNT(*) FROM kb_chunks").fetchone()[0]

    if total == 0:
        print("状态: ⚠️  数据库为空")
        print("请运行: uv run skills/knowledge-base/scripts/kb_ingest.py --all")
        conn.close()
        sys.exit(1)

    # Check if new columns exist
    cursor = conn.execute("PRAGMA table_info(kb_chunks)")
    columns = {row[1] for row in cursor.fetchall()}
    has_new_cols = "domain" in columns

    rows = conn.execute("""
        SELECT source_id, source_name, source_type,
               COUNT(*) AS chunk_count,
               MAX(created_at) AS last_updated
        FROM kb_chunks
        GROUP BY source_id, source_name, source_type
        ORDER BY source_id
    """).fetchall()

    last_updated = max(r[4] for r in rows) if rows else "N/A"
    print(f"总块数:   {total}")
    print(f"最后更新: {last_updated[:19]}")
    print()
    print(f"  {'ID':<8} {'类型':<6} {'块数':>5}  {'更新日期':<12}  名称")
    print(f"  {'─'*7} {'─'*5} {'─'*5}  {'─'*11}  {'─'*35}")

    for source_id, source_name, source_type, chunk_count, last_upd in rows:
        upd = (last_upd or "")[:10]
        print(f"  {source_id:<8} {source_type:<6} {chunk_count:>5}  {upd:<12}  {source_name}")

    # Domain/Region summary (only if columns exist)
    if has_new_cols:
        print()
        print("Domain/Region 分布:")

        domain_rows = conn.execute("""
            SELECT COALESCE(NULLIF(domain, ''), '(unset)') AS d, COUNT(*) AS cnt
            FROM kb_chunks
            GROUP BY d
            ORDER BY cnt DESC
        """).fetchall()
        for domain_val, cnt in domain_rows:
            label = DOMAIN_LABELS.get(domain_val, domain_val)
            print(f"  {label:<25} {cnt:>5} chunks")

        print()
        region_rows = conn.execute("""
            SELECT COALESCE(NULLIF(region, ''), '(unset)') AS r, COUNT(*) AS cnt
            FROM kb_chunks
            GROUP BY r
            ORDER BY cnt DESC
        """).fetchall()
        for region_val, cnt in region_rows:
            print(f"  Region: {region_val:<18} {cnt:>5} chunks")

    conn.close()
    print()
    print("状态: ✅ 知识库就绪")


if __name__ == "__main__":
    main()
