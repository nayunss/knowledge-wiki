---
title: Claude 5 세대의 컨텍스트 엔지니어링 — 80% 삭제는 어디까지 우리 것인가
type: 개념
description: "Anthropic이 Claude Code 시스템 프롬프트의 80% 이상을 지웠다고 밝힌 글(2026-07-24)을 원문 대조로 검토한다. 여섯 개 'Then → Now' 전환이 각각 어떤 근거를 딛고 있는지, 그 수치의 범위가 어디서 끊기는지, 우리 CLAUDE.md·스킬로 옮길 때 무엇부터 지우고 무엇은 지우면 안 되는지."
tags: [컨텍스트-엔지니어링, claude-code, 하네스, 프롬프트]
resource: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
date: 2026-08-02
sources:
  - id: claude-com-the-new-rules-of-context-engi
    resource: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
    title: The new rules of context engineering for Claude 5 generation models
  - id: anthropic-com-effective-context-engineer
    resource: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    title: context engineering
  - id: claude-com-a-field-guide-to-claude-fable
    resource: https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns
    title: A field guide to Claude Fable 5
  - id: claude-com-a-harness-for-every-task-dyna
    resource: https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code
    title: 파일 트리
  - id: code-claude-com-skills
    resource: https://code.claude.com/docs/en/skills
    title: Claude Code
  - id: code-claude-com-commands
    resource: https://code.claude.com/docs/en/commands
    title: Reports findings first and asks for confirmation before changing anything
---

지난 2년간 컨텍스트 엔지니어링의 미덕은 촘촘함이었다. 규칙을 빠짐없이 적고, 예시를 붙이고, 중요한 건 두 번 쓰고, 팀 지식을 `CLAUDE.md` 한 파일에 모았다. 그런데 2026년 7월 24일, Anthropic의 Thariq Shihipar가 정반대 이야기를 들고 나왔다. Claude Code 시스템 프롬프트의 **80% 이상을 지웠는데** 자사 코딩 평가에서 측정 가능한 손실이 없었다는 것이다.[^claude-com-the-new-rules-of-context-engi]

숫자가 크다. 그래서 위험하다.

## 결론부터

**이 글에서 우리 저장소로 넘어오는 것은 80%라는 숫자가 아니라 삭제의 순서와 예외다.**

원문의 80%는 세 가지가 동시에 성립하는 조건에서 나온 값이다. 지운 대상은 Anthropic이 직접 쓴 Claude Code 시스템 프롬프트이고, 대상 모델은 Anthropic이 훈련한 Claude Opus 5·Fable 5 계열이며, 손실 없음을 판정한 주체는 "our coding evaluations"라고만 표기된 자사 평가다. 셋 다 Anthropic의 것이라는 뜻이다. 우리가 `CLAUDE.md`를 열 때 우리 것이라 할 만한 건 그중 파일 하나뿐이고, 모델도 평가도 우리 것이 아니다.

그렇다고 이 글이 마케팅인 것은 아니다. 원문에 흩어진 항목을 우리가 순서로 묶은 삭제 우선순위(충돌하는 지시부터, 다음은 뻔한 것, 다음은 반복)는 수치 없이도 성립하고, 그중 일부는 오늘 바로 적용해도 안전하다. 반대로 그대로 옮기면 다치는 항목도 섞여 있다. 그 둘을 가르는 것이 이 글의 목적이다.

관련 배경은 [[컨텍스트-엔지니어링]]과 [[ai-엔지니어링-4계층]]에 있으니 여기서는 다시 설명하지 않는다. 참고로 원문이 "context engineering"이라는 표현에 거는 링크는 Anthropic의 "Effective context engineering for AI agents"인데, 우리 [[컨텍스트-엔지니어링]] 노트가 근거로 쓴 바로 그 문서다.[^anthropic-com-effective-context-engineer] 같은 계보의 후속편으로 읽으면 된다.

## 원문이 정확히 무엇에 대해 말했나

여기가 가장 미끄러지기 쉬운 자리다. 원문의 **진단**과 **측정**은 범위가 다르다.

