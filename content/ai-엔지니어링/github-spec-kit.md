---
title: GitHub spec-kit — 명세 주도 개발(SDD) 툴킷 해부
type: 도구
description: spec-kit v0.12.11을 실제로 설치해 뜯어본 기록. 워크플로·강제 메커니즘·트레이드오프와 superpowers·ideas-come-true와의 비교, 그리고 "우리 팀에 도입할 것인가"에 대한 답.
tags: [spec-driven-development, 코딩에이전트, sdlc, 도구비교]
resource: https://github.com/github/spec-kit
date: 2026-07-11
---

프롬프트 한 줄로 기능을 만들어달라고 하면 에이전트는 만들어준다. 문제는 그다음이다. 무엇을 만들기로 했는지가 어디에도 남지 않아서, 다음 세션의 에이전트는 어제의 결정을 모른다. spec-kit은 이 구멍을 "명세를 파일로 남기고, 파일을 게이트로 삼는다"로 메운다.

## 핵심 주장

**spec-kit은 방법론이 아니라 강제 장치다.** 명세 주도 개발(SDD, Spec-Driven Development — 코드보다 명세를 먼저 확정하고 명세를 소스 오브 트루스로 삼는 방식)이라는 아이디어 자체는 새롭지 않다. spec-kit의 실질은 그 아이디어를 **파일 구조·템플릿 게이트·읽기 전용 감사**로 못박아, 에이전트가 건너뛰지 못하게 만든 프로젝트 스캐폴드라는 점이다. 얻는 것은 규율과 재현성. 내는 것은 토큰과 리드타임, 경직성이다. 기능 하나가 반나절짜리인 팀에는 과하고, 명세 불일치가 며칠을 태우는 팀에는 싸다.

다만 미리 밝혀둔다. **"명세를 먼저 쓰면 결함이 준다"는 명제에는 지금 공개된 반증이 하나 서 있다.** 뒤에서 자세히 다룬다.

이 글은 2026-07-11에 **v0.12.11**을 실제로 설치·init해서 나온 산출물을 1차 자료로 쓴다. 문서가 아니라 디스크에 떨어진 파일을 근거로 삼는다.

## 1. 사용 방법

### 설치 — CLI는 전역, 나머지는 프로젝트별

```bash
# 1) CLI 설치 (전역, uv tool)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.12.11

# 2) 프로젝트 스캐폴드 생성
specify init my-project --integration claude
# 기존 폴더 안에서: specify init --here --integration claude  (비어있지 않으면 --force)
```

요구 사항은 Python 3.11+, git, uv(또는 pipx)다. `specify integration list`로 지원 에이전트를 확인한다 — 실측 목록에 Claude Code(`installed (default)`), Copilot, Gemini CLI, Codex CLI, Cursor, Cline, Devin, Amp, Auggie, Antigravity, Generic 등이 늘어서 있고, 공식 README는 이를 "30+ agents"로 표현한다.

이 구조가 중요하다. **`specify` CLI는 전역에 한 번 설치되지만, 실제 규칙(스킬·템플릿·스크립트)은 프로젝트 디렉터리 안에 복사돼 들어간다.** 플러그인처럼 "설치하면 모든 프로젝트에서 쓰이는" 물건이 아니다. spec-kit을 쓰는 레포는 자기 안에 자기 규칙을 통째로 들고 다닌다. 팀원이 clone하면 규칙도 따라오고, 규칙 수정은 커밋으로 남는다. 뒤에서 다룰 비교의 핵심 축이 여기서 갈린다.

CLI 자체도 단순한 스캐폴더를 넘어섰다. v0.12.11의 서브커맨드는 `init, check, version, self, extension, integration, preset, bundle, workflow`다 — 확장·프리셋·번들·워크플로가 각각 1급 개념으로 분리돼 있고, `self`로 CLI가 자기를 업그레이드한다. 다만 **기본 init 직후엔 확장도 프리셋도 하나도 안 깔린다**(`specify extension list` → "No extensions installed", `specify preset list` → "No presets installed"). 기본형은 얇고, 무거운 것들은 옵트인이다.

### init이 실제로 만드는 것 (v0.12.11, `--integration claude` 실측)

```
.claude/skills/          # 10개 스킬
  speckit-constitution/ speckit-specify/ speckit-clarify/ speckit-plan/
  speckit-checklist/ speckit-tasks/ speckit-analyze/ speckit-implement/
  speckit-converge/ speckit-taskstoissues/
.specify/
  memory/constitution.md            # 프로젝트 헌법 (init 시점엔 빈 템플릿)
  templates/{spec,plan,tasks,checklist,constitution}-template.md
  scripts/bash/{check-prerequisites,common,create-new-feature,setup-plan,setup-tasks}.sh
  workflows/speckit/workflow.yml    # specify→plan→tasks→implement + 리뷰 게이트
  workflows/workflow-registry.json
  integrations/{claude,speckit}.manifest.json
  integration.json
  init-options.json                 # {"ai":"claude","feature_numbering":"sequential",...}
.git/                               # git 저장소 자동 초기화 + "Initial commit from Specify template" 커밋
```

