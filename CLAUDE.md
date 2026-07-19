# knowledge-wiki

## 하네스: 기술 글 파이프라인

**목표:** IT 전분야 기술 글을 작성(에반젤리스트+CTO 시각)→검증(최신성·팩트·오탈자·윤문)→발행(OKF 위키)까지 자동 처리.

**트리거:** 기술 글 작성+발행 요청 시 `wiki-post` 스킬 사용 (예: "~에 대해 글 써서 위키에 올려줘"). 완성 노트 업로드만은 `wiki-note`. 로컬 설치: `.claude/agents/`·`.claude/skills/`를 `~/.claude/`에 복사 (윤문은 humanize-korean 플러그인 별도 설치 권장).

**종속 문서:** 하네스(에이전트·스킬·게이트) 변경 시 `content/위키-하네스.md`와 README의 하네스·비용 섹션을 같은 커밋에서 갱신하라.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-07-05 | 초기 구성 (tech-writer·fact-checker·copy-editor + tech-writing·wiki-verify·wiki-post) | 전체 | - |
| 2026-07-05 | copy-editor에 '대기 금지' 지침 추가 | .claude/agents/copy-editor.md | 첫 실행에서 humanize-korean 대기 중 정지 |
| 2026-07-05 | 병합 게이트(validate-note.py)·수치 전수/UNVERIFIED 발행 규칙·경계선 재확인 추가 | .claude/skills/wiki-post, wiki-verify | 에이전트-평가-evals 노트의 원칙을 하네스 자신에 적용 |
| 2026-07-05 | 마크다운 렌더 검증·근사표기 규칙 추가, 깨진 강조 3곳·~N 10곳 교정, 종속 문서 동기화 규칙 | wiki-verify·validate-note.py·위키-하네스·README | 발행물에서 리터럴 **·~ 노출 발견 (규칙 부재) |
| 2026-07-12 | 검증 규칙 2개: ⑦ 상류 근거 파일도 검증 대상(리서치 산출물은 1차 소스 아님), ⑧ 해석 검증(수치가 맞아도 그 위 인과·비교·일반화를 별도 반증) | wiki-verify·위키-하네스·README | 리서치 파일의 오류가 초안까지 전파됐고, FAIL이 틀린 수치가 아니라 맞는 수치 위 틀린 해석에서 남 |
| 2026-07-17 | 최종 가독성 게이트 신설: readability-reviewer 에이전트 + readability-review 스킬, wiki-post에 Phase 3.5(병합 뒤·발행 앞) 배선 | .claude/agents·.claude/skills·wiki-post·위키-하네스·README | 윤문·병합을 통과하고도 발행본에 AI 티·난해 용어가 남음. 통독 검수자가 부재 |
| 2026-07-17 | tech-writing에 '연결의 근거'(⑥ 엣지 근거)·'집계 방법 병기' 규칙 + wiki-post Phase 1 선행 리서치 코드화(엣지 금지·자기 경고 헤더 의무) | tech-writing·wiki-post·위키-하네스·README | 해석 FAIL 3연속의 공통 구조가 '엣지'(사실 둘을 잇는 자리). ⑧을 작성 쪽에 미러링 |
| 2026-07-19 | 규칙 ⑥ 측정 종료 → **확정: 유효.** wiki-post Phase 5의 '측정 중' 절을 '원장 기록(회귀 계측)'으로 교체 | wiki-post·위키-하네스·README | 6편 창에서 해석 FAIL 1편뿐 + 확정 조건인 비토론형 해석 고밀도 편(turbovec)이 도착해 버팀 |
| 2026-07-19 | **wiki-debug 스킬 신설**(tinker-cookbook `/tinker:debug` 차용) — 발행 사후 진단·⑥ 원장 행 초안·현재 원격 원장 재대조. 스킬 미러 동기화 + README 스킬 로스터 표 | .claude/skills·claude-skill·wiki-post·위키-하네스·README | tinker 편에서 원장 행을 낡은 상태에 써 push 충돌. 병목은 진단이 아니라 '행 쓰기 전 원장 재대조' 절차. tinker의 run/debug 분리를 차용 |
