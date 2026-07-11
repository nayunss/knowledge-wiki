---
title: Claude Code에서 Codex를 서브에이전트로 — 교차 모델 위임과 멀티에이전트 오케스트레이션의 현재
type: 플레이북
description: Claude Code에 OpenAI Codex 플러그인을 붙여 교차 모델 위임을 구성하는 절차를 직접 실행해 검증하고(2026-07-11), 그것이 실제로 어떤 구조인지(세션 교체가 아닌 on-demand 도구 호출)와 멀티에이전트 오케스트레이션 지형 속 위치를 정리한다.
tags: [claude-code, 멀티에이전트, 오케스트레이션, 서브에이전트]
date: 2026-07-11
---

## 한 오케스트레이터가 남의 모델을 부린다

Claude Code의 서브에이전트는 보통 같은 벤더의 모델을 호출한다. 그런데 Claude Code 안에 Codex 구독을 그대로 붙여, Fable 5가 오케스트레이터로 앉고 GPT 계열 모델이 구현 담당 서브에이전트를 맡는 설정이 공유됐다. 벤더 경계를 넘는 위임(cross-model delegation)이다.

이 글은 그 설정을 **2026-07-11에 실제 머신에서 실행해본 기록**을 담는다. 결론은 셋이다. 첫째, **설치는 정말 커맨드 몇 줄이다** — 이번 실행에서 npm 설치가 3초, 전체 설정이 스모크 테스트 1회까지 포함해 끝났다. 둘째, 그러나 **이 플러그인이 무엇인지 오해하기 쉽다.** 세션이 Codex로 바뀌는 게 아니다. Claude Code는 계속 오케스트레이터로 남고, Codex는 필요할 때만 켜지는 도구다. 셋째, **그 위임이 놓인 멀티에이전트 오케스트레이션 지형은 여전히 비싸고 실험적**이며, 한 소스의 결론대로 "일반적인 AI 보조 개발 작업의 95%에는 멀티에이전트가 불필요"하다.

## 왜 교차 모델 위임인가: 역할 분담과 비용

핵심 아이디어는 모델별 강점에 작업을 배정하는 것이다. 원 소스(X 포스트)가 제시한 분담은 다음과 같다.

- **오케스트레이터 = Fable 5**: 계획 수립, 저장소 파악, 아키텍처 결정, 작업 분해, 최종 검토
- **구현 담당 = Codex(codex-rescue)**: 대규모 구현, 디버깅, 테스트 수정, 리팩터링, 다중 파일 편집

동기는 비용이다. 값비싼 오케스트레이터 모델의 토큰을 계획·검토에만 쓰고, 반복적이고 분량 많은 구현은 별도 구독(Codex)으로 넘긴다. 작성자는 이 방식으로 Fable 5 토큰 소모량을 **최소 60% 절약**할 수 있다고 주장한다(작성자 주장, 벤치마크 미제시·독립 검증 불가). 절약폭은 작업 성격과 위임 비율에 따라 달라질 수밖에 없으므로, 수치 자체보다 "무거운 구현을 별도 과금 경로로 분리한다"는 구조가 요점이다.

다만 분리는 소멸이 아니다. 뒤에서 보겠지만 Codex 호출은 OpenAI 쪽 구독 사용량을 쓴다. 아끼는 게 아니라 옮기는 것이다.

이 발상은 이미 위키에 정리한 [[claude-code-advisor-도구]]("결정의 순간에만 더 강한 모델을 부른다")와 방향이 반대이면서 상보적이다. advisor는 결정 순간에만 더 강한 모델을 부르고, 여기서는 무거운 실행을 다른 모델로 내려보낸다. 둘 다 [[하네스-엔지니어링]]의 모델 라우팅 문제 — 어떤 판단에 어떤 모델을 쓸지 — 를 다룬다.

## 먼저 구조부터: 세션이 바뀌는 게 아니다

설정 절차를 밟기 전에 답해야 할 질문이 있다. **"이 플러그인을 깔면 Codex가 실행되는 상태가 되는 건가, 아니면 Claude Code에서 Codex를 같이 쓰는 구조인가?"**

후자다. 2026-07-11 실행에서 확인한 구조는 이렇다.

- 세션이 Codex로 **바뀌지 않는다.** 대화 상대, 파일 편집, 계획, 판단은 계속 Claude Code가 한다.
- `/codex:rescue` 또는 `codex:codex-rescue` 서브에이전트를 부를 때만, 그 서브에이전트가 Bash로 companion 스크립트를 실행한다 → 로컬 Codex CLI 프로세스가 뜬다 → GPT 계열 모델에 작업이 전달된다 → 결과 텍스트가 Claude에 돌아온다.
- Codex는 **상주 데몬이 아니다.** setup 출력의 `"mode": "direct"`가 이를 명시한다: "No shared Codex runtime is active yet. The first review or task command will start one on demand." 공유 런타임은 아직 없고, 첫 review/task 커맨드가 필요할 때 띄운다.

