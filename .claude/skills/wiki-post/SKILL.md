---
name: wiki-post
description: IT 기술 글을 작성→검증→발행까지 한 번에 처리하는 knowledge-wiki 오케스트레이터. "~에 대해 글 써서 위키에 올려줘", "기술 글 작성해서 발행해줘", "위키 글 파이프라인", "글 다시 검증해서 올려줘", "이전 글 수정해서 재발행" 등 작성+발행이 함께 요청되면 반드시 이 스킬을 사용. (작성 없이 이미 완성된 노트를 올리기만 할 땐 wiki-note 스킬.)
---

# wiki-post — 작성→검증→발행 오케스트레이터

tech-writer가 쓰고, fact-checker·copy-editor가 병렬 검증하고, 통과하면 wiki-note 방식으로 발행한다.
**실행 모드: 서브 에이전트 파이프라인** (검증 2종만 병렬). 데이터 전달: 파일 기반(`_workspace/`).

## Phase 0: 컨텍스트 확인

작업 폴더: `{scratchpad}/wiki-post-workspace/` (= `_workspace`).
- `_workspace` 있음 + 부분 수정 요청("검증만 다시", "윤문만") → **부분 재실행**: 해당 에이전트만 재호출.
- `_workspace` 있음 + 새 주제 → 기존을 `_workspace_prev/`로 이동 후 **새 실행**.
- 없음 → **초기 실행**.

## Phase 1: 작성

1. 위키 최신 상태 파악: 레포(`~/.claude/wiki-note-repo.txt`)를 temp clone해 기존 노트 목록·frontmatter를 수집 → `_workspace/00_wiki_inventory.md` (링크 걸 관련 노트 파악용).
2. **Agent 호출**: `tech-writer` (model: opus). 입력 = 주제 + 인벤토리 + (사용자 제공 자료). tech-writing 스킬을 따르게 한다.
3. 산출: `_workspace/01_writer_draft.md` (작성일 메타 필수 — 오늘 날짜).

## Phase 2: 검증 (병렬)

**Agent 병렬 호출** (`run_in_background: true`, 둘 다 model: opus, wiki-verify 스킬을 따르게 한다):
- `fact-checker` → `02_factcheck_report.md` (최신성 §1 + 팩트 §2)
- `copy-editor` → `02_edited_draft.md` + `02_editing_report.md` (오탈자 §3 + 윤문 §4)

## Phase 3: 판정·수정 루프

1. 두 리포트 판정 수집.
2. **모두 PASS/PASS-WITH-NOTES** → 병합: `02_edited_draft.md`(윤문본)에 팩트 지적의 각주/수정 반영 + 검증 통과한 `(검증 필요)` 마커 제거 + 선두 워크스페이스 메타 주석 제거 → `03_final.md`는 **발행 준비 완료본**이어야 한다. Phase 4는 이 파일을 그대로 배치만 한다.
3. **FAIL 있음** → `tech-writer` 재호출(수정 모드, FAIL 항목 전달) → FAIL 항목만 해당 검증자로 재검증. **최대 2회**, 그래도 FAIL이면 중단하고 쟁점을 사용자에게 보고.
4. 병합 충돌(같은 문장을 팩트·윤문이 다르게 수정) 시 **팩트 수정 우선**.
5. **병합 게이트 (필수)** — 병합도 작업이므로 검증한다(MAST '작업 검증 실패' 방지). `03_final.md`에 대해 실행:
   ```bash
   python3 ~/.claude/skills/wiki-post/scripts/validate-note.py _workspace/03_final.md _workspace/00_wiki_inventory.md
   ```
   FAIL(마커 잔존·frontmatter 누락·메타주석·펜스 불일치) 시 병합을 고치고 재실행 — 게이트 통과 전엔 Phase 4 진입 금지.

## Phase 4: 발행

**wiki-note 스킬의 절차를 그대로 따른다** (재구현 금지):
temp clone → `content/`(AI 엔지니어링 주제는 `content/ai-엔지니어링/`)에 `03_final.md` 배치 → 홈 `index.md` 카드/시작점 갱신 → commit → **rebase-retry push**(최대 5회) → temp 삭제 → 배포 확인(실패 시 `gh workflow run deploy.yml -R nayunss/knowledge-wiki` 재시도).

## Phase 5: 완료 보고

사용자에게: 발행 URL, 검증 요약(판정·주요 지적·UNVERIFIED 목록), 수정 루프 횟수. `_workspace`는 보존(감사 추적).

## 에러 핸들링

| 상황 | 처리 |
|---|---|
| 에이전트 1회 실패 | 1회 재시도 → 재실패 시 해당 검증 SKIP으로 진행하되 보고에 명시 |
| 검증 2회 루프 후에도 FAIL | 발행 중단, 쟁점 보고 (강행은 사용자 승인 필요) |
| push 충돌 | wiki-note의 rebase-retry. 같은 파일 충돌 시 최신 재클론 후 재적용 |
| 배포 flake | workflow_dispatch 재실행 1회 |

## 테스트 시나리오

- **정상**: "WebAssembly 서버사이드 활용에 대해 글 써서 위키에 올려줘" → 초안 → 병렬 검증 PASS → 발행 → URL 보고.
- **에러**: 초안에 낡은 버전 정보 → fact-checker FAIL → tech-writer 수정 → 재검증 PASS → 발행. 2회 초과 시 중단·보고.
