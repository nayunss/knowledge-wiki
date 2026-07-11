---
title: OpenKnowledge 에이전트 활용법 — 실전 플레이북
type: 플레이북
description: OpenKnowledge v0.29.1의 MCP 19개 툴·워크플로·스킬 심링크를 로컬 전용으로 쓰는 법. ok init부터 코드베이스 위키 생성·그래프 위생 복구·인제스트까지, 기존 위키 파이프라인과 충돌 없이 붙이는 경계 설계.
tags: [openknowledge, mcp, 에이전트, 지식관리]
resource: https://openknowledge.ai/docs
---

앱을 깔았고, 첫 실행 다이얼로그를 수락했고, Claude Code·Claude Desktop·Codex 세 군데에 MCP 서버가 등록됐다. 그런데 Claude Code에서 "내 노트 검색해줘"라고 하면 아무 일도 일어나지 않는다. 고장이 아니다. **OpenKnowledge의 MCP 서버는 프로젝트 스코프로 동작하고, 아직 프로젝트가 하나도 없기 때문이다.**

이 글은 [[openknowledge]] 전편이 답한 "무엇이고 쓸 만한가" 다음 질문 — **"에이전트 연동을 실제로 어떻게 쓰는가"** — 에 답한다. 설치·장단점은 전편으로 넘긴다. 기준 버전은 **v0.29.1** (2026-07-11 확인, macOS 데스크톱 앱). v0.30 베타가 이미 돌고 있으니, 아래 설정 기본값은 `ok config validate`로 한 번 재확인하고 쓰기 바란다.

## 핵심 주장

세 줄이면 된다.

1. **연동은 `ok init`으로 켜진다.** 앱 설치는 MCP *등록*까지만 한다. 툴이 실제로 붙을 대상 — `.ok/` 프로젝트 — 은 폴더마다 직접 만들어야 한다.
2. **로컬 전용을 지키면서 거의 다 쓸 수 있다.** 시맨틱 검색(임베딩 egress)은 **기본이 꺼져 있고**, 끈 채로도 렉시컬 BM25 + 링크 그래프 + 브리핑 루프가 실전 검색의 대부분을 커버한다. 벡터 DB를 켤 이유가 없다.
3. **켜지 말아야 할 것이 셋 있다.** 자동 git 동기화, `agents.autoApproveOkTools`(기본 `true`), 내장 터미널(미설정이면 활성). 자동 승인은 흔히 알려진 것보다 범위가 좁지만 — 파괴적 툴은 여전히 프롬프트한다 — `write`·`edit`이 무승인으로 열리는 건 사실이고, 검증 게이트가 있는 파이프라인에서는 이 셋이 사고의 입구다.

그리고 자주 오해하는 지점 하나를 먼저 정리한다. **`ok init --local-only`는 "네트워크를 안 쓴다"는 뜻이 아니다.** CLI 도움말이 직접 말한다 — *"Keep OK config out of git via `.git/info/exclude` (per-clone, not committed)"*. 즉 `.ok/` 설정을 커밋하지 않는다는 뜻이지 egress 차단이 아니다. 데이터 유출을 막는 스위치는 따로 있다(아래 표).

---

## 1. 연동이 켜지는 조건 — `ok init`이 실제로 하는 일

`ok init`은 이 도구의 **유일한 셋업 동사**다. 로컬 스킬 `open-knowledge-discovery/SKILL.md`가 정확히 그렇게 부른다 — *"`ok init` is the one setup verb."* 프로젝트 루트에서 돌리면 네 가지가 생긴다.

| 산출물 | 내용 | 끄는 플래그 |
|---|---|---|
| `.ok/` 디렉터리 | 프로젝트 설정(`config.yml`). `content.dir` 기본값 `.` | — |
| MCP 등록 | 감지된 에디터(Claude Code·Cursor·Codex)에 서버 등록 | `--no-mcp` |
| 프로젝트-로컬 스킬 | `.claude/skills/open-knowledge/` — **에이전트에게 툴 사용법을 가르치는 런타임 계약** | — |
| 유저-글로벌 스킬 번들 | `discovery`, `write-skill` (이미 설치돼 있음) | `--no-skills` |

세 번째가 핵심이다. 지금 머신에 깔린 `~/.agents/skills/open-knowledge-discovery`는 **설치 안내용**이지 런타임용이 아니다. 스킬 본문이 스스로 그렇게 못 박는다.

