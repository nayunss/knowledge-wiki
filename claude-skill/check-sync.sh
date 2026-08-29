#!/usr/bin/env bash
# 배포 묶음(claude-skill)과 프로젝트 로컬 실행본(.claude)의 드리프트 검사.
set -euo pipefail
cd "$(dirname "$0")"

status=0
for area in agents skills; do
  if ! diff -qr "$area" "../.claude/$area"; then
    status=1
  fi
done

# 런타임(~/.claude) 대조 — 레포가 앞서 나간 역방향 드리프트를 잡는다.
# 2026-08-03 커밋 3개가 미러에만 들어가 26일간 방치된 사고가 근거다.
# Stop 훅과 sync-from-local.sh는 런타임→미러 방향만 본다.
RT="${HOME}/.claude"
if [ -d "$RT" ]; then
  for name in wiki-note wiki-post wiki-verify tech-writing readability-review wiki-debug; do
    [ -d "skills/$name" ] || continue
    [ -d "$RT/skills/$name" ] || { echo "런타임에 없음: skills/$name — install.sh 필요" >&2; status=1; continue; }
    diff -qr "skills/$name" "$RT/skills/$name" >/dev/null || {
      echo "런타임 불일치: skills/$name" >&2; status=1; }
  done
  for a in agents/*.md; do
    [ -f "$a" ] || continue
    [ -f "$RT/$a" ] || { echo "런타임에 없음: $a — install.sh 필요" >&2; status=1; continue; }
    diff -q "$a" "$RT/$a" >/dev/null || { echo "런타임 불일치: $a" >&2; status=1; }
  done
else
  echo "런타임(~/.claude) 없음 — 런타임 대조는 건너뛴다." >&2
fi

if [ "$status" -ne 0 ]; then
  echo "하네스 불일치 — install.sh(미러→런타임) 또는 sync-from-local.sh(런타임→미러)로 같은 커밋에서 맞춰라." >&2
  exit 1
fi
echo "하네스 일치 (미러 2곳 + 런타임)"
