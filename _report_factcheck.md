# 검증 리포트 — 팩트/최신성 (위키 스팟 체크)

검증일: 2026-07-05 / 대상: batch-work/content/ (7개 노트 스팟 체크, 노트당 3~5개 최고위험 주장)
방식: 반증 지향 + 작성일 기준 최신성. 🔴(발행 차단급 오류·낡음)만 타깃. 웹 검색 14회.
검증 제외: `에이전트-평가-evals.md`(어제 검증), 메타 노트 4종(레포 자체 근거).

## 노트별 판정

| 노트 | 판정 | 🔴 | 🟡 |
|---|---|---|---|
| google-agents-cli.md | PASS-WITH-NOTES | 0 | 1 |
| agents-cli-lifecycle-sdlc.md | PASS | 0 | 0 |
| 프로덕션-ai-에이전트-기본-개념.md | PASS | 0 | 0 |
| ai-엔지니어링-4계층.md | PASS | 0 | 0 |
| 프롬프트-엔지니어링.md | PASS-WITH-NOTES | 0 | 1 (+UNVERIFIED 1) |
| 컨텍스트-엔지니어링.md | PASS | 0 | 0 |
| 하네스-엔지니어링.md | PASS | 0 | 0 |
| 루프-엔지니어링.md | PASS | 0 | 0 |

**전체: 🔴 0개.** 발행 차단 사유 없음. 🟡 2건(각주 권장), UNVERIFIED 1건.

---

## 지적 사항

| # | 위치(인용) | 문제 | 심각도 | 수정 제안 | 근거(URL) |
|---|---|---|---|---|---|
| 1 | google-agents-cli.md: "최신: v0.6.1 (2026-06-28 기준, 공개 71일간 13번 업데이트)" | **최신성**: 오늘(07-05) 기준 이미 **v1.0.0(2026-07-01 릴리스)**이 나와 v0.6.1은 최신이 아님. 단 노트가 "(2026-06-28 기준)"으로 스냅샷 명기 → 정직한 표기라 차단은 아님. | 🟡 | "v1.0.0(2026-07-01) 출시로 GA 전환" 각주 추가 또는 버전 줄 갱신 | https://github.com/google/agents-cli |
| 2 | 프롬프트-엔지니어링.md: "CoT는 어떤 추론 벤치에서 정확도를 17.7%에서 78.7%까지 끌어올린 사례가 보고됐다." | **팩트(수치 출처 불명)**: Wei et al. 2022 원 CoT 논문의 대표 수치는 GSM8K PaLM-540B **17.9%→56.9%**. "17.7→78.7" 짝은 원 논문·self-consistency 논문(GSM8K 56.5→74.4) 어디에도 정확히 일치하지 않음. 인터넷 반복 인용이나 1차 출처 확인 불가. 노트가 "어떤 벤치에서…보고됐다"로 hedge해 명백한 오류로 단정은 불가. | 🟡 | 정확한 벤치·출처를 못 박거나(예: GSM8K 17.9→56.9로 교정), 못 찾으면 수치 삭제하고 "벤치마크마다 큰 폭 향상 보고"로 일반화 | https://arxiv.org/abs/2201.11903 · https://arxiv.org/abs/2203.11171 |

---

## 검증 통과(반박 실패 = PASS)한 고위험 주장