여기서 확인해둘 세 가지.

첫째, **git 저장소를 자동으로 초기화하고 커밋까지 만든다.** 그리고 v0.12.11에는 이를 끄는 `--no-git` 옵션이 없다(실행하면 `No such option: --no-git`). 레포가 아닌 곳에 spec-kit을 깔 방법은 사실상 없다.

둘째, `.specify/memory/constitution.md`는 init 직후 `[PRINCIPLE_1_NAME]` 같은 **플레이스홀더로 가득한 빈 템플릿**이다. 설치했다고 바로 시작되는 게 아니다. `/speckit-constitution`을 돌려 헌법을 채우는 것이 실제 0단계다.

셋째, **CLAUDE.md는 생성되지 않는다.** 스킬 10종이 곧 인터페이스이고, 에이전트 지침 파일을 건드리지 않는다. (0.9.x는 `<!-- SPECKIT START/END -->` 마커 블록이 든 CLAUDE.md를 만들었다 — 뒤의 버전 diff 참고.)

문서 표기는 `/speckit.constitution` 형태지만, Claude Code 통합에서는 스킬로 설치되므로 실제 호출은 `/speckit-constitution`이다 — 명령 이름의 점(`.`)을 하이픈(`-`)으로 치환하라는 규칙이 스킬 본문에 명시돼 있다.

### 워크플로

기본 사이클은 이렇게 흐른다.

```
constitution → specify → (clarify) → plan → (checklist) → tasks → (analyze) → implement
                                                                         ↓
                              기존 코드베이스·미완 구현 → converge → implement (반복)
```

| 단계 | 명령 | 산출물 | 필수? |
|---|---|---|---|
| 0 | `/speckit-constitution` | `.specify/memory/constitution.md` | 사실상 필수 |
| 1 | `/speckit-specify` | `specs/NNN-<이름>/spec.md` + `checklists/requirements.md` | 필수 |
| 2 | `/speckit-clarify` | spec.md 갱신 (모호점 질의응답) | 선택 |
| 3 | `/speckit-plan` | `plan.md` (+ research/contracts) | 필수 |
| 4 | `/speckit-checklist` | `checklists/*.md` | 선택 |
| 5 | `/speckit-tasks` | `tasks.md` | 필수 |
| 6 | `/speckit-analyze` | 교차 아티팩트 일관성 리포트 (읽기 전용) | 선택 |
| 7 | `/speckit-implement` | 실제 코드 | 필수 |
| 7.5 | `/speckit-converge` | `tasks.md`에 `## Phase N: Convergence` 추가 | 조건부 |
| — | `/speckit-taskstoissues` | GitHub 이슈 동기화 | 선택 |

**converge는 v0.11.2에 들어온 새 얼굴이다**(릴리스 노트: "feat: add /speckit.converge command"). SKILL.md의 정의를 그대로 옮기면 "현재 코드베이스를 해당 기능의 spec·plan·tasks에 비추어 평가하고, 남은 미구현 작업을 새 태스크로 tasks.md에 덧붙여 implement가 마저 끝내게 한다". 갭을 `missing / partial / contradicts / unrequested` 네 종류로 분류하고, **append-only**로만 쓴다 — spec.md·plan.md는 손대지 않고, 기존 태스크를 재작성·재번호·삭제하지 않으며, 다 만족됐으면 `tasks.md`를 **바이트 단위로 그대로 둔다**. 이게 왜 중요한가. SDD의 최대 약점은 "그린필드에서만 예쁜 방법론"이라는 것인데, converge는 **이미 코드가 있는 상태를 명세 기준으로 다시 수렴시키는** 진입로다. 브라운필드에 spec-kit을 얹을 때 첫 문장이 여기서 시작한다.

### "권고"가 아니라 "강제"인 지점들

스킬·템플릿 본문에서 직접 확인한 것만 적는다.