- **진단의 범위**: 원문은 "we were overconstraining Claude Code, both through our system prompt and in our CLAUDE.md files and skills"라고 쓴다. 과잉 제약이라는 판정은 시스템 프롬프트·`CLAUDE.md`·스킬 셋 모두를 겨냥한다.
- **측정의 범위**: 반면 "over 80%"와 "no measurable loss"가 붙은 대상은 **시스템 프롬프트 하나뿐이다**. `CLAUDE.md`와 스킬에 대해 원문이 주는 것은 정량 결과가 아니라 정성 권고다 — 글 말미에서도 "you may need to simplify just like we did"라고만 쓰고 숫자를 붙이지 않는다.

즉 "CLAUDE.md를 80% 줄여도 된다"는 문장은 원문에 없다. 진단이 셋을 향한다고 해서 측정치까지 셋에 붙는 건 아니다.

한 가지 더. 80%는 비율이고, 감축 전 시스템 프롬프트의 절대 길이는 공개되지 않았다. 분모를 모르면 절대 절감량도 모른다. 다른 출처의 토큰 수치와 나란히 놓고 비교할 근거가 없다는 뜻이기도 하다. 시중에 도는 "구 800토큰 → 신 164토큰" 같은 수치도 마찬가지다. 1차 출처가 확인되지 않는다 — 매체마다 출처를 7월 2일 컨퍼런스와 7월 24일 블로그로 다르게 적는데, 정작 블로그 본문에는 그 수치가 없다.

## 여섯 개의 전환, 각각이 딛고 선 근거

원문은 "Then → Now" 형식으로 여섯 쌍을 제시한다(원문 소제목 기준 6개). 흥미로운 건 여섯이 같은 체급의 근거를 갖고 있지 않다는 점이다. 아래 표의 "원문이 제시한 것" 열은 원문 본문을 읽고 정리한 것이다. 판정이 아니라 근거 유형의 분류다.

| Then → Now | 원문이 제시한 것 | 원문이 말한 적용 대상 |
|---|---|---|
| 규칙 주기 → 판단에 맡기기 | 구·신 시스템 프롬프트 문장을 **둘 다 인용** | Claude Code 시스템 프롬프트 |
| 예시 주기 → 인터페이스 설계 | 주장 + Todo 도구 열거형 예시 1건. 측정치 없음 | **도구 사용법** 예시 |
| 앞에 다 넣기 → 점진 공개 | 실제 변경 서술(검증·코드 리뷰를 별도 스킬로 분리, deferred loading 도구는 ToolSearch로 조회) | 시스템 프롬프트·도구. `CLAUDE.md`·`SKILL.md`에는 권고 |
| 반복하기 → 간결한 도구 설명 | 구세대 모델의 경향 서술 + "삭제할 수 있었다"는 서술 | 시스템 프롬프트 ↔ 도구 설명 |
| CLAUDE.md 메모리 → 자동 메모리 | 제품 동작 변경 서술 | Claude Code 제품 |
| 단순 스펙 → 풍부한 참조 | 권고 + 예시(HTML 아티팩트, 테스트 스위트, 루브릭). 비교 측정 없음 | 계획·스펙 참조 |

**가장 단단한 항목은 첫 줄이다.** 원문은 옛 문장과 새 문장을 나란히 보여준다. 옛 문장은 "In code: default to writing no comments. Never write multi-paragraph docstrings…"였고, 새 문장은 한 줄이다 — "Write code that reads like the surrounding code: match its comment density, naming, and idiom." 금지 목록을 판단 기준 하나로 바꾼 것이다. 무엇을 어떻게 지웠는지 독자가 직접 볼 수 있는 유일한 항목이기도 하다.

**가장 조심할 항목은 둘째 줄이다.** "예시를 주면 오히려 탐색 공간을 제약한다"는 주장은 few-shot 프롬프팅 통념과 정면으로 부딪히는데, 원문이 붙인 근거는 Todo 도구 열거형 하나이고 비교 수치는 없다. 그리고 범위가 좁다. 원문의 문장은 "The number one rule for **tool usage** was to give Claude examples on how to use them"이다. 도구 사용법 예시에 대한 이야기지 few-shot 일반에 대한 이야기가 아니다. 이 항목을 "예시를 다 빼라"로 확장하면 원문에 없는 주장을 만드는 셈이 된다.