- **agents-cli 공개/후속작**: Cloud Next 2026(4월 22일) 발표, agent-starter-pack 후속·starter-pack 유지보수 모드 전환 — 확인. 설치 스킬 7종(workflow/adk-code/scaffold/eval/deploy/publish/observability), `uvx google-agents-cli setup` / `npx skills add`, Python 3.11+·uv·Node 요구 — 전부 GitHub와 일치. (github.com/google/agents-cli)
- **SKILL.md 오픈 스펙 = Anthropic 2025년 12월**: 정확히 **2025-12-18** 공개. 점진적 공개(progressive disclosure) 구조 일치. 여러 노트(google-agents-cli, 컨텍스트-엔지니어링)에서 반복되는 이 날짜 주장 모두 PASS. (anthropic.com/engineering/equipping-agents...)
- **GPT-3.5 HumanEval 48.1%→95.1%(에이전트 루프)** [프롬프트]: Andrew Ng/DeepLearning.AI "Four AI Agent Strategies"와 일치 — PASS.
- **LangChain Terminal Bench 2.0 52.8→66.5(+13.7), gpt-5.2-codex 고정, Top30→Top5** [하네스/lifecycle]: 공식 블로그와 일치 — PASS.
- **90% 하네스 / 10% 모델** [하네스]: 하네스 엔지니어링 문헌(Google 귀속)에서 널리 인용되는 주장, 노트가 "한 정리에 따르면"으로 hedge — PASS.
- **arXiv 2606.06324 "harness flaws"** [하네스/lifecycle]: 실재(2026-06-04 제출, "From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws"). '하네스 격차' 개념 일치 — PASS.
- **METR RCT: 체감 20%↑ vs 실제 19%↓, 16명·246태스크·2025 상반기, arXiv 2507.09089** [lifecycle]: 완전 일치 — PASS. (단 "METR 2026-02 방법론 한계 인정"은 컷오프 이후 세부라 미검증이나 hedge 문구라 저위험.)
- **Loop Engineering 코이닝(2026-06, Osmani 명명, Steinberger·Cherny)** [루프]: Steinberger 원문·Cherny 발언·Osmani 명명 모두 확인 — PASS.
- **Chroma Context Rot(2025, 프론티어 18모델 전수 확인)** [컨텍스트]: 18개 모델, 모든 길이 구간 저하 — 일치, PASS.
- **AB-MCTS/TreeQuest(Sakana AI, arXiv:2503.04412)** [프로덕션]: 실재·귀속 정확 — PASS.
- **AgentVista(HKUST-NLP, 209과제, arXiv:2602.23166, 최상위<30%)** [프로덕션]: 최상위 Gemini-3-Pro 27.27% — "30% 넘기기 어렵다" 정확, PASS.
- **OWASP Top 10 for Agentic Applications(2026), ASI02 도구 오용** [프로덕션]: 2025-12-09 공개, ASI02 = Tool Misuse and Exploitation — 일치, PASS.
- **Lusser의 법칙(직렬 신뢰성=곱, Robert Lusser, 1950년대 로켓/미사일)** [프로덕션]: Redstone Arsenal, V-2 계열 미사일 실패 분석 — 정확, PASS.
- **MCP = Anthropic 2024년 11월** [컨텍스트/프로덕션]: 사전지식 확인(2024-11) — PASS.
- **컨텍스트/하네스/루프 계보 계층 서술**: 개념 정리로 반박 대상 아님 — PASS.

---

## UNVERIFIED (판단 보류)

- **CoT 17.7%→78.7%** (프롬프트-엔지니어링.md): 1차 출처(arXiv 2201.11903 본문 수치표)에서 이 정확한 짝을 확인/반박 모두 불가. 위 지적 #2로 처리 — 오케스트레이터 판단 요청. 반증 지향 원칙상 "확인 실패"이므로 발행 전 출처 확정 또는 수치 완화 권고.
- **agents-cli "공개 71일간 13번 업데이트"** (google-agents-cli.md): 릴리스 카운트 세부는 미검증(저위험 트리비아). 다른 정황(6-28 릴리스, adk 2.2→2.3)과 모순 없음.
- **METR "2026-02 방법론적 한계 인정"** (lifecycle): 컷오프 이후 세부라 미확인. hedge 문구라 저위험.

---

## 종합 권고

발행 차단(🔴) 없음 → **PASS-WITH-NOTES로 발행 가능**. 다만 두 각주 반영 권장:
1. google-agents-cli 버전 줄을 v1.0.0(07-01)로 갱신하거나 GA 각주 추가.
2. 프롬프트 노트의 CoT 17.7→78.7 수치를 1차 출처로 확정하거나(권장: GSM8K 17.9→56.9) 완화.
