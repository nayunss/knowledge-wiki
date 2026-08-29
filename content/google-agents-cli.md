---
title: Google agents-cli
type: 도구
description: 코딩 어시스턴트를 Google Cloud 에이전트 개발 전문가로 바꾸는 오픈소스 CLI + 스킬 묶음
resource: https://github.com/google/agents-cli
tags: [agent, tool]
sources:
  - id: github-com-agents-cli
    resource: https://github.com/google/agents-cli
    title: google/agents-cli (GitHub)
  - id: google-github-io-agents-cli
    resource: https://google.github.io/agents-cli/
    title: agents-cli 공식 문서
  - id: docs-cloud-google-com-quickstart-adk
    resource: https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents/quickstart-adk
    title: Google Cloud 문서
  - id: github-com-releases
    resource: https://github.com/google/agents-cli/releases
    title: agents-cli 릴리스
---

# Google agents-cli

구글이 2026년 4월 21일 공개(4월 22일 Cloud Next 2026에서 발표)한 오픈소스 도구. **"어떤 코딩 어시스턴트든 Google Cloud 위에서 AI 에이전트를 만들고·평가하고·배포하는 전문가로 바꿔주는 CLI + 스킬 묶음**"이다. 기존 오픈소스 `agent-starter-pack`의 후속작이며, starter-pack은 유지보수 전용 모드로 전환됐다.[^github-com-agents-cli]

> 에이전트를 "만드는 도구"이고, 그 에이전트를 어떻게 팀·반복으로 설계하느냐는 [[ai-엔지니어링-4계층]] 참고. · [[index|홈]]

- 저장소: `github.com/google/agents-cli`
- 문서: `google.github.io/agents-cli`
- 현재 릴리스: **v1.2.1** (2026-07-23 릴리스, GitHub Releases API로 2026-08-03 확인) · v1.0.0 GA 전환은 2026-07-01[^github-com-releases]

## 무엇을 해결하나

에이전트를 프로덕션에 올리려면 원래 여러 CLI·서비스(ADK, 배포, 평가, 관측)를 따로 익혀야 했다. agents-cli는 이 전체 라이프사이클을 **코딩 에이전트가 대신 수행할 수 있는 기계 판독용 인터페이스**(스킬)로 감싼다. 사용자는 "인시던트를 분류하는 에이전트 만들어줘" 같은 자연어만 던지면 된다.

## 설치

```bash
uvx google-agents-cli setup
# 또는
npx skills add google/agents-cli
```

요구사항: Python 3.11+, `uv`, Node.js.

설치하면 코딩 어시스턴트의 스킬 디렉터리에 **7개의 SKILL.md 파일**을 심는다.[^google-github-io-agents-cli] 이 포맷은 Anthropic이 2025년 12월 공개한 [[SKILL.md 오픈 스펙]]을 따르므로, Claude Code·Codex·Antigravity CLI 등 아무 코딩 에이전트에서나 동작한다.

## 설치되는 스킬 (7개)

| 스킬 | 역할 |
|------|------|
| `workflow` | 개발 라이프사이클·모델 선택 가이드 |
| `adk-code` | ADK Python API 패턴 |
| `scaffold` | 프로젝트 생성/보강 |
| `eval` | 평가 방법론 |
| `deploy` | Google Cloud 배포 |
| `publish` | Gemini Enterprise 등록 |
| `observability` | 모니터링·로깅 (Cloud Trace, BigQuery) |

## 핵심 커맨드

```bash
agents-cli create <name>            # 새 프로젝트 생성
agents-cli run "prompt"             # 로컬에서 에이전트 실행
agents-cli eval generate / grade    # 평가 생성/채점
agents-cli deploy                   # Google Cloud 배포
agents-cli publish gemini-enterprise # 에이전트 레지스트리 등록
```

## 다른 것과의 관계

- **ADK (Agent Development Kit)**: 실제 에이전트를 짜는 하위 프레임워크. agents-cli는 그 위의 툴링.[^docs-cloud-google-com-quickstart-adk]
- **Gemini Enterprise Agent Platform**: 배포 대상 플랫폼.
- **코딩 어시스턴트(Claude Code·Codex 등)**: agents-cli 스킬을 실행 주체로 삼는 오케스트레이터.

터미널에서 단독으로도, 코딩 에이전트에 통합해서도 쓸 수 있다.

## 메모

이건 우리가 쓰는 [[하네스-엔지니어링]] 관점에서 보면, 구글이 "에이전트 개발 라이프사이클" 자체를 스킬 묶음으로 표준화해 코딩 에이전트에 주입하는 하네스 배포 방식이다. Anthropic SKILL.md 스펙을 벤더 중립 배포 채널로 채택했다는 게 핵심이다.

---

## 출처
- [google/agents-cli (GitHub)](https://github.com/google/agents-cli)
- [agents-cli 공식 문서](https://google.github.io/agents-cli/)
- [Google Cloud 문서 — ADK + Agents CLI 퀵스타트](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents/quickstart-adk)
- [agents-cli 릴리스](https://github.com/google/agents-cli/releases)

[^github-com-agents-cli]: google/agents-cli 저장소 — 도구 소개와 agent-starter-pack 후속 관계. [github.com/google/agents-cli](https://github.com/google/agents-cli)
[^google-github-io-agents-cli]: agents-cli 공식 문서 — 설치·스킬 구성. [google.github.io/agents-cli](https://google.github.io/agents-cli/)
[^docs-cloud-google-com-quickstart-adk]: Google Cloud 문서 — ADK + Agents CLI 퀵스타트. [docs.cloud.google.com](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents/quickstart-adk)
[^github-com-releases]: agents-cli 릴리스 목록. [github.com/google/agents-cli/releases](https://github.com/google/agents-cli/releases)