원문이 인용한 새 시스템 프롬프트 문장은 실제로 돌아가고 있다. 이 글을 작성한 Claude Code 세션(2026-08-02, `claude --version` → 2.1.220)의 시스템 프롬프트에 "Write code that reads like the surrounding code: match its comment density, naming, and idiom."이 그대로 들어 있었고, deferred 도구를 ToolSearch로 당겨 쓰는 동작과 파일 기반 자동 메모리도 함께 있었다. 다만 이건 **관찰 한 건**이다. 원문의 80% 감축이나 평가 결과를 확인해주지는 않는다. 확인해주는 것은 "원문이 서술한 메커니즘이 실물로 존재한다"까지다.

## 우리 저장소로 옮길 때 사라지는 세 가지

여기서부터는 원문의 주장이 아니라 이 글의 검토다.

**첫째, 모델을 쥔 쪽이 아니다.** 원문이 규칙을 지운 근거는 "newer models have better judgement"다. 그런데 같은 원문이 반대 방향의 문장도 남겨뒀다 — "without these guardrails for older models, the comments Claude wrote would be incorrect in many cases and we had to accept this tradeoff." 가드레일은 구세대 모델에서 실제로 값을 했다는 얘기다. `CLAUDE.md`는 대개 한 모델만 읽지 않는다. 팀원마다 다른 모델을 쓰고, 서브에이전트에는 더 싼 모델을 물리고, 같은 파일을 다른 도구가 읽기도 한다. 그렇다면 삭제 기준은 최신 모델이 아니라 **그 파일을 읽는 가장 약한 독자**여야 한다. 이건 원문의 문장에서 우리가 끌어낸 추론이지 원문의 권고가 아니다.

**둘째, 평가가 없다.** "no measurable loss"라는 말을 하려면 measure가 있어야 한다. 원문은 자사 코딩 평가를 갖고 있고 우리는 대개 없다. 평가 없는 삭제는 개선이 아니라 그냥 변경이다. 잘 됐는지 안 됐는지 모른 채로 컨텍스트를 흔든 것이고, 문제가 나중에 드러나면 원인 후보가 하나 더 늘어난 상태다. 이 지점의 방법론은 [[에이전트-평가-evals]]로 넘긴다. 요지는 단발 성공률이 아니라 반복 일관성을 봐야 한다는 것이다. 프롬프트 다이어트의 손실은 정확히 그 일관성 쪽에서 먼저 나타날 가능성이 크다(추정).

**셋째, 분모가 없다.** 앞서 적었듯 80%는 비율이다. 우리 `CLAUDE.md`에서 80%를 지우는 일과 Anthropic이 시스템 프롬프트에서 80%를 지운 일은 대상도 절대량도 다르다. 같은 백분율이라는 이유로 같은 효과를 기대할 수 없다.

## 그래도 지금 바로 옳은 부분

비판만 하면 글이 게을러진다. 원문에서 계측 없이도 값을 하는 대목이 셋 있다.

**충돌 지시 감사.** 원문이 사내 트랜스크립트에서 관찰한 장면이 아프다. 한 요청 안에서 "leave documentation as appropriate"와 "DO NOT add comments"가 시스템 프롬프트·스킬·사용자 요청 사이를 오가며 부딪힌다. 원문의 표현대로 Claude는 대개 의도를 읽어내지만, 그 전에 "겹치고 충돌하는 메시지를 더 신중히 따져봐야" 한다. 이건 모델 세대와 무관한 순손실이다. 지워도 잃는 정보가 없는 유일한 종류의 삭제이기도 하다.

**뻔한 것 빼고 gotcha에 토큰 쓰기.** 원문의 `CLAUDE.md` 지침은 명확하다. 저장소 용도는 짧게 쓰고, 토큰 대부분을 코드베이스의 함정에 쓰고, 파일시스템이나 저장소만 봐도 아는 것은 적지 말라는 것이다. 이 규칙이 좋은 이유는 삭제 판단이 쉽기 때문이다. 에이전트가 도구로 1초 만에 확인할 수 있는 사실이면 텍스트로 중복해 적을 이유가 약하다.

**점진 공개.** 원문은 검증·코드 리뷰를 시스템 프롬프트에서 빼 별도 스킬로 옮겼고, 도구 일부는 정의를 검색해야 쓸 수 있는 deferred loading으로 돌렸다. 같은 원리를 `CLAUDE.md`·`SKILL.md`에도 적용하라고 권한다 — 모든 관행을 담은 중앙 저장소 대신 **필요할 때 로드되는 파일 트리**로. 우리 위키의 [[에이전트-스킬은-워크플로다]]가 다른 출처(Addy Osmani)에서 같은 자리에 도착해 있다. 두 글이 서로를 입증하는 건 아니지만, 권고의 방향은 겹친다.

