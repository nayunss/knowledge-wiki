---
name: wiki-note
description: 완성된 노트를 Quartz knowledge-wiki에 추가하거나 편집하고 배포한다. 작성·검증 파이프라인 없이 업로드만 요청했을 때 사용한다.
---

# wiki-note — 완성 노트 발행

완성된 Markdown 노트를 위키에 추가·편집하고 배포한다. 임시 clone에서 작업하고 push한 뒤 임시 작업 폴더를 정리한다. 삭제 전에 경로를 명시적으로 확인하며, 저장소 루트나 홈 디렉터리를 대상으로 재귀 삭제하지 않는다.

## 저장소 결정
1. 현재 작업 중인 저장소가 대상 knowledge-wiki이면 그 저장소를 사용한다.
2. 아니면 `~/.claude/wiki-note-repo.txt` 첫 줄의 저장소 주소를 사용한다.
3. 둘 다 없으면 발행을 멈추고 사용자에게 저장소 주소를 요청한다.

## 발행 프로필
- OKF v0.2의 `type`은 필수다. 이 위키는 품질 프로필로 `title`, `description`, `tags`도 요구한다.
- 출처가 있는 새 노트는 `sources`에 원문을 기록하고, 개별 주장에는 `sources[].id`와 같은 Markdown 각주 라벨을 사용한다.
- `generated`, `verified`, `status`, `stale_after`는 의미가 있을 때만 쓴다. 검증하지 않은 내용을 `verified`로 표시하지 않는다.
- 내부 링크는 OKF 표준 Markdown 링크를 우선한다. 기존 `[[위키링크]]`는 Quartz 호환 확장으로 유지할 수 있다.
- `index.md`와 `log.md`는 예약 파일이다. 일반 개념 노트 파일명으로 쓰지 않는다.

## 절차
1. 대상 저장소를 `mktemp -d`로 만든 명시적 임시 경로에 `--depth 1` clone한다.
2. 기존 노트를 먼저 읽고 `content/` 아래 한 주제당 한 파일로 작성·수정한다.
3. 새 노트라면 홈 `index.md` 카드와 시작점을 갱신하고 `data-date="YYYY-MM-DD"`를 넣는다.
4. 저장소에 포함된 `.claude/skills/wiki-post/scripts/validate-note.py`로 노트를 검사한다. 설치본만 있다면 그 경로를 사용한다.
5. 커밋하고 `git pull --rebase` 뒤 push한다. 비충돌 실패는 최대 5회 재시도한다. 같은 파일 충돌은 rebase를 중단하고 최신 파일에 수정 의도를 다시 적용한다.
6. 배포를 확인한다. 실패하면 저장소의 배포 workflow가 수동 실행을 지원하는지 확인한 뒤 한 번 재시도한다.
7. 생성한 임시 경로가 실제 임시 디렉터리인지 확인한 뒤 정리한다. `_workspace` 감사 산출물은 삭제하지 않는다.

## 실패 처리
- 검증 실패, push 충돌 미해소, 배포 재실패는 숨기지 않고 사용자에게 정확한 단계와 남은 조치를 보고한다.
- 비밀·개인정보가 포함된 공개 노트는 발행하지 않는다.
