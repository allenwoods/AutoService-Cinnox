#!/usr/bin/env python3
"""
Query Router — keyword-based routing for sales-demo queries.
Returns suggested domain/region/role based on keywords in the query.
Agent can use this suggestion or override based on conversation context.

Usage:
    uv run skills/sales-demo/scripts/route_query.py --query "US DID pricing"
    uv run skills/sales-demo/scripts/route_query.py --query "WhatsApp integration"
    uv run skills/sales-demo/scripts/route_query.py --query "What is DID?"
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ── Glossary loading ────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_REFERENCES_DIR = _SCRIPT_DIR.parent / "references"

_SYNONYM_MAP: dict[str, str] = {}
_GLOSSARY: dict[str, dict] = {}

def _load_glossary() -> None:
    """Load glossary.json and synonym-map.json once at import time."""
    global _SYNONYM_MAP, _GLOSSARY
    synonym_path = _REFERENCES_DIR / "synonym-map.json"
    glossary_path = _REFERENCES_DIR / "glossary.json"
    if synonym_path.exists():
        with open(synonym_path, "r", encoding="utf-8") as f:
            _SYNONYM_MAP = json.load(f)
    if glossary_path.exists():
        with open(glossary_path, "r", encoding="utf-8") as f:
            _GLOSSARY = json.load(f)

_load_glossary()

# Build case-insensitive glossary lookup
_GLOSSARY_LOWER: dict[str, str] = {k.lower(): k for k in _GLOSSARY}

# ── Domain keyword sets ──────────────────────────────────────────────

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "contact_center": [
        "cinnox", "plan", "subscription", "feature", "integration",
        "omnichannel", "contact center", "cx hub", "whatsapp", "webchat",
        "live chat", "m800", "pricing plan", "enterprise plan",
    ],
    "ai_sales_bot": [
        "ai sales bot", "voice bot", "sales bot", "ai bot",
    ],
    "global_telecom": [
        "did", "virtual number", "toll-free", "toll free", "tollfree",
        "local number", "rate", "call rate", "sms rate", "international",
        "vn rate", "vn pricing", "number pricing", "number fee",
        "number cost", "number rate",
        "idd", "pstn", "sip trunk", "dtmf",
    ],
}

# ── Region patterns ──────────────────────────────────────────────────

REGION_MAP: dict[str, list[str]] = {
    "US": ["us", "united states", "usa"],
    "UK": ["uk", "united kingdom", "britain", "england"],
    "HK": ["hong kong", "hk"],
    "SG": ["singapore", "sg"],
    "JP": ["japan", "jp"],
    "AU": ["australia", "au"],
    "DE": ["germany", "de", "deutschland"],
    "FR": ["france", "fr"],
    "CA": ["canada", "ca"],
    "IN": ["india", "in"],
    "CN": ["china", "cn", "mainland china"],
    "TW": ["taiwan", "tw"],
    "KR": ["south korea", "kr"],
    "MY": ["malaysia", "my"],
    "TH": ["thailand", "th"],
    "PH": ["philippines", "ph"],
    "ID": ["indonesia", "id"],
    "AE": ["uae", "united arab emirates"],
}

# ── Country alias → xlsx exact name (for FTS5 query expansion) ──────

COUNTRY_ALIAS_MAP: dict[str, str] = {
    # Short codes → xlsx exact name
    "us": "United States",
    "usa": "United States",
    "uk": "United Kingdom",
    "uae": "United Arab Emirates",
    "hk": "Hong Kong",
    "sg": "Singapore",
    "jp": "Japan",
    "au": "Australia",
    "de": "Germany",
    "fr": "France",
    "ca": "Canada",
    "cn": "China",
    "tw": "Taiwan",
    "kr": "South Korea",
    "my": "Malaysia",
    "th": "Thailand",
    "ph": "Philippines",
    # Common aliases → xlsx exact name
    "america": "United States",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "deutschland": "Germany",
    "mainland china": "China",
}

# ── Ambiguous country names (must clarify before searching) ─────────

# ── Region → country expansion (for broad "Europe"/"Asia" queries) ────

REGION_COUNTRIES: dict[str, list[str]] = {
    "europe": [
        "United Kingdom", "Germany", "France", "Netherlands", "Ireland",
        "Spain", "Italy", "Belgium", "Austria", "Switzerland",
        "Sweden", "Norway", "Denmark", "Finland", "Poland",
        "Portugal", "Czech Republic", "Greece", "Romania", "Hungary",
    ],
    "asia": [
        "China", "Japan", "South Korea", "Hong Kong", "Singapore",
        "Taiwan", "India", "Thailand", "Malaysia", "Philippines",
        "Indonesia", "Vietnam", "Cambodia", "Bangladesh", "Pakistan",
    ],
    "north america": [
        "United States", "Canada", "Mexico",
    ],
    "south america": [
        "Brazil", "Argentina", "Chile", "Colombia", "Peru",
        "Venezuela", "Ecuador", "Uruguay",
    ],
    "middle east": [
        "United Arab Emirates", "Saudi Arabia", "Israel", "Qatar",
        "Bahrain", "Kuwait", "Oman", "Jordan",
    ],
    "oceania": [
        "Australia", "New Zealand",
    ],
    "africa": [
        "South Africa", "Nigeria", "Kenya", "Egypt", "Ghana",
        "Tanzania", "Morocco",
    ],
}

# Aliases for region names (including Chinese)
REGION_ALIASES: dict[str, str] = {
    "european": "europe", "eu": "europe",
    "欧洲": "europe", "欧": "europe",
    "asian": "asia", "亚洲": "asia", "亚太": "asia",
    "north american": "north america", "北美": "north america",
    "south american": "south america", "latin america": "south america",
    "南美": "south america", "拉丁美洲": "south america",
    "middle eastern": "middle east", "中东": "middle east",
    "大洋洲": "oceania", "非洲": "africa",
}

AMBIGUOUS_COUNTRIES: dict[str, list[str]] = {
    "america": ["United States", "American Samoa"],
    "american": ["United States", "American Samoa"],
    "guinea": ["Guinea", "Equatorial Guinea", "Guinea Bissau", "Papua New Guinea"],
    "congo": ["Congo", "Democratic Republic of the Congo"],
    "sudan": ["Sudan", "South Sudan"],
    "niger": ["Niger", "Nigeria"],
    "dominica": ["Dominica", "Dominican Rep"],
    "netherlands": ["Netherlands", "Netherlands Antilles"],
    "samoa": ["Samoa", "American Samoa"],
    "korea": ["South Korea", "North Korea"],
    "vietnam": ["Vietnam", "Vietnam (120 - VNPT network)", "Vietnam (121 - Mobifone network)", "Vietnam (122 - Viettel network)"],
}

# ── Number type keywords ─────────────────────────────────────────────

TOLL_FREE_KW = ["toll-free", "toll free", "tollfree", "1800", "800 number", "freephone"]
LOCAL_KW = ["local number", "local did", "geographic number"]

# ── Role mapping ─────────────────────────────────────────────────────

ROLE_FOR_DOMAIN: dict[str, str] = {
    "contact_center": "product_specialist",
    "ai_sales_bot": "product_specialist",
    "global_telecom": "region_specialist",
}

# Pricing keywords override role to pricing_specialist for contact_center
PRICING_KW = ["pricing", "price", "cost", "how much", "fee", "charge", "rate card", "subscription fee"]

# ── Complex intent keywords (disqualify glossary-only) ───────────────

_COMPLEX_INTENT_KW = [
    "pricing", "price", "cost", "how much", "fee", "compare", "vs",
    "how to", "how do", "set up", "configure", "integrate", "enable",
    "difference between", "which one", "recommend",
]

# ── Glossary-only detection patterns ─────────────────────────────────

_GLOSSARY_ONLY_PATTERNS = [
    re.compile(r"^what\s+is\s+(?:a\s+|an\s+|the\s+)?(.+?)[\?\s]*$", re.IGNORECASE),
    re.compile(r"^what\s+does\s+(.+?)\s+mean[\?\s]*$", re.IGNORECASE),
    re.compile(r"^define\s+(.+?)[\?\s]*$", re.IGNORECASE),
    re.compile(r"^(.+?)是什么[？\?\s]*$"),
    re.compile(r"^什么是(.+?)[？\?\s]*$"),
    re.compile(r"^explain\s+(.+?)[\?\s]*$", re.IGNORECASE),
]


def _lower_has(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in text (case-insensitive)."""
    for kw in keywords:
        if kw in text:
            return True
    return False


