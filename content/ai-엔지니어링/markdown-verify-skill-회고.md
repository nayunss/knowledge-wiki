---
title: Markdown Verify Skill 회고 — 문법 검수에서 두 마켓플레이스까지
type: 회고
description: 깨진 Markdown을 막는 검수 스킬을 만들고, 단일 원본을 Codex와 Claude Code의 독립 마켓플레이스로 배포하며 배운 설계 원칙과 한계를 정리한다.
tags: [agent-skills, markdown, codex, claude-code]
resource: https://github.com/nayunss/md-verify-skill
date: 2026-08-03
sources:
  - id: github-com-md-verify-skill
    resource: https://github.com/nayunss/md-verify-skill
    title: Markdown Verify Skill 저장소
  - id: spec-commonmark-org-current
    resource: https://spec.commonmark.org/current/
    title: CommonMark Specification
  - id: github-github-com-gfm
    resource: https://github.github.com/gfm/
    title: GitHub Flavored Markdown Specification
  - id: developers-openai-com-plugins
    resource: https://developers.openai.com/plugins/build/plugins
    title: OpenAI, Package your plugin
  - id: developers-openai-com-submission
    resource: https://developers.openai.com/plugins/deploy/submission
    title: OpenAI, Submit plugins
  - id: code-claude-com-plugin-marketplaces
    resource: https://code.claude.com/docs/en/plugin-marketplaces
    title: Claude Code, Create and distribute a plugin marketplace
  - id: code-claude-com-plugins
    resource: https://code.claude.com/docs/en/plugins
    title: Claude Code, Create plugins
  - id: code-claude-com-plugins-reference
    resource: https://code.claude.com/docs/en/plugins-reference
    title: Claude Code, Plugins reference
---

문서 생성은 성공했는데 결과를 열어 보면 강조 기호가 글자 그대로 남고, 줄바꿈은 붙고, 목록은 불릿이 아니라 평문으로 보였다. 내용은 맞아도 읽을 수 없는 Markdown은 완성품이 아니다. 그런데 이 문제를 매번 눈으로만 찾으면 같은 실수가 반복된다.

그래서 Markdown Verify Skill을 만들었다. 출발점은 `**`와 `~~`, `<br>`, 목록과 개행 같은 눈에 띄는 파손이었다. 결과적으로 만든 것은 문법 팁 모음이 아니라 **정적 검사 → 사람의 문맥 판단 → 실제 렌더링 → 배포 환경 설치 검증**으로 이어지는 품질 게이트였다.

## 결론부터: 스킬의 본체보다 검증층과 배포 경계가 더 중요했다

이번 작업에서 얻은 결론은 세 가지다.

1. Markdown 검수는 문자열 짝 맞추기로 끝나지 않는다. 렌더러가 최종 제품을 결정한다.
2. 같은 스킬을 여러 에이전트에서 쓰려면 본문은 한 벌로 두고, 런타임별 manifest와 marketplace catalog만 분리해야 한다.
3. GitHub 기반 독립 마켓플레이스 등록과 벤더의 공개 디렉터리 심사 등재는 다른 단계다. “등록 완료”라는 말은 어느 층을 뜻하는지 밝혀야 한다.

이 세 결론은 [[에이전트-스킬은-워크플로다]]에서 말한 “스킬은 지식이 아니라 실행 순서”라는 주장과 맞닿아 있다. 이번 작업에서는 그 실행 순서를 문서 품질과 배포까지 넓혔다.

## 시작은 작은 렌더링 파손이었다

처음 떠올린 실패는 단순했다.

- 닫히지 않은 `**`와 `~~`가 그대로 노출된다.
- raw HTML 줄바꿈 태그가 텍스트로 보인다.
- 한 줄 개행을 시각적 줄바꿈으로 기대했지만 문장이 붙는다.
- 목록 마커 뒤 공백이나 들여쓰기가 잘못돼 불릿이 평문이나 코드로 바뀐다.

조사를 시작하자 범위가 넓어졌다. 닫히지 않은 코드 펜스는 문서 나머지를 코드로 삼킬 수 있고, 닫히지 않은 HTML 주석은 이후 내용을 숨길 수 있다. reference link와 footnote 정의가 빠질 수 있고, frontmatter가 닫히지 않으면 본문이 metadata로 오인될 수 있다. 중복 제목은 deep link anchor를 흔들고, raw HTML은 렌더러의 sanitizer와 tag filter에 따라 사라지거나 글자로 남는다.

CommonMark와 GFM을 함께 본 이유가 여기 있다. CommonMark가 코드 펜스·목록·강조·링크·줄바꿈의 기본 파싱을 정한다면, GFM은 표·task list·취소선·autolink 같은 확장을 더한다. MDX, 수학, Mermaid, wiki link까지 가면 “유효한 Markdown”이라는 단일 판정만으로는 부족하다. **어디서 렌더링할 것인지가 문법의 일부다.**

## 구현: 정적 검사기는 판사가 아니라 선별기다

