# wiki-note 스킬 설치

Claude Code에서 **"위키에 올려줘"** 한마디로 노트를 자동 작성·배포하는 스킬입니다.
설치하면 Claude가: 임시 clone → `content/`에 md 작성 → push → 임시폴더 삭제 를 알아서 합니다.

## 설치 (한 번만)

```bash
# 1. 이 스킬을 개인 스킬 폴더로 복사
mkdir -p ~/.claude/skills/wiki-note
cp SKILL.md ~/.claude/skills/wiki-note/SKILL.md

# 2. 내 위키 레포 주소 등록 (setup.sh를 돌렸으면 이미 되어 있음)
mkdir -p ~/.claude
echo "git@github.com:내아이디/knowledge-wiki.git" > ~/.claude/wiki-note-repo.txt
```

> `git@...` (SSH) 주소를 권장. HTTPS 주소를 쓰면 push 때 GitHub 토큰 인증이 필요할 수 있습니다.

## 쓰기

Claude Code(어느 폴더에서든)에서:

```
회의 내용 정리해서 위키에 올려줘: [내용]
도커 네트워킹 개념 노트로 만들어줘
"llm-wiki-구조" 노트에 RAG 섹션 추가해줘
```

로컬엔 아무것도 안 남고, 1~2분 뒤 사이트에 반영됩니다.

## 동작 원리

`SKILL.md`의 `description`이 위 같은 요청과 매칭되면 Claude가 스킬 절차를 따라 실행합니다.
레포 주소만 `~/.claude/wiki-note-repo.txt`로 바꾸면 누구의 위키에도 그대로 씁니다.