> *"Do NOT load to perform OpenKnowledge reads/writes — the runtime guidance for editing markdown inside an initialized OK project ships as a separate project-local skill at `.claude/skills/open-knowledge/` whenever `ok init` runs."*

즉 **`ok init`을 돌리기 전까지 에이전트는 툴을 쓸 대상도, 쓰는 법도 모른다.** MCP 등록만으로 아무 일도 안 일어나는 이유가 이것이다.

### 로컬 전용으로 켜는 명령

```bash
# 노트 폴더나 실험용 작업 폴더에서
cd ~/work/ok-lab

# 설정은 커밋하지 않고(per-clone), MCP는 프로젝트 스코프로만 등록
ok init --local-only --scope project --content-dir .
```

- `--scope project|user|both` — MCP 설정을 어느 레벨에 쓸지. **`project`를 권한다.** 프로젝트 밖 세션까지 툴이 따라다니지 않는다.
- `--local-only` — `.ok/`를 `.git/info/exclude`로 빼서 커밋되지 않게 한다. 남의 레포에 실험할 때, 그리고 위키 레포처럼 **커밋 이력이 검증 게이트인 곳**에서 필수.
- `--content-dir <dir>` — 코드 레포 안에서 `docs/`만 대상으로 삼고 싶을 때. 리포지토리 전체를 인덱싱하지 않는다.

### egress를 막는 스위치는 따로다

| 켤 것 / 끌 것 | 키 | 기본값 | 사는 곳(scope) | 의미 |
|---|---|---|---|---|
| 시맨틱 검색 | `search.semantic.enabled` | **`false`** | project-local | 켜면 쿼리·매칭 텍스트가 임베딩 제공자(OpenAI 등)로 나간다 |
| 자동 git 동기화 | `autoSync.enabled` | `null` (첫 오픈 시 선택) | project-local | 켜면 에이전트 편집이 자동 커밋·푸시된다 |
| MCP 툴 자동 승인 | `agents.autoApproveOkTools` | **`true`** | user | 내장 터미널에서 띄운 에이전트에 한해, 비파괴 툴을 프롬프트 없이 실행 |
| 내장 터미널 | `terminal.enabled` | **`null`** (미설정 = 활성) | project-local | 앱 안에서 셸. `false`로만 opt-out |

한 가지 함정을 먼저 걷어내자. **이 네 키는 한 파일에 몰아넣을 수 없다.** 스키마상 `agents.autoApproveOkTools`만 유저 스코프이고, 나머지 셋은 전부 **project-local** — 즉 `.ok/local/config.yml`(프로젝트별·머신별, 커밋되지 않음)에 살아야 한다. 유저 config는 이 값들이 살 자리가 아니다.

**(1) 유저 스코프 — 머신당 한 번:**

```yaml
# 유저 config (이 머신 기준 `~/.ok/global.yml`. 실경로는 `ok config validate`로 확인)
agents:
  autoApproveOkTools: false
```

**(2) 프로젝트-로컬 — `ok init`한 프로젝트마다:**

```yaml
# .ok/local/config.yml — 커밋되지 않고 팀과 공유되지도 않는다
search:
  semantic:
    enabled: false      # 기본값이지만 명시. project-local이라 팀이 대신 켜줄 수도 없다
autoSync:
  enabled: false
terminal:
  enabled: false
```

번거롭지만 이게 사실이다. 프로젝트를 새로 열 때마다 세 줄을 다시 박아야 한다. 다만 뒤집어 보면 안전한 설계이기도 하다 — project-local 값은 **협업자와 공유되지 않으므로**, 팀이 커밋한 config가 내 로컬 결정을 덮어쓰는 일도 없다.

`terminal.enabled`는 앱 소스상 `agentSettable:false`다. 에이전트가 스스로 켤 수 없고, 커밋되는 프로젝트 파일에도 놓을 수 없다. 적용 후 `ok config validate`로 병합 결과를 확인한다. (참고로 `telemetry.localSink.enabled`는 기본 `true`지만 egress가 아니다 — `.ok/local/`에 진단 로그를 쓸 뿐이고, `ok diagnose bundle`을 직접 돌리기 전까지 머신을 떠나지 않는다. 민감한 워크스페이스라면 꺼도 된다.)

