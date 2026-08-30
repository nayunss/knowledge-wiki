#!/usr/bin/env python3
"""knowledge-wiki 발행 게이트: OKF v0.2 + 위키 품질 프로필.

사용: python3 validate-note.py <final.md> [inventory.md]
종료: 0=PASS, 1=FAIL, 2=호출 오류

외부 YAML 패키지 없이 실행되도록, 검증에 필요한 최상위 키와 제한된
중첩 계약만 읽는다. 완전한 YAML 파서가 아니므로 파싱 불가능한 모양은
관대하게 통과시키지 않고 명시적으로 FAIL한다.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path


PROFILE_REQUIRED = ("type", "title", "description", "tags")
RESERVED_NAMES = {"index.md", "log.md"}
STATUS_VALUES = {"draft", "stable", "deprecated"}


def split_document(text: str) -> tuple[str | None, str]:
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", text, re.S)
    if not match:
        return None, text
    return match.group(1), text[match.end() :]


def top_level(frontmatter: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current: str | None = None
    for raw in frontmatter.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$", raw)
        if match:
            current = match.group(1)
            result[current] = (match.group(2) or "").strip()
        elif raw[:1].isspace() and current:
            result[current] += "\n" + raw
        else:
            raise ValueError(f"해석할 수 없는 frontmatter 줄: {raw}")
    return result


def clean_scalar(value: str) -> str:
    first = value.splitlines()[0].strip() if value else ""
    first = re.sub(r"\s+#.*$", "", first).strip()
    if len(first) >= 2 and first[0] == first[-1] and first[0] in "'\"":
        first = first[1:-1]
    return first


def mapping_has(value: str, key: str) -> bool:
    return bool(re.search(rf"(?:^|[{{,\n])\s*(?:-\s*)?{re.escape(key)}\s*:\s*[^,}}\n]+", value))


def list_item_blocks(value: str) -> list[str]:
    lines = value.splitlines()[1:]
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if re.match(r"^\s+-\s+", line):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def source_ids(value: str, fails: list[str]) -> set[str]:
    blocks = list_item_blocks(value)
    if not blocks:
        fails.append("sources는 하나 이상의 YAML 목록 항목이어야 함")
        return set()
    ids: set[str] = set()
    for index, block in enumerate(blocks, 1):
        resource = re.search(r"(?:^|\n)\s*(?:-\s+)?resource:\s*(\S.+)$", block, re.M)
        if not resource:
            fails.append(f"sources[{index}].resource 누락")
        source_id = re.search(r"(?:^|\n)\s*(?:-\s+)?id:\s*([^\s#]+)", block)
        if source_id:
            value_id = clean_scalar(source_id.group(1))
            if value_id in ids:
                fails.append(f"sources[].id 중복: {value_id}")
            ids.add(value_id)
    return ids


def valid_iso_datetime(value: str) -> bool:
    candidate = clean_scalar(value).replace("Z", "+00:00")
    try:
        dt.datetime.fromisoformat(candidate)
        return "T" in candidate
    except ValueError:
        return False


FENCE = re.compile(r"^```.*?^```", re.M | re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """코드 펜스와 인라인 코드를 지운다. 길이가 바뀌어도 무방한 검사에만 쓴다.

    코드는 산문이 아니다 — `grep -oE '<link[^>]*rel'` 안의 `[^>]`는 각주가 아니고,
    `(검증 필요)`를 인용한 코드스팬은 잔존 마커가 아니다. (kinetics·위키-하네스 실측)
    """
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return INLINE_CODE.sub("", text)


def validate(path: Path, inventory: Path | None = None) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    fails: list[str] = []
    warns: list[str] = []

    if path.name in RESERVED_NAMES:
        fails.append(f"{path.name}는 OKF 예약 파일명 — 일반 개념 노트로 발행 불가")

    frontmatter, body = split_document(text)
    fields: dict[str, str] = {}
    if frontmatter is None:
        fails.append("파일 시작점의 YAML frontmatter 없음")
    else:
        try:
            fields = top_level(frontmatter)
        except ValueError as exc:
            fails.append(str(exc))

    for key in PROFILE_REQUIRED:
        if key not in fields or not clean_scalar(fields[key]):
            label = "OKF v0.2 필수" if key == "type" else "knowledge-wiki 프로필 필수"
            fails.append(f"{label} frontmatter `{key}` 누락/빈 값")

    if "tags" in fields:
        tags = clean_scalar(fields["tags"])
        if not (tags.startswith("[") and tags.endswith("]") and tags != "[]"):
            fails.append("tags는 비어 있지 않은 YAML 인라인 목록이어야 함")

    if "status" in fields and clean_scalar(fields["status"]) not in STATUS_VALUES:
        fails.append("status는 draft | stable | deprecated 중 하나여야 함")

    if "stale_after" in fields:
        try:
            stale = dt.date.fromisoformat(clean_scalar(fields["stale_after"]))
            if stale <= dt.date.today():
                warns.append(f"stale_after 도달/경과: {stale.isoformat()}")
        except ValueError:
            fails.append("stale_after는 YYYY-MM-DD여야 함")

    if "generated" in fields:
        if not mapping_has(fields["generated"], "by"):
            fails.append("generated.by 누락")
        at = re.search(r"(?:^|[{,\n]\s*)at\s*:\s*([^,}\n]+)", fields["generated"])
        if at and not valid_iso_datetime(at.group(1)):
            fails.append("generated.at은 ISO 8601 datetime이어야 함")

    if "verified" in fields:
        verified = fields["verified"]
        blocks = list_item_blocks(verified)
        checks = blocks or [verified]
        for index, event in enumerate(checks, 1):
            if not mapping_has(event, "by"):
                fails.append(f"verified 이벤트 {index}의 by 누락")
            at = re.search(r"(?:^|[{,\n]\s*)at\s*:\s*([^,}\n]+)", event)
            if not at:
                fails.append(f"verified 이벤트 {index}의 at 누락")
            elif not valid_iso_datetime(at.group(1)):
                fails.append(f"verified 이벤트 {index}의 at은 ISO 8601 datetime이어야 함")

    if clean_scalar(fields.get("type", "")) == "Attested Computation":
        if not clean_scalar(fields.get("runtime", "")):
            fails.append("Attested Computation에는 runtime 필수")
        if not clean_scalar(fields.get("computation", "")) and "# Computation" not in body:
            fails.append("Attested Computation에는 computation 경로 또는 # Computation 본문 필수")

    ids: set[str] = set()
    if "sources" in fields:
        ids = source_ids(fields["sources"], fails)
    prose = strip_code(body)
    footnote_uses = set(re.findall(r"\[\^([^\]]+)\]", prose))
    footnote_defs = set(re.findall(r"(?m)^\[\^([^\]]+)\]:", body))
    for label in sorted(footnote_uses - footnote_defs):
        fails.append(f"각주 정의 누락: [^{label}]")
    for label in sorted(footnote_defs - ids):
        fails.append(f"각주 [^{label}]에 대응하는 sources[].id 없음")
    for source_id in sorted(ids & footnote_uses - footnote_defs):
        fails.append(f"sources id `{source_id}`의 각주 정의 누락")
    if "## 출처" in body:
        if "sources" not in fields:
            fails.append("v0.1 `## 출처`만 존재 — OKF v0.2 sources로 이관 필요")
        else:
            warns.append("`## 출처`는 v0.1 호환 섹션 — 중복이면 제거 권장")

    prose_text = strip_code(text)
    if "(검증 필요)" in prose_text:
        fails.append(f"'(검증 필요)' 마커 {prose_text.count('(검증 필요)')}건 잔존")
    if re.search(r"<!--\s*대상독자:", text):
        fails.append("워크스페이스 대상독자 메타 주석 잔존")
    if text.count("```") % 2:
        fails.append("코드펜스(```) 짝 불일치")
    for match in re.finditer(r"[)\]]\*\*[가-힣]", prose_text):
        fails.append(f"깨진 강조: …{text[max(0, match.start()-15):match.end()+5]}…")
    for match in re.finditer(r"[\"\u201d\u2019']\*\*[가-힣]", prose_text):
        warns.append(f"강조 인접 따옴표 — 렌더 확인: …{text[max(0, match.start()-15):match.end()+5]}…")
    for match in re.finditer(r"~(?=[0-9])", prose_text):
        warns.append(f"물결 표기 — 근사 '약 N', 범위 'N–M' 권장: …{text[max(0, match.start()-10):match.end()+8]}…")

    if inventory and inventory.exists():
        # 인벤토리는 `이름.md`로, 위키링크는 [[이름]]으로 적힌다 — 확장자를 떼고 대조한다.
        # 안 떼면 전건이 오탐으로 떠서 진짜 깨진 링크가 경고 더미에 묻힌다.
        known = {re.sub(r"\.md$", "", os.path.basename(item))
                 for item in re.findall(r"`([^`]+)`", inventory.read_text(encoding="utf-8"))}
        for target in set(re.findall(r"\[\[([^\]|#]+)", text)):
            if target.strip() not in known:
                warns.append(f"[[{target.strip()}]] 대상 미존재 — 의도적 stub인지 확인")

    return fails, warns


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("사용: validate-note.py <final.md> [inventory.md]", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"입력 파일 없음: {path}", file=sys.stderr)
        return 2
    inventory = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    fails, warns = validate(path, inventory)
    for warning in warns:
        print(f"⚠️  {warning}")
    for failure in fails:
        print(f"❌ {failure}")
    if fails:
        print("GATE: FAIL")
        return 1
    print("GATE: PASS" + (f" (경고 {len(warns)})" if warns else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
