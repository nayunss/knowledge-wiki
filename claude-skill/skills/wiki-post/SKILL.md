---
name: wiki-post
description: IT 기술 글을 작성→검증→발행까지 한 번에 처리하는 knowledge-wiki 오케스트레이터. "~에 대해 글 써서 위키에 올려줘", "기술 글 작성해서 발행해줘", "위키 글 파이프라인", "글 다시 검증해서 올려줘", "이전 글 수정해서 재발행", "가독성/최종 검수만 다시" 등 작성+발행이 함께 요청되면 반드시 이 스킬을 사용. (작성 없이 이미 완성된 노트를 올리기만 할 땐 wiki-note 스킬.)
---

# wiki-post — 작성→검증→발행 오케스트레이터

tech-writer가 쓰고, fact-checker·copy-editor가 병렬 검증하고, 병합본을 readability-reviewer가 최종 검수한 뒤 wiki-note 방식으로 발행한다.
**실행 모드: 서브 에이전트 파이프라인** (검증 2종만 병렬). 데이터 전달: 파일 기반(`_workspace/`).

## Phase 0: 컨텍스트 확인

작업 폴더: `{scratchpad}/wiki-post-workspace/` (= `_workspace`).
- `_workspace` 있음 + 부분 수정 요청("검증만 다시", "윤문만", "가독성/최종 검수만 다시") → **부분 재실행**: 해당 에이전트만 재호출(예: "가독성만 다시" → Phase 3.5의 readability-reviewer만).
- `_workspace` 있음 + 새 주제 → 기존을 `_workspace_prev/`로 이동 후 **새 실행**.
- 없음 → **초기 실행**.

## Phase 1: 작성

0. **선행 리서치 (선택)** — 원문 정독·배경 조사·deep-research를 앞단에 붙일 때. 산출 = `_workspace/00_research.md` 등. **리서치 프롬프트에 아래 둘을 반드시 넣는다:**
   - **엣지를 만들지 마라.** 사실을 수집하되 사실 사이의 **인과·비교·일반화**는 만들지 않는다 — 그건 작가의 일이고 원문 근거가 필요하다. 특히 **출처가 다른 수치끼리 비교 금지**(척도·측정 체제가 다르면 대소 자체가 성립하지 않는다). 1차 출처 우선·URL 필수·확인 못한 건 "확인 불가"로 명시.
   - **산출 파일 맨 위에 자기 경고를 박게 한다** (아래 형식 그대로). 이게 없으면 하류가 1차 소스처럼 쓴다. **실측**: 경고를 단 `00_critique_leads.md`는 작가가 지켰고, 경고 없던 `00_research.md`의 척도 비교는 초안까지 전파돼 FAIL이 됐다.

   ```markdown
   > ⚠️ **1차 소스 아님.** 리서치 산출물이며 오류가 있을 수 있다.
   > 여기 적힌 비교·인과·일반화는 **가설**이다 — 1차 출처에 직접 대조해 확인한 뒤에만 쓸 것.
   > 그대로 옮겨 쓰지 마라. (wiki-verify §2 ⑦)
   ```

   tech-writer에 넘길 땐 **"가설 목록"으로 명시**하고 리드를 그대로 옮기지 말라고 지시한다. fact-checker에는 이 파일이 검증 대상임을(⑦) 알린다.
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
   FAIL(마커 잔존·frontmatter 누락·메타주석·펜스 불일치) 시 병합을 고치고 재실행 — 게이트 통과 전엔 Phase 3.5 진입 금지.

## Phase 3.5: 최종 가독성 게이트

기계 게이트(validate-note.py)는 결함을 막지만 **읽기 경험**은 못 본다. 발행 직전, 병합본을 독자 눈으로 최종 판정한다.

1. **Agent 호출**: `readability-reviewer` (model: opus, readability-review 스킬을 따르게 한다). 입력 = `03_final.md`. 산출 = `03b_readability_report.md`.
2. **PASS/PASS-WITH-NOTES** → 🟡 지적은 오케스트레이터 재량으로 `03_final.md`에 반영(문체·용어 표현·흐름만, 사실·수치·링크·마커 불가침) → 병합 게이트(validate-note.py) **재실행** → Phase 4.
3. **FAIL** → 지적을 라우팅: 문체·AI 티·문장 → `copy-editor` 재호출(해당 구간 재윤문), 용어 풀이 누락 → `tech-writer` 재호출(보강). 수정본을 `03_final.md`에 병합 → 병합 게이트 재실행 → `readability-reviewer` 재검수. **최대 2회**, 그래도 FAIL이면 발행 중단하고 쟁점을 사용자에게 보고.
4. 이 게이트의 제안이 사실·수치를 건드리는 것으로 보이면 **적용하지 말고** fact-checker 소관으로 리포트에만 남긴다(가독성 게이트는 문체 층위만 바꾼다).

