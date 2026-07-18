# 위키 하네스 — 스킬·에이전트 설치

이 폴더는 knowledge-wiki의 **기술 글 파이프라인 하네스** 전체를 담는다. 위키 노트 [`위키-하네스`](../content/위키-하네스.md)가 이 하네스의 *설계와 이유*를 설명한다면, 여기는 그 *실물*(스킬·에이전트 파일)이다. 문서와 코드가 갈라지지 않도록 둘을 같은 레포에 둔다.

## 구성

```
claude-skill/
├── skills/
│   ├── wiki-note/         "위키에 올려줘" — 검증 없이 노트 1개 발행
│   ├── wiki-post/         작성→검증→발행 오케스트레이터 (+ scripts/validate-note.py 병합 게이트)
│   ├── wiki-verify/       검증 프로토콜 (최신성·팩트·오탈자·윤문)
│   ├── tech-writing/      글 작성 가이드
│   └── readability-review/ 발행 직전 최종 가독성 게이트
├── agents/
│   ├── tech-writer.md          초안 작성
│   ├── fact-checker.md         최신성·팩트 검증
│   ├── copy-editor.md          오탈자·윤문
│   └── readability-reviewer.md 최종 통독 검수
├── CLAUDE.project.md     프로젝트 CLAUDE.md 사본(참조용) — 하네스 트리거·변경 이력
├── install.sh            이 레포 → ~/.claude 설치
├── sync-from-local.sh    ~/.claude → 이 레포 (발행 전 백업)
└── secrets.sh            커밋 전 시크릿·개인정보 게이트
```

## 설치

```bash
git clone git@github.com:<OWNER>/knowledge-wiki.git
cd knowledge-wiki/claude-skill
./install.sh                       # 스킬·에이전트를 ~/.claude 로 복사
echo "git@github.com:<OWNER>/knowledge-wiki.git" > ~/.claude/wiki-note-repo.txt
```

## 시크릿을 레포에 넣지 않는 규칙

**위키 레포 주소는 이 레포에 커밋하지 않는다.** 주소는 각 머신의 `~/.claude/wiki-note-repo.txt`(로컬 전용, git 밖)에 두고, 스킬은 그 파일을 읽기만 한다. 그래서 하네스 파일 어디에도 GitHub 핸들·레포 이름이 박히지 않는다(플레이스홀더 `<owner>/<repo>`만 쓴다).

하네스를 이 레포로 다시 밀 때(`sync-from-local.sh`)는 **커밋 전 반드시 `./secrets.sh`를 돌린다.** API 키·토큰·PEM·실제 이메일·홈 경로 username·하드코딩된 레포 핸들을 스캔하고, 하나라도 걸리면 exit 1로 커밋을 막는다.

```bash
./sync-from-local.sh   # ~/.claude 의 현재 하네스를 끌어옴
./secrets.sh           # 게이트 (통과해야 커밋)
git add claude-skill && git commit && git push
```

## 드리프트 주의

`~/.claude`가 원본이고 이 레포는 백업·배포본이다. 한쪽만 고치면 갈라진다 — 로컬에서 스킬을 고쳤으면 `sync-from-local.sh`로 밀고, 이 레포를 다른 머신에서 클론했으면 `install.sh`로 당긴다. 하네스를 바꿀 땐 위키 노트 `위키-하네스`와 레포 README, 그리고 여기까지 같은 커밋에서 맞춘다(종속 문서 동기화 규칙).
