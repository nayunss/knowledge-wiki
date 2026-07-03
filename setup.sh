#!/usr/bin/env bash
# 지식 위키 원클릭 설정. "Use this template"로 만든 레포를 clone한 뒤, 그 안에서 실행하세요.
# 하는 일: baseUrl 자동 설정 → public 전환 → GitHub Pages(Actions) 켜기 → AI 스킬용 레포 주소 저장
set -euo pipefail

command -v gh >/dev/null || { echo "❌ GitHub CLI 필요: https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login

slug=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
owner=${slug%%/*}; name=${slug##*/}
url="${owner}.github.io/${name}"

echo "▶ baseUrl → ${url}"
sed -i.bak -E "s#^([[:space:]]*baseUrl:).*#\1 ${url}#" quartz.config.yaml && rm -f quartz.config.yaml.bak
git add quartz.config.yaml
git commit -m "Set baseUrl to ${url}" >/dev/null 2>&1 || true
git push origin main

echo "▶ 레포 public 전환"
gh repo edit "$slug" --visibility public --accept-visibility-change-consequences || true

echo "▶ GitHub Pages(Actions) 활성화"
gh api -X POST "repos/${slug}/pages" -f build_type=workflow >/dev/null 2>&1 \
  || gh api -X PUT "repos/${slug}/pages" -f build_type=workflow >/dev/null 2>&1 || true

echo "▶ AI 스킬용 레포 주소 저장 (~/.claude/wiki-note-repo.txt)"
mkdir -p ~/.claude
git remote get-url origin > ~/.claude/wiki-note-repo.txt

echo ""
echo "✅ 완료! 사이트: https://${url}/  (첫 배포 1~2분)"
echo "   Actions 탭에서 진행 확인. 첫 배포가 실패하면 그 실행을 Re-run 하세요."