설정은 여러 층으로 병합된다 — 기본값 → 유저 → 프로젝트(`./.ok/config.yml`, git 공유) → 프로젝트-로컬(`./.ok/local/config.yml`) 순으로 뒤가 앞을 덮고, CLI 플래그가 최우선이다. 층별 우선순위를 외우기보다 `ok config validate`로 최종 병합값을 보는 편이 빠르다.

---

## 2. MCP 툴 19개를 "작업 단위"로 묶기

툴 목록을 외울 필요는 없다. **네 가지 상황**에 각각 어떤 조합이 붙는지만 알면 된다. 툴 나열은 공식 레퍼런스에 있다.

### 탐색 — `search` → `exec` → `links`

```
search(intent, scopes, limit)   BM25 + 최신성. semantic은 켜졌을 때만 랭킹에 블렌딩
exec(...)                       읽기 전용 셸(cat·ls·grep·find·head·tail·wc·sort·uniq·cut). 서버 없이도 동작
links(kind=backlinks|forward)   그래프 이동. kind에 배열을 넘겨 여러 뷰를 한 번에
```

이 셋의 핵심은 반환값이 **바이트가 아니라 브리핑**이라는 점이다. 파일 하나를 읽으면 프론트매터·백링크·아웃바운드 링크·버전 이력이 함께 온다. grep 결과에도 제목·상태·백링크 수가 붙는다. 그래서 에이전트가 "잘 연결된 허브"와 "스쳐 지나가는 언급"을 구분한다. [[컨텍스트-엔지니어링]]에서 말하는 "검색 결과에 메타데이터를 실어 보내라"의 구현체다.

### 작성 — `write` → `edit` → `links kind=dead` 피드백 루프

```
write(position=replace|append|prepend, extension=.md|.mdx)   문서·폴더·템플릿·스킬·에셋 생성
edit(...)                                                     본문 find/replace 또는 프론트매터 merge-patch
links(kind=dead)                                              방금 쓴 글의 깨진 링크 회수 → 다시 edit
```

쓰고 → 깨진 링크를 확인하고 → 고치는 루프를 **에이전트가 스스로 돈다.** 사람이 링크 오타를 주워 담을 일이 없다. 쓰기 툴은 최대 80자 `summary`를 받아 타임라인에 남긴다.

### 정리 — `links kind=[dead,orphans,hubs,suggest]` + `move`

`move`가 이 조합의 주인공이다. 파일을 옮기면서 **영향받는 링크를 재작성한다**. 손으로 `[[old-name]]`을 grep해 고치던 일이 통째로 없어진다. 스킬은 프로젝트↔글로벌 스코프 사이로도 `move`할 수 있다.

### 복구 — `history` → `checkpoint` → `restore_version`

`checkpoint`는 프로젝트 전체 스냅샷을 뜨고 버전 SHA를 돌려준다. 에이전트에게 대량 편집을 맡기기 전에는 반드시 먼저 부른다. 사고가 나면 `history`(kind=checkpoint/wip/upstream으로 필터)로 시점을 찾고 `restore_version`으로 되돌린다. **git 없이도 동작하는 별도 이력 레이어**이므로, 자동 커밋을 껐다고 해서 되돌리기를 포기하는 게 아니다.

나머지(`config`·`palette`·`preview_url`·`share_link`·`delete`·`skills`·`install`·`workflow`·`conflicts`·`resolve_conflict`)는 필요할 때 찾아 쓰면 그만이다.

---

## 3. 벡터 DB 없이 에이전틱 서치 쓰기

**시맨틱을 켜지 않아도 되는 이유는 이 도구의 검색이 "한 번의 임베딩 조회"가 아니라 "루프"이기 때문이다.** 공식 레퍼런스의 표현을 그대로 옮기면, 에이전트는 *"searches, greps, and follows backlinks in a loop over live files that come back with their graph context attached"*. 질문을 한 번 임베딩해 고정된 청크를 뽑는 RAG와 설계가 다르다.

루프의 각 스텝은 MCP 툴 호출이고, 다음 행동은 모델이 정한다 — 검색할지, 읽을지, 백링크를 따라갈지, 질의를 다시 쓸지. 인덱스 역할은 **저자가 만든 구조**(링크·폴더·description)가 대신한다. 링크가 잘 걸린 위키에서는 이게 임베딩보다 정확하다. 사람이 "이 둘은 관련 있다"고 명시적으로 선언한 신호이기 때문이다.

**렉시컬 + 그래프가 못 하는 것도 분명하다.**