- **specify**: spec-template을 복사해 채운 뒤, 스스로 품질 체크리스트(구현 세부 누출 금지, 요구사항의 테스트 가능성, 성공 기준의 측정 가능성)를 만들어 **최대 3회 반복 검증**한다. `[NEEDS CLARIFICATION]` 마커는 **최대 3개로 제한**하고 나머지는 합리적 기본값으로 추정한 뒤 Assumptions에 기록하라고 지시한다. 성공 기준은 "기술 비종속·측정 가능"이어야 하며, `API 응답 200ms 이하` 같은 표현은 **나쁜 예시로 명시**돼 있다.
- **plan**: plan-template에 `## Constitution Check` 섹션이 있고 *"GATE: Must pass before Phase 0 research. Re-check after Phase 1 design."* 라고 박혀 있다. 스킬은 "게이트 위반이 정당화되지 않으면 ERROR"로 처리한다.
- **implement**: 시작 전에 `checklists/`를 전부 스캔해 미완료 항목이 있으면 표를 띄우고 **STOP — "그래도 진행할까요?"를 묻는다.** 태스크 실행은 "테스트 태스크를 대응 구현 태스크보다 먼저".
- **analyze**: 엄격히 읽기 전용. 헌법 위반은 **자동 CRITICAL**이며 "원칙을 희석·재해석·묵살하지 말고 spec/plan/tasks를 고쳐라"고 못박는다. CRITICAL이 있으면 `/speckit-implement` 전에 해소를 권고한다.
- **converge**: 헌법 MUST 위반 코드는 최고 심각도다. 다만 헌법이 빈 템플릿이면 헌법 체크를 **우아하게 건너뛴다** — 헌법을 안 채우면 게이트의 절반이 조용히 꺼진다는 뜻이다.
- **workflow.yml**: `description: "Runs specify → plan → tasks → implement with review gates"`. steps에 `- id: review-spec` / `type: gate`, `- id: review-plan` / `type: gate`가 있고 거부 시 `on_reject: abort`다. **사람이 승인하지 않으면 다음 단계로 못 간다.**

강제력의 출처는 세 군데다 — 템플릿에 박힌 게이트 문구, 스킬 본문의 STOP/ERROR 지시, workflow의 사람 승인 게이트. 셋 다 결국 LLM이 읽는 텍스트라는 한계는 뒤에서 다시 짚는다.

### 브랜치는? — 기본 설치에선 안 만든다

오해하기 쉬운 지점이라 실측을 그대로 적는다. `.specify/scripts/bash/create-new-feature.sh`를 읽어보면 **git 명령을 단 하나도 실행하지 않는다.** 하는 일은 (1) 설명에서 불용어를 걸러 2–4단어 짧은 이름 생성, (2) `specs/` 안 최대 번호+1로 `NNN-<이름>` 결정, (3) `specs/NNN-이름/spec.md`를 템플릿에서 복사, (4) `.specify/feature.json`에 경로 기록. 출력하는 `BRANCH_NAME`은 **작명 규칙일 뿐 실제 브랜치가 아니다.** 실제 브랜치 생성은 스킬 본문 표현 그대로 "optional, via hook" — git 확장을 따로 설치했을 때만 일어난다. 기본 설치에서 git이 관여하는 순간은 `specify init`의 저장소 초기화 한 번뿐이다.

## 2. 장단점 — 무엇을 얻고 무엇을 내는가

### 얻는 것

**컨텍스트가 파일로 응고된다.** 에이전트 세션은 휘발되지만 `spec.md`·`plan.md`·`tasks.md`는 레포에 남는다. 다음 세션, 다음 사람, 다음 모델이 같은 문서를 읽고 시작한다. [[컨텍스트-엔지니어링]]의 저장 계층 문제를 파일 시스템으로 푼 것이고, [[하네스-엔지니어링]] 관점에선 모델 밖의 하네스가 상태를 들고 있는 전형적 패턴이다.

**"에이전트가 멋대로 시작하는" 실패 모드를 막는다.** 요구가 모호할 때 LLM은 멈추지 않고 그럴듯하게 채운다. spec-kit은 그 지점에 체크리스트와 게이트를 박아 최소한 *어디를 추정했는지*(Assumptions), *무엇이 불명확한지*(NEEDS CLARIFICATION)를 문서에 남기게 한다.

**리뷰 대상이 코드에서 명세로 앞당겨진다.** 500줄 diff를 리뷰하는 것보다 40줄짜리 spec.md에서 "이건 우리가 하려던 게 아닌데"를 잡는 게 싸다. 에이전트가 코드를 대량 생산할수록 리뷰 병목은 커지고, 이 앞당김의 가치도 커진다. workflow.yml의 `review-spec` / `review-plan` 게이트가 정확히 이 지점을 노린다.

**브라운필드 진입로가 생겼다.** converge 덕분에 "이미 반쯤 만든 코드"에 명세를 사후 부착하고 갭을 태스크로 뽑아낼 수 있다. SDD 도구 대부분이 못 하던 일이다.

