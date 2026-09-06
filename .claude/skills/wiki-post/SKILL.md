---
name: wiki-post
description: IT 기술 글을 작성→검증→발행까지 한 번에 처리하는 knowledge-wiki 오케스트레이터. "~에 대해 글 써서 위키에 올려줘", "기술 글 작성해서 발행해줘", "위키 글 파이프라인", "글 다시 검증해서 올려줘", "이전 글 수정해서 재발행", "가독성/최종 검수만 다시" 등 작성+발행이 함께 요청되면 반드시 이 스킬을 사용. (작성 없이 이미 완성된 노트를 올리기만 할 땐 wiki-note 스킬.)
---

# wiki-post — 작성→검증→발행 오케스트레이터

tech-writer가 쓰고, fact-checker·copy-editor가 병렬 검증하고, 병합본을 readability-reviewer가 최종 검수한 뒤 wiki-note 방식으로 발행한다.
**실행 모드: 서브 에이전트 파이프라인** (검증 2종만 병렬). 데이터 전달: 파일 기반(`_workspace/`).

## Phase 0: 컨텍스트 확인

0. **의존성 프리플라이트** — 실행 전에 다음 구성요소를 확인한다.
   - 필수 에이전트: `tech-writer`, `fact-checker`, `copy-editor`, `readability-reviewer`
   - 필수 스킬: `tech-writing`, `wiki-verify`, `readability-review`, `wiki-note`, `wiki-debug`
   - 필수 게이트: `wiki-post/scripts/validate-domain-brief.py`, `wiki-post/scripts/validate-note.py`
   - 선택 의존성: `humanize-korean`. 없으면 copy-editor의 자체 최소 윤문 폴백을 쓰고 리포트에 기록한다.

   ```bash
   python3 ~/.claude/skills/wiki-post/scripts/preflight.py ~/.claude
   ```

   필수 구성요소가 없으면 **발행을 시작하지 않는다.** 위키 레포의 `claude-skill/install.sh`로 설치한 뒤 다시 프리플라이트한다. 필수 검증을 SKIP하고 발행하는 폴백은 없다.

작업 폴더: `{scratchpad}/wiki-post-workspace/` (= `_workspace`).
- `_workspace` 있음 + 부분 수정 요청("검증만 다시", "윤문만", "가독성/최종 검수만 다시") → **부분 재실행**: 해당 에이전트만 재호출(예: "가독성만 다시" → Phase 3.5의 readability-reviewer만).
- `_workspace` 있음 + 새 주제 → 기존을 `_workspace_prev/`로 이동 후 **새 실행**.
- 없음 → **초기 실행**.

## Phase 1: 작성

