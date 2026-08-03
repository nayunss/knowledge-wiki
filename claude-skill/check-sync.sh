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

if [ "$status" -ne 0 ]; then
  echo "하네스 미러 불일치 — 두 트리를 같은 커밋에서 동기화하라." >&2
  exit 1
fi
echo "하네스 미러 일치"