셋은 여기까지다. 반대로 자동 메모리 전환은 편의만 있는 변화가 아니다. `#` 단축키로 사용자가 명시적으로 저장하던 것이 모델의 자동 판단으로 옮겨갔다는 뜻이고, 그러면 무엇이 기억됐는지 사람이 덜 들여다보게 된다. 무엇이 저장·삭제됐는지 증명해야 하는 환경이라면 이 전환은 편익만큼 감사 부담을 낳는다. [[하네스의-미래]]가 컴팩션을 두고 던진 질문과 인접한 자리다(같은 메커니즘은 아니다).

## 트레이드오프 — 지우면 안 되는 것

새 규칙에도 가격표가 붙는다.

- **점진 공개는 "안 읽힐 수 있음"을 사는 설계다.** 항상 실리던 문장을 조건부로 바꾸는 일이므로 정의상 그렇다. 원문 자신도 deferred loading 도구는 에이전트가 ToolSearch로 정의를 찾아야 쓸 수 있다고 명시한다. 즉 단계가 하나 늘어난다. 반드시 읽혀야 하는 한 문장을 하위 파일로 내리는 건 절약이 아니라 도박이다.
- **판단에 맡기면 출력 분산이 커진다.** 원문이 옛 규칙을 뒀던 이유가 바로 그 분산이었고, 원문은 그 대가를 "we had to accept this tradeoff"라고 표현했다. 트레이드오프의 방향을 뒤집는 것이므로, 일관성 자체가 계약인 곳 — 고정 포맷 출력, 규정 준수 문구, 외부에 나가는 산출물 — 에서는 규칙이 여전히 싸다(우리 판단).
- **결정론적 게이트는 애초에 컨텍스트가 아니다.** 이 위키의 발행 파이프라인([[위키-하네스]])처럼 스크립트로 집행되는 검사는 프롬프트가 아니라 코드다. "규칙을 지워라"의 사정권 밖에 있다. 지울 수 있는 건 산문으로 된 지시이고, 남는 건 실행되는 검사다.
- **원문 스스로 예외를 뒀다.** 스킬에 대해 "Avoid making them overconstrained, **except in highly important areas**"라고 쓴다. 삭제는 기본값이지 전면 규칙이 아니다.

## 실무 적용 — 삭제의 순서

내일 할 수 있는 순서로 적는다.

1. **재보기 전에는 지우지 않는다.** Claude Code에서 `/doctor`를 돌려 컨텍스트 비용과 가장 큰 기여자를 먼저 본다. 원문이 말한 "rightsize"가 무엇인지는 공식 커맨드 문서에 그대로 적혀 있고, 블로그의 표현과 같은 기능을 달리 요약한 것이다.
   - 쓰이지 않는 스킬·MCP 서버·플러그인을 컨텍스트 비용과 견줘 찾아낸다.
   - 로컬 `CLAUDE.md`를 체크인된 것과 중복 제거한다.
   - 체크인된 `CLAUDE.md`에서 Claude가 코드베이스만 봐도 유추할 수 있는 내용을 잘라낸다. 디렉터리 구조·의존성 목록·아키텍처 개요 같은 절이다. 함정과 근거, 도구 기본값과 다른 관례는 남긴다(이 트림은 Claude Code v2.1.206 이상에서만 동작한다).
   - 남는 상시 로드 지침은 스킬과, 필요할 때 로드되는 중첩 `CLAUDE.md`로 옮긴다.

   삭제 판단을 사람이 쥐라는 권고는 이 도구의 설계와도 맞아떨어진다. 문서는 `/doctor`가 "Reports findings first and asks for confirmation before changing anything"이라고 못 박는다.[^code-claude-com-commands] 먼저 재보고, 무엇을 지울지는 확인을 거친 뒤에 정한다.