**감사 가능성.** 무엇을 왜 그렇게 만들었는지가 `specs/`에 명세·계획·태스크로 남는다. 규제 산업이나 인수인계가 잦은 조직에서 이건 부수 효과가 아니라 본 기능이다.

### 내는 것

**토큰과 시간.** 한 기능에 대해 헌법·명세·계획·태스크·체크리스트·분석 리포트가 각각 LLM 호출로 생성되고, 각 단계는 이전 산출물을 다시 읽는다. 코드 한 줄 쓰기 전에 문서 수천 줄이 만들어진다. 실측하면 스킬·템플릿 본문 합계가 약 151KB다. 스킬은 호출될 때만 로드되므로 전부가 매번 들어가진 않지만, `/speckit-specify` 한 번에 348줄짜리 스킬 + 131줄 템플릿 + 헌법이 함께 읽히고, 뒤 단계일수록 읽어야 할 선행 산출물이 늘어난다.

오버헤드의 크기는? 같은 과제(스트리밍·세션을 갖춘 AI 챗 MVP)를 두 SDD 도구에 각각 물린 공개 벤치마크가 있다. spec-kit은 OpenSpec 대비 토큰을 약 두 배 썼다 — 1차 120,947 대 57,740, 2차 181,040 대 91,729. 어시스턴트 턴과 툴 콜도 더 많았다. 단서를 정확히 달자. 이건 **SDD 도구끼리의 비교이지 "그냥 시켰을 때"와의 대조가 아니다.** 무명세 베이스라인과 spec-kit을 붙인 공개 자료는 아직 없다. 그래도 이 숫자는 오버헤드가 실재하고 작지 않다는 하한선은 준다.

**경직성.** 파이프라인은 기능 단위로 설계돼 있다. 오타 수정, 의존성 업그레이드, 로그 한 줄 추가에 헌법 체크와 태스크 분해를 통과시키는 것은 명백한 낭비다. 실무에선 "spec-kit 쓸 일"과 "그냥 할 일"을 사람이 매번 판단해야 하고, 이 판단 자체가 마찰이다.

**강제력의 바닥은 결국 프롬프트다.** 게이트도 STOP도 CRITICAL도 전부 **스킬 본문에 적힌 자연어 지시**다. 스크립트가 exit 1을 뱉거나 CI가 막아주는 게 아니다. 모델이 무시하면 게이트는 없는 것과 같다. spec-kit이 그럼에도 다른 도구보다 잘 지켜지는 이유는 명령이 세서가 아니라 **명세 파일이 없으면 다음 스킬이 읽을 입력 자체가 없기 때문**이다. 진짜 하드 게이트를 원하면 `specs/` 검사를 CI에 따로 붙여야 한다.

**문서가 진실이라는 가정.** 명세는 만들어진 순간부터 코드와 어긋나기 시작한다. analyze와 converge가 봐주지만 둘 다 LLM이고, analyze는 읽기 전용, converge는 append-only다. **둘 다 spec.md를 고치지 않는다.** 코드를 고치고 명세를 안 고치는 순간 spec-kit은 "거짓말하는 문서를 잘 관리하는 도구"가 된다. 도구의 결함이 아니라 SDD 방법론 전체가 30년간 못 푼 문제다.

### 가장 불편한 사실 — 효과에 반증이 서 있다

"명세를 먼저 쓰면 결과물이 좋아진다"는 직관은 강력하다. 그런데 이 명제를 정면으로 검증한 대규모 실증 연구는 **벤더 주장에서 도출한 5개 가설 중 하나도 지지하지 못했다.**

Brenn Hill의 연구(SSRN, 2026-04-28)는 오픈소스 119개 레포의 PR 100,247건을 SZZ 알고리즘으로 결함 추적하고 저자 내 고정효과로 분석했다. 같은 사람이 쓴 PR끼리 비교했더니, 명세가 붙은 PR은 결함률이 오히려 1.4pp 높았고(p=0.056) 재작업은 5.0pp 높았다(p<0.001). 명세의 품질이 재작업에 미치는 효과는 사실상 0이었다(p=0.997). 저자의 해석은 이렇다 — 명세는 품질의 **원인**이 아니라 **어려운 과제의 표식**이다. 어려우니까 명세를 쓰고, 어려우니까 결함과 재작업이 는다는 것이다. 이 연구는 GitHub Spec Kit을 명시적으로 지목한다.

