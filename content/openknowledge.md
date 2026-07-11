---
title: OpenKnowledge — 에이전트가 읽고 쓰는 마크다운 위키 도구
type: 도구
description: inkeep/open-knowledge v0.29.1 설치·사용법과 냉정한 장단점. MCP·에이전틱 서치·git 동기화를 갖춘 로컬 우선 마크다운 에디터를, 이미 Quartz+git 위키를 굴리는 사람 관점에서 평가한다.
tags: [도구, 위키, mcp, 마크다운]
resource: https://github.com/inkeep/open-knowledge
---

마크다운 위키를 LLM과 함께 굴려본 사람은 같은 벽에 부딪힌다. 파일은 쌓이는데 링크는 끊기고, 에이전트는 `cat`과 `grep`으로 더듬거리며, 정리는 영원히 "나중에"다. 벡터 DB를 붙이면 원본과 인덱스가 갈라지고, Obsidian을 쓰면 에이전트가 볼트의 관례를 모른다.

OpenKnowledge는 그 사이를 메우겠다는 도구다. **마크다운 파일을 유일한 진실 원천으로 두고, 사람에게는 WYSIWYG 에디터를, 에이전트에게는 MCP 툴 19개를 같은 파일 위에 얹는다.** 별도 DB가 없고, 인덱스는 당신이 쓴 링크·폴더·제목 그 자체다.

## 결론부터

**당신이 이미 마크다운 위키를 git으로 굴리고 있다면 OpenKnowledge는 대체재가 아니라 작성·정리 레이어의 보완재다.** 발행(퍼블리싱)은 여전히 [[llm-wiki-구조]]의 Quartz가 하고, OpenKnowledge는 "쓰고 잇는" 구간을 가져간다. 반대로 위키가 아직 없다면, 스타터팩 하나로 Karpathy식 LLM 위키를 5분 만에 세울 수 있는 가장 빠른 경로다.

값은 치러야 한다. v0.29.1은 **0.x**다. 데스크톱 앱은 **Apple Silicon macOS 전용**이고, CLI 웹앱은 **Node.js 24 이상**을 요구한다. 라이선스는 **GPL-3.0-or-later** — 사내 제품에 코드를 끌어다 쓸 생각이라면 지금 멈춰야 한다.

---

## 1. 무엇인가, 왜 지금인가

OpenKnowledge는 Inkeep이 만든 오픈소스 마크다운 지식베이스 IDE다. 공식 문서는 스스로를 세 겹으로 설명한다.

| 레이어 | 정체 | 누가 쓰나 |
|---|---|---|
| 에디터 | WYSIWYG 마크다운 (소스 모드 토글, Mermaid·LaTeX·HTML 프리뷰) | 사람 |
| 지식 엔진 | MCP 서버 — `search`·`links`·`write`·`edit` 등 19개 툴 | 에이전트 |
| 콘텐츠 | 프로젝트 폴더의 평문 `.md` 파일, git 버전 관리 | 둘 다 |

세 레이어가 **같은 파일**을 만진다. 앱으로 고치든, 에이전트가 MCP로 고치든, vim으로 고치든 결과는 동일한 마크다운이다. 문서의 표현을 빌리면 "파일 시스템이 데이터베이스"이고, DB 의존성이 없다.

왜 지금이냐. 두 흐름이 만났기 때문이다. 하나는 노션 대신 마크다운을 단일 원본으로 삼는 흐름([[위키-설계-결정]]), 다른 하나는 Claude Code·Codex 같은 하네스가 파일을 직접 편집하는 [[에이전틱-엔지니어링]] 흐름. 전자는 에디터가 투박했고 후자는 문서의 관례를 몰랐다. OpenKnowledge는 그 교집합을 제품으로 만든 첫 시도에 가깝다. 실제로 공식 워크플로 문서는 Andrej Karpathy의 2026년 4월 LLM 위키 gist를 명시적으로 구현 대상으로 삼는다.

---

## 2. 설치 — 두 갈래

### 경로 A: macOS 데스크톱 앱

요구사항: **Apple Silicon(M1 이상) macOS**, `git`. DMG를 열어 Applications로 드래그하면 끝이다.