스킬은 네 부분으로 나눴다.

```text
review-markdown/
├── SKILL.md
├── agents/openai.yaml
├── references/render-risk-catalog.md
└── scripts/
    ├── check_markdown.py
    └── test_check_markdown.py
```

`SKILL.md`는 작업 순서를 정한다. 대상 렌더러와 저장소 규칙을 먼저 확인하고, 검사기를 실행한 뒤, 진단을 문맥에서 판단하고, 가능하면 실제 preview나 build를 확인한다. `render-risk-catalog.md`는 확실한 구조 오류, 이식성 위험, 확장 문법 위험을 나눈다. Python 검사기는 의존성 없이 흔한 파손을 line number와 함께 찾는다.

검사기는 코드 span과 fenced code block 안의 예시를 건너뛴다. 그렇지 않으면 “잘못된 Markdown 예시”를 설명하는 문서가 전부 실패한다. 반대로 강조 문법 전체를 직접 파싱하려 들지 않았다. `*`와 `_`는 주변 공백과 문장부호에 따라 opener와 closer 여부가 달라지므로 단순 개수 검사가 쉽게 거짓 양성을 만든다.

이 선택은 타협이다. 검사기는 확실히 잡을 수 있는 실패를 앞단에서 거르고, 애매한 것은 warning으로 돌린다. 최종 판정은 production renderer가 맡는다. [[에이전트-평가-evals]]의 언어로 말하면, heuristic checker 하나를 품질의 정답지로 쓰지 않고 서로 다른 증거층을 겹쳤다.

회귀 테스트는 6개다. 정상 문서, 코드 내부 literal, 코드 펜스·강조·제목 파손, reference와 task list, raw HTML, frontmatter와 thematic break를 각각 다룬다. 개수는 저장소의 `test_check_markdown.py`에서 `def test_` 선언을 센 값이다.

## 단일 원본: 스킬 하나, 포장지는 둘

처음에는 Claude Code 전역 폴더를 원본으로 두고 Codex 경로를 symbolic link로 연결했다. 개인 환경에서는 간단했지만, GitHub 배포에는 맞지 않았다. 절대 경로 link는 다른 컴퓨터에서 깨지고, marketplace installer는 plugin directory를 cache로 복사하므로 바깥 파일을 참조하면 안 된다.

저장소 구조를 다음처럼 바꿨다.

```text
.
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
└── plugins/md-verify/
    ├── .codex-plugin/plugin.json
    ├── .claude-plugin/plugin.json
    └── skills/review-markdown/
```

핵심은 `skills/review-markdown/`가 한 벌이라는 점이다. Codex와 Claude Code의 manifest와 marketplace catalog는 서로 다른 규격이므로 분리하지만, 실행 지침·reference·검사기·테스트는 복제하지 않는다. 양쪽 설명문이 조금씩 달라지는 문제를 구조로 막았다.

그렇다고 중복이 완전히 사라진 것은 아니다. 이름과 설명, 작성자 정보는 manifest와 catalog에 반복되고, 버전은 두 manifest와 Claude catalog에 적힌다. 지금은 파일 수가 작아 사람이 맞출 수 있지만, 릴리스가 잦아지면 생성 스크립트나 CI 일관성 검사가 필요하다.

## 마켓플레이스: 같은 단어, 다른 계약

Codex 쪽은 `.codex-plugin/plugin.json`으로 plugin identity를 정의하고, 저장소의 `.agents/plugins/marketplace.json`이 설치 가능한 plugin을 가리킨다. GitHub 원격 저장소를 격리된 설정에서 추가한 뒤 `md-verify` 설치와 활성 상태까지 확인했다.

Claude Code는 저장소 루트의 `.claude-plugin/marketplace.json`과 plugin 내부의 `.claude-plugin/plugin.json`을 읽는다. plugin skill은 namespace가 붙어 `/md-verify:review-markdown`으로 호출된다. 이쪽도 로컬 경로와 GitHub 원격 저장소 양쪽에서 marketplace 추가와 plugin 설치를 확인했다.

여기서 표현을 바로잡아야 한다. **이번에 완료한 것은 두 제품에서 설치 가능한 GitHub 기반 독립 마켓플레이스다.** OpenAI의 universal plugin directory와 Anthropic의 community marketplace에 공개 심사 등재된 상태는 아니다. 두 벤더 모두 공개 directory 제출에는 별도 심사 절차가 있다. repository marketplace가 배포 가능한 상태라는 것과 공식 catalog에 검색 노출된다는 것은 다르다.

이 구분은 사소하지 않다. “마켓플레이스 등록”이라고만 쓰면 독자는 공식 directory에서 검색될 것으로 기대한다. 배포 문서에는 custom marketplace, workspace 공유, public directory를 서로 다른 release channel로 써야 한다.

## 잘된 결정

### 1. 실패 사례에서 시작해 분류 체계로 확장했다

