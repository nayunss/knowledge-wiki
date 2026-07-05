#!/usr/bin/env python3
"""발행 전 결정적 검증 게이트 (경량 인터셉터).
근거: MAST '작업 검증 실패' 범주 + 오류 전파 차단 — [[에이전트-평가-evals]] 노트의 원칙을 하네스 자신에 적용.
사용: python3 validate-note.py <final.md> [inventory.md]  → exit 0(PASS) / 1(FAIL)
"""
import re, sys, os

def main():
    path = sys.argv[1]
    inv = sys.argv[2] if len(sys.argv) > 2 else None
    s = open(path, encoding="utf-8").read()
    fails, warns = [], []

    # 1) frontmatter 스키마 (OKF)
    m = re.match(r"^---\n(.*?)\n---", s, re.S)
    if not m:
        fails.append("frontmatter 없음")
    else:
        fm = m.group(1)
        for k in ("title:", "type:", "description:"):
            if k not in fm:
                fails.append(f"frontmatter {k} 누락")

    # 2) 워크스페이스 잔여물
    if s.lstrip().startswith("<!--"):
        fails.append("워크스페이스 메타 주석(<!--)이 파일 선두에 잔존")
    if "(검증 필요)" in s:
        fails.append(f"'(검증 필요)' 마커 {s.count('(검증 필요)')}건 잔존 — 검증 후 제거/완화 필요")

    # 2.5) 마크다운 렌더 검증 (발행물에서 리터럴 ** 노출 사고 재발 방지)
    for mm in re.finditer(r"[)\]]\*\*[가-힣]", s):
        fails.append(f"깨진 강조(닫는 ** 앞 괄호+뒤 한글): …{s[max(0,mm.start()-15):mm.end()+5]}…")
    for mm in re.finditer(r"[\"\u201d\u2019']\*\*[가-힣]", s):
        warns.append(f"강조 인접 따옴표 — 렌더 확인 필요: …{s[max(0,mm.start()-15):mm.end()+5]}…")
    for mm in re.finditer(r"~(?=[0-9])", s):
        warns.append(f"물결 표기 발견(근사→약 N, 범위→N–M 권장, GFM 취소선 위험): …{s[max(0,mm.start()-10):mm.end()+8]}…")

    # 3) 구조 필수 요소
    if "## 출처" not in s and "resource:" not in (m.group(1) if m else ""):
        warns.append("`## 출처` 섹션 없음 (외부 주장 없는 메타 노트면 무시 가능)")
    if s.count("```") % 2 != 0:
        fails.append("코드펜스(```) 짝 불일치")

    # 4) 위키링크 — 대상 없으면 경고만 (stub는 설계상 허용)
    if inv and os.path.exists(inv):
        known = set(re.findall(r"`([^`]+)`", open(inv, encoding="utf-8").read()))
        known = {os.path.basename(k) for k in known}
        for t in set(re.findall(r"\[\[([^\]|#]+)", s)):
            if t.strip() not in known and not any(t.strip() == os.path.basename(k) for k in known):
                warns.append(f"[[{t.strip()}]] 대상 미존재 (의도적 stub인지 확인)")

    for w in warns:
        print(f"⚠️  {w}")
    if fails:
        for f in fails:
            print(f"❌ {f}")
        print("GATE: FAIL")
        sys.exit(1)
    print("GATE: PASS" + (f" (경고 {len(warns)})" if warns else ""))

if __name__ == "__main__":
    main()
