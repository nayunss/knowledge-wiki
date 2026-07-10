---
title: Hermes Agent — 자가개선형 오픈소스 에이전트와 Claude Code 위임 구조
type: 도구
description: Nous Research의 Hermes Agent는 스스로 스킬을 만들고 세션 간 기억을 유지하는 자가개선형 에이전트이자, Claude Code CLI를 번들 스킬로 위임해 코딩을 넘기는 오케스트레이션 계층이다.
tags: [ai-에이전트, 오케스트레이션, 오픈소스, claude-code]
resource: https://github.com/nousresearch/hermes-agent
date: 2026-07-10
---

## 도구를 늘리는 게 아니라 연결하는 문제

Claude로 코드를 짜고, Codex로 리뷰하고, ChatGPT로 문서를 다듬는다. 창을 세 개 띄워 놓고 결과물을 손으로 복사해 나른다. 도구는 늘었는데 작업은 여전히 사람의 손을 거쳐 이어 붙는다.

문제는 도구의 수가 아니라 도구 사이의 연결이다. AI들을 따로 쓰지 말고 하나의 작업 흐름 안에서 엮으라는 것 — 이것이 감자(@nowlovepan)의 X 포스트가 던진 문제의식이다. 그 연결을 맡는 계층으로 이 글은 Nous Research의 **Hermes Agent**를 본다.

## 핵심 주장: Hermes는 '연결 계층'이고, Claude Code 위임이 그 증거다

Hermes Agent는 두 얼굴을 가진다. 하나는 대화를 거치며 스스로 스킬을 만들고 세션을 넘어 기억을 유지하는 **자가개선형 에이전트**다. 다른 하나는 텔레그램·슬랙·CLI 같은 채널과 300개 넘는 모델, 40여 개 도구를 단일 프로세스로 묶는 **오케스트레이션 게이트웨이**다.

이 두 번째 얼굴을 가장 잘 보여주는 것이 Claude Code 위임이다. Hermes는 자기가 코딩을 직접 하는 대신, 코딩에 특화된 Claude Code CLI를 번들 스킬로 호출해 작업을 넘긴다. 이는 [[codex-교차모델-위임]]에서 다룬 교차 모델 위임 — 한 에이전트가 다른 모델·CLI에 하위 작업을 맡기는 패턴 — 의 또 다른 실사례다. "AI를 하나의 작업 안에서 연결하라"는 주장이 제품 구조로 굳어진 셈이다.

## Hermes가 스스로 자라는 방식

Hermes의 자가개선은 세 가지 폐쇄 루프로 요약된다. 각 루프는 [[루프-엔지니어링|루프 엔지니어링]]에서 말하는 "관찰→개선→반영"의 구현체에 가깝다.

- **스킬 자동 생성 (절차적 메모리).** 에이전트가 경험에서 스킬을 직접 만들고, 쓰는 동안 개선한다. agentskills.io 오픈 표준과 호환돼 외부 스킬을 가져오거나 내보낼 수 있다.
- **대화 히스토리 검색.** 과거 대화를 FTS5(SQLite 전문 검색)와 LLM 요약으로 뒤져 지속적으로 맥락을 이어간다. 세션이 끝나도 기억이 사라지지 않는다는 뜻이다.
- **사용자 프로필 자동 학습.** "Honcho 변증법"이라 부르는 방식으로 사용자의 성향을 대화에서 학습해 프로필을 갱신한다. (Honcho 변증법의 내부 동작은 소스에 상세가 없어 명칭만 소개한다.)

아키텍처는 Python 82.6% + TypeScript 14.8%로 구성되고(2026-07-10 GitHub 기준), 컴포넌트는 Agent 루프, Skills 시스템(절차적 메모리), Memory 서브시스템, MCP 통합, Gateway로 나뉜다. 이 구조 자체가 [[하네스-자기개선|자기개선하는 하네스]]의 한 형태다.

## 하나의 게이트웨이로 묶는 멀티플랫폼

Hermes는 텔레그램·디스코드·슬랙·왓츠앱·시그널·CLI를 **단일 게이트웨이 프로세스**로 통합한다. 채널마다 봇을 따로 운영하지 않고 한 프로세스가 받아 처리한다.