첫 실행 시 "Connect your AI tools to OpenKnowledge" 다이얼로그가 뜬다. 여기서 (1) 감지된 AI 에디터에 MCP 서버 등록, (2) `ok` 명령을 셸 `PATH`에 추가할지를 **한 번에 동의**받는다. 거절해도 앱 내장 터미널과 MCP는 동작한다.

### 경로 B: CLI + 로컬 웹앱 (Linux / Windows / Intel Mac)

요구사항: **Node.js 24+**, `git`.

```bash
npm install -g @inkeep/open-knowledge

mkdir my-knowledge-base && cd my-knowledge-base
ok init          # .ok/ 스캐폴딩 + AI 에디터에 MCP 등록
ok start --open  # 같은 에디터를 브라우저로 서빙
```

데스크톱 앱과 **같은 에디터**를 브라우저에서 띄우는 구조다. 다만 내장 터미널·브랜치별 창·네이티브 맞춤법 검사 등 일부 기능은 데스크톱 전용이다.

### `ok init`이 실제로 무엇을 쓰는가

여기가 중요하다. OpenKnowledge는 **프로젝트 밖에도 파일을 쓴다.** 공식 문서 "What OpenKnowledge writes to your system"이 전부 나열하는데, 요약하면 이렇다.

**프로젝트 안 (커밋됨)**
- `.ok/`, `.ok/config.yml` — 프로젝트 설정
- `.okignore` — 에디터·검색·에이전트가 볼 수 없는 경로
- `.mcp.json`, `.cursor/mcp.json`, `.codex/config.toml`, `opencode.json` — 프로젝트 스코프 MCP 등록 (설치 여부와 무관하게 씀 — 팀원을 위한 준비)
- `.claude/skills/`, `.cursor/skills/` 등 — 프로젝트 로컬 스킬(`SKILL.md`)

**프로젝트 안 (gitignore)**
- `.ok/local/` — 서버 락, 로컬 신원, 동기화 상태, 로그·텔레메트리(로컬 전용, 각각 약 25MB·약 50MB에서 로테이트)
- `.git/ok/` — **섀도 git 저장소**. 타임라인·복구 기능이 여기서 나온다

**홈 디렉터리 / 에디터 설정 (프로젝트 밖)**
- `~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`, `~/.config/opencode/opencode.json` 등 — 감지된 에디터의 **유저 레벨** MCP 등록
- `~/.agents/skills/open-knowledge-discovery/` — npm `postinstall`이 설치하는 디스커버리 스킬
- `~/.ok/` — 글로벌 설정, 스킬 상태, 로그, 시크릿(`secrets.yml`, `0600`)
- macOS 앱은 여기에 더해 `~/.zshrc`에 **펜스 처리된 관리 블록**을 넣는다(동의한 경우에만)

MCP 등록은 "surgical"하다고 문서화돼 있다 — 자기 항목만 추가하고 나머지는 바이트 단위로 보존하며, 파싱이 불안하면 아예 손대지 않고 `left unchanged (<reason>)`를 출력한다. 그래도 **남의 홈 디렉터리 설정을 건드리는 도구**라는 사실은 변하지 않는다. 싫으면 옵트아웃이 다 있다.

| 끄고 싶은 것 | 방법 |
|---|---|
| postinstall 스킬 설치 | `npm install --ignore-scripts` |
| 모든 에디터 MCP 등록 | `ok init --no-mcp` |
| 유저 레벨(홈) 쓰기 | `ok init --scope project` |
| `.ok/`를 git에서 제외 | `ok init --local-only` |
| 셸 `PATH` 블록·복구 스윕 | `OK_RECLAIM_DISABLE=1` |
| 로컬 진단 로그 | `telemetry.localSink.enabled: false` |

되돌리기도 명령이 있다. `ok deinit`은 프로젝트 하나에서, `ok uninstall`은 머신 전체에서 제거한다. **둘 다 마크다운은 건드리지 않고**, `--dry-run`으로 미리 볼 수 있다. 이 정도로 정직한 설치 문서는 흔하지 않다.

---

## 3. 사용법

### 기존 폴더를 그냥 연다

