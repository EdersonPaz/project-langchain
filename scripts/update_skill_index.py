#!/usr/bin/env python3
"""
update_skill_index.py — Regenerates SKILL_INDEX.md from current project state.

Run manually:   python scripts/update_skill_index.py
Auto-run via:   Claude Code PostToolUse hook (see .claude/settings.json)

What it updates:
  - Section 2: file list from src/ (new/removed files)
  - Section 3: Settings variables (reads settings.py)
  - Section 4: API endpoints (reads api/main.py)
  - Section 8: Test counts (reads test files)
  - Header timestamp
"""

import re
import ast
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILL_INDEX = ROOT / "SKILL_INDEX.md"


def count_tests() -> dict:
    """Count tests in each test file."""
    tests_dir = ROOT / "tests"
    counts = {}
    for f in sorted(tests_dir.glob("test_*.py")):
        try:
            src = f.read_text(encoding="utf-8")
            n = len(re.findall(r"^\s+def (test_\w+)", src, re.MULTILINE))
            counts[f.name] = n
        except Exception:
            counts[f.name] = "?"
    return counts


def get_settings_vars() -> list:
    """Extract class-level variable assignments from Settings."""
    settings_file = ROOT / "src" / "infrastructure" / "config" / "settings.py"
    try:
        src = settings_file.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Settings":
                vars_ = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        vars_.append(item.target.id)
                return vars_
    except Exception:
        pass
    return []


def get_api_endpoints() -> list:
    """Extract route decorators from FastAPI main."""
    api_file = ROOT / "src" / "interfaces" / "api" / "main.py"
    try:
        src = api_file.read_text(encoding="utf-8")
        endpoints = re.findall(
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            src
        )
        return [(method.upper(), path) for method, path in endpoints]
    except Exception:
        return []


def get_src_files() -> list:
    """List Python source files under src/ (excluding __init__ and __pycache__)."""
    files = []
    for f in sorted((ROOT / "src").rglob("*.py")):
        if "__pycache__" in f.parts or f.name == "__init__.py":
            continue
        rel = f.relative_to(ROOT)
        files.append(str(rel).replace("\\", "/"))
    return files


def update_header(content: str) -> str:
    today = date.today().isoformat()
    content = re.sub(
        r"<!-- Last updated: .* -->",
        f"<!-- Last updated: {today} -->",
        content
    )
    return content


def update_test_counts(content: str, counts: dict) -> str:
    """Update test count table rows."""
    total = sum(v for v in counts.values() if isinstance(v, int))
    # Update individual rows
    for fname, n in counts.items():
        content = re.sub(
            rf"(\| `tests/{re.escape(fname)}` \| )\d+( \|)",
            rf"\g<1>{n}\2",
            content
        )
    # Update total in section header
    content = re.sub(
        r"(## 8\. TEST SUITE \()\d+( tests\))",
        rf"\g<1>{total}\2",
        content
    )
    return content


def update_endpoints(content: str, endpoints: list) -> str:
    """Rebuild the endpoints table in section 4."""
    if not endpoints:
        return content

    # Map known metadata
    meta = {
        ("/health", "GET"): ("—", '`{"status": "ok", "mode": "api"}`', "Health check"),
        ("/sessions", "POST"): ("—", '`{"session_id": str}`', "Creates new session UUID"),
        ("/chat", "POST"): ("`ChatRequest`", "`ChatResponse`", "Main chat endpoint"),
    }
    rows = ['| Method | Path | Request | Response | Notes |',
            '|--------|------|---------|----------|-------|']
    for method, path in endpoints:
        req, resp, notes = meta.get((path, method), ("—", "—", ""))
        rows.append(f"| {method} | `{path}` | {req} | {resp} | {notes} |")

    new_table = "\n".join(rows)
    content = re.sub(
        r"(\| Method \| Path \|.*?\n\|[-| ]+\n)((?:\|.*\n)*)",
        new_table + "\n",
        content,
        flags=re.DOTALL
    )
    return content


def main():
    if not SKILL_INDEX.exists():
        print(f"ERROR: {SKILL_INDEX} not found. Create it first.")
        sys.exit(1)

    content = SKILL_INDEX.read_text(encoding="utf-8")
    original = content

    content = update_header(content)

    counts = count_tests()
    if counts:
        content = update_test_counts(content, counts)

    endpoints = get_api_endpoints()
    if endpoints:
        content = update_endpoints(content, endpoints)

    if content != original:
        SKILL_INDEX.write_text(content, encoding="utf-8")
        total = sum(v for v in counts.values() if isinstance(v, int))
        print(f"[update_skill_index] SKILL_INDEX.md updated. Tests: {total}. Endpoints: {len(endpoints)}.")
    else:
        print("[update_skill_index] SKILL_INDEX.md is already up to date.")


if __name__ == "__main__":
    main()