## Phase 4: 발행

**wiki-note 스킬의 절차를 그대로 따른다** (재구현 금지):
temp clone → `content/`(AI 엔지니어링 주제는 `content/ai-엔지니어링/`)에 `03_final.md` 배치 → 홈 `index.md` 카드/시작점 갱신 → commit → **rebase-retry push**(최대 5회) → temp 삭제 → 배포 확인(실패 시 `gh workflow run deploy.yml -R <owner>/<repo>` 재시도 — `<owner>/<repo>`는 `~/.claude/wiki-note-repo.txt`의 주소에서 딴다).

## Phase 5: 완료 보고

사용자에게: 발행 URL, 검증 요약(fact·copy·**가독성** 3종 판정·주요 지적·UNVERIFIED 목록), 수정 루프 횟수. `_workspace`는 보존(감사 추적).

### 규칙 ⑥ 측정 (2026-07-17~, 판정 나면 이 절 삭제)

⑥(tech-writing '연결의 근거')은 **아직 검증되지 않은 가설**이다. 근거가 n=1이라 안 먹힐 수 있다. 매 편 재고 판정한다.

1. **FAIL을 분류하라** — 팩트 FAIL이 났으면 `수치`(틀린 값) / `해석`(맞는 값 위의 틀린 인과·비교·일반화) / `기타` 중 무엇이었는지 보고에 명시한다. FAIL이 없었으면 "FAIL 없음"도 데이터다.
2. **원장에 남겨라** — 위키 `content/위키-하네스.md`의 "실전 기록" 표에 한 줄 추가한다(발행과 같은 커밋). 표 아래 카운터도 갱신.
3. **3편이 모이면 판정하라** — ⑥ 이후 3편 기준:
   - 해석 FAIL 0~1편 → ⑥ 유효. 이 절을 지우고 CLAUDE.md 이력에 결과를 남긴다.
   - 해석 FAIL 2편 이상 → **규칙이 아니라 구조 문제.** 규칙을 더 세게 쓰지 마라 — 작성 단계의 구조(초안 전 주장 추출, 게이트 위치)를 사용자와 다시 논의한다.
   - 셋 다 FAIL 자체가 없으면 → 표본 부족. 계속 센다.

**주의**: 규칙이 생겼다고 FAIL을 관대하게 판정하지 마라. 측정이 오염된다. fact-checker는 ⑥의 존재를 모른 채 평소대로 반증한다.

## 에러 핸들링

| 상황 | 처리 |
|---|---|
| 에이전트 1회 실패 | 1회 재시도 → 재실패 시 해당 검증 SKIP으로 진행하되 보고에 명시 |
| 검증 2회 루프 후에도 FAIL | 발행 중단, 쟁점 보고 (강행은 사용자 승인 필요) |
| 가독성 게이트 과검열(사소한 취향 지적으로 FAIL) | ⚪ 참고로 내려 발행 진행 — 잔존 AI 티보다 발행 지연이 나쁠 때. 리포트에 남긴다 |
| push 충돌 | wiki-note의 rebase-retry. 같은 파일 충돌 시 최신 재클론 후 재적용 |
| 배포 flake | workflow_dispatch 재실행 1회 |

## 테스트 시나리오

- **정상**: "WebAssembly 서버사이드 활용에 대해 글 써서 위키에 올려줘" → 초안 → 병렬 검증 PASS → 병합·게이트 → 가독성 게이트 PASS → 발행 → URL 보고.
- **에러(팩트)**: 초안에 낡은 버전 정보 → fact-checker FAIL → tech-writer 수정 → 재검증 PASS → 발행. 2회 초과 시 중단·보고.
- **에러(가독성)**: 병합본에 풀이 없는 난해 용어·잔존 번역투 → readability-reviewer FAIL → 용어는 tech-writer 보강·문체는 copy-editor 재윤문 → 병합 게이트 재실행 → 재검수 PASS → 발행.
- **부분 재실행**: "방금 글 가독성만 다시 봐줘" → Phase 0에서 `_workspace` 감지 → Phase 3.5의 readability-reviewer만 재호출 → 리포트 갱신.