가장 큰 진입장벽 제거 지점이다. 마이그레이션이 없다. 기존 Obsidian 볼트, 코드베이스, 문서 폴더에서 `ok init && ok start --open`을 치면 끝이다. Obsidian 볼트의 경우 콜아웃(`> [!note]`), 하이라이트(`==...==`), 코멘트(`%%...%%`), 수식, Mermaid, 각주, `![[image.png]]` 에셋 임베드가 그대로 렌더된다. `.obsidian/` 폴더는 무시한다.

안 되는 것도 문서에 정직하게 적혀 있다. **노트 트랜스클루전**(`![[Some Note]]`)은 내용을 인라인하지 않고 링크로만 렌더되고, **블록 참조**(`^block-id`)는 인식하지 않으며, **커뮤니티 플러그인**은 당연히 안 돈다(Dataview 쿼리는 평문으로 남는다).

### 스타터팩

빈 프로젝트 대신 스타터팩을 고를 수 있다(`ok seed --list-packs`). "Knowledge base" 팩이 Karpathy식 LLM 위키의 직접 구현이다. 여기에 공식 문서는 Karpathy가 형식화하지 않은 확장을 하나 얹는다 — 위키를 `research/`(status: provisional)와 `articles/`(status: canonical)로 쪼개고, `consolidate` 워크플로를 명시적 승격 단계로 두는 것. 성급한 정본화를 "기본값"이 아니라 "선택"으로 만든다.

### 에이전트가 위키를 읽고 쓰는 흐름

이 도구의 핵심 주장은 하나다 — **벡터 DB 없이 검색한다.** 그 근거가 agentic search 문서에 있고, 두 가지 메커니즘으로 나뉜다.

**(1) 검색이 루프다.** 고전 RAG는 질문을 한 번 임베딩하고 가장 가까운 청크를 붙여 넣는다. 그게 틀리면 답도 틀린다. OpenKnowledge에서는 각 단계가 MCP 툴 호출이고 모델이 다음 수를 고른다: search → read → 백링크 추적 → 재질의. 첫 히트가 틀려도 비용은 한 스텝이지 답 전체가 아니다. [[컨텍스트-엔지니어링]] 관점에서 보면 검색 자체를 에이전트 루프에 위임한 설계다.

**(2) 모든 읽기가 브리핑이다.** MCP `exec` 툴로 `cat`을 하면 파일 바이트만 오는 게 아니라 프론트매터, **백링크**, 아웃바운드 링크, 버전 이력이 함께 온다. `ls`는 파일명 목록이 아니라 각 문서의 제목·status·백링크 수가 붙은 지도로 돌아온다. `grep` 히트에도 같은 맥락이 붙는다. 그래서 루프가 짧다.

쓰기도 응답을 준다. `write`/`edit`는 매번 `brokenLinks`를 돌려주고(전부 해석되면 빈 배열), 아무도 링크하지 않는 새 문서는 orphan으로 플래그되며 연결할 허브를 제안한다. Mermaid 펜스가 깨지면 `mermaid-parse-error` 경고가 온다. **`cat >>`는 침묵하지만 `write`는 말대꾸를 한다** — 실수가 그래프에서 썩기 전에 쓰기 시점에 드러난다.

주요 MCP 툴:

| 툴 | 하는 일 |
|---|---|
| `exec` | 읽기 전용 셸(`cat`/`ls`/`grep`/`find` 등). 서버 없이도 동작 |
| `search` | 랭킹 검색 (제목 부스트 + 본문 BM25 + 최신성). cmd-K 팔레트와 같은 엔진 |
| `links` | 링크 그래프. `kind`로 `backlinks`/`forward`/`dead`/`orphans`/`hubs`/`suggest` 선택 |
| `history`·`checkpoint`·`restore_version` | 섀도 git 기반 버전 관리 |
| `write`·`edit`·`delete`·`move` | 네이티브 CRUD. `move`는 영향받는 모든 링크를 재작성한다 |
| `workflow` | 절차 가이드 — `ingest`/`research`/`consolidate`/`discover`/`wiki` |