과장하지는 말자. 이건 무작위 대조 실험(RCT)이 아니라 관측 연구다. 인과를 확정하지 못하고, 관측 연구 한 편이 도구를 사형시키지도 않는다. 하지만 온도는 정확히 맞춰야 한다. **spec-kit을 도입하면 규율의 값을 문서 산출물로 지불하는데, 그 문서가 결함을 줄인다는 증거는 지금 없고 반대 방향의 관측이 하나 서 있다.** GitHub 별 약 11만 9천 개는 관심의 지표지 효과의 지표가 아니다. 그럴듯한 프로세스가 실제 성공률을 담보하지 않는다는 [[에이전트-평가-evals]]의 함정이 여기에도 적용된다.

그렇다면 spec-kit의 값은 어디서 나오는가. 결함률이 아니라 **조율(coordination)** 에서 나온다고 보는 게 정직하다. 여러 사람과 여러 세션이 같은 문서를 읽고 같은 결정을 공유하는 것 — 이건 위 연구가 측정한 대상이 아니다. 아래 "하나만 고르라면"의 결론이 그 위에 선다.

### 움직이는 표적 — v0.9.5와 v0.12.11 사이의 실측 diff

이 글을 쓰며 v0.9.5를 먼저 설치했다가 최신이 v0.12.11임을 확인하고 같은 폴더를 다시 init했다. **두 스캐폴드는 실질적으로 다른 물건이었다.**

| 항목 | v0.9.5 | v0.12.11 |
|---|---|---|
| 설치되는 스킬 | 15종 | **10종** |
| git 확장 스킬(`speckit-git-*` 5종) | 기본 포함 | **없음** (확장으로 옵트인) |
| `.specify/extensions.yml` (단계별 훅) | 기본 생성 | **없음** |
| `speckit-agent-context-update` | 있음 | 없음 |
| `speckit-converge` | 없음 | **신규** (v0.11.2) |
| `CLAUDE.md` 생성 | 함 (SPECKIT 마커 블록) | **안 함** |
| `specify init --no-git` | 있음 | **제거됨** |
| CLI 서브커맨드 | init/check/… | + `self`, `extension`, `preset`, `bundle`, `workflow` |

훅 메커니즘 자체가 죽은 건 아니다. converge를 포함한 모든 스킬 본문에 여전히 "`.specify/extensions.yml`이 있으면 훅을 읽어라"는 조건부 체크가 남아 있다. **기본 설치에서 빠졌을 뿐 옵트인으로 살아 있다.** 그래도 결과는 분명하다 — 0.9.x에서 기본으로 얻던 "기능 = 브랜치 = specs 디렉터리, 단계마다 자동 커밋"이라는 그림은 0.12.x 기본 설치에는 **없다.**

표의 좌우 열은 두 태그의 기본 init 결과를 직접 비교한 실측이고, 핵심 항목은 릴리스 노트로 교차 확인했다 — git 확장 옵트인 전환과 `--no-git` 제거는 v0.10.0, CLAUDE.md 생성을 담당하던 agent-context 확장의 옵트인 전환은 v0.12.0이다. (스킬 15종에서 10종으로 줄어든 산수와 `.specify/extensions.yml`이 기본 생성되지 않는다는 사실은 릴리스 노트에 직접 문장이 없다. 이 두 항목은 로컬 실측이 유일한 근거이며, 위 두 릴리스의 옵트인 전환과 정합적이다.)

시사점은 뚜렷하다. 저장소가 2025-08-21에 생겼고 1년이 채 안 돼 마이너 버전이 열두 번 넘게 올랐다. README도 별도의 "실험적 목표(Experimental Goals)" 절을 두고 프로젝트를 연구·실험의 산물로 규정한다. **프로젝트에 파일로 박히는 스캐폴드가 이 속도로 갈라진다는 것 자체가 도입 리스크의 실증이다.** 버전은 태그로 고정하고, 업그레이드는 별도 작업으로 취급하라.

### 맞는 프로젝트 / 과한 프로젝트

| 상황 | 판단 |
|---|---|
| 여러 사람이 같은 코드베이스에 에이전트를 붙임 | **맞음.** 명세가 사람 간·세션 간 공유 프로토콜이 된다 |
| 기능 하나가 며칠 이상, 요구가 자주 오해됨 | **맞음.** 리뷰 앞당김의 이득이 오버헤드를 넘는다 |
| 규제·감사·인수인계 요구가 있는 도메인 | **맞음.** 추적성이 본 기능이다 |
| 이미 굴러가는 코드베이스에 규율을 얹고 싶음 | **조건부 맞음.** converge가 진입로다. 다만 명세를 사후 작성하는 비용은 온전히 든다 |
| 그린필드 + 요구가 애초에 흐릿함 | **조건부.** clarify로 흐릿함을 드러내는 값은 있으나, 탐색 단계라면 명세가 조기 고착을 부른다 |
| 1인 프로젝트, 프로토타입, 스파이크 | **과함.** 명세를 읽을 사람이 자신뿐이면 문서는 순수 비용이다 |
| 버그 픽스·리팩터링·유지보수 | **과함.** 기능 단위 파이프라인이 안 맞는다 |
| "결함을 줄이려고" 도입 | **근거 없음.** 위 실증 연구가 정면으로 반대한다. 조율이 목적일 때만 값이 선다 |