def _expand_query(query: str) -> tuple[str, list[dict]]:
    """
    Expand query using synonym-map + country alias map.
    Returns (expanded_query, matched_terms).
    """
    expanded = query
    matched_terms = []
    q_lower = query.lower()

    # 1. Synonym-map expansion (telecom terms)
    if _SYNONYM_MAP:
        for colloquial, official in sorted(_SYNONYM_MAP.items(), key=lambda x: -len(x[0])):
            pattern = re.compile(re.escape(colloquial), re.IGNORECASE)
            if pattern.search(q_lower):
                expanded = pattern.sub(official, expanded)
                q_lower = expanded.lower()
                matched_terms.append({"original": colloquial, "official": official})

    # 2. Country alias expansion: append xlsx exact name for FTS5 precision
    exp_lower = expanded.lower()
    for alias, full_name in sorted(COUNTRY_ALIAS_MAP.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(alias)}\b", exp_lower):
            if full_name.lower() not in exp_lower:
                expanded += f" {full_name}"
                matched_terms.append({"original": alias, "official": full_name})
            break  # only match the first country alias

    return expanded, matched_terms


def _detect_ambiguous_country(query: str) -> tuple[bool, str | None, list[str] | None]:
    """
    Check if query contains a country name that could refer to multiple countries.
    Returns (is_ambiguous, matched_keyword, candidate_countries).
    """
    q_lower = query.lower()
    for keyword, candidates in sorted(AMBIGUOUS_COUNTRIES.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(keyword)}\b", q_lower):
            # Check if user already specified a precise name (e.g. "American Samoa", "South Korea")
            precise = False
            for c in candidates:
                if c.lower() in q_lower and c.lower() != keyword:
                    precise = True
                    break
            if not precise:
                return True, keyword, candidates
    return False, None, None


