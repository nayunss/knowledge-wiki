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
