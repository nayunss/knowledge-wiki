#!/usr/bin/env bash
# 커밋 전 시크릿·개인정보 게이트. claude-skill/ 안의 모든 추적 파일을 스캔한다.
# 통과 = exit 0. 하나라도 걸리면 exit 1 (커밋 금지).
set -uo pipefail
cd "$(dirname "$0")"

FILES=$(find skills agents -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' \) 2>/dev/null; ls CLAUDE.project.md 2>/dev/null)
fail=0

scan() { # $1=라벨 $2=정규식 $3=제외(선택)
  local hits
  hits=$(grep -rEn -i "$2" $FILES 2>/dev/null | { [ -n "${3:-}" ] && grep -vEi "$3" || cat; })
  if [ -n "$hits" ]; then echo "❌ $1"; echo "$hits" | sed 's/^/     /'; fail=1
  else echo "✅ $1"; fi
}

# 고신뢰 시크릿
scan "API 키/토큰/PEM"  'sk-[a-zA-Z0-9]{20}|ghp_[a-zA-Z0-9]{36}|github_pat_|gho_[a-zA-Z0-9]|AKIA[0-9A-Z]{16}|xox[baprs]-|-----BEGIN|bearer [a-zA-Z0-9._-]{20}'
# 개인정보 — 실제 이메일(플레이스홀더 USER/OWNER, noreply 제외)
scan "이메일"          '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}' 'noreply|@anthropic|example\.|USER/|OWNER/|<owner>|git@github\.com:(USER|OWNER|<)'
# 홈 경로에 박힌 실제 username (플레이스홀더 <owner> 제외)
scan "홈경로 username"  '/Users/[a-z0-9._-]+/'
# 하드코딩된 GitHub 핸들 (owner/repo 플레이스홀더는 허용)
scan "하드코딩 레포핸들" 'github\.com[:/][a-z0-9-]+/[a-z0-9._-]+' 'USER/|OWNER/|<owner>|<repo>|USER|OWNER'

echo
if [ "$fail" -eq 0 ]; then echo "게이트 통과 — 커밋 가능."; else echo "게이트 실패 — 위 항목을 제거하기 전엔 커밋 금지."; fi
exit $fail
