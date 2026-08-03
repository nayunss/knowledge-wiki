#!/usr/bin/env python3
"""wiki-post 필수 하네스 구성요소를 실행 전에 확인한다."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED = (
    "agents/tech-writer.md",
    "agents/fact-checker.md",
    "agents/copy-editor.md",
    "agents/readability-reviewer.md",
    "skills/tech-writing/SKILL.md",
    "skills/wiki-verify/SKILL.md",
    "skills/readability-review/SKILL.md",
    "skills/wiki-note/SKILL.md",
    "skills/wiki-debug/SKILL.md",
    "skills/wiki-post/scripts/validate-note.py",
)


def resolve(roots: list[Path]) -> tuple[dict[str, Path], list[str]]:
    found: dict[str, Path] = {}
    missing: list[str] = []
    for relative in REQUIRED:
        match = next((root / relative for root in roots if (root / relative).is_file()), None)
        if match:
            found[relative] = match
        else:
            missing.append(relative)
    return found, missing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="*", type=Path)
    args = parser.parse_args()
    roots = args.roots or [Path.cwd() / ".claude", Path.home() / ".claude"]
    found, missing = resolve(roots)
    for relative, path in found.items():
        print(f"PASS {relative} -> {path}")
    optional = next((root / "skills/humanize-korean/SKILL.md" for root in roots if (root / "skills/humanize-korean/SKILL.md").is_file()), None)
    print(f"OPTIONAL humanize-korean -> {optional}" if optional else "OPTIONAL humanize-korean 없음 — 자체 윤문 폴백")
    if missing:
        for relative in missing:
            print(f"FAIL {relative}")
        print("PREFLIGHT: FAIL")
        return 1
    print("PREFLIGHT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