`links`의 `dead`·`orphans`·`hubs`·`suggest` 네 뷰가 위키 위생의 핵심이다. 방치해 썩게 두는 대신, 에이전트가 작업하면서 그래프를 수리하고 조밀하게 만든다.

**시맨틱 검색은 옵트인이다.** 기본 꺼짐. 켜고 API 키를 넣으면 임베딩 신호가 렉시컬 랭킹에 **융합**된다(대체가 아니다). 대가는 명확히 경고돼 있다. 질의와 매칭된 페이지 내용이 임베딩 제공자(기본 OpenAI)로 나간다. 키는 `~/.ok/secrets.yml`에 `0600`으로만 저장된다.

### 스킬

에이전트에게 관례를 가르치는 층이다. OpenKnowledge의 차별점은 **스킬이 설정 파일이 아니라 콘텐츠**라는 것 — WYSIWYG 에디터에서 다른 문서처럼 쓰고, 위키와 함께 버전 관리되고, `install` 하면 각 에디터의 스킬 디렉터리로 **심링크**된다. 복사가 아니라 심링크라서 드리프트가 없다. 한 번 고치면 모든 에이전트가 즉시 반영된다. [[하네스-엔지니어링]] 관점의 SSOT 원칙을 스킬 배포에 적용한 셈이다.

문서는 경고도 붙인다. 스킬은 스크립트를 품을 수 있고 그 스크립트는 당신 머신에서 돈다. 서드파티 스킬은 소프트웨어 설치처럼 다루라는 것이다.

### git / GitHub 동기화와 공유

동기화는 git이 실체다. 자동 동기화를 켜면 OpenKnowledge가 리모트에서 커밋을 당기고, 당신 편집을 로컬 커밋하고, 다시 푸시한다. 충돌은 에디터에서 통합 diff 뷰로 뜨고, 충돌 상태의 문서는 **사람도 에이전트도 쓸 수 없다**(모든 mutating MCP 툴이 거부).

공유 버튼을 누르면 `https://openknowledge.ai/d/…` 딥링크가 클립보드에 복사된다. 실체는 GitHub다. 리모트가 없으면 "Publish to GitHub" 마법사가 먼저 뜬다. 받는 쪽은 스플래시 페이지에서 macOS 앱으로 열거나 `ok clone <owner/repo> -b <branch>`로 받는다.

---

## 4. 트레이드오프 — CTO 시각

장점만 나열한 도구 소개는 신뢰를 잃는다. 소스에서 확인되는 단점만 적는다.

### 성숙도: 0.x이고, 아주 빠르다

- v0.29.1이 현재 최신 스테이블이고, 같은 날(2026-07-10) v0.30.0-beta.2까지 나갔다. 태그가 327개, 커밋 1,095개. **첫 공개 커밋이 2026-06-03** — 공개 저장소로서는 약 5주 됐다.
- 이 속도는 양날이다. 버그가 빨리 잡히지만, 당신이 의존하는 동작이 다음 마이너에서 바뀔 수 있다. 실제로 v0.29.1 바로 다음인 v0.30.0-beta.2 릴리스 노트에는 "Breaking for consumers"가 붙는다 — `preview_url` MCP 툴에서 `armPaneTarget` 파라미터가, `/api/config` 응답에서 `paneTarget` 필드가 빠졌다. 최근 릴리스 25건 중 breaking을 명시한 건 이 한 건뿐이라 빈도 자체는 낮지만, MCP 툴 시그니처가 마이너에서 바뀔 수 있다는 사실은 남는다. 프로덕션 팀 위키의 유일한 편집 경로로 삼기엔 이르다.
- 완충재는 있다. 데이터는 그냥 마크다운이고 git이다. **도구가 마음에 안 들면 `ok deinit` 치고 나가면 되고, 콘텐츠는 그대로 남는다.** 락인이 없다는 게 0.x 리스크를 감당 가능하게 만드는 유일한 이유다.

### 플랫폼: macOS 편중

