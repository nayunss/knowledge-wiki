# 📚 지식 위키 (LLM-Wiki + RAG)

AI가 작성한 마크다운을 **한 곳에 모아** 위키로 보고, RAG로도 쓰는 개인 지식 베이스 템플릿.

- **단일 원본**: `content/` 폴더의 `.md` 파일들 (`[[위키링크]]`로 연결)
- **웹 위키**: [Quartz](https://quartz.jzhao.xyz/)가 GitHub Pages로 자동 배포
- **RAG**: 같은 레포를 claude.ai Project에 연결하면 질의응답 가능
- **작성**: Claude Code 스킬로 "위키에 올려줘" 한마디 → 자동 커밋·배포 (`claude-skill/` 참고)

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

원본: [jackyzha0/quartz](https://github.com/jackyzha0/quartz) (MIT) 기반.
