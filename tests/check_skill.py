#!/usr/bin/env python3
"""Validate SKILL.md and references/*.md structure. Exits 1 on any error.

Run from anywhere: python3 tests/check_skill.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMPACTS = {"CRITICAL", "HIGH", "MEDIUM-HIGH"}
PREFIXES = ("query-", "conn-", "security-", "schema-", "lock-", "data-")
REQUIRED_KEYS = ("title", "impact", "impactDescription", "tags")


def frontmatter(text, label, errors):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{label}: missing frontmatter block")
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")) or not line.strip():
            continue  # skip nested metadata and blanks
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


def main():
    errors = []

    skill_text = (ROOT / "SKILL.md").read_text()
    fm = frontmatter(skill_text, "SKILL.md", errors)
    for key in ("name", "description", "license"):
        if not fm.get(key):
            errors.append(f"SKILL.md: missing frontmatter key '{key}'")
    if "review" not in fm.get("description", "").lower():
        errors.append("SKILL.md: description no longer mentions 'review'")

    refs = sorted((ROOT / "references").glob("*.md"))
    if not refs:
        errors.append("references/: no rule files found")
    for path in refs:
        rel = f"references/{path.name}"
        if not path.name.startswith(PREFIXES):
            errors.append(f"{rel}: filename prefix not one of {list(PREFIXES)}")
        text = path.read_text()
        fm = frontmatter(text, rel, errors)
        for key in REQUIRED_KEYS:
            if not fm.get(key):
                errors.append(f"{rel}: missing frontmatter key '{key}'")
        if fm.get("impact") and fm["impact"] not in IMPACTS:
            errors.append(f"{rel}: impact '{fm['impact']}' not in {sorted(IMPACTS)}")
        body = text.split("---\n", 2)[-1]
        for marker, label in (
            ("\n## ", "H2 heading"),
            ("**Incorrect", "'Incorrect' example"),
            ("**Correct", "'Correct' example"),
            ("Reference:", "Reference link"),
        ):
            if marker not in body:
                errors.append(f"{rel}: missing {label}")
        h2 = re.search(r"\n## (.+)\n", body)
        if fm.get("title") and h2 and h2.group(1).strip() != fm["title"]:
            errors.append(f"{rel}: H2 '{h2.group(1).strip()}' != title '{fm['title']}'")

    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: SKILL.md and {len(refs)} rule files pass all checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
