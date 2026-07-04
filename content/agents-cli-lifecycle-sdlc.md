---
title: agents-cli 라이프사이클과 AI 시대 SDLC
---

# agents-cli 8단계 라이프사이클 & AI 시대 SDLC

[[google-agents-cli]]가 제안하는 에이전트 개발 라이프사이클(8단계)을 정리하고, 이 구조가 **AI로 소프트웨어를 개발할 때 그대로 차용할 수 있는 SDLC**인지 심도 있게 살펴본다.

출처 페이지: `google.github.io/agents-cli/guide/lifecycle/`

---

## 1부 — agents-cli의 8단계 라이프사이클

핵심 아이디어: **"노트북에서 잘 돈다"에서 "프로덕션에서 살아있다"까지를 `scaffold → eval → deploy → observe` 네 동사의 무한 루프로 잇는다.** Phase 0(Spec)이 루프 전체의 앵커다 — eval 루브릭, scaffold 플래그, 안전 가드레일, 트레이스 속성이 전부 스펙에서 파생된다.

| # | 단계 | 하는 일 | CLI / 스킬 | 입·출력 |
|---|------|---------|-----------|---------|
| **0** | **Spec** | `.agents-cli-spec.md`에 도구·제약·성공 기준을 한 화면 분량으로 명세 | `workflow` 스킬 | 입력: Agent Garden 템플릿 → 출력: 마크다운 스펙 |
| **1** | **Scaffold** | 프로덕션 형태의 프로젝트(~72개 파일: 에이전트 코드·테스트·eval 보일러플레이트·Terraform·CI/CD·매니페스트) 생성 | `scaffold create` | 입력: 스펙+플래그 → 출력: 완성된 프로젝트 디렉터리 |
| **2** | **Build** | 에이전트 본체 작성 — 모델·instruction·tools·`App` 래퍼(~30줄) | `adk-code` 스킬 | 입력: ADK 프레임워크 → 출력: 동작하는 에이전트 코드 |
| **3** | **Orchestrate** | 한 에이전트가 팀으로 커지면 전문 에이전트들을 조합. 프로세스 간 호출은 A2A 프로토콜 | `adk-code` 스킬 | 입력: 에이전트 코드 → 출력: 멀티에이전트 아키텍처 |
| **4** | **Evaluate** | 배포 전에 데이터셋 대비 점수화. LLM 심판 + 루브릭 | `eval generate/grade/synthesize/compare/analyze/optimize` | 입력: 데이터셋 → 출력: eval 점수 · **5~10회+ 반복** |
| **5** | **Deploy** | Agent Runtime / Cloud Run / GKE로 배포 | `deploy` | 플래그: `--dry-run`, `--agent-identity`, `--iap` → 출력: 라이브 엔드포인트 |
| **6** | **Publish** | Gemini Enterprise 카탈로그에 등록(ADK/A2A 모드)해 발견 가능하게 | `publish` | 입력: 배포된 엔드포인트 → 출력: 카탈로그 항목 |
| **7** | **Observe** | Cloud Trace 스팬 + BigQuery 분석. **프로덕션 데이터가 다음 반복의 데이터셋으로 되먹임** | `observability` 스킬 | 입력: 실제 트래픽 → 출력: 트레이스·비용·회귀 |

### 루프의 핵심

Phase 7(관측)의 프로덕션 관찰이 → Phase 4(평가)의 내일 데이터셋이 되고 → 수정·재평가·재배포로 이어진다. 즉 **선형 파이프라인이 아니라 되먹임 루프**다.

권장 실천:
- 빈 화면에서 시작하지 말고 Agent Garden 템플릿부터.
- eval은 임계값 넘기까지 5~10회+ 반복을 기대할 것.
- 프로덕션 보안은 에이전트별 서비스 계정(`--agent-identity`) + IAP.
- scaffold 시점에 `--bq-analytics`를 켜서 관측 루프를 처음부터 닫아둘 것.

---

## 2부 — 이걸 일반 AI 개발 SDLC로 차용할 수 있는가?

