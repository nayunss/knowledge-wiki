---
name: wiki-note
description: Add or edit a note in the user's personal knowledge wiki (Quartz + GitHub Pages). Use when the user says things like "위키에 올려줘", "노트로 정리해서 올려줘", "지식 위키에 추가해줘", "add this to my wiki", "save as a wiki note". Clones the wiki repo to a temp dir, writes/edits markdown under content/, pushes, then deletes the temp clone so nothing stays on the local machine.
---

# wiki-note

사용자의 Quartz 지식 위키에 마크다운 노트를 추가/편집하고 배포한다. push하면 GitHub Pages가 자동 빌드하며, **로컬에는 아무것도 남기지 않는다** (임시 clone → 작업 → push → 삭제).

## 설정 (repo 주소)

위키 레포 주소는 `~/.claude/wiki-note-repo.txt` 첫 줄에 저장되어 있다 (예: `git@github.com:USER/knowledge-wiki.git`).
- 파일이 없거나 비어 있으면 사용자에게 위키 레포 주소를 묻고, 그 파일에 저장한 뒤 진행한다.

## 절차

1. `~/.claude/wiki-note-repo.txt` 에서 레포 주소를 읽는다 (없으면 위처럼 묻고 저장).
2. 임시 작업 폴더를 만들고 얕은 clone:
   ```bash
   TMP=$(mktemp -d)
   git clone --depth 1 "$(cat ~/.claude/wiki-note-repo.txt)" "$TMP"
   ```
3. `"$TMP/content/"` 아래에 `.md` 노트를 쓴다 (OKF 규약 — Open Knowledge Format 차용):
   - 파일명은 주제를 담은 kebab-case + `.md`.
   - front matter(YAML):
     - `title:` 표시 제목
     - `type:` 개념 종류 — `개념`/`도구`/`설계결정`/`레퍼런스`/`플레이북` 등 (자유값이되 서술적으로). 라우팅·필터·index 그룹핑에 쓰임.
     - `description:` 한 줄 요약 — index·검색 스니펫·미리보기·RAG 근거에 쓰임.
     - `tags:` (선택)
     - 특정 도구/레포/API를 다루는 노트면 `resource:` 정식 URL.
   - 본문은 **구조적 마크다운 우선**(제목·목록·표·코드블록 > 프로즈) — 사람·에이전트 검색에 유리.
   - 관련 노트는 `[[다른-노트]]` 위키링크로 연결. 없는 노트를 링크해도 됨(Quartz가 stub로 표시 = 아직 안 쓴 지식).
   - 외부 출처는 맨 아래 `## 출처` 섹션에 목록으로 정리.
   - **기존 노트 편집**이면 clone 안의 해당 파일을 먼저 읽고 수정한다.
4. 커밋 후 **동시성 안전 푸시** (다른 터미널/챗이 동시에 push해도 안전 — 락·큐 없이 rebase 재시도):
   ```bash
   cd "$TMP" && git add -A && git commit -m "노트: 제목"
   for i in $(seq 1 5); do
     git pull --rebase origin main && git push origin main && break
     sleep 2   # 다른 세션이 먼저 push했으면 최신으로 rebase 후 재시도
   done
   ```
   - 서로 **다른 노트 파일**이면 git이 자동 병합 → 두 작업 모두 반영(진짜 병렬).
   - **같은 파일**을 동시 수정해 `git pull --rebase`가 충돌나면: `git rebase --abort` → 그 파일의 최신본을 다시 읽어 수정 의도를 재적용 → 다시 4번.
5. 임시 폴더 삭제: `rm -rf "$TMP"`.
6. 배포 성공을 확인하고(실패 시 GitHub Actions에서 해당 run을 **Re-run** — CI flake 자가치유), 1~2분 뒤 Pages URL 갱신을 안내.

## 유의

- 레포가 public이면 사이트도 공개다 → 비밀/개인정보를 노트에 넣지 말 것. 비공개 성격이면 `content/private/` 아래에 두면 사이트에서 빠진다(단 레포엔 남음).
- **한 파일 = 한 주제/사실** 원칙을 지켜야 위키링크와 RAG 검색이 깨끗하다.
- **동시성**: 여러 세션이 병렬로 작업 가능. 다른 노트면 자동 병합, 같은 노트만 재적용 필요. 배포는 Pages `concurrency` 그룹이 직렬 큐잉하므로 서로 안 부딪힌다.
