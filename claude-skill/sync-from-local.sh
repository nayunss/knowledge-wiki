#!/usr/bin/env bash
# 역방향 — ~/.claude 의 현재 하네스를 이 레포로 끌어온다(발행 전 백업).
# 시크릿 가드: 커밋 전 secrets.sh 를 돌려 스캔한다.
set -euo pipefail
cd "$(dirname "$0")"
SRC="$HOME/.claude"

for name in wiki-note wiki-post wiki-verify tech-writing readability-review; do
  [ -d "$SRC/skills/$name" ] || continue
  mkdir -p "skills/$name"
  rsync -a --delete "$SRC/skills/$name/" "skills/$name/"
  echo "  ← skill  $name"
done

for a in tech-writer fact-checker copy-editor readability-reviewer; do
  [ -f "$SRC/agents/$a.md" ] && cp "$SRC/agents/$a.md" "agents/" && echo "  ← agent  $a"
done

echo
echo "다음: ./secrets.sh 로 스캔한 뒤 커밋하라 (스캔 통과 전 커밋 금지)."