한 줄로 줄이면 이렇다. **Codex는 세션을 대체하는 모델이 아니라, Claude가 호출하는 도구다.** 서브에이전트 정의가 이를 뒷받침한다 — `codex:codex-rescue`가 쓸 수 있는 도구는 **Bash 하나뿐**이다. 파일을 직접 고치는 권한도, Claude의 대화 맥락도 갖지 않는다. 프롬프트를 받아 외부 프로세스를 돌리고 텍스트를 반환하는 창구에 가깝다.

이 멘탈 모델을 먼저 잡아야 뒤에 나올 트레이드오프, 특히 컨텍스트 미공유가 왜 따라붙는지 곧바로 보인다.

## 설정 절차 — 그리고 직접 실행해보니

원 소스가 제시한 4단계에, 2026-07-11 실행에서 관찰한 실제 출력을 붙인다. `openai/codex-plugin-cc` 마켓플레이스와 `codex@openai-codex` 플러그인은 OpenAI 공식 GitHub 조직(github.com/openai) 소유 저장소로, OpenAI Developer Community가 2026-03-30 공식 발표한 1st-party 플러그인이다.

**1단계 — Codex 플러그인 설치**

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
```

실행 결과 그대로: `Successfully added marketplace: openai-codex` → `✓ Installed codex. Run /reload-plugins to apply.` → `Reloaded: 10 plugins · 8 skills · 22 agents · 7 hooks · 0 plugin MCP servers · 1 plugin LSP server`. 설치된 플러그인 버전은 codex 1.0.6이었다(`~/.claude/plugins/cache/openai-codex/codex/1.0.6/`).

**2단계 — 오케스트레이터에게 설정 마무리를 지시** (프롬프트)

```
이 Claude Code 환경에 Codex를 설정해줘. 방금 설치된 공식 OpenAI Codex
플러그인을 사용해줘. /codex:setup을 실행해줘. Codex CLI가 없으면 설치해줘.
인증이 안 되어 있으면 ChatGPT 계정으로 인증하라고 알려줘. 인증이 끝나면
Claude Code 안에서 Codex가 작동하는지 확인해줘. codex:codex-rescue
서브에이전트를 사용할 수 있는지 확인해줘. 설정 중에는 프로젝트 코드를
변경하지 마.
```

`/codex:setup`의 실체는 노드 스크립트 한 줄이다 — `node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs setup --json`. 스킬 문서 자체가 "Codex 미설치 + npm 있음 → 설치 여부를 한 번 묻고, 승낙 시 `npm install -g @openai/codex` 실행 후 재점검"이라는 분기를 규정한다. 설치 판단 로직이 스킬에 하드코딩돼 있는 셈이다.

1차 실행(Codex 설치 전) JSON 출력의 요지:

```
"ready": false
"node":  { "available": true, "detail": "v22.23.1" }   ← 이 환경 기준
"npm":   { "available": true, "detail": "10.9.8" }     ← 이 환경 기준
"codex": { "available": false, "detail": "not found" }
"auth":  { "available": false, "loggedIn": false, "detail": "not found" }
"sessionRuntime": { "mode": "direct", "label": "direct startup" }
"reviewGateEnabled": false
```

이어 `npm install -g @openai/codex`를 돌리자 `added 2 packages in 3s`. 의존성 2개, 3초다.

**3단계 — 인증: 항상 필요한 단계는 아니었다**

원 소스는 "ChatGPT/Codex 계정으로 1회 인증한다"를 독립 단계로 뒀다. 이번 실행에서는 **별도 `codex login` 단계가 필요 없었다.** 설치 후 2차 setup 출력:

```
"ready": true
"codex": { "available": true, "detail": "codex-cli 0.144.1; advanced runtime available" }
"auth": {
  "available": true, "loggedIn": true,
  "source": "app-server", "authMethod": "chatgpt",
  "verified": true, "requiresOpenaiAuth": true
}
```

머신에 이미 살아 있던 ChatGPT 로그인 세션을 companion이 `app-server` 경유로 감지해 `verified: true`로 확인했다. 즉 **ChatGPT에 이미 로그인된 머신이라면 인증은 자동으로 넘어간다.** 로그인 세션이 없는 머신에서는 `codex login`이 필요할 것으로 보이나, 그 경로는 이번 세션에서 관찰하지 못했다.

**4단계 — 위임 워크플로 지시** (프롬프트)

```
너는 오케스트레이터. 계획 수립·저장소 파악·아키텍처 결정·작업 분해·
최종 검토 = Fable 5. 대규모 구현·디버깅·테스트 수정·리팩터링·다중 파일
편집 = codex-rescue(/codex:rescue). Codex 모델은 GPT-5.5(xtra high) 우선.
Codex 작업은 좁고 구체적으로. 끝나면 결과를 직접 검토하고 맹신하지 마.
```

> 프롬프트의 `xtra high`는 원문 표기 그대로다. GPT-5.5 API의 실제 reasoning effort 값은 `xhigh`다.

> **모델 표기 주의 — 이 프롬프트를 그대로 복붙하지 말 것.** "GPT-5.5"는 원 소스(X 포스트) 시점의 모델이다. 2026-07-09에 GPT-5.6(Sol/Terra/Luna)이 Codex에 GA되어, 이 글 작성일 기준으로 **GPT-5.5는 이미 현행 세대가 아니다.** 쓸 때 `/model` 목록에서 현재 모델을 확인하라. 덧붙여 어느 모델이 실제로 응답했는지는 이번 실행에서 확인되지 않았다 — 아래 스모크 테스트 참고.

작성자가 덧붙인 운용 팁:

1. 이 과정을 스킬로 만들어(작성자 명명 'Fable-GPT') 세션 시작 시 호출한다.
2. 스킬 + 목표(goal) 조합으로 무거운 작업을 처리한다. 목표는 장기 작업에 특히 유용하다.
3. Codex 20x pro 플랜이면 서브에이전트를 여러 개 띄울 수 있다. 작성자는 동시 5–7개 에이전트를 쓰며 5시간 사용 제한에 걸린 적이 없다고 한다.
4. 컨텍스트가 길어지면 성능이 떨어지는 컨텍스트 로트(context rot)가 실재한다 — 컴팩션 4회 후 대화를 정리하고, 컨텍스트 보존에 `/handoff` 스킬을 쓴다. (컨텍스트 관리 일반론은 [[컨텍스트-엔지니어링]] 참고)

## 스모크 테스트: 붙긴 붙었는데, 무슨 모델인지는 안 보인다

설정이 끝났다고 믿지 말고 한 번 불러본다. 읽기 전용 스모크 테스트로 `codex:codex-rescue` 서브에이전트를 호출해 "Reply with exactly: CODEX_OK"를 넘겼다.

- 결과: 호출 성공, 응답 `CODEX_OK`. 경로는 살아 있다.
- 사용량: subagent_tokens 12,666 / tool_uses 1 / duration 9.7초. 왕복 한 번에 Claude 쪽 컨텍스트도 1만 토큰대를 쓴다는 뜻이다 — 위임이 공짜가 아님을 보여주는 첫 신호.
- **한계: companion 스크립트 출력에 모델 필드가 노출되지 않았다.** 어떤 GPT 모델이 응답했는지 이 경로로는 확인할 수 없다. 원 소스가 말한 GPT-5.5가 실제로 돌았는지는 이번 실행에서 확인되지 않았다.

한편 setup 출력의 `reviewGateEnabled: false`는 켜지 않은 옵션 하나를 가리킨다. `/codex:setup --enable-review-gate`를 쓰면 세션 정지(stop) 전에 최신 Codex 리뷰를 강제한다. 위임을 상시로 쓸 거라면 검토해볼 만한 스위치다. 이번엔 켜지 않았다.

## 이 위임이 놓인 지형: 오케스트레이션 4종

교차 모델 위임은 더 넓은 흐름의 한 사례다. 2026년 들어 "단일 세션으로 처리 못 하는 복잡 작업"을 위한 멀티에이전트 오케스트레이터가 공식·비공식으로 여럿 등장했다. 소스가 다룬 네 가지를 성격별로 정리한다.

| 도구 | 주체 / 성격 | 조정 방식 | 강점 | 약점·비용 |
|------|------------|-----------|------|-----------|
| **Dynamic Workflows** | Anthropic 공식 (2026-05-28 발표, 2026-07-11 현재 GA) | 사용자 목표로 워크플로 즉석 생성 → 전문 에이전트 병렬 분배 → 결과 비교·검증 → 수렴까지 반복 | 계획–검증 자동화, 진행 상황 저장으로 재개 가능 | 일반 세션보다 토큰 소모가 크게 늘 수 있음 |
| **Agent Teams** | Claude Code 공식, 실험·기본 비활성 | "팀 리더" 세션이 공유 작업 목록으로 조정, 팀원 간 직접 소통 | 대규모 프로젝트 | 팀원마다 별도 인스턴스 → 토큰 비용 높고 서브에이전트보다 비효율 |
| **Gas Town** | Steve Yegge, 비공식 | AI 에이전트용 "Kubernetes" — "시장(Mayor)" 에이전트가 작업 분해·에이전트 생성 | 병렬 실행 우수, 솔로 개발자 개인 프로젝트 적합 | 구조 복잡, Yegge 언급 기준 Claude Max 계정 3개 필요 |
| **Multiclaude** | Dan Lorenc, 비공식 | "감독자" 에이전트가 하위 에이전트에 작업 할당, Brownian Ratchet(CI 통과 시 PR 자동 병합) | 팀 사용·코드 리뷰 지원, 긴 프롬프트 후 방치 방식에 강함 | 자동 병합의 코드 품질 위험 |

각 설치 커맨드:

```
# Agent Teams — settings.json (Claude Code v2.1.32+)
"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"