- **동의어**: "인증"으로 쓴 문서를 "auth"로 검색하면 BM25는 못 찾는다.
- **개념 유사도**: "이거랑 비슷한 논의 어디 있었지?" 같은 질의.
- **링크가 안 걸린 신규 문서**: 그래프에 아직 붙지 않은 노트는 그래프로 못 찾는다.

**대응은 두 가지다.** (1) 프론트매터 `description`을 검색어처럼 쓴다 — 여기 동의어를 심어두면 렉시컬 히트 확률이 올라간다. 다만 이건 확인된 랭킹 요소가 아니라 **경험적 팁**이다. 문서가 밝힌 랭킹 요소는 BM25와 최신성까지다. (2) 에이전트에게 "한 번의 검색으로 끝내지 말고 동의어 두세 개로 재질의한 뒤 백링크를 따라가라"고 지시한다. 임베딩 대신 **토큰을 더 쓴다.** 로컬 전용을 지키는 대가는 egress가 아니라 컨텍스트 예산이다.

여기서 문서와 내 판단을 갈라두자. **공식 문서가 보장하는 건 두 가지까지다** — 시맨틱은 *"Off by default. Enable it per project, per machine"*이고, 켜더라도 *"an embeddings signal blends into the ranking; it never replaces lexical search"*다. 즉 임베딩은 랭킹에 얹히는 보조 신호이지 검색의 기반이 아니다. **여기서 "그러니 굳이 켜지 마라"까지 가는 건 문서의 결론이 아니라 내 결론이다.** 근거는 위의 셋 — 대체가 아니라 정제이고, 대가는 content egress이며, 링크가 잘 걸린 위키에서는 정제의 이득이 작다. 링크가 성긴 노트 더미라면 계산이 달라질 수 있다.

---

## 4. `workflow` 툴 — 데이터가 아니라 절차를 준다

`workflow`는 **데이터를 반환하지 않는다.** 앱 소스의 툴 설명이 명시한다 — *"returns a procedural guide, not data. Use it when the work fits the layer."* 즉 에이전트가 "지금부터 이 절차를 따르라"는 지시문을 스스로 받아오는 툴이다. [[하네스-엔지니어링]] 관점에서는 **런타임에 로드되는 스킬**이나 마찬가지다.

`kind`는 다섯 개고, 앞의 넷은 Karpathy식 3계층 지식베이스(`external-sources/` → `research/` → `articles/`)의 각 층에 대응한다.

| kind | 언제 | 산출 |
|---|---|---|
| `ingest` | 원문(URL·PDF·복사본)이 새로 들어왔을 때 | `external-sources/`에 **원문 그대로** 저장 + 원본 URL·수집일 프론트매터. 에이전트는 이후 읽기만 하고 고치지 않는다 |
| `research` | 소스 여러 개를 종합해 잠정 결론을 낼 때 | `research/<slug>.md`, `status: provisional`, 소스 경로 인용 |
| `consolidate` | 결론이 굳었을 때 **승격** | `articles/`로, `status: canonical` + `supersedes:` 체인으로 잠정본을 가리킨다 |
| `discover` | 쌓인 지식에서 답을 뽑을 때 | 서버 연결 없이도 동작하는 탐색 절차 |
| `wiki` | 코드베이스 위키 생성/갱신 | 아래 시나리오 A |

이 파이프라인의 규율 하나가 특히 좋다. *"Every downstream claim traces upstream to a preserved source. Cite local paths in `external-sources/`, never bare web URLs — the KB must survive link rot."* **웹 URL이 아니라 로컬에 박제한 원문 경로를 인용하라.** 링크가 썩어도 근거가 살아남는다. 이 위키의 `## 출처` 규칙보다 한 단계 엄격한 버전이다 — 우리 파이프라인에도 가져올 만하다.

---

## 5. 스킬 = 콘텐츠 (심링크 SSOT)

이 도구에서 가장 [[하네스-엔지니어링]]스러운 기능. **스킬이 설정 파일이 아니라 위키 문서다.** 공식 문서 표현으로 *"A skill in OpenKnowledge is content, not a config file: authored in the WYSIWYG editor, versioned with your base, and symlinked into every editor from one source."*

동작은 이렇다.

1. `.ok/skills/<name>/`(프로젝트) 또는 `~/.ok/skills/<name>/`(글로벌)에 스킬을 **문서로** 쓴다.
2. `install` 툴(또는 `ok skills`)로 대상 에디터에 배포한다 — `targets: claude | cursor | codex | opencode | pi`.
3. 배포는 복사가 아니라 **심링크**다. 원본 하나를 고치면 *"every agent has the change, with no re-install."*

