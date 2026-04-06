"""Universal behavior rules stored as YAML in .autoservice/rules/."""

import yaml
from pathlib import Path
from datetime import datetime, timezone

RULES_DIR = Path(".autoservice/rules")


def load_rules() -> list[dict]:
    """Load all rules from all YAML files in .autoservice/rules/."""
    rules = []
    if not RULES_DIR.exists():
        return rules
    for f in sorted(RULES_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text()) or []
            if isinstance(data, list):
                for r in data:
                    r["_source"] = f.name
                rules.extend(data)
        except Exception:
            pass
    return rules


def save_rules(filename: str, rules: list[dict]) -> Path:
    """Save rules to a YAML file."""
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    path = RULES_DIR / filename
    path.write_text(yaml.dump(rules, allow_unicode=True, default_flow_style=False))
    return path


def add_rule(context: str, rule: str, created_by: str = "", filename: str = "general.yaml") -> dict:
    """Add a rule to a YAML file."""
    path = RULES_DIR / filename
    existing = []
    if path.exists():
        existing = yaml.safe_load(path.read_text()) or []

    max_id = max((r.get("id", 0) for r in existing), default=0) if existing else 0
    new_rule = {
        "id": max_id + 1,
        "context": context,
        "rule": rule,
        "created_by": created_by,
        "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
    }
    existing.append(new_rule)
    save_rules(filename, existing)
    return new_rule


def delete_rule(rule_id: int, filename: str = "general.yaml") -> bool:
    """Delete a rule by ID from a YAML file."""
    path = RULES_DIR / filename
    if not path.exists():
        return False
    rules = yaml.safe_load(path.read_text()) or []
    before = len(rules)
    rules = [r for r in rules if r.get("id") != rule_id]
    if len(rules) == before:
        return False
    save_rules(filename, rules)
    return True


def format_rules_for_prompt() -> str:
    """Format all universal rules as a text block for channel instructions."""
    rules = load_rules()
    if not rules:
        return "(暂无通用行为规则)"
    lines = []
    for r in rules:
        ctx = f"[{r.get('context', 'general')}] " if r.get('context') else ""
        lines.append(f"- {ctx}{r['rule']}")
    return "\n".join(lines)