# Gas Town
brew install gastown

# Multiclaude
go install github.com/dlorenc/multiclaude/cmd/multiclaude@latest
```

공통점이 있다. 넷 다 **한 오케스트레이터가 계획을 세우고, 하위 에이전트에 병렬로 분배하고, 결과를 검증·수렴**하는 구조다. Codex 위임 설정도 정확히 같은 골격 — Claude가 계획·검토, Codex가 실행 — 이며, 앞에서 확인한 `"mode": "direct"` 역시 이 골격의 변주다. 하위 실행자를 상주시키지 않고 필요할 때만 띄운다는 점이 다를 뿐이다. 나머지 차이는 하위 에이전트가 같은 벤더냐 다른 벤더냐, 그리고 오케스트레이션을 공식 기능으로 쓰느냐 외부 도구로 얹느냐다. Dynamic Workflows에 대한 개발자 반응(Reddit)이 "많은 개발자가 수동으로 구성하던 워크플로우의 정식화"라는 평가였다는 점은, 이 골격이 이미 현장에서 손으로 조립되던 패턴임을 보여준다. 오케스트레이터-워커 구조 일반론은 [[에이전틱-엔지니어링]]에 정리돼 있다.

## 트레이드오프: 언제 쓰지 말아야 하나

먼저 이번 실행에서 **직접 확인한** 네 가지 대가다.

- **컨텍스트가 공유되지 않는다.** Codex는 별도 프로세스라 Claude 세션의 대화 맥락을 물려받지 않는다. `/codex:rescue`에 넘기는 프롬프트에 배경을 직접 담아야 한다. 위임 작업을 "좁고 구체적으로" 쓰라는 조언은 스타일 권고가 아니라 구조적 요구다.
- **비용은 소멸하지 않고 이전된다.** 호출할 때마다 ChatGPT/Codex 계정의 구독 사용량을 쓴다. Claude 토큰을 아끼는 대신 OpenAI 쪽 쿼터를 태우는 구조다. 게다가 위임 왕복 자체가 Claude 쪽 토큰도 쓴다 — 이번 스모크 테스트 한 번에 12,666 토큰이었다.
- **모델이 불투명하다.** companion 출력에 모델 필드가 없어, 어떤 모델이 응답했는지 확인할 수 없다. "GPT-5.5에 위임하고 있다"는 확신은 최소한 이 경로로는 얻을 수 없다.
- **신뢰 경계가 하나 는다.** 타사(OpenAI) 계정 자격증명이 로컬 CLI를 통해 오간다. 사내 정책이 있다면 여기서 먼저 걸린다.

여기에 소스들이 일관되게 지적하는 오케스트레이션 일반의 한계가 겹친다.

- **토큰 비용이 크게 는다.** Dynamic Workflows는 "일반 Claude Code 세션보다 상당히 많은 토큰을 소모할 수 있다"고 명시하고 소규모부터 시작하길 권한다. Agent Teams는 팀원마다 별도 인스턴스라 비용이 특히 높다. 사용량 제한에도 빨리 도달한다.
- **초기 프롬프트가 결과를 좌우한다.** 초기 지시가 부정확하면 수 시간의 컴퓨팅이 낭비되고, 실행 도중 방향을 되돌릴 기회는 제한적이다.
- **결과를 맹신하면 안 된다.** 원 소스조차 "끝나면 결과를 직접 검토하고 맹신하지 마"라고 못 박는다. Multiclaude의 CI 통과 시 자동 병합은 코드 품질 위험을 안는다. E2E 테스트 검증과 피드백 루프 구현이 사실상 전제 조건이다 — [[루프-엔지니어링]]과 [[에이전트-평가-evals]]가 다루는 검증 루프가 여기서 안전장치 역할을 한다.
- **비공식 도구는 버그·보안 결함 가능성을 안는다.** Gas Town·Multiclaude는 개인이 만든 도구다. Codex 플러그인은 OpenAI 1st-party라 이 범주와 다르다.
- **대부분의 작업엔 과하다.** 소스의 결론은 분명하다 — 멀티에이전트 워크플로는 일반적인 AI 보조 개발 작업의 **95%에 불필요**하며, 현재로선 "큰 프로젝트를 완료하는 비싸고 실험적인 방식"이다.

"그래도 자율성과 속도가 매력적이지 않나"라고 생각할 수 있다. 맞다. 다만 그 매력은 **작업 규모가 단일 세션의 한계를 넘을 때** 값을 한다. 버그 하나 고치고 함수 몇 개 다듬는 일에 오케스트레이션을 얹으면 비용과 관리 복잡도만 늘어난다.

## 실무 적용: 도입 판단 기준

- **설치 비용은 낮다 — 그러니 판단은 설치가 아니라 운용에서 하라.** 이번 실행 기준 설정은 커맨드 몇 줄과 스모크 테스트 1회로 끝났다. 문제는 "깔 것인가"가 아니라 "무엇을 얼마나 넘길 것인가"다.
- **먼저 물어라 — 이 작업이 정말 단일 세션을 넘는가?** 아니라면 서브에이전트 하나, 혹은 그냥 단일 세션이 낫다. 95% 규칙을 기본값으로 둔다.
- **교차 모델 위임부터 시험한다.** 오케스트레이션 프레임워크를 통째로 들이기 전에, 계획=오케스트레이터 / 무거운 구현=다른 모델 위임이라는 역할 분담만 먼저 써 보는 편이 비용·복잡도가 낮다. 이미 Codex(또는 다른) 구독이 있다면 진입 장벽이 작다.
- **위임 프롬프트에 배경을 다 담는 습관을 들인다.** 컨텍스트가 공유되지 않으므로, 넘기는 작업은 자체 완결적이어야 한다. 파일 경로·재현 절차·기대 결과를 프롬프트에 명시한다.
- **공식부터 비공식 순으로.** 대규모 작업이 상시라면 Dynamic Workflows(공식·GA, 재개 가능)를 먼저 본다. Agent Teams는 실험 단계이고 비용이 높다. Gas Town·Multiclaude 같은 비공식 도구는 보안·품질 리스크를 감수할 수 있을 때만.
- **검증 루프를 먼저 깐다.** E2E 테스트와 피드백 루프 없이 자율 멀티에이전트를 돌리는 건 도입이 아니라 도박이다. 위임을 상시화한다면 `--enable-review-gate`처럼 강제 검토 장치를 켜는 것도 선택지다.
- **양쪽 예산을 함께 본다.** Claude 토큰만 보고 절약을 판단하면 착시다. OpenAI 구독 사용량까지 합쳐 상한을 정하고 소규모로 시작한다.

관련: [[하네스-엔지니어링]] · [[에이전틱-엔지니어링]] · [[루프-엔지니어링]] · [[에이전트-평가-evals]] · [[claude-code-advisor-도구]] · [[컨텍스트-엔지니어링]]

## 출처

- **2026-07-11 직접 실행 검증** — 이 세션 머신에서 `openai/codex-plugin-cc` 마켓플레이스 추가 → `codex@openai-codex` 1.0.6 설치 → `/codex:setup` 2회 실행(설치 전/후) → `npm install -g @openai/codex`(codex-cli 0.144.1) → `codex:codex-rescue` 서브에이전트 스모크 테스트. 본문의 JSON 출력·버전·사용량 수치는 이 세션의 실제 출력이다. 환경 의존적 값(node v22.23.1, npm 10.9.8)은 이 머신 기준.
- CJ Zafir (@cjzafir), X 포스트 — Claude Code에서 Codex 서브에이전트 설정법: https://x.com/i/status/2074875092090470469
- Anthropic — "Introducing dynamic workflows in Claude Code" (2026-05-28 발표, 이후 GA): https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- InfoQ — "Dynamic Workflows in Claude Code" (2026-06-01): https://www.infoq.com/news/2026/06/dynamic-workflows-claude-code/
- Shipyard — "Multi-agent orchestration for Claude Code in 2026" (2026-03-18): https://shipyard.build/blog/claude-code-multi-agent/
- OpenAI — Codex 모델 목록·체인지로그 (GPT-5.6 Sol/Terra/Luna는 2026-07-09 GA): https://developers.openai.com/codex/models