## 3. 비교 — superpowers vs ideas-come-true vs spec-kit

세 도구를 같은 것으로 착각하기 쉽다. 셋 다 "코딩 에이전트를 규율 있게 만든다"고 말하기 때문이다. 하지만 **덮는 SDLC 구간이 다르고, 무엇보다 강제하는 방식이 다르다.**

| 축 | **ideas-come-true** | **spec-kit** | **superpowers** |
|---|---|---|---|
| SDLC 구간 | 아이디어 → 명세 → 제품 형태·로드맵 | 명세 → 계획 → 태스크 → 구현 → 교차검증·수렴 | 계획 → 구현 → 검증 → 머지 |
| 한 문장 | 무엇을 만들지 정해준다 | 어떻게 만들지 문서로 못박는다 | 만드는 동안 규율을 지키게 한다 |
| 배포 형태 | 전역 플러그인 (마켓플레이스) | **프로젝트 스캐폴드** (레포에 파일 복사) | 전역 플러그인 (Anthropic 공식 마켓플레이스) |
| 강제력의 출처 | 대화 흐름 (스킬 권고) | **아티팩트 의존성 + 템플릿 게이트 + 사람 승인 게이트** | 세션 시작 규칙 주입 + 스킬 권고 |
| 에이전트 종속성 | Claude Code 전용 | **30+ 에이전트** (통합 매니페스트) | Claude Code 전용 |
| 산출물이 레포에 남나 | 명세 .md (또는 Notion) | **spec/plan/tasks/checklist 전부 커밋** | 계획 문서·워크트리·커밋 |
| 핵심 철학 | 소크라테스 문답으로 아이디어 다듬기 | 명세가 소스 오브 트루스 | TDD 필수, 증거 > 주장 |
| 팀 확산 방식 | 각자 플러그인 설치 | **clone하면 규칙이 따라옴** | 각자 플러그인 설치 |
| git 관여 | 없음 | init 시 repo 초기화. 브랜치·커밋은 확장 옵트인 | 워크트리·브랜치 종료 흐름 관리 |

### 해설: 세 도구가 서로 다른 층에 산다

**ideas-come-true**(brown-claude-marketplace)는 SDLC의 **앞단**이다. sharpen이 소크라테스식 문답으로 흐릿한 아이디어를 명세서로 깎고, productify가 그 명세를 "스킬로 만들까, CLI로 만들까, 로컬 HTML로 만들까"라는 **제품 형태 결정**과 페이즈 로드맵으로 바꾼다. spec-kit이 `/speckit-specify`에서 요구하는 입력 — 명확한 기능 서술 — 을 만들어주는 도구다. 겹치지 않는다. **선행한다.**

**spec-kit**은 **중간**이다. 명세를 받아 계획·태스크로 분해하고 구현까지 몰고 간다. 셋 중 유일하게 **레포에 파일로 내려앉고**, 유일하게 **에이전트 중립**이며, 강제력이 대화가 아니라 **아티팩트 의존성**에서 나온다. plan은 spec.md를 읽어야 굴러가고, tasks는 plan.md를 읽어야 굴러간다. 건너뛰면 입력이 없어서 멈춘다 — 이게 "그렇게 하시죠"와 "그러지 않으면 진행이 안 됩니다"의 차이다.

**superpowers**는 **구현 규율**이다. TDD(RED-GREEN-REFACTOR)를 필수로 걸고, 서브에이전트 병렬 실행·워크트리 격리·코드 리뷰 요청/수령·완료 전 검증을 스킬로 제공한다. spec-kit의 tasks.md를 받아 **각 태스크를 어떻게 제대로 구현할지**를 다룬다. spec-kit의 implement 스킬도 "테스트 먼저"를 지시하지만 한 줄 지침 수준이고, superpowers는 그것 하나에 스킬 전체를 쓴다. 강제 방식은 프롬프트 규칙 주입 — using-superpowers 스킬이 "해당하는 스킬이 있으면 반드시 호출하라"를 세션 시작에 심는다. 파일이 아니라 프롬프트로 거는 강제이므로, 모델이 무시하면 무시된다.

### 겹치는 구간과 충돌 지점

셋을 다 쓰면 이렇게 이어진다.

