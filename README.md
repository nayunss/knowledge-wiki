# 📚 지식 위키 (LLM-Wiki + RAG)

AI가 작성한 마크다운을 **한 곳에 모아** 위키로 보고, RAG로도 쓰는 개인 지식 베이스 템플릿.

- **단일 원본**: `content/` 폴더의 `.md` 파일들 (`[[위키링크]]`로 연결)
- **웹 위키**: [Quartz](https://quartz.jzhao.xyz/)가 GitHub Pages로 자동 배포
- **RAG**: 같은 레포를 claude.ai Project에 연결하면 질의응답 가능
- **작성**: Claude Code 스킬로 "위키에 올려줘" 한마디 → 자동 커밋·배포 (`claude-skill/` 참고)

## 전체 구조

```
                        ┌─→ Quartz → <USER>.github.io/knowledge-wiki   (위키 뷰)
 GitHub 레포 (원본만) ──┤
   content/*.md [[링크]] └─→ claude.ai Project 연결                    (RAG 질의응답)
        ▲
        │ 작성/편집할 때만: 임시 clone → 쓰기 → push → 삭제
    Claude Code (wiki-note 스킬)
```

로컬 컴퓨터엔 상시 사본을 두지 않는다 — 원본은 GitHub 레포 하나, 작성하는 순간에만 임시 clone → push → 삭제.

## 시작하기

👉 **[SETUP.md](SETUP.md)** 를 따라 하세요. (비개발자: 클릭 방식 / 개발자: `setup.sh` 한 방)

설치 후 매일 쓰는 법은 **[GUIDE.md](GUIDE.md)** 참고 (노트 추가·위키링크·RAG·비공개 노트).

## 구조

| 경로 | 역할 |
|---|---|
| `content/*.md` | 노트 원본 (여기만 편집) |
| `quartz.config.yaml` | 사이트 설정 (`baseUrl`만 본인 것으로) |
| `.github/workflows/deploy.yml` | push하면 자동 빌드·배포 |
| `setup.sh` | 개발자용 원클릭 설정 |
| `claude-skill/` | "AI가 써주는" Claude Code 스킬 |

## RAG로 쓰기 — claude.ai Project에 연결

내 노트를 근거로 Claude에게 질문하려면 레포를 claude.ai Project의 knowledge에 연결한다.

### 방법 A — GitHub 레포 연결 (자동 동기화, 가능하면 추천)
1. claude.ai → 왼쪽 **Projects** → 기존 프로젝트 열거나 **+ 새 프로젝트**
2. 프로젝트의 **Knowledge(지식)** 영역 → **Add content / Add from GitHub** 버튼
3. 처음이면 **GitHub 인증(Authorize)** 창 → 승인 → 레포 목록에서 본인 `knowledge-wiki` 선택
4. 연결되면 `content/`의 md가 knowledge로 들어오고, 이후 push하면 갱신됨

> GitHub 연결 메뉴는 플랜(Pro/Team)·계정 설정에 따라 **Settings → Connectors**에서 GitHub를 먼저 켜야 보이기도 한다. 메뉴가 아예 없으면 방법 B로.

### 방법 B — 수동 업로드 (연결 메뉴가 없을 때, 항상 됨)
1. 프로젝트 **Knowledge → "파일" 옆 `+`** → 파일 업로드
2. `content/`의 md 파일들을 선택해 올림
3. 단, 자동 동기화가 아니라 **노트를 추가/수정하면 그 파일을 다시 업로드**해야 반영됨

---

원본: [jackyzha0/quartz](https://github.com/jackyzha0/quartz) (MIT) 기반.