0. **상류 산출물 (선행 리서치·사실 추출·토론 등)** — 원문 정독·배경 조사·deep-research를 앞단에 붙이거나, 오케스트레이터가 직접 사실을 정리할 때. 산출 = `_workspace/00_research.md`·`00_source.md`·`00_session_facts.md`·`00_debate_*.md` 등.

   **아래 둘은 `_workspace/00_*.md` 전부에 걸린다 — 서브에이전트가 만든 것이든 오케스트레이터가 자기 손으로 쓴 것이든 같다.** 리서치를 시킬 땐 프롬프트에 넣고, 네가 직접 쓸 땐 네가 지킨다:
   - **엣지를 만들지 마라.** 사실을 수집하되 사실 사이의 **인과·비교·일반화**는 만들지 않는다 — 그건 작가의 일이고 원문 근거가 필요하다. 특히 **출처가 다른 수치끼리 비교 금지**(척도·측정 체제가 다르면 대소 자체가 성립하지 않는다). 1차 출처 우선·URL 필수·확인 못한 건 "확인 불가"로 명시.
   - **산출 파일 맨 위에 자기 경고를 박는다** (아래 형식 그대로). 이게 없으면 하류가 1차 소스처럼 쓴다. **실측**: 경고를 단 `00_critique_leads.md`는 작가가 지켰고, 경고 없던 `00_research.md`의 척도 비교는 초안까지 전파돼 FAIL이 됐다.

   ```markdown
   > ⚠️ **1차 소스 아님.** 상류 산출물이며 오류가 있을 수 있다.
   > 여기 적힌 비교·인과·일반화는 **가설**이다 — 1차 출처에 직접 대조해 확인한 뒤에만 쓸 것.
   > 문장에 붙은 `[의견]`·`[확인 불가]`·`(추정)` 라벨은 **떼지 말고 함께 옮겨라.**
   > 그대로 옮겨 쓰지 마라. (wiki-verify §2 ⑦)
   ```

   **문장 단위 라벨도 보존 대상이다.** 상류가 개별 주장에 단 `[의견]`·`[확인 불가]`·`(추정)` 같은 표시는 파일 헤더와 **별개로** 하류까지 따라가야 한다. 헤더는 "이 파일이 1차 소스가 아니다"까지만 말하고 문장의 지위는 규정하지 않는다 — ai-prd 편에서 토론 파일 6개 **전부** 헤더를 달고 있었고 문제의 두 주장에 라벨까지 정확히 붙어 있었는데, 초안이 **라벨만 떨어뜨리고 내용을 가져와** FAIL이 났다.

   tech-writer에 넘길 땐 **"가설 목록"으로 명시**하고 리드를 그대로 옮기지 말라고 지시한다. fact-checker에는 이 파일이 검증 대상임을(⑦) 알린다.

   > **실측(15편 전수, 2026-08-30)**: ⑦ 상류 오염이 관여한 편이 8/15. 오염이 FAIL까지 간 4편 중 **셋이 오케스트레이터 자신이 만든 파일**에서 발원했다(`00_source.md`·`00_debate_*.md`·`00_session_facts.md`). 막힌 쪽은 전부 경고 헤더를 단 리서치 산출물이었다. 검증(⑦)은 오케스트레이터 산출물을 이미 대상에 넣고 있었는데 예방(경고 헤더)만 리서치에 걸려 있던 것이 이 구멍이다.
1. 위키 최신 상태 파악: 레포(`~/.claude/wiki-note-repo.txt`)를 temp clone해 기존 노트 목록·frontmatter를 수집 → `_workspace/00_wiki_inventory.md` (링크 걸 관련 노트 파악용). **각 줄에 파일명을 백틱으로도 함께 적는다** — 병합 게이트가 백틱 안의 이름만 읽으므로 이게 없으면 위키링크 전건이 오탐으로 뜬다.

   ```
   - [[이름]] (`이름.md`) — title: … | date: … | tags: …
   ```
2. **Agent 호출**: `tech-writer` (model: opus). 입력 = 주제 + 인벤토리 + (사용자 제공 자료). tech-writing 스킬을 따르게 한다. 본문 전에 **도메인 캘리브레이션**(tech-writing §0)을 수행하게 한다.
3. 산출: `_workspace/00_domain_brief.md` + `_workspace/01_writer_draft.md` (대상 독자·도메인·작성일 메타 필수 — 오늘 날짜). 아래 게이트를 통과하지 못하면 브리프를 보완하며 Phase 2로 넘어가지 않는다.
   ```bash
   python3 ~/.claude/skills/wiki-post/scripts/validate-domain-brief.py _workspace/00_domain_brief.md
   python3 ~/.claude/skills/wiki-post/scripts/validate-note.py --render-only _workspace/01_writer_draft.md
   ```
4. **렌더 게이트 출력을 copy-editor 입력에 그대로 첨부한다.** `--render-only`는 초안용 모드라 프론트매터·마커·각주 계약은 보지 않고 렌더 파손(깨진 강조·물결 취소선·펜스 짝)만 본다. 이걸 앞에서 돌려야 copy-editor가 정규식으로 될 일을 손으로 훑지 않고 문체에 시간을 쓴다(wiki-verify §3). FAIL이면 초안 단계에서 먼저 고친다 — 뒤로 미룰수록 같은 결함을 더 많은 눈이 지나친다.

## Phase 2: 검증 (병렬)

**Agent 병렬 호출** (`run_in_background: true`, 둘 다 model: opus, wiki-verify 스킬을 따르게 한다):
- `fact-checker` → `02_factcheck_report.md` (최신성 §1 + 팩트 §2 + 도메인·용어 §2.5)
- `copy-editor` → `02_edited_draft.md` + `02_editing_report.md` (오탈자 §3 + 윤문 §4)

## Phase 3: 판정·수정 루프