- 데스크톱 앱은 **Apple Silicon macOS 전용**. Intel Mac·Windows·Linux 사용자는 CLI 웹앱 경로만 있다.
- 웹앱은 "같은 에디터"지만 데스크톱 전용 기능이 있다. 내장 TUI/터미널(`Cmd+J`), 브랜치별 창(worktree), 네이티브 맞춤법 검사, Finder 연동이 그렇다. 팀이 섞여 있으면 경험이 갈린다.
- CLI는 **Node.js 24 이상**을 요구한다. 사내 표준이 Node 20 LTS라면 별도 설치가 필요하다.

### 라이선스: GPL-3.0-or-later

- 전체 모노레포(desktop·app·server·cli·core)가 GPL-3.0-or-later다. 도구로 **사용**하는 데는 아무 제약이 없다 — 당신이 쓴 마크다운은 당신 것이다.
- 하지만 코드를 **가져다 사내 제품에 파생**시킬 생각이라면 카피레프트가 전염된다. 사내 포크를 배포하지 않고 내부에서만 쓰는 건 GPL상 배포가 아니라 문제없지만, 제품에 임베드해 고객에게 넘기는 순간 소스 공개 의무가 붙는다. **법무 확인 없이 진행하지 말 것.**

### 로컬 우선의 협업 제약

- 실시간 협업은 CRDT(Yjs)로 되지만, 그건 **같은 로컬 서버에 붙은 세션들** 사이 이야기다. 팀 간 동기화의 실체는 **git 폴링**이다. Notion처럼 몇 초 만에 남의 커서가 보이는 협업이 아니다.
- git 동기화의 한계가 그대로 상속된다. 보호된 브랜치(리뷰·서명·상태 체크 요구)에 푸시하면 GitHub가 거부하고, OpenKnowledge는 재시도를 멈추기 위해 **동기화를 자동으로 꺼버린다**. 강제 푸시로 히스토리가 갈라지면 CLI에서 손으로 수습해야 한다. 푸시 권한이 없으면 동기화 토글 자체가 비활성화된다.
- 자동 동기화는 **리모트 히스토리에 커밋을 쓴다**. 공식 문서가 직접 경고한다 — "자동 커밋이 git 히스토리를 어지럽히는 게 걱정되면 그 저장소에는 동기화를 켜지 마라."
- 풀(pull)이 **커밋되지 않은 로컬 변경을 덮어쓸 수 있다.** 문서에 명시돼 있다. 동기화를 켜기 전에 작업 중인 것을 커밋하거나 버려라.

### 보안·프라이버시 표면

- 기본값은 방어적이다. 텔레메트리와 진단 로그는 **로컬 전용**이고 자격증명 계열 속성은 기록 전에 `[REDACTED]` 처리된다. `ok diagnose bundle`을 명시적으로 돌리기 전엔 아무것도 머신을 떠나지 않는다.
- 예외는 셋. (1) 데스크톱 앱은 **자동으로 업데이트를 확인**하고(버전·채널 전송), 첫 실행 때 브라우저를 한 번 열어 공유 링크를 확인한다. (2) 시맨틱 검색을 켜면 콘텐츠가 임베딩 제공자로 나간다. (3) GitHub 동기화·공유는 당연히 GitHub로 나간다.
- 내장 터미널은 **전체 유저 권한의 실제 로그인 셸**이다. `agents.autoApproveOkTools` 기본값이 `true`라 도킹된 터미널에서 띄운 에이전트는 OK의 MCP 툴을 승인 없이 쓴다(파괴적 툴인 `delete`·`move`·`share_link`·`install`은 여전히 물어본다). 편하지만, 민감한 워크스페이스라면 `terminal.enabled: false`를 고려하라.

### 공식 문서가 말하지 않는 것

- 대규모 볼트에서의 성능 수치가 없다. "벡터 DB 없이 수천 개 파일에 걸쳐 답한다"는 문장이 agentic search 문서 첫 줄에 있지만, 그걸 뒷받침하는 벤치마크는 문서 어디에도 없다.
- Windows 지원은 "된다"고 적혀 있지만 CLI 경로 한정이고, 문서상 예외 처리(PowerShell 런처, `%APPDATA%` 경로)가 여럿이라 1급 시민은 아니다.

---

## 5. 누가 써야 하고, 누가 안 써도 되는가

**써야 한다**