SSOT(단일 진실 원천)가 파일시스템 레벨에서 강제된다. Claude Code용 사본과 Codex용 사본이 갈라져 어느 쪽이 최신인지 모르는 사고가 구조적으로 불가능하다. 우리 위키 하네스([[위키-하네스]])는 스킬을 `~/.claude/skills/`에 두고 사람이 동기화한다 — 심링크 모델이 명백히 우월한 지점이다. [[codex-교차모델-위임]]처럼 여러 호스트에 같은 스킬을 물려야 하는 구성이라면 특히.

기존 에디터 스킬을 끌어오려면:

```bash
ok skills manage --on   # .claude/skills 등을 OK 관리로 흡수, 원본 자리에 심링크
```

**경고 하나.** 스킬 번들에는 참조 파일과 **실행 스크립트**가 들어갈 수 있다. 공식 문서가 서드파티 스킬 채택에 주의를 요구하는 이유다. 위키에서 스킬을 받아 `install`하는 순간, 그건 **문서를 읽는 게 아니라 코드를 신뢰 경계 안으로 들이는 행위**다. 남의 스킬은 `scripts/`가 있는지부터 보고, 있으면 한 줄씩 읽은 뒤에 넣는다.

---

## 6. 실전 시나리오

### A. 코드베이스 위키 자동 생성 (`seed` → `wiki`)

여기서 경로 함정을 하나 밟기 쉽다. `codebase-wiki` 팩은 **루트 아래에 `wiki/` 하위폴더를 깐다** — `wiki/OVERVIEW.md`, `wiki/architecture/`, `wiki/modules/`, `wiki/flows/`, `wiki/concepts/`, `wiki/guides/`, 그리고 감사 추적용 `wiki/log.md`. 그래서 `--content-dir`를 `docs/wiki`로 잡아두고 `ok seed`를 그냥 돌리면 산출물이 `./wiki/`에 떨어져 **인덱싱 대상 밖**이 된다. 에이전트가 자기가 만든 위키를 못 읽는다.

`--root`로 맞춰준다.

```bash
cd ~/work/some-repo
ok init --local-only --scope project --content-dir docs/wiki
ok seed --pack codebase-wiki --root docs   # → docs/wiki/… 에 깔린다
```

레포 전체를 대상으로 삼아도 되면 `--content-dir .`로 두고 `ok seed --pack codebase-wiki`를 기본 경로 그대로 돌리면 된다. 어느 쪽이든 원칙은 하나 — **팩이 까는 `wiki/`가 `content.dir` 안쪽에 들어와야 한다.** 그다음 Claude Code에서:

```
Generate the codebase wiki.
```

에이전트는 `OVERVIEW.md`의 `source_commit`이 비어 있는 걸 보고 **생성 모드**로 들어가, 레포를 훑고 → 두 노브(`audience`: internal|public, `depth`: tour|standard|exhaustive)를 묻고 → 페이지 목록을 확인받고 → 생성한다. 각 페이지는 실제 소스 파일을 링크하고 필요하면 mermaid 다이어그램을 넣는다.

코드가 바뀐 뒤에는:

```
Refresh the codebase wiki.
```

이번엔 **갱신 모드**로 들어가 "only the pages the diff touched"만 다시 쓰고 `source_commit`을 다시 찍는다. 전체 재생성이 아니라 diff 기반이라는 점이 실용의 핵심이다.

다른 팩도 같은 방식으로 깔린다 — `knowledge-base`(Karpathy 3계층), `okf`(이 위키가 쓰는 Open Knowledge Format), `writing-pipeline`, `entity-vault`, `software-lifecycle`, `plain-notes`, `worldbuilding`. `ok seed --list-packs`로 확인.

### B. 흩어진 노트 폴더의 그래프 위생 복구

`ok init` 후 에이전트에게:

```
links 툴로 kind=[dead, orphans, hubs]를 한 번에 받아와 현황을 표로 보고해줘.
그다음 (1) dead link는 대상 문서가 있으면 링크를 고치고, 없으면 링크를 제거하되
목록으로 남겨줘. (2) orphan 문서는 hubs 중 가장 가까운 허브에서 한 줄 문맥과 함께
링크를 걸어줘. 파일을 옮겨야 하면 반드시 move 툴을 써서 링크가 함께 재작성되게 해.
시작 전에 checkpoint를 찍어줘.
```