def _is_glossary_only(query: str) -> tuple[bool, str | None, str | None]:
    """
    Check if query is a pure terminology question.
    Returns (is_glossary_only, matched_term, definition).
    """
    if not _GLOSSARY:
        return False, None, None

    q_lower = query.lower().strip()

    # Try each glossary-only pattern
    for pattern in _GLOSSARY_ONLY_PATTERNS:
        m = pattern.match(query.strip())
        if m:
            candidate = m.group(1).strip()
            candidate_lower = candidate.lower()

            # Direct glossary match — takes priority over complex-intent filter
            if candidate_lower in _GLOSSARY_LOWER:
                official_term = _GLOSSARY_LOWER[candidate_lower]
                entry = _GLOSSARY[official_term]
                return True, official_term, entry["description"]

            # Try synonym-map lookup: candidate might be a synonym
            if candidate_lower in _SYNONYM_MAP:
                official_term = _SYNONYM_MAP[candidate_lower]
                if official_term in _GLOSSARY:
                    entry = _GLOSSARY[official_term]
                    return True, official_term, entry["description"]

    # No glossary match — disqualify if complex intent keywords present
    if _lower_has(q_lower, _COMPLEX_INTENT_KW):
        return False, None, None

    return False, None, None


def route(query: str) -> dict:
    q = query.lower().strip()

    # ── 0. Glossary expansion ─────────────────────────────────────────
    expanded_query, matched_terms = _expand_query(query)
    is_glossary_only, glossary_term, glossary_definition = _is_glossary_only(query)

    # Use expanded query for domain detection
    eq = expanded_query.lower().strip()

    # ── 1. Detect domains ────────────────────────────────────────────
    matched_domains: list[str] = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if _lower_has(eq, keywords):
            matched_domains.append(domain)

    # ── 2. Detect region (specific country or broad region) ─────────
    detected_region: str | None = None
    detected_broad_region: str | None = None
    expanded_countries: list[str] | None = None

    # 2a. Check broad region keywords first (Europe, Asia, etc.)
    for alias, canonical in sorted(REGION_ALIASES.items(), key=lambda x: -len(x[0])):
        if re.search(rf"(?:^|\b|(?<=[\u4e00-\u9fff])){re.escape(alias)}(?:\b|(?=[\u4e00-\u9fff])|$)", eq):
            detected_broad_region = canonical
            expanded_countries = REGION_COUNTRIES.get(canonical, [])
            break
    if not detected_broad_region:
        for region_name, countries in REGION_COUNTRIES.items():
            if re.search(rf"\b{re.escape(region_name)}\b", eq):
                detected_broad_region = region_name
                expanded_countries = countries
                break

    # 2b. Check specific country
    for code, aliases in REGION_MAP.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", q):
                detected_region = code
                break
        if detected_region:
            break

    # ── 2c. Broad region implies global_telecom domain ──────────────
    if detected_broad_region and "global_telecom" not in matched_domains:
        matched_domains.append("global_telecom")

    # ── 3. Detect number type (toll-free vs local) ───────────────────
    is_toll_free = _lower_has(q, TOLL_FREE_KW)
    is_local = _lower_has(q, LOCAL_KW)
    # DID = Direct Inward Dialing = local number by definition
    has_did = bool(re.search(r"\bdid\b", q))
    if has_did and not is_toll_free:
        is_local = True
    number_type: str | None = None
    if is_toll_free and not is_local:
        number_type = "toll-free"
    elif is_local and not is_toll_free:
        number_type = "local"

    # ── 4. Handle ambiguity ──────────────────────────────────────────
    if len(matched_domains) > 1:
        result = {
            "ambiguous": True,
            "candidates": matched_domains,
            "region": detected_region,
            "number_type": number_type,
            "clarify_message": (
                "Your question could relate to multiple areas: "
                + ", ".join(matched_domains)
                + ". Could you clarify which one you're asking about?"
            ),
            "expanded_query": expanded_query,
            "matched_terms": matched_terms,
            "is_glossary_only": is_glossary_only,
        }
        if is_glossary_only and glossary_term:
            result["glossary_term"] = glossary_term
            result["glossary_definition"] = glossary_definition
        return result

    # ── 5. Build result ─────────────────────────────────────────────
    domain = matched_domains[0] if matched_domains else None
    confidence = "high" if domain else "low"

    # Determine role
    role: str | None = None
    if domain:
        role = ROLE_FOR_DOMAIN.get(domain, "product_specialist")
        if domain == "contact_center" and _lower_has(q, PRICING_KW):
            role = "pricing_specialist"

    # Build region string with number type suffix for global_telecom
    region_str = detected_region
    if domain == "global_telecom" and detected_region and number_type:
        region_str = f"{detected_region}/{number_type}"

    # Confidence scoring
    if domain and detected_region:
        confidence = "high"
    elif domain:
        confidence = "medium"
    else:
        confidence = "low"

    # Glossary expansion boosts confidence
    if matched_terms and confidence == "low":
        confidence = "medium"

    # ── 6. Ambiguity flags for missing info ──────────────────────────
    ambiguous = False
    clarify_message: str | None = None

    # 6a. Ambiguous country name detection (must clarify before searching)
    country_ambiguous, ambig_keyword, ambig_candidates = _detect_ambiguous_country(query)
    if country_ambiguous and ambig_candidates:
        ambiguous = True
        options = ", ".join(ambig_candidates[:-1]) + f", or {ambig_candidates[-1]}"
        clarify_message = f"Could you clarify which country/region you mean? We have rates for {options}."

    # 6b. Standard ambiguity checks (only if no country ambiguity)
    if not ambiguous:
        if domain == "global_telecom":
            if not detected_region and not detected_broad_region:
                ambiguous = True
                clarify_message = "Which country are you asking about?"
            elif not number_type and _lower_has(q, ["number", "did", "vn"]) and not detected_broad_region:
                ambiguous = True
                clarify_message = "Are you looking for toll-free or local numbers?"

        if not domain and not is_glossary_only:
            ambiguous = True
            clarify_message = "Could you tell me more about what you're looking for?"

    result = {
        "domain": domain,
        "region": region_str,
        "role": role,
        "confidence": confidence,
        "ambiguous": ambiguous,
        "expanded_query": expanded_query,
        "matched_terms": matched_terms,
        "is_glossary_only": is_glossary_only,
    }
    if clarify_message:
        result["clarify_message"] = clarify_message
    if is_glossary_only and glossary_term:
        result["glossary_term"] = glossary_term
        result["glossary_definition"] = glossary_definition
    if detected_broad_region and expanded_countries:
        result["broad_region"] = detected_broad_region
        result["expanded_countries"] = expanded_countries

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a customer query to the appropriate KB domain/role.")
    parser.add_argument("--query", required=True, help="Customer query text")
    args = parser.parse_args()

    result = route(args.query)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