처음부터 Markdown 전체 parser를 만들려 하지 않았다. 실제로 반복된 파손을 모으고, 공식 specification에서 인접 실패를 조사한 뒤 “확실한 오류 / 이식성 warning / renderer extension”으로 나눴다. 이 분류가 검사기의 자유도를 정했다.

### 2. 검증을 한 번이 아니라 층으로 만들었다

Python syntax, 회귀 테스트, skill manifest validator, plugin validator, Markdown checker, 실제 marketplace install을 각각 실행했다. schema가 맞는 것과 사용자가 설치할 수 있는 것은 다른 주장이다. 마지막 원격 설치가 앞의 검사를 대체하지 않지만, 앞의 검사만으로는 보여주지 못한 경로를 확인했다.

### 3. 런타임 차이를 숨기지 않았다

두 제품 모두 “skill”과 “marketplace”라는 말을 쓰지만 directory와 호출 namespace는 다르다. 억지로 하나의 manifest로 합치지 않고, 공통 core와 vendor adapter를 갈랐다. [[하네스-엔지니어링]]에서 말하는 실행 환경의 차이를 packaging layer에 드러낸 셈이다.

## 아쉬웠던 점과 트레이드오프

| 선택 | 얻은 것 | 치른 비용 |
|---|---|---|
| 의존성 없는 정적 검사기 | 어디서나 바로 실행 | 완전한 Markdown AST를 만들지 못함 |
| warning 중심의 보수적 검사 | 자동 수정으로 문서를 망칠 위험 감소 | 사람이 문맥을 판정해야 함 |
| 스킬 본문 단일 원본 | 지침 drift 감소 | vendor metadata 중복은 남음 |
| 두 marketplace 실설치 검증 | 배포 경로 증거 확보 | 테스트한 OS·CLI 버전 밖은 보장하지 못함 |
| version을 manifest에 명시 | 릴리스 identity 명확 | 내용 변경 때 version을 가진 manifest·catalog metadata를 함께 갱신해야 함 |

가장 큰 한계는 “렌더링 확인”의 자동화가 아직 약하다는 점이다. repository마다 Quartz, GitHub, MDX, Docusaurus 등 renderer가 다르다. 범용 스킬이 production preview까지 자동으로 만들려면 대상별 adapter가 필요하다. 지금 스킬은 기존 build가 있으면 실행하라고 지시하지만, renderer 자체를 제공하지 않는다.

또 검사기가 고칠 수 있는 문제와 글쓴이의 의도를 알아야 하는 문제를 나눠야 한다. `<br>`가 노출됐다고 무조건 삭제하면 표 안의 의도적 줄바꿈을 망칠 수 있다. 네 칸 들여쓰기 목록도 문맥에 따라 중첩 항목의 본문일 수 있다. 목표는 warning을 없애는 것이 아니라, **설명되지 않은 warning을 없애는 것**이다.

## 다시 한다면

1. 먼저 broken fixture와 expected diagnostic을 만든다. 규칙을 쓴 뒤 예시를 맞추는 순서를 피한다.
2. renderer profile을 옵션으로 둔다. CommonMark, GFM, MDX, Quartz에서 허용할 extension을 분리한다.
3. 두 vendor manifest의 공통 metadata를 한 파일에서 생성한다. version drift를 CI에서 차단한다.
4. release test에 GitHub 원격 marketplace 설치를 포함한다. local path 설치만 성공하면 Git source와 cache 경로 문제를 놓칠 수 있다.
5. public directory 제출 전에는 privacy, support, license, logo, positive·negative test case를 별도 release gate로 둔다.

## 남은 결론

처음 문제는 “별표가 그대로 보인다”였다. 해결 과정은 parser specification, deterministic checker, render preview, cross-runtime packaging, marketplace install까지 갔다. 범위가 커진 이유는 단순하다. 사용자가 보는 결과를 품질 기준으로 삼으면, 소스 작성만으로는 일이 끝나지 않기 때문이다.

좋은 스킬은 지시를 잘 적은 Markdown 파일 하나가 아니다. **반복 실패를 분류하고, 싼 검사부터 실제 환경 검증까지 증거를 쌓으며, 배포된 자리에서도 같은 본문을 읽게 만드는 작은 하네스**다. Markdown Verify Skill은 그 정의를 문서 품질 문제에 적용한 첫 구현이었다.

관련: [[에이전트-스킬은-워크플로다]] · [[하네스-엔지니어링]] · [[에이전트-평가-evals]] · [[위키-하네스]] · [[컨텍스트-엔지니어링]]

## 출처

- [Markdown Verify Skill 저장소](https://github.com/nayunss/md-verify-skill)
- [CommonMark Specification](https://spec.commonmark.org/current/)
- [GitHub Flavored Markdown Specification](https://github.github.com/gfm/)
- [OpenAI, Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI, Submit plugins](https://developers.openai.com/plugins/deploy/submission)
- [Claude Code, Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code, Create plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code, Plugins reference](https://code.claude.com/docs/en/plugins-reference)
