#!/usr/bin/env bash
# 역방향 백업 — ~/.claude 의 현재 하네스를 이 레포로 끌어와 커밋·푸시한다.
# 성공하면 ~/.claude/.harness-synced-hash 마커를 갱신해 Stop 훅 안내를 멈춘다.
# 시크릿 게이트(secrets.sh)를 통과하지 못하면 커밋하지 않는다.
set -euo pipefail
cd "$(dirname "$0")"
SRC="$HOME/.claude"

# 훅과 동일한 방식으로 하네스 해시를 계산해 마커에 쓴다
write_marker() {
  local FILES=(
    "$SRC/skills/wiki-note/SKILL.md" "$SRC/skills/wiki-post/SKILL.md"
    "$SRC/skills/wiki-post/scripts/validate-note.py" "$SRC/skills/wiki-verify/SKILL.md"
    "$SRC/skills/tech-writing/SKILL.md" "$SRC/skills/readability-review/SKILL.md"
    "$SRC/agents/tech-writer.md" "$SRC/agents/fact-checker.md"
    "$SRC/agents/copy-editor.md" "$SRC/agents/readability-reviewer.md"
  )
  local f; for f in "${FILES[@]}"; do [ -f "$f" ] && shasum -a 256 "$f"; done \
    | sort | shasum -a 256 | cut -d' ' -f1 > "$SRC/.harness-synced-hash"
}

# 1. 하네스 파일 끌어오기
for name in wiki-note wiki-post wiki-verify tech-writing readability-review; do
  [ -d "$SRC/skills/$name" ] || continue
  mkdir -p "skills/$name"
  rsync -a --delete "$SRC/skills/$name/" "skills/$name/"
  echo "  ← skill  $name"
done
for a in tech-writer fact-checker copy-editor readability-reviewer; do
  [ -f "$SRC/agents/$a.md" ] && cp "$SRC/agents/$a.md" "agents/" && echo "  ← agent  $a"
done
[ -f "$HOME/Documents/vibe-coding/CLAUDE.md" ] && cp "$HOME/Documents/vibe-coding/CLAUDE.md" "CLAUDE.project.md" && echo "  ← CLAUDE.project.md"

# 2. 시크릿 게이트 (실패 시 커밋 금지)
echo; ./secrets.sh || { echo "시크릿 게이트 실패 — 커밋 중단."; exit 1; }

# 3. 커밋 + rebase-retry 푸시 (변경 있을 때만)
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT"
if [ -z "$(git status --porcelain -- claude-skill)" ]; then
  echo; echo "변경 없음 — 커밋할 게 없다."
else
  git add claude-skill
  git commit -q -m "claude-skill: 하네스 백업 동기화 (sync-from-local)"
  for i in 1 2 3 4 5; do
    git pull --rebase -q origin main && git push -q origin main && { echo "푸시 완료"; break; }
    sleep 3
  done
fi

# 4. 마커 갱신 → Stop 훅 안내 멈춤
write_marker
echo "마커 갱신 완료 — Stop 훅 안내가 멈춘다."