- **Karpathy식 LLM 위키를 세우려는 개인.** 스타터팩 → `ok init` → 에이전트 연결까지 5분. 직접 하네스를 짜는 것보다 훨씬 빠르다.
- **Obsidian을 쓰는데 에이전트 연동이 답답한 사람.** 볼트를 그대로 열고, 안 맞으면 `ok deinit`. 위험이 거의 0이다.
- **코드베이스 위키가 필요한 팀.** `workflow` 툴의 `discover`·`wiki` kind가 레포를 훑어 소스 그라운디드 위키를 만든다.
- **markdown SSOT + 에이전트 편집을 이미 믿는 사람.** [[위키-설계-결정]]의 전제를 공유한다면 철학적 마찰이 없다.

**안 써도 된다**

- **Notion급 실시간 팀 협업이 필요한 조직.** git 폴링은 그 대체재가 아니다.
- **Node 24나 Apple Silicon을 깔 수 없는 환경.**
- **GPL이 걸리는 제품 팀** — 사용은 되지만 파생은 별개 문제다.
- **위키 규모가 문서 20개 수준.** 이 도구의 가치는 그래프가 커질 때 나온다. 작은 위키에서 `.ok/`·MCP·섀도 git은 순수 오버헤드다.
- **에이전트에게 문서 편집을 맡기고 싶지 않은 사람.** 그러면 그냥 좋은 마크다운 에디터일 뿐이고, 그 값에 이만한 설치 흔적은 과하다.

---

## 6. 이 위키와의 관계 — 대체재인가 보완재인가

솔직하게: **보완재다. 그리고 겹치는 구간이 꽤 있다.**

[[llm-wiki-구조]]에서 정리했듯 이 저장소는 위키·RAG·편집 세 렌즈로 동작한다. 그 셋을 OpenKnowledge와 나란히 두면 이렇게 갈린다.

| 축 | 이 위키 (Quartz + git + 하네스) | OpenKnowledge |
|---|---|---|
| 단일 원본 | `content/**.md` | 프로젝트 폴더의 `.md` |
| 편집 | 에디터 자유, 에이전트가 파일 직접 씀 | WYSIWYG + MCP 툴 19개 |
| 검색 | 에이전트의 grep/read + Quartz 전문 검색 | 에이전틱 서치(백링크 브리핑) + 옵션 시맨틱 |
| 링크 위생 | 사람이 관리, 깨져도 조용함 | `links` 툴 — dead/orphan/hub/suggest |
| 발행 | **Quartz → GitHub Pages (공개 웹)** | **없음** — 공유는 GitHub 딥링크뿐 |
| 품질 게이트 | [[위키-하네스]]의 fact-checker·copy-editor·validate-note.py | 없음 (스킬로 직접 짜야 함) |

핵심 비대칭 두 가지다.

**OpenKnowledge에 없는 것: 발행.** 이 위키의 존재 이유 중 하나는 공개된 URL이다. OpenKnowledge의 공유는 GitHub 저장소 딥링크 — 받는 쪽도 OpenKnowledge를 깔거나 GitHub에서 raw 마크다운을 봐야 한다. **Quartz를 대체하지 못한다.**

**이 위키에 없는 것: 링크 그래프 위생과 WYSIWYG.** 우리 파이프라인에는 `dead`/`orphans`를 잡아주는 장치가 없다. 위키링크가 깨져도 조용히 깨진 채로 남는다. 그리고 우리는 에이전트가 파일을 직접 쓰지, 쓰기 시점에 `brokenLinks`를 돌려받지 않는다.

그래서 현실적인 조합은 이렇다.

```
[OpenKnowledge]  로컬에서 쓰고·잇고·정리          ← 작성 레이어
       ↓ 같은 .md 파일, 같은 git 저장소
[위키 하네스]    tech-writer → fact-checker → copy-editor   ← 검증 레이어
       ↓
[Quartz]        빌드 → GitHub Pages                ← 발행 레이어
```

