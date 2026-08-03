#!/usr/bin/env python3
"""본문 작성 전 도메인·용어 캘리브레이션 산출물 게이트."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    fails: list[str] = []
    for label in ("도메인", "하위 분야", "대상 독자"):
        if not re.search(rf"(?m)^-\s*\*\*{label}\*\*:\s*\S", text):
            fails.append(f"{label} 선언 누락")
    if "## 용어 기준 출처" not in text:
        fails.append("`## 용어 기준 출처` 섹션 누락")
    urls = set(re.findall(r"https?://[^\s)>]+", text))
    if len(urls) < 2:
        fails.append(f"용어 기준 URL 2개 미만: {len(urls)}개")
    if "## 핵심 용어" not in text:
        fails.append("`## 핵심 용어` 섹션 누락")
    table_header = next((line for line in text.splitlines() if line.startswith("|") and "채택 표기" in line), "")
    for column in ("개념", "채택 표기", "첫 등장 표기", "피할 표기", "근거"):
        if column not in table_header:
            fails.append(f"핵심 용어 표 `{column}` 열 누락")
    table_rows = [line for line in text.splitlines() if line.startswith("|") and not re.match(r"^\|[ :|-]+\|$", line)]
    if table_header and len(table_rows) < 2:
        fails.append("핵심 용어 표에 용어 행 없음")
    return fails


def main() -> int:
    if len(sys.argv) != 2:
        print("사용: validate-domain-brief.py <00_domain_brief.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"입력 파일 없음: {path}", file=sys.stderr)
        return 2
    fails = validate(path)
    for failure in fails:
        print(f"❌ {failure}")
    if fails:
        print("DOMAIN GATE: FAIL")
        return 1
    print("DOMAIN GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