1. 두 리포트 판정 수집.
2. **모두 PASS/PASS-WITH-NOTES** → 병합: `02_edited_draft.md`(윤문본)에 팩트 지적의 각주/수정 반영 + 검증 통과한 `(검증 필요)` 마커와 그 옆 `(1차 확인 시도: …)` 기록 제거 + 선두 워크스페이스 메타 주석 제거 → `03_final.md`는 **발행 준비 완료본**이어야 한다. Phase 4는 이 파일을 그대로 배치만 한다.
3. **FAIL 있음** → `tech-writer` 재호출(수정 모드) → FAIL 항목만 해당 검증자로 재검증. **최대 2회**, 그래도 FAIL이면 중단하고 쟁점을 사용자에게 보고.

   **재호출은 국소 패치다 — 초안을 다시 쓰게 하지 마라.** 입력은 ⑴ FAIL 항목과 근거, ⑵ 그 문장이 든 **절만**, ⑶ 판정에 필요한 **원문 발췌만**(전문 아님). 산출도 그 절만 받아 오케스트레이터가 갈아 끼운다. 원문 전문·초안 전문을 다시 실으면 재호출이 초안 작성과 같은 값이 되고, 손대지 않아도 될 문장이 바뀌어 재검증 범위까지 넓어진다.
   - **실측**: 재호출 52–90k는 초안 작성 45–95k와 거의 같다. AIDE² 편이 비쌌던 것도 글이 길어서가 아니라 원문 약 30k를 작성·검증·재검증이 각각 다시 읽어서였다.
   - 원문 전문을 쓰는 편이면 Phase 1에서 `_workspace/00_source_verbatim.md`로 한 번만 떨궈두고, 이후 단계엔 **해당 발췌**를 인용해 넘긴다.
   - FAIL이 글의 뼈대(논지·구조)를 흔드는 경우만 예외 — 그때는 절 단위로 못 고치므로 범위를 넓히되, 넓힌 이유를 리포트에 남긴다.
4. 병합 충돌(같은 문장을 팩트·윤문이 다르게 수정) 시 **팩트 수정 우선**.
5. **병합 게이트 (필수)** — 병합도 작업이므로 검증한다(MAST '작업 검증 실패' 방지). `03_final.md`에 대해 실행:
   ```bash
   python3 ~/.claude/skills/wiki-post/scripts/validate-note.py _workspace/03_final.md _workspace/00_wiki_inventory.md
   ```
   FAIL(마커 잔존·frontmatter 누락·메타주석·펜스 불일치) 시 병합을 고치고 재실행 — 게이트 통과 전엔 Phase 3.5 진입 금지.

## Phase 3.5: 최종 가독성 게이트

기계 게이트(validate-note.py)는 결함을 막지만 **읽기 경험**은 못 본다. 발행 직전, 병합본을 독자 눈으로 최종 판정한다.

1. **Agent 호출**: `readability-reviewer` (model: opus, readability-review 스킬을 따르게 한다). 입력 = `03_final.md` + 도메인·용어 기준용 `00_domain_brief.md` + 대상 독자 확인용 `01_writer_draft.md`. 산출 = `03b_readability_report.md`.
2. **PASS/PASS-WITH-NOTES** → 🟡 지적은 오케스트레이터 재량으로 `03_final.md`에 반영(문체·용어 표현·흐름만, 사실·수치·링크·마커 불가침) → 병합 게이트(validate-note.py) **재실행** → Phase 4.
3. **FAIL** → 지적을 라우팅: 문체·AI 티·문장 → `copy-editor` 재호출(해당 구간 재윤문), 용어 풀이 누락 → `tech-writer` 재호출(보강). 수정본을 `03_final.md`에 병합 → 병합 게이트 재실행 → `readability-reviewer` 재검수. **최대 2회**, 그래도 FAIL이면 발행 중단하고 쟁점을 사용자에게 보고.
4. 이 게이트의 제안이 사실·수치를 건드리는 것으로 보이면 **적용하지 말고** fact-checker 소관으로 리포트에만 남긴다(가독성 게이트는 문체 층위만 바꾼다).

## Phase 4: 발행

**wiki-note 스킬의 절차를 그대로 따른다** (재구현 금지):
temp clone → `content/`(AI 엔지니어링 주제는 `content/ai-엔지니어링/`)에 `03_final.md` 배치 → 홈 `index.md` 카드/시작점 갱신(**새 카드에 `data-date="YYYY-MM-DD"` 필수** — 이게 없으면 NEW 뱃지가 안 붙는다) → commit → **rebase-retry push**(최대 5회) → temp 삭제 → 배포 확인(실패 시 `gh workflow run deploy.yml -R <owner>/<repo>` 재시도 — `<owner>/<repo>`는 `~/.claude/wiki-note-repo.txt`의 주소에서 딴다).