같은 마크다운 파일 위에서 세 레이어가 겹치지 않는다. 이게 "파일 시스템이 데이터베이스"라는 설계의 진짜 배당금이다 — **도구를 겹쳐 쌓을 수 있다.** OKF 프론트매터(`type`·`tags`·`description`)는 OpenKnowledge의 열린 프론트매터 모델에 그대로 통과하고, `[[위키링크]]`도 그래프 뷰에서 인식된다.

다만 두 가지가 충돌 지점이다. 첫째, OpenKnowledge의 자동 동기화는 **커밋을 자동으로 밀어넣는다** — 우리 파이프라인이 검증 게이트를 통과한 것만 발행한다는 원칙과 정면으로 부딪힌다. 둘째, `ok init`이 `.mcp.json`·`.claude/skills/`를 커밋 대상으로 쓴다 — 이미 하네스 설정이 있는 레포에서는 관리 주체가 둘이 된다.

**권고:** 위키 레포에 OpenKnowledge를 붙인다면 **`ok init --local-only` + 자동 동기화 끄기**로 시작하라. 편집·그래프 위생은 OpenKnowledge에게, 커밋·검증·발행은 기존 하네스에게. 경계가 명확할 때만 두 도구가 공존한다.

---

## 실무 판단 요약

| 질문 | 답 |
|---|---|
| 지금 도입? | 개인 위키면 **예**. 팀 프로덕션 위키의 유일 경로로는 **아직**. |
| 비용 | 소프트웨어는 무료(GPL). 시맨틱 검색만 임베딩 API 비용(`text-embedding-3-small`로 볼트 전체 임베딩이 센트 단위라고 문서는 주장한다). |
| 팀 역량 요구 | git 기본기 필수. MCP·에이전트 하네스 이해가 있으면 가치가 배가된다. |
| 되돌리기 비용 | **거의 0.** `ok deinit`, 마크다운은 그대로. 이게 이 도구를 시도해볼 가장 강한 이유다. |
| 가장 큰 리스크 | 0.x의 동작 변경. 완충재는 데이터가 평문 git이라는 것. |

관련: [[llm-wiki-구조]] · [[위키-설계-결정]] · [[위키-하네스]] · [[하네스-엔지니어링]] · [[컨텍스트-엔지니어링]] · [[에이전틱-엔지니어링]]

## 출처

- inkeep/open-knowledge — GitHub 저장소 (v0.29.1, GPL-3.0-or-later): https://github.com/inkeep/open-knowledge
- OpenKnowledge 공식 문서 (로컬 클론 `docs/content/` 기준, v0.29.1):
  - Quickstart — 설치 요구사항(macOS Apple Silicon / Node.js 24+ / git): `docs/content/get-started/quickstart.mdx`
  - What OpenKnowledge writes to your system — 파일 시스템 쓰기·옵트아웃·데이터 유출 목록: `docs/content/reference/what-open-knowledge-writes.mdx`
  - CLI & web app — `ok` 명령 전체: `docs/content/reference/cli.mdx`
  - MCP — 19개 툴 명세: `docs/content/reference/mcp.mdx`
  - Agentic search — 벡터 DB 없는 검색 루프: `docs/content/reference/agentic-search.mdx`
  - Core concepts — 3레이어·파일시스템=DB·백링크: `docs/content/reference/core-concepts.md`
  - Configuration — 설정 스키마·시맨틱 검색 egress 경고: `docs/content/reference/configuration.mdx`
  - GitHub sync — 자동 커밋 경고·실패 모드: `docs/content/features/github-sync.mdx`
  - Skills — 심링크 기반 스킬 배포: `docs/content/features/skills.mdx`
  - From Obsidian — 호환·비호환 표: `docs/content/migrate/obsidian.mdx`
  - LLM wiki workflow — Karpathy 패턴 구현: `docs/content/workflows/karpathy-llm-wiki.mdx`
- 릴리스 이력 (`gh release list`, 2026-07-11 확인): v0.29.1 (2026-07-10, latest), v0.30.0-beta.2 (2026-07-10, pre-release)
- 저장소 통계 (`git log`, 2026-07-11 확인): 최초 공개 커밋 2026-06-03, 커밋 1,095개, 태그 327개
- Andrej Karpathy, LLM 큐레이션 위키 gist (2026-04): https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