**결론: 그렇다.** agents-cli의 8단계는 에이전트에 특화됐지만, 뼈대(Spec → Scaffold → Build → Evaluate → Deploy → Observe → 되먹임)는 2026년 업계가 수렴 중인 **AI 시대 SDLC의 실체적 형태**와 거의 일치한다. 아래는 여러 소스를 교차 검증한 심화 정리다.

### 2-1. 무엇이 바뀌었나 — "생성은 풀렸고, 검증이 새 기술이다"

전통 SDLC와 AI 시대 SDLC의 결정적 차이는 **속도가 아니라 무게중심의 이동**이다.

> "Generation is largely solved. Verification, judgment, and direction are the new craft."
> (생성은 대체로 해결됐다. 검증·판단·방향 설정이 새로운 기술이다.)

인간의 역할이 **구현자(implementer) → 오케스트레이터(orchestrator)**로 이동한다. 코드를 쓰는 대신, 스펙을 정밀화하고·에이전트 출력을 리뷰하고·아키텍처 트레이드오프를 판단한다.

### 2-2. 바이브 코딩 ↔ 에이전틱 엔지니어링 스펙트럼

이분법이 아니라 **검증 엄격도의 스펙트럼**이다:

| 수준 | 특징 | 적합 |
|------|------|------|
| **Vibe Coding** | 즉흥 프롬프트, 최소 테스트 | 프로토타입·버리는 코드 |
| **Structured AI-Assisted** | 제약 있는 상세 프롬프트, 수동 테스트 | 기존 코드베이스 |
| **Agentic Engineering** | 정식 스펙·아키텍처 문서·메모리 파일·자동 테스트·CI/CD 게이트 | 프로덕션 |

> 결정적 통찰: **결정론적 테스트(tests)와 비결정론적 평가(evals) 둘 다 없으면, 프롬프트가 아무리 정교해도 그냥 바이브 코딩이다.**

agents-cli가 Phase 4(Evaluate)를 배포 앞에 강제로 끼워넣는 이유가 바로 이것이다.

### 2-3. AI 시대 SDLC의 페이즈별 재편

업계 소스들이 공통으로 그리는 그림(전통 → AI-First):

- **요구사항/기획**: 2~6주 → 1~2일. AI가 스펙·유저스토리·데이터모델·API 스키마 초안을 몇 시간 안에. 인간은 생성이 아니라 **검토·정련**.
- **설계**: AI가 와이어프레임·컴포넌트 생성. 단, **아키텍처 트레이드오프의 주인은 여전히 인간**.
- **구현**: 코드의 60~80%를 AI가 생성(에러 핸들링·유닛테스트 포함). 인간은 쓰기→**리뷰·유도**로 전환.
- **테스트/QA**: **스펙에서 테스트를 코드보다 먼저 생성**(test-first 역전). 프로덕션 전 버그 검출 ~45% 개선. 결과물 품질뿐 아니라 **궤적(trajectory, 에이전트가 어떻게 도달했나)**도 평가.
- **배포**: IaC 템플릿화, 환경 패리티 자동 강제, 롤백 트리거 처음부터 내장. 1~3주 → 1~3일.
- **유지보수/관측**: 반응형 → 능동형. **관측을 배포 스펙에 처음부터 넣는다(observability as architecture).** 손댈 수 없던 레거시가 탐색 가능해지는 게 가장 큰 이득.

velocity 주장: 전체 SDLC가 6~12개월 → 6~12주(10~20배). (마케팅성 수치라 감안해 읽을 것.)

### 2-4. 자율성 스펙트럼과 거버넌스 (학술 리뷰)

에이전틱 AI를 SDLC에 적용할 때의 자율성 축(Assistance → Autonomy):

- **Assistance**: 제안, 개발자 승인 필요(코드 완성·린팅).
- **Semi-Autonomous**: 정의된 작업을 인간 감독 하에 실행(자동 테스트·제한적 리팩터링).
- **Autonomous**: 복잡한 SDLC 활동을 최소 개입으로 수행(엔드투엔드 생성·자율 버그 수정).