## Phase 5: 완료 보고

사용자에게: 발행 URL, 검증 요약(fact·copy·**가독성** 3종 판정·주요 지적·UNVERIFIED 목록), 수정 루프 횟수. `_workspace`는 보존(감사 추적).

### 규칙 ⑥ 원장 기록 (측정 완료 2026-07-19, ⑥ 확정: 유효)

⑥(tech-writing '연결의 근거')은 **측정을 거쳐 유효로 확정**됐다(6편 창, 해석 FAIL 1편뿐 + 비토론형 해석 고밀도 편 turbovec-벡터압축이 확정 조건을 채움 — [[위키-하네스]] 창 상태 6편 참). 판정 machinery는 종료. 다만 **회귀 계측은 계속**한다:

1. **FAIL을 분류하라** — 팩트 FAIL이 났으면 `수치`(틀린 값) / `해석`(맞는 값 위의 틀린 인과·비교·일반화) / `기타` 중 무엇이었는지 보고에 명시한다. FAIL이 없었으면 "FAIL 없음"도 데이터다.
2. **원장에 남겨라** — 위키 `content/위키-하네스.md`의 "실전 기록" 표에 한 줄 추가(발행과 같은 커밋). ⑥ 카운터 표도 갱신. **`wiki-debug` 스킬로 진단·행 초안을 받는다** — 특히 원장 행을 쓰기 전 **현재 원격 원장을 다시 읽어** 순번·창 상태·다른 세션의 추가를 재대조한다(낡은 상태에 쓰면 push 충돌·중복이 난다. tinker-cookbook 편 실측).
3. **해석 FAIL이 다시 몰리면**(예: 2편 연속) 재고한다 — ⑥이 회귀했거나 규칙이 아니라 구조 문제일 수 있다. 그땐 규칙을 세게 쓰지 말고 작성 단계 구조를 사용자와 논의.

**주의**: 확정됐다고 FAIL을 관대하게 판정하지 마라. 계측이 오염된다. fact-checker는 ⑥의 존재를 모른 채 평소대로 반증한다.

## 에러 핸들링

| 상황 | 처리 |
|---|---|
| 작성 에이전트 1회 실패 | 1회 재시도 → 재실패 시 중단하고 보고 |
| 필수 검증 에이전트 실패 | 1회 재시도 → 재실패 시 발행 중단. **SKIP 발행 금지** |
| 선택 humanize-korean 실패 | copy-editor 자체 최소 윤문으로 폴백하고 리포트에 명시 |
| 검증 2회 루프 후에도 FAIL | 발행 중단, 쟁점 보고 (강행은 사용자 승인 필요) |
| 가독성 게이트 과검열(사소한 취향 지적으로 FAIL) | ⚪ 참고로 내려 발행 진행 — 잔존 AI 티보다 발행 지연이 나쁠 때. 리포트에 남긴다 |
| push 충돌 | wiki-note의 rebase-retry. 같은 파일 충돌 시 최신 재클론 후 재적용 |
| 배포 flake | workflow_dispatch 재실행 1회 |

## 테스트 시나리오

- **정상**: "WebAssembly 서버사이드 활용에 대해 글 써서 위키에 올려줘" → 초안 → 병렬 검증 PASS → 병합·게이트 → 가독성 게이트 PASS → 발행 → URL 보고.
- **에러(팩트)**: 초안에 낡은 버전 정보 → fact-checker FAIL → tech-writer 수정 → 재검증 PASS → 발행. 2회 초과 시 중단·보고.
- **에러(가독성)**: 병합본에 풀이 없는 난해 용어·잔존 번역투 → readability-reviewer FAIL → 용어는 tech-writer 보강·문체는 copy-editor 재윤문 → 병합 게이트 재실행 → 재검수 PASS → 발행.
- **부분 재실행**: "방금 글 가독성만 다시 봐줘" → Phase 0에서 `_workspace` 감지 → Phase 3.5의 readability-reviewer만 재호출 → 리포트 갱신.