2. **충돌부터 지운다.** 한 요청에 실리는 모든 텍스트(시스템 프롬프트·`CLAUDE.md`·활성 스킬·사용자 지시)를 실제 로드 순서대로 늘어놓고 서로 부딪히는 문장을 찾는다. 가장 싼 삭제다.
3. **뻔한 것을 지운다.** 에이전트가 `ls` 한 번, `grep` 한 번으로 확인할 사실은 뺀다. 그 자리를 gotcha로 채운다.
4. **반복을 도구 설명으로 옮긴다.** 같은 지시가 시스템 프롬프트와 도구 설명에 이중으로 있으면 도구 쪽만 남긴다.
5. **예시는 도구·스크립트·파일의 설계에 한해 재검토한다.** 원문의 처방이 "the design of your tools, scripts and files"까지 걸쳐 있다. 다만 few-shot 전반으로 확장하지는 않는다. 예시를 뺀 자리는 인터페이스로 메운다 — 자유 문자열 대신 열거형, 모호한 이름 대신 동작이 드러나는 파라미터.
6. **남은 큰 덩어리는 스킬로 분리한다.** 단, 반드시 읽혀야 하는 문장은 위에 남긴다.
7. **한 번에 한 덩어리씩, 되돌릴 수 있게.** 판정 가능한 태스크 몇 개를 골라 변경 전후를 반복 실행해 비교한다. 그게 없으면 "손실 없음"이라고 말할 자격이 없다 — 원문은 그 자격을 갖고 그 문장을 썼다.

## 이 글이 확인하지 못한 것

- 감축 전후 Claude Code 시스템 프롬프트의 절대 길이 — **공개되지 않았다.** 그래서 80%의 절대 효과는 계산 불가.
- "our coding evaluations"의 정체 — 원문에 명시가 없다. 벤치마크 이름도 구성도 알 수 없으므로 재현이나 제3자 검증이 불가능하다.
- 세션 관찰(신 시스템 프롬프트 문장·deferred 도구·자동 메모리)은 **한 세션 한 건**이다. 다른 버전·다른 플랜에서 같은지는 확인하지 않았다.

원문은 벤더가 자기 제품·자기 모델에 대해 쓴 1차 소스다. "무엇을 바꿨는가"에는 권위가 있고, "그것이 당신 환경에서도 옳은가"에는 권위가 없다. 그 경계에서 읽으면 이 글은 좋은 재료다.

---

관련: [[컨텍스트-엔지니어링]] · [[ai-엔지니어링-4계층]] · [[에이전트-스킬은-워크플로다]] · [[하네스의-미래]] · [[에이전트-평가-evals]] · [[위키-하네스]] · [[system-prompts-leaks]]

## 출처

- [The new rules of context engineering for Claude 5 generation models — Thariq Shihipar, Anthropic (2026-07-24)](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) — 이 글의 1차 소스. 본문 인용은 전부 여기서 땄다.
- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — 원문이 "context engineering"에 거는 링크.
- [A field guide to Claude Fable 5: Finding your unknowns — Thariq Shihipar, Anthropic (2026-07-06)](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns) — 원문이 서두·말미에서 거는 프롬프팅 가이드.
- [A harness for every task: dynamic workflows in Claude Code — Anthropic](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code) — 원문이 "파일 트리"·"dynamic workflows"에 거는 링크.
- [Claude Code — Skills 문서](https://code.claude.com/docs/en/skills) — `/doctor`가 번들 스킬이라는 사실의 출처(2026-08-02 확인).
- [Claude Code — Slash commands 문서](https://code.claude.com/docs/en/commands) — `/doctor`의 동작 범위(미사용 스킬·MCP·플러그인 점검, `CLAUDE.md` 중복 제거·트림·이관), "Reports findings first and asks for confirmation before changing anything", v2.1.206 버전 조건의 출처(2026-08-02 확인).

**세션 관찰의 방법**: 이 글을 작성한 Claude Code 세션에서 시스템 프롬프트에 노출된 문자열을 직접 확인했다. 환경은 macOS, `claude --version` → `2.1.220`, 모델 Claude Opus 5(1M), 확인 시점 2026-08-02. 다른 버전·플랜에서는 다를 수 있다.

[^claude-com-the-new-rules-of-context-engi]: Thariq Shihipar(Anthropic), "The new rules of context engineering for Claude 5 generation models" (2026-07-24) — 이 글의 1차 소스. [claude.com/blog](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
[^anthropic-com-effective-context-engineer]: Anthropic, "Effective context engineering for AI agents" — 원문이 "context engineering"에 거는 링크. [anthropic.com/engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
[^code-claude-com-commands]: Claude Code Docs, "Slash commands" — `/doctor`의 동작 범위와 확인 절차 문구. [code.claude.com/docs](https://code.claude.com/docs/en/commands)