도구 생태계도 넓다. 40개 이상의 기본 도구, 6종의 터미널 백엔드(로컬·Docker·SSH·Singularity·Modal·Daytona), 내장 cron 스케줄러, 격리된 하위 에이전트 생성, Python RPC 도구 호출을 갖춘다. 모델은 Nous Portal(원클릭)·OpenRouter·OpenAI·커스텀 엔드포인트를 통해 300개 이상을 붙일 수 있고, Tool Gateway로 웹 검색(Firecrawl)·이미지 생성(FAL)·TTS(OpenAI)·클라우드 브라우저(Browser Use)를 연동한다.

인프라 유연성도 설계에 반영돼 있다. $5짜리 VPS부터 GPU 클러스터, 서버리스(Daytona/Modal은 유휴 시 최소 비용)까지 폭넓게 얹을 수 있다.

설치는 한 줄이다.

```bash
# Linux / macOS / WSL2 / Termux
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

```powershell
# Windows PowerShell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

설치 스크립트가 uv, Python 3.11, Node.js, ripgrep, ffmpeg, 포터블 MinGit까지 함께 깔아준다. 주요 명령은 다음과 같다.

```bash
hermes          # 대화 시작 (TUI)
hermes model    # 모델 선택·전환
hermes gateway  # 멀티플랫폼 게이트웨이 실행
hermes tools    # 도구 관리
hermes setup    # 초기 설정
hermes doctor   # 진단
```

기존 OpenClaw 사용자는 `hermes claw migrate`로 페르소나·메모리·스킬·API 키·허용목록·메시징 설정을 이전할 수 있다.

## Claude Code 위임: 두 가지 실행 모드

여기서 앞의 주장이 코드로 드러난다. Hermes는 코딩 작업을 Claude Code CLI에 넘기며, 상황에 따라 두 모드를 고른다.

| 구분 | 프린트 모드 (`claude -p`) | 대화형 PTY 모드 (tmux) |
|------|--------------------------|------------------------|
| 성격 | 원샷, 대화 없음, PTY 불필요 | 완전한 REPL, 후속 질문·슬래시 명령 |
| 조율 방식 | 명령 한 번 실행, JSON 출력 가능 | tmux로 send-keys/capture-pane 제어 |
| 적합한 일 | 버그 수정·기능 추가·리팩토링·CI/CD | 반복 리팩토링, 인간 개입, 탐색적 코딩 |
| 권장도 | 자동화 친화 — 기본 권장 | 상호작용이 꼭 필요할 때만 |

단일·명확한 작업이라면 프린트 모드가 낫다. 대화 상태를 유지할 필요가 없어 자동화에 잘 맞는다.

```bash
claude -p '이 함수의 null 처리 버그를 고쳐라' \
  --allowedTools 'Read,Edit' \
  --max-turns 10
```

여러 턴에 걸친 탐색이나 사람이 중간에 끼어들어야 하는 작업이면 PTY 모드를 tmux로 조율한다. 이때 대화창 처리에 함정이 하나 있다. 작업영역 신뢰 대화창은 Enter로 넘기면 되지만, `--dangerously-skip-permissions` 경고 대화창은 기본 선택이 "No, exit"라서 Down+Enter로 승인을 골라야 한다. 문서는 이 흐름을 sleep 기반 타이밍 패턴으로 다룬다.

Hermes 문서는 위임 품질을 위한 에이전트 규칙 10가지를 못 박아 둔다. 요지는 단일 작업엔 `-p`, 다중 턴엔 tmux, workdir 지정, `--max-turns` 필수, capture-pane로 모니터링, `❯` 프롬프트가 뜨면 입력 대기 신호, 세션 정리, 결과 보고, 느린 세션을 강제 종료하지 말 것, `--allowedTools`는 최소 권한으로. 위임을 '던지고 잊기'가 아니라 감독 가능한 절차로 만드는 [[하네스-엔지니어링|하네스 엔지니어링]]의 실전 규범이다.