세 가지가 이 프롬프트를 안전하게 만든다. **`checkpoint` 선행**, **`move`로만 이동**(수동 `mv`는 링크를 깬다), **삭제 대신 목록화**. `links kind=suggest`를 추가로 물리면 걸 만한 링크 후보까지 제안받는다.

### C. 자료·회의록 인제스트 → 승격

```
ingest this: https://example.com/some-spec
```

원문이 `external-sources/`에 **원문 그대로** 박히고 원본 URL·수집일이 프론트매터에 남는다. 소스가 몇 개 쌓이면:

```
research the X question; synthesize the sources in external-sources/
```

`research/x.md`가 `status: provisional`로 생기고, 각 주장이 로컬 소스 경로를 인용한다. 결론이 굳으면:

```
consolidate the X research into a canonical article
```

`articles/`로 승격되고 `status: canonical` + `supersedes:` 체인이 붙는다. **잠정본이 지워지지 않고 체인으로 남는 게 요점이다.** 나중에 "왜 이렇게 결론 냈지"를 되짚을 수 있다.

회의록은 `meetings/<source>-<source_meeting_id>` 이름 규칙을 쓴다. 소스+회의ID가 중복 제거 키라서, 같은 회의를 다시 싱크해도 **새 문서가 생기지 않고 같은 문서를 덮어쓴다.** 규율 하나 — *"Keep the transcript verbatim. Notes and summaries are yours to edit; the transcript is the record."*

### D. Obsidian 볼트에 에이전트 붙이기

```bash
cd ~/Obsidian/MyVault
ok init --local-only --scope project --content-dir .
```

**마이그레이션은 필요 없다.** 볼트는 이미 `[[위키링크]]`와 프론트매터로 된 마크다운이고, 이 도구가 그대로 먹는 포맷이다. 변환도, 임포트도, 재색인 스크립트도 없다. `ok init` 한 줄이면 끝이다. (`ok migrate`라는 명령이 있긴 하지만 서브커맨드는 `notion` 하나뿐 — Notion의 "Markdown & CSV" 익스포트를 정리해주는 전용 도구다. Obsidian은 애초에 정리할 게 없다.)

**`--local-only`가 특히 중요하다.** 볼트가 git으로 동기화 중이라면 `.ok/`가 커밋에 섞이지 않는다.

붙이고 나면 볼트를 검색하는 게 아니라 **볼트에 질문하게 된다.** Obsidian 검색은 문자열 매칭이지만, 여기선 에이전트가 백링크를 따라가며 브리핑을 쌓는다.

---

## 7. 이 위키 파이프라인과 공존시키기 — 경계 설계

**결론부터: OpenKnowledge를 위키 레포에 붙이지 않는다.** 이유는 취향이 아니라 구조다. 우리 파이프라인([[위키-하네스]])은 **발행 전에 fact-checker·copy-editor·병합 게이트를 통과해야 커밋이 나가는** 설계다. OpenKnowledge의 `autoSync`는 **에이전트 편집을 곧바로 커밋·푸시한다.** 두 모델은 양립할 수 없다 — 자동 커밋이 켜지는 순간, 검증 게이트는 우회 가능한 장식이 된다. [[위키-설계-결정]]에 기록해 둘 만한 트레이드오프다.

대신 **두 레포를 분리하고 산출물만 넘긴다.**

```
~/work/ok-lab/            ← OpenKnowledge 프로젝트 (ok init --local-only)
  external-sources/       ← 인제스트한 원문
  research/               ← 잠정 초안. 에이전트가 마음껏 편집
  articles/               ← consolidate로 승격된 완성분
        │
        │  (사람이 완성분만 골라 복사 — 여기가 게이트)
        ▼
~/…/knowledge-wiki/       ← 기존 파이프라인. OpenKnowledge 미설치
  content/                ← wiki-post가 검증 후 발행
```

경계를 지키는 규칙 셋.

1. **위키 레포에서는 절대 `ok init`을 돌리지 않는다.** 실수로 돌렸다면 `ok deinit`이 `.ok/`·MCP 엔트리·git-exclude 줄·섀도 레포를 걷어내고 마크다운은 남긴다.
2. **넘기는 단위는 `articles/`의 canonical 문서뿐이다.** `research/`는 넘기지 않는다 — 검증되지 않은 잠정본이다.
3. **복사는 사람이 한다.** 자동화하는 순간 게이트가 다시 뚫린다.