현재 대부분 도구는 assistance~semi 사이에 몰려 있다. 분류 차원: **의사결정 권한 · 작업 복잡도 · 감독 요구 · 실패 결과**. 핵심 경고: **overtrust(맹신) 리스크** — 검증 없이 수용하는 것. 그래서 프로덕션 임계 결정에는 모든 자율성 수준에서 인간 감독이 필수.

### 2-5. 차용 가능한 실천 원칙 (바로 적용)

1. **스펙을 앵커로.** 서술형 문서 말고 기계 판독 가능한 스펙(YAML/JSON schema/구조화 마크다운). → agents-cli Phase 0.
2. **에이전트 설정을 코드처럼.** `AGENTS.md`·프롬프트·eval을 버전관리하고 PR에서 리뷰.
3. **데모가 아니라 eval 스위트로 게이트.** 워크플로를 평가 통과 여부로 막는다. → Phase 4.
4. **Test-first를 기본값으로.** 스펙에서 테스트를 코드 전에 생성.
5. **관측을 아키텍처로.** 배포 첫날부터 모니터링·롤백 내장, 프로덕션 데이터를 다음 eval로 되먹임. → Phase 7→4 루프.
6. **하네스를 재사용 자산으로.** 프로젝트마다 다시 만들지 말고 공용 하네스 인프라로. → [[하네스-vs-루프-엔지니어링]]
7. **프로토타이핑(빠르게)과 프로덕션(규율 있게)을 명시적으로 구분.**
8. **컨텍스트 엔지니어링이 진짜 기술.** 출력 품질은 영리한 프롬프트보다 제공한 컨텍스트 품질에 달렸다. 6종(지시·지식·메모리·예시·도구·가드레일)을 정적/동적으로 관리.

### 2-6. 세 가지 불변 원칙

1. **구조는 확장되고, 바이브는 안 된다(Structure scales, vibes don't).**
2. **AI는 기존 문화를 증폭한다** — 강점도 약점도 함께 곱한다.
3. **인간의 역할이 진화한다** — 명세·평가·아키텍처 판단·시스템 설계가 곧 craft.

---

## 매핑 요약: agents-cli ↔ 일반 AI SDLC

| agents-cli 단계 | 일반 AI SDLC 대응 |
|---|---|
| Spec (0) | 스펙 주도 개발 (기계 판독 스펙) |
| Scaffold (1) | 프로젝트/IaC/CI-CD 템플릿 생성 |
| Build (2) / Orchestrate (3) | AI 구현 + 인간 리뷰·유도, 멀티에이전트 조합 |
| Evaluate (4) | Eval 게이트 + test-first (검증이 새 craft) |
| Deploy (5) / Publish (6) | 자동화 배포·롤백 내장·레지스트리 |
| Observe (7) → 4 | 관측을 아키텍처로, 프로덕션→데이터셋 되먹임 루프 |

**한 줄 결론:** agents-cli의 라이프사이클은 "에이전트 배포 도구"의 얼굴을 하고 있지만, 실제로는 **2026년 AI 개발이 수렴하는 SDLC(스펙 앵커 + eval 게이트 + 관측 되먹임 루프 + 인간은 오케스트레이터)를 벤더 툴로 구현한 참조 구현**이다. 도메인이 에이전트가 아니어도 이 뼈대는 그대로 차용할 수 있다.

---

리서치 출처:
- [agents-cli lifecycle 공식 문서](https://google.github.io/agents-cli/guide/lifecycle/)
- [working software — The New SDLC: From Vibe Coding to Agentic Engineering](https://www.workingsoftware.dev/the-new-software-development-lifecycle-sdlc-from-vibe-coding-to-agentic-engineering/)
- [arXiv 2605.15245 — Assistance to Autonomy: SLR of Agentic AI across the SDLC](https://arxiv.org/pdf/2605.15245)
- [GroovyWeb — SDLC in the AI Era 2026](https://www.groovyweb.co/blog/sdlc-ai-era-software-development-2026)
