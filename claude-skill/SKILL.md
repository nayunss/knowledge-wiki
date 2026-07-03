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
3. `"$TMP/content/"` 아래에 `.md` 노트를 쓴다:
   - 파일명은 주제를 담은 kebab-case + `.md`.
   - 맨 위에 front matter: `---\ntitle: 제목\n---`.
   - 관련 노트는 `[[다른-노트]]` 위키링크로 연결. 아직 없는 노트를 링크해도 됨(Quartz가 stub로 표시).
   - **기존 노트 편집**이면 clone 안의 해당 파일을 먼저 읽고 수정한다.
4. 커밋 & 푸시:
   ```bash
   cd "$TMP" && git add -A && git commit -m "노트: 제목" && git push origin main
   ```
5. 임시 폴더 삭제: `rm -rf "$TMP"`.
6. 사용자에게 완료를 알리고, 1~2분 뒤 Pages URL에서 사이트가 갱신된다고 안내.

## 유의

- 레포가 public이면 사이트도 공개다 → 비밀/개인정보를 노트에 넣지 말 것. 비공개 성격이면 `content/private/` 아래에 두면 사이트에서 빠진다(단 레포엔 남음).
- **한 파일 = 한 주제/사실** 원칙을 지켜야 위키링크와 RAG 검색이 깨끗하다.
