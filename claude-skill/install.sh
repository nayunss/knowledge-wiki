#!/usr/bin/env bash
# 위키 하네스 설치 — 이 레포의 스킬·에이전트를 ~/.claude 로 복사한다.
# 사용법: claude-skill/ 에서  ./install.sh
set -euo pipefail
cd "$(dirname "$0")"

DEST="$HOME/.claude"
echo "위키 하네스 → $DEST"

# 스킬
for s in skills/*/; do
  name="$(basename "$s")"
  mkdir -p "$DEST/skills/$name"
  cp -R "$s". "$DEST/skills/$name/"
  echo "  skill  $name"
done

# 에이전트
mkdir -p "$DEST/agents"
for a in agents/*.md; do
  cp "$a" "$DEST/agents/"
  echo "  agent  $(basename "$a")"
done

# 훅 (하네스 변경 시 백업 안내 Stop 훅)
if [ -d hooks ]; then
  mkdir -p "$DEST/hooks"
  for h in hooks/*.sh; do cp "$h" "$DEST/hooks/"; chmod +x "$DEST/hooks/$(basename "$h")"; echo "  hook   $(basename "$h")"; done
fi

# 위키 레포 주소 (시크릿 아님, 하지만 이 레포에 넣지 않는다 — 로컬 전용)
if [ ! -f "$DEST/wiki-note-repo.txt" ]; then
  echo
  echo "⚠️  위키 레포 주소가 없다. 등록해야 발행이 된다:"
  echo "    echo 'git@github.com:<OWNER>/<REPO>.git' > $DEST/wiki-note-repo.txt"
fi

echo
echo "Stop 훅을 켜려면 $DEST/settings.json 에 아래를 넣어라 (하네스가 바뀌면 백업 안내):"
cat <<'JSON'
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command",
        "command": "bash \"$HOME/.claude/hooks/harness-sync-reminder.sh\"" } ] }
    ]
  }
JSON
echo
echo "완료. CLAUDE.project.md 는 참조용이다 — 프로젝트 루트의 CLAUDE.md 와 맞춰 둘 것."