이 구조에서 OpenKnowledge는 **파이프라인의 상류 작업대**가 된다. 자료를 모으고, 초안을 굴리고, 링크를 정리하는 곳. 발행 권한은 여전히 위키 하네스에만 있다. [[에이전틱-엔지니어링]]에서 말하는 "쓰기 권한을 가진 에이전트일수록 경계를 좁게" 원칙 그대로다.

---

## 8. 트레이드오프 — 안 하는 게 나은 것

장점만 늘어놓으면 이 글은 광고다. 실제로 꺼야 할 것들을 짚는다.

**`agents.autoApproveOkTools`는 기본 `true`다 — 다만 알려진 것보다 범위가 좁다.** 스키마 설명이 경계를 그어준다: 자동 승인은 *"for agents launched from the built-in terminal"*에만 적용되고, *"Destructive tools (delete/move/share/install) still prompt."* 실제로 코드에도 `delete`·`move`·`share_link`·`install`이 deny 목록으로 박혀 있다. 내가 직접 연 Claude Code 세션은 애초에 대상이 아니다.

그래서 진짜 쟁점은 `delete`가 아니라 **`write`·`edit`이다.** 비파괴 툴은 프롬프트 없이 돈다. 파일을 지우지는 않지만 **덮어쓰기(`position=replace`)는 한다.** 앱 터미널에서 에이전트를 굴린다면, 내용이 조용히 바뀌는 것과 파일이 사라지는 것 중 어느 쪽이 더 무서운지 한 번 저울질해 볼 만하다. `checkpoint`가 그 저울의 반대편이다.

승인 인자가 어떻게 전달되는지도 짚어두자. Claude Code에는 **휘발성 `--settings <json>` CLI 플래그**로 allow/deny 목록을 실어 보낸다 — `~/.claude/settings.json`에는 **아무것도 쓰지 않는다.** Codex에는 `-c mcp_servers.open-knowledge.default_tools_approval_mode="approve"`를 넘긴다. 기법은 다르지만 **둘 다 배선돼 있다.** 그리고 둘 다 앱 터미널에서 에이전트를 띄우는 경로에서만 작동하므로, `ok init`이 내 에디터 설정 파일에 승인 권한을 몰래 심어놓는 일은 없다.

**내장 터미널은 미설정이면 켜져 있고, 앱 안에서 전체 권한 셸이다.** `terminal.enabled: false`로만 끌 수 있다. 이 값은 `agentSettable:false`이고 scope가 project-local이라 — **유저 config로는 못 끄고, 커밋되는 프로젝트 config로 팀에 강제할 수도 없다.** 프로젝트마다 각자 `.ok/local/config.yml`에서 꺼야 한다. 노트만 쓸 거면 켜둘 이유가 없다.

**`autoSync`는 첫 프로젝트 오픈 때 선택을 묻는다.** 혼자 쓰는 노트 폴더라면 편의지만, 검증 게이트가 있는 레포에서는 사고다. 여기서 위험은 "팀 설정이 내 값을 덮는 것"이 아니다 — 머신별 `autoSync.enabled` 선택이 **팀 기본값보다 우선한다.** 위험은 그 반대다. **내가 아직 아무것도 고르지 않았다면**(값이 `null`) 그때가 위험하다. 팀이 커밋해 둔 `autoSync.default: true`가 첫 오픈에 그대로 먹는다. 남의 프로젝트를 클론했으면 열기 전에 내 값부터 박아라.

**시맨틱 검색은 켜지 마라 — 적어도 먼저는.** 켜면 쿼리와 매칭 텍스트가 임베딩 제공자로 나간다. 얻는 건 랭킹 정제이지 새로운 능력이 아니다(문서 표현대로 *"it never replaces lexical search"*). 렉시컬로 못 찾는 상황이 **실제로 반복될 때** 켜도 늦지 않다. 순서를 거꾸로 하면 필요하지도 않은 egress부터 떠안는다.

**그리고 이 도구가 잘 못하는 것.**