```
아이디어 → [sharpen] → 명세서 → [productify] → 제품 형태·페이즈
                                      ↓
        [speckit-constitution → specify → plan → tasks]
                                      ↓
        각 태스크 → [superpowers: TDD·워크트리·코드리뷰] → 커밋
                                      ↓
                    [speckit-analyze] → [speckit-implement] → [speckit-converge]
```

**이 조합은 이미 공식적으로 상상된 적이 있다.** spec-kit v0.11.0 릴리스 노트에 "Superpowers Implementation Bridge" 확장이 들어 있다 — spec-kit과 superpowers를 잇는 확장이 카탈로그에 존재한다는 뜻이다. 즉 "둘 중 뭘 고를까"라는 프레임 자체가 절반은 잘못된 질문이다. 겹치는 구간을 정리하면 둘은 같이 쓰인다.

정리해야 할 지점은 세 군데다.

1. **계획 문서의 이중화.** superpowers의 `writing-plans`/`executing-plans`와 spec-kit의 `plan.md`/`tasks.md`는 정확히 같은 일을 한다. 둘 다 켜두면 에이전트가 어느 계획을 진실로 볼지 흔들린다. **spec-kit을 쓰면 superpowers의 계획 스킬은 꺼라.** 남길 것은 TDD·디버깅·리뷰·워크트리·검증 쪽이다. 브리지 확장이 노리는 분업도 정확히 이 선이다.
2. **명세의 이중화.** sharpen의 명세서와 spec-kit의 spec.md는 형식이 다르다. sharpen 결과를 `/speckit-specify`의 **입력 텍스트**로 쓰고, 정본은 spec.md 하나로 유지하는 게 맞다. 두 문서를 나란히 유지하면 그 순간부터 어긋난다.
3. **git 주도권 — 생각보다 덜 부딪친다.** v0.12.11 기본 설치의 spec-kit은 브랜치를 만들지 않는다. `create-new-feature.sh`는 `specs/NNN-이름/` 디렉터리와 작명만 하고 git 명령을 실행하지 않는다. 따라서 **브랜치·워크트리 오너십은 superpowers에 그대로 맡기면 된다.** 단, spec-kit의 git 확장을 옵트인으로 설치하는 순간 단계별 자동 커밋과 기능 브랜치 생성이 부활해 superpowers의 워크트리 흐름과 정면으로 겹친다. 그때는 **둘 중 하나만 브랜치 오너로 두라.** (0.9.x를 쓰고 있다면 이 충돌은 기본값이다.)

### 하나만 고르라면

**질문은 "어떤 도구가 좋은가"가 아니라 "내 병목이 어디인가"다.**

- **뭘 만들지가 안 정해졌다** → **ideas-come-true**. 명세도 계획도, 만들 게 틀렸으면 전부 낭비다.
- **여러 명이 붙고, 결정이 공유되지 않고, 세션마다 결과가 다르게 나온다** → **spec-kit**. 레포에 규칙이 박히고 clone으로 전파되는 도구는 셋 중 이것뿐이다. 조율 도구다.
- **뭘 만들지도 알고 혼자 빠르게 짜는데, 코드 품질이 들쭉날쭉하다** → **superpowers**. 실증 근거의 방향도 이쪽이 낫다. 명세를 늘리는 것이 결함을 줄인다는 증거는 없지만, 테스트를 먼저 쓰는 것의 값은 훨씬 오래 검증돼 왔다. 개인 도구다.

셋 중 가장 값비싼 것이 spec-kit이다. 그리고 **혼자 쓰면 셋 중 가장 손해다.** 명세의 가치는 그것을 읽는 사람 수에 비례하는데, 비용은 읽는 사람 수와 무관하게 발생하기 때문이다. 결함률을 낮추려고 spec-kit을 도입한다면 지금 서 있는 증거는 그 기대를 지지하지 않는다. **여러 사람의 머릿속을 한 파일로 맞추려고 도입한다면, 그건 아직 반박되지 않았다.**

## 실무 적용 — 도입 판단 체크리스트

