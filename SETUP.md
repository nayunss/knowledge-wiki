# 셋업 가이드

내 지식 위키를 만드는 데 5분. GitHub 계정만 있으면 됩니다.

---

## 🟢 비개발자용 — 클릭 방식 (터미널 불필요)

### 1. 내 레포 만들기
이 레포 페이지 상단의 초록색 **"Use this template" → "Create a new repository"** 클릭.
- Repository name: `knowledge-wiki` (아무거나 가능)
- **Public** 선택 (무료 GitHub Pages는 public 필요)
- Create

### 2. baseUrl 한 줄 수정
내 새 레포에서 `quartz.config.yaml` 파일 열기 → 연필(✏️) 아이콘 →
`baseUrl:` 줄을 **내 것**으로 바꾸기:
```yaml
  baseUrl: 내GitHub아이디.github.io/knowledge-wiki
```
(레포 이름을 다르게 지었으면 `knowledge-wiki` 자리도 그 이름으로)
→ **Commit changes**

### 3. Pages 켜기
레포 **Settings → Pages → Build and deployment → Source** 를 **"GitHub Actions"** 로 선택.

### 4. 끝
1–2분 뒤 `https://내아이디.github.io/knowledge-wiki/` 에 위키가 뜹니다.
레포 **Actions** 탭에서 배포 진행 상황을 볼 수 있어요. (첫 실행이 "try again later"로 실패하면 그 실행을 **Re-run** 하면 됩니다 — Pages 전파 지연.)

---

## 🔵 개발자용 — 원클릭 스크립트

[GitHub CLI](https://cli.github.com) 설치 후:

```bash
# 1. 위 "Use this template"로 레포 생성 후 clone
git clone git@github.com:내아이디/knowledge-wiki.git
cd knowledge-wiki

# 2. 스크립트 실행 (baseUrl 설정 + public 전환 + Pages 켜기 자동)
./setup.sh
```

끝나면 사이트 URL이 출력됩니다.

---

## ✍️ "AI가 써주는" 기능 켜기 (선택)

Claude Code에서 "위키에 올려줘" 한마디로 노트를 올리려면 → **[claude-skill/README.md](claude-skill/README.md)** 참고.

## 🔎 RAG로 쓰기 (선택)

claude.ai → **Projects** → 새 프로젝트 → **knowledge**에 이 GitHub 레포 연결.
그 프로젝트에서 대화하면 내 노트를 근거로 답합니다.

## ⚠️ 주의

레포가 **public**이라 사이트도 공개됩니다. 개인정보·비밀은 넣지 마세요.
공개하기 싫은 노트는 `content/private/` 폴더에 두면 사이트에선 빠집니다 (단, 레포엔 남으므로 진짜 민감한 건 아예 넣지 말 것).