비용도 통제 대상이다. 문서는 `--max-turns`(5–10), `--max-budget-usd`(최소 약 $0.05), `--effort low/high`, CI용 `--bare`, `--allowedTools` 최소화, `/compact`, 파이프 입력, `--model haiku/opus` 구분, `--fallback-model`, 5시간 지속되는 새 세션 등을 비용 팁으로 정리한다.

## 트레이드오프 — 언제 쓰지 말아야 하나

Hermes는 만능이 아니다. 도입 전에 다음을 저울질해야 한다.

- **자율성은 그대로 위험 표면이다.** 스스로 스킬을 만들고 터미널·컨테이너·다중 메신저를 다루는 에이전트는 그만큼 사고 반경이 넓다. Hermes가 명령 승인 시스템·DM 페어링·컨테이너 격리 옵션을 두는 것도 이 때문이다. 이 안전장치를 켜지 않고 자율성만 쓰면 위임이 곧 사고로 번진다.
- **오케스트레이션 자체가 새로운 복잡도다.** 채널 6종, 모델 300종, 백엔드 6종을 한 프로세스로 묶는다는 건 장애 지점도 그만큼 늘어난다는 뜻이다. 단일 채널에서 단일 모델만 쓰는 팀이라면 이 계층은 과할 수 있다. `hermes doctor`가 진단 명령으로 존재한다는 사실 자체가 운영 난도를 방증한다.
- **위임에는 컨텍스트 한계가 그대로 따라온다.** 문서는 Claude Code 컨텍스트가 70%를 넘으면 품질이 떨어지고 85%를 넘으면 환각 위험이 급증한다고 경고한다. 위임한다고 [[컨텍스트-엔지니어링|컨텍스트 관리]] 책임이 사라지지 않는다. `/compact`·`/clear`, 세션 분할은 여전히 사람의 몫이다.
- **성숙도 신호를 확인하라.** 최신 버전 v0.18.2, 마지막 릴리스 2026-07-08 — 활발히 갱신되지만 아직 0.x 대다. 라이선스는 MIT다. GitHub 스타 212,000+·포크 39,100+(2026-07-10 GitHub API 기준)인데, 2025-07-22에 만들어진 저장소라는 점을 감안하면 이례적으로 빠른 성장이다.

## 실무 적용 — 내일 무엇을 할까

기술 의사결정자 관점에서 판단 기준은 단순하다. **여러 채널·여러 모델을 하나의 자동화로 엮어야 하고, 그 자동화가 스스로 스킬을 축적하며 자라기를 바란다면** Hermes는 후보가 된다. 반대로 단일 리포에서 코딩 작업만 자동화하려는 거라면, Hermes 없이 Claude Code CLI를 직접 스크립트로 부르는 편이 더 가볍다.

가장 낮은 리스크의 첫걸음은 게이트웨이가 아니라 위임이다. `$5 VPS`에 설치한 뒤, 코딩 작업 하나를 `claude -p ... --max-turns 5 --max-budget-usd 0.05`로 프린트 모드 위임해 본다. 비용·권한·턴 수를 모두 상한으로 묶은 채 위임이 어떻게 감독되는지 먼저 체감하는 것이다. 멀티플랫폼 게이트웨이와 자율 스킬 생성은 그다음 단계다.

결국 Hermes가 던지는 물음은 "AI 도구를 몇 개나 쓰는가"가 아니다. "그 도구들이 하나의 작업 안에서 서로에게 일을 넘길 수 있는가"다. 그 질문에 답하려는 시도가 [[에이전틱-엔지니어링|에이전틱 엔지니어링]]의 현재 좌표다.

관련: [[codex-교차모델-위임]] · [[하네스-엔지니어링]] · [[에이전틱-엔지니어링]] · [[루프-엔지니어링]] · [[컨텍스트-엔지니어링]] · [[하네스-자기개선]]

## 출처

- 감자(@nowlovepan), "AI 자동화 제대로 하려면 Hermes를 알면 좋습니다", X 포스트 — https://x.com/i/status/2075132466751549632 (원문 직접 접근 불가, Notion 저장본 기준)
- Nous Research, hermes-agent README — https://github.com/nousresearch/hermes-agent
- Hermes 공식 문서, Claude Code 번들 스킬 — https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code