1. **도입 목적을 결함률이 아니라 조율로 두라.** "명세를 쓰면 버그가 준다"는 기대는 공개 실증 연구가 반대한다. "명세를 쓰면 팀이 같은 것을 만든다"는 기대는 아직 유효하다. 목적을 헷갈리면 성과 측정에서 반드시 실망한다.
2. **파일럿은 한 기능으로.** 실제 기능 하나를 constitution → implement까지 완주시키고, 소요 시간과 토큰을 "그냥 시켰을 때"와 비교하라. 숫자 없이 도입하면 나중에 되돌릴 근거도 없다.
3. **헌법에 진짜 제약만 넣어라.** `.specify/memory/constitution.md`는 빈 템플릿으로 온다. 여기 적는 모든 원칙은 plan의 게이트, analyze의 CRITICAL, converge의 최고 심각도로 되돌아온다. 지킬 생각 없는 원칙을 적으면 게이트가 소음이 되고, **안 채우면 게이트 절반이 조용히 꺼진다.**
4. **버전을 태그로 고정하라.** `@v0.12.11`처럼 박고, `.specify/` 업그레이드는 별도 작업으로 취급하라. 0.9에서 0.12 사이에 스캐폴드가 얼마나 갈렸는지는 위 표가 보여준다.
5. **적용 범위를 문서화하라.** "기능은 spec-kit, 버그 픽스·리팩터링은 아님" 같은 한 줄을 팀 규칙에 박아라. 없으면 팀은 매번 재협상한다.
6. **명세 갱신을 리뷰 항목으로 만들어라.** analyze도 converge도 spec.md를 고쳐주지 않는다. 코드만 고치고 명세를 안 고치는 PR을 막지 못하면, 6개월 뒤 `specs/`는 거짓말 아카이브가 된다.
7. **하드 게이트가 필요하면 CI로 내려라.** 스킬 본문의 STOP은 LLM에게 하는 부탁이다. 정말 막아야 할 것(예: spec.md 없는 PR)은 CI 체크로 박아야 진짜 게이트가 된다.

spec-kit은 [[agents-cli-lifecycle-sdlc]]가 그리는 "AI 시대의 SDLC"를 GitHub가 자기 방식으로 구현한 한 표본이다. [[google-agents-cli]]가 전역 CLI+스킬 묶음으로 배포되는 것과 달리 프로젝트에 파일로 내려앉는다는 점에서, **배포 형태가 곧 강제력의 크기를 결정한다**는 사실을 잘 보여준다. 도구 여러 개를 나란히 놓고 실제로 돌려본 뒤 판단하는 방식은 [[디자인-스킬-비교-실험]]에서 이미 한 번 검증했고, [[위키-하네스]]가 그러하듯 하네스는 자기 자신에게 적용될 때 진짜 값이 나온다.

관련: [[하네스-엔지니어링]] · [[컨텍스트-엔지니어링]] · [[에이전트-평가-evals]] · [[루프-엔지니어링]] · [[ai-엔지니어링-4계층]]

## 출처

- GitHub, [github/spec-kit](https://github.com/github/spec-kit) — 레포 README("30+ AI coding agents", "Experimental Goals" 절), 최신 릴리스 v0.12.11 (2026-07-10), 저장소 생성 2025-08-21, 별 약 119,410개 (GitHub API 조회, 2026-07-11)
- GitHub, [Spec Kit 공식 문서](https://github.github.io/spec-kit/) — SDD 정의, 워크플로 명령
- GitHub, [spec-kit 릴리스 노트](https://github.com/github/spec-kit/releases) — v0.10.0(git 확장 옵트인 전환, `--no-git` 제거), v0.11.0(Superpowers Implementation Bridge 확장), v0.11.2(`/speckit.converge` 추가), v0.12.0(agent-context 확장 옵트인 전환)
- Brenn Hill, ["Does Spec-Driven Development Reduce Defects? An Empirical Test of Industry Claims Across 119 Open-Source Repositories"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6515898) (SSRN, 2026-04-28) — OSS 119개 레포·PR 100,247건, SZZ + 저자 내 고정효과. 벤더 주장 5개 가설 모두 미지지. 관측 연구
- Jamie Telin, ["Is Your Safe Choice Burning Your Budget?"](https://medium.com/it-chronicles/is-your-safe-choice-burning-your-budget-1cfddf8782e4) (2026-03-18) — 동일 과제에서 Spec-Kit 120,947 / 181,040 토큰 대 OpenSpec 57,740 / 91,729 토큰
- 로컬 실측 (2026-07-11): `specify 0.12.11` 설치 후 `specify init --here --integration claude --force` 산출물 — `.claude/skills/*/SKILL.md` 10종, `.specify/templates/*.md` 5종, `.specify/scripts/bash/create-new-feature.sh`, `.specify/workflows/speckit/workflow.yml`, `.specify/init-options.json`, `specify {integration,extension,preset} list` 출력
- 로컬 실측 (2026-07-11): `specify 0.9.5` 동일 폴더 init 산출물 — 버전 diff 표의 좌측 열 근거
- obra/superpowers v6.1.1 (Anthropic 공식 마켓플레이스) — 로컬 설치 스킬 14종
- kimyoon21/brown-claude-marketplace, ideas-come-true v1.0.0 — 로컬 설치 스킬 2종(sharpen, productify)
