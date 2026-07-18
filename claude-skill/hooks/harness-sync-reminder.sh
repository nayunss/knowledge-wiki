#!/usr/bin/env bash
# Stop 훅 — 위키 하네스 파일이 마지막 백업 이후 바뀌었으면 sync 안내만 출력한다.
# 자동 sync/커밋은 하지 않는다(사람이 통제). 조용할 땐 아무것도 출력하지 않는다.
set -uo pipefail

CL="$HOME/.claude"
MARK="$CL/.harness-synced-hash"

# 추적 대상 — claude-skill/ 로 백업되는 하네스 파일들
FILES=(
  "$CL/skills/wiki-note/SKILL.md"
  "$CL/skills/wiki-post/SKILL.md"
  "$CL/skills/wiki-post/scripts/validate-note.py"
  "$CL/skills/wiki-verify/SKILL.md"
  "$CL/skills/tech-writing/SKILL.md"
  "$CL/skills/readability-review/SKILL.md"
  "$CL/agents/tech-writer.md"
  "$CL/agents/fact-checker.md"
  "$CL/agents/copy-editor.md"
  "$CL/agents/readability-reviewer.md"
)

now="$(for f in "${FILES[@]}"; do [ -f "$f" ] && shasum -a 256 "$f"; done | sort | shasum -a 256 | cut -d' ' -f1)"
prev="$(cat "$MARK" 2>/dev/null || echo '')"

# 마커가 없으면(최초) 조용히 현재 상태로 초기화 — 안내 안 함
if [ -z "$prev" ]; then echo "$now" > "$MARK"; exit 0; fi

if [ "$now" != "$prev" ]; then
  # Stop 훅은 systemMessage JSON을 내보내야 사용자에게 보인다.
  # 메시지에 JSON 특수문자(따옴표·역슬래시·개행)를 쓰지 않아 직접 출력해도 안전하다.
  printf '{"systemMessage": "위키 하네스 파일이 마지막 백업 이후 바뀌었다. knowledge-wiki 클론에서 cd claude-skill 후 ./sync-from-local.sh 로 백업하라 (동기화·시크릿게이트·커밋·푸시 일괄). 끝나면 이 안내는 자동으로 멈춘다."}\n'
fi
exit 0