| 한계 | 실제 영향 |
|---|---|
| 프로젝트마다 `ok init` 필요 | 노트가 5개 폴더에 흩어져 있으면 5번 돌려야 한다. 전역 검색 없음 |
| 안전 설정도 프로젝트마다 | 핵심 세 키가 project-local이라, 새 프로젝트를 열 때마다 다시 꺼야 한다 |
| 렉시컬 검색의 동의어 취약성 | 한/영 혼용 위키에서 눈에 띄게 아프다. `description` 프론트매터로 보완(경험적) |
| 스킬 심링크의 양날 | 원본 하나 고치면 전 에디터 반영 — 잘못 고쳐도 전 에디터 반영 |
| 워크플로가 절차 지시문일 뿐 | 에이전트가 지시를 안 따르면 그만이다. 결정론적 게이트가 아니다 |

마지막 줄이 이 도구의 본질이다. **OpenKnowledge는 게이트가 아니라 브리핑이다.** 강제하지 않고 안내한다. 검증이 필수인 작업은 여전히 [[하네스-엔지니어링]]식 게이트가 필요하다 — 그래서 위키 파이프라인을 대체하는 게 아니라 앞단에 붙이는 것이다.

---

## 내일 뭘 하면 되나

1. 위키 레포가 **아닌** 작업 폴더를 하나 만들고 `ok init --local-only --scope project`.
2. 안전 설정을 두 군데에 나눠 박는다(위 §1) — 유저 config에 `agents.autoApproveOkTools: false` 한 번, 그리고 이 프로젝트의 `.ok/local/config.yml`에 `search.semantic.enabled`·`autoSync.enabled`·`terminal.enabled`를 `false`로. 끝나면 `ok config validate`로 병합 결과 확인.
3. Claude Code에서 *"List the first 5 documents you come across in this project"* — 연결 확인.
4. 코드 레포 하나에 `ok seed --pack codebase-wiki` → *"Generate the codebase wiki."* 30분이면 이 도구가 내 워크플로에 남을지 판가름 난다.

관련: [[openknowledge]] · [[하네스-엔지니어링]] · [[컨텍스트-엔지니어링]] · [[에이전틱-엔지니어링]] · [[llm-wiki-구조]] · [[위키-하네스]] · [[위키-설계-결정]] · [[codex-교차모델-위임]]

## 출처

- OpenKnowledge Docs — MCP Reference: https://openknowledge.ai/docs/reference/mcp (19개 툴, 파라미터, `links kind` 값, `install` targets)
- OpenKnowledge Docs — Agentic Search: https://openknowledge.ai/docs/reference/agentic-search (BM25+recency 기본, 시맨틱 기본 off·"never replaces lexical search", 브리핑 루프)
- OpenKnowledge Docs — Configuration: https://openknowledge.ai/docs/reference/configuration (config 층 병합, `search.semantic.enabled`, `autoSync.enabled`/`autoSync.default`, `agents.autoApproveOkTools`, `terminal.enabled`, `telemetry.localSink`)
- OpenKnowledge Docs — Skills: https://openknowledge.ai/docs/features/skills (스킬=콘텐츠, 심링크 설치, `ok skills manage --on`, 서드파티 스킬 경고)
- OpenKnowledge Docs — Codebase Wiki workflow: https://openknowledge.ai/docs/workflows/codebase-wiki (`ok seed --pack codebase-wiki`, generate/refresh 모드)
- OpenKnowledge Docs — Karpathy LLM Wiki workflow: https://openknowledge.ai/docs/workflows/karpathy-llm-wiki (3계층 `external-sources/`·`research/`·`articles/`, ingest→research→consolidate→discover 프롬프트)
- OpenKnowledge Docs — Meeting Ingestion workflow: https://openknowledge.ai/docs/workflows/meeting-ingestion (`meetings/<source>-<source_meeting_id>` 중복 제거 키, 트랜스크립트 원문 보존)
- OpenKnowledge Docs — Claude Code integration: https://openknowledge.ai/docs/integrations/claude-code
- 로컬 설치본 v0.29.1 (2026-07-11 확인) — `ok --help` / `ok init --help` / `ok seed --list-packs` / `ok seed --pack codebase-wiki --dry-run` / `ok migrate --help` / `ok skills --help` / `ok config --help` 출력, `cli/dist/config-schema.json`·`config.user.schema.json`(키별 `scope`·기본값), `cli/dist`의 MCP 툴 등록부·자동 승인 deny 목록(`delete`·`move`·`share_link`·`install`)·에디터별 승인 인자 배선, `~/.agents/skills/open-knowledge-discovery/SKILL.md`
