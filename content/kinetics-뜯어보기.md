---
title: Kinetics 뜯어보기 — 스프링 물리 라이브러리라는 간판, 프롬프트 카탈로그라는 실체
type: 도구
description: kinetics.colorion.co를 소스 수준에서 분석한다. 슬라이더는 히어로의 공 하나만 움직이고 117개 스니펫은 고정 이징이다. 그런데 그 실체가 간판보다 흥미롭다.
tags: [프론트엔드, 애니메이션, css, 프롬프트]
resource: https://kinetics.colorion.co
---

## 슬라이더를 움직여도 복사되는 코드는 바뀌지 않는다

[Kinetics](https://kinetics.colorion.co)의 히어로는 이렇게 말한다. "stiffness와 damping을 튜닝하고, 그 CSS·React·AI 프롬프트를 복사해 앱에 그대로 넣어라. 당신은 추측이 아니라 튜닝된 스프링을 복사하는 것이다."

솔깃한 약속이다. 그래서 슬라이더를 끝까지 밀고 스니펫을 열어봤다. 코드는 한 글자도 바뀌지 않았다.

## 핵심 주장

Kinetics는 스프링 물리 라이브러리가 아니다. **취향 좋게 큐레이션된 고정 이징(easing) 스니펫 117개의 카탈로그**다. 이징은 애니메이션이 시간에 따라 어떤 속도 곡선을 그리는지 정하는 함수다. 스프링은 강성(stiffness)·감쇠(damping)·질량을 매 프레임 적분해 곡선을 만들지만, Kinetics의 스니펫은 대부분 미리 정해진 고정 이징을 쓴다 — 그마저도 `cubic-bezier`보다 `ease` 같은 키워드가 더 많다.

간판이 과장됐다는 뜻이다. 하지만 이 글의 결론은 "쓰지 마라"가 아니다. **간판과 실체가 다르고, 실체가 간판보다 오히려 더 흥미롭다.** 스프링 물리 라이브러리로는 과장이지만, 취향 좋은 스니펫 카탈로그로는 잘 만들었고, 세 번째 탭(Prompt)에 이르면 컴포넌트 라이브러리의 배포 단위가 어디로 가고 있는지를 보여주는 진짜 사례가 된다.

## 1. 튜너와 라이브러리는 서로 연결돼 있지 않다

히어로의 슬라이더 두 개(stiffness / damping)는 실제로 스프링을 시뮬레이션한다. `physics-demo.js`는 semi-implicit Euler로 수치적분을 돌리고, 그 결과를 **`#physics-ball` 하나의 transform과 화면의 숫자 라벨**에 반영한다. 딱 거기까지다.

117개 카드의 코드 패널은 그 시뮬레이터와 아무 배선도 공유하지 않는다.

| 확인 항목 | 결과 | 재현 |
|---|---|---|
| `main.js`(55,934바이트, 카드 데모 담당)의 stiffness/damping/cubic-bezier 참조 | 0건 | `curl -sL https://kinetics.colorion.co/js/main.js \| grep -niE 'stiff\|damp\|cubic'` → 매칭 1건인데 데모용 문자열이라 무관(`spring(320, 24);damping matters;ship the motion`) |
| 슬라이더가 조작하는 DOM | `#physics-ball`, `#stiff-val`, `#damp-val`뿐 | `curl -sL .../js/physics-demo.js \| grep -nE 'getElementById'` |
| 코드 패널의 정체 | HTML에 하드코딩된 정적 문자열 | `grep -o 'data-lang="css"' index.html \| wc -l` → 234 (탭 버튼 117 + `<pre>` 패널 117). 모달 클론은 `main.js`가 런타임에 생성 |

`main.js`가 하는 일은 이 정적 패널을 런타임에 모달로 복제하고, 탭을 전환하고, 클립보드에 복사하는 것이다. 슬라이더 값이 스니펫으로 흘러가는 경로는 코드상 존재하지 않는다.

그러니 "튜닝된 스프링을 복사한다"는 문장은 구현과 일치하지 않는다. 정확히 쓰자면 "튜너를 구경한 뒤, 그와 무관한 고정 스니펫을 복사한다"이다.

## 2. "스프링"의 정체는 베지어 곡선 하나

이펙트 CSS 세 파일(`effects-a/b/c.css`)의 transition·animation 선언 177개를 전부 세어봤다.

| 이징 | 횟수 |
|---|---|
| `ease` (키워드) | 89 |
| `var(--spring)` | 58 |
| `var(--glide)` | 19 |
| `ease-in-out` | 22 |
| `linear` (키워드) | 17 |
| `ease-out` | 10 |
| 인라인 `cubic-bezier(...)` | 13 (서로 다른 값 5종) |
| `ease-in` | 2 |
| `steps()` | 3 |
| **`linear()` 이징 함수** | **0** |

재현: 세 CSS를 합친 뒤 `transition|animation` 선언에서 타이밍 함수 토큰만 추출해 집계했다(멀티라인 선언 포함).

```bash
curl -sL https://kinetics.colorion.co/css/effects-{a,b,c}.css > eff.css
python3 -c "
import re,collections,sys
src=open('eff.css').read()
decls=re.findall(r'\b(?:transition|animation)\s*:\s*([^;{}]*)',src)
c=collections.Counter(m for d in decls for m in re.findall(
  r'cubic-bezier\([^)]*\)|linear\([^)]*\)|var\(--[a-z-]+\)|steps\([^)]*\)|ease-in-out|ease-out|ease-in|ease|linear',d))
print(len(decls), c.most_common())"
```

`--spring`의 정의는 `base.css` 한 줄에 있다.

```css
--spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--glide:  cubic-bezier(0.16, 1, 0.3, 1);
```

즉 사이트 전체의 "스프링"은 사실상 **고정 오버슈트 베지어 딱 하나**다. 흔히 back-out으로 불리는 곡선이고, 제어점 y=1.56이 1을 넘으므로 목표값을 한 번 지나쳤다가 돌아온다. 물리 시뮬레이션이 아니라 물리처럼 보이는 모양을 손으로 그린 것이다. 그 하나마저 소수파다. 이펙트 CSS를 지배하는 이징은 `ease` 키워드(89회)다.

세 파일 어디에도 CSS `linear()` 이징 함수는 쓰이지 않았다(0회). `linear()`는 여러 번 진동하며 잦아드는 진짜 스프링 곡선을 CSS만으로 근사하는 표준 수단이다. 값 목록으로 임의의 곡선을 찍는다. 게다가 실험적 도구도 아니다 — Baseline "널리 사용 가능"(2026-06) 등급이고, Chrome/Edge 113·Firefox 112·Safari 17.2 이상에서 돌아간다. 이미 널리 쓸 수 있는 표준 도구를 두고 안 썼다는 뜻이다. 스프링을 표방하는 라이브러리가 스프링을 CSS로 표현하는 그 도구를 쓰지 않는다는 건, 이 프로젝트의 관심이 물리가 아니라 룩앤필에 있다는 가장 정직한 증거다.

### 사이트 자신의 설명도 어긋난다

"Card Resize" 카드 데모 안에 적힌 자기 설명은 이렇다.

> Spring-driven height with a single cubic-bezier that mimics **critically damped** motion.

그런데 이 카드가 쓰는 값은 `cubic-bezier(0.34, 1.56, 0.64, 1)`, 오버슈트하는 곡선이다. 임계감쇠(critically damped, ζ=1)는 정의상 오버슈트 없이 가장 빨리 정착하는 경우다. 오버슈트하는 곡선을 임계감쇠의 모방이라 부르는 건 방향이 반대다. 저감쇠(underdamped, ζ<1)에 해당한다.

재미있는 건, 같은 카드의 Prompt 탭이 정반대로 정확하다는 점이다. "gently overshoots before settling"이라고 적혀 있다. 자기 설명은 틀렸고, 프롬프트는 맞았다.

## 3. React 탭은 스프링 런타임이 아니다

React 스니펫 99개 중 `framer-motion`·`react-spring`을 임포트하는 것은 0개다(`grep -cE 'framer-motion|react-spring|useSpring' index.html` → 0). 이펙트는 117개인데 React 탭은 99개뿐이다 — 2026-07-17 재확인 기준 나중에 늘어난 18개에는 React 탭이 아예 붙지 않았다. 실체는 이런 식이다.

```jsx
style={{ transition: 'height 0.5s cubic-bezier(0.34,1.56,0.64,1)' }}
```

같은 CSS transition을 JSX로 감싼 것이다. 나쁜 코드는 아니다. 오히려 의존성 0개로 굴러가는, 가벼운 정답에 가깝다. 다만 "React로도 제공한다"는 문장에서 독자가 기대하는 스프링 런타임은 아니다.

## 4. 진짜 새로운 건 Prompt 탭이다

여기서 이 사이트의 진짜 새로움이 나온다. 모든 이펙트에 세 번째 탭이 붙어 있다. AI에게 그대로 붙여넣는 프롬프트다.

> Build a number that increments on click and bumps elastically each time. On each increment briefly apply scale(1.22) translateY(-6px), then settle back with a spring cubic-bezier(0.34,1.56,0.64,1) over ~0.4s. Restart the animation cleanly on rapid clicks by forcing a reflow.

프롬프트는 스프링을 신비화하지 않는다. 어떤 베지어를 몇 초 동안 쓰는지 그대로 적는다. 프롬프트 패널 117개 중 `cubic-bezier` 값을 명시한 것이 44개, `~0.4s` 같은 구체적 지속시간을 명시한 것이 75개(약 3분의 2)다.

세 탭 중에서 **자기 구현을 가장 정직하게 서술하는 탭이 프롬프트다.** 히어로 카피는 물리를 팔고, React 탭은 독자가 런타임을 기대하게 두고, 프롬프트만이 "이건 0.4초짜리 베지어입니다"라고 실토한다.

그리고 이 탭이 던지는 질문이 흥미롭다. 표본 하나로 세대를 논하는 건 이르지만, 하나의 가설로 놓고 보자. **컴포넌트 라이브러리의 배포 단위가 옮겨가고 있는지도 모른다.**

| 세대 | 배포 단위 | 사용자가 하는 일 | 대가 |
|---|---|---|---|
| 1세대 | npm 패키지 | `install` 후 API 학습 | 의존성·번들·버전 |
| 2세대 | 복붙 코드 (shadcn류) | 소스를 내 레포로 가져옴 | 유지보수는 내 몫 |
| 3세대 | **프롬프트** | 의도를 붙여넣고 코드를 생성 | 재현성·비결정성 |

프롬프트는 코드보다 앞선 층위의 산출물이다. 내 스택·내 컨벤션·내 디자인 토큰에 맞춰 재생성되며, 라이선스 표면적도 코드보다 작다(적어도 겉보기에는). [[프롬프트-엔지니어링]]에서 다루는 "명세로서의 프롬프트"가 UI 라이브러리 유통에 그대로 적용된 사례다. 지식과 워크플로를 실행 가능한 텍스트로 포장해 배포한다는 점에서 [[에이전트-스킬은-워크플로다]]의 논지와도 겹친다.

물론 3세대에는 치명적 약점이 있다. 프롬프트는 컴파일되지 않는다. 모델이 바뀌면 결과도 바뀌고, 같은 프롬프트가 같은 컴포넌트를 두 번 주지 않는다. 그럼에도 Kinetics가 보여준 건, 이미 프롬프트를 배포 가능한 형식으로 다루기 시작했다는 것이다.

## 5. 잘한 것은 잘했다고 하자

저격이 목적이 아니므로 균형을 맞춰야 한다. 엔지니어링 자체는 대체로 좋다.

- **`prefers-reduced-motion` 존중.** 히어로 시뮬레이터는 reduce 설정에서 애니메이션을 멈추고 정적 파형을 그린다(`physics-demo.js`가 `matchMedia`로 분기).
- **정적 사이트.** Astro로 빌드된 순수 정적 HTML/CSS/JS다. 이펙트 상당수가 JS 없이 CSS만으로 동작한다.
- **접근성 기본기.** 코드 모달에 `role="dialog"`·`aria-modal`·포커스 복귀 처리가 들어 있다.
- **분석 도구 자체 호스팅.** Plausible을 자체 도메인(plausible.elerion.com)에서 서빙한다.
- **큐레이션.** 117개 이펙트의 취향과 다양성이 좋다. 카탈로그로서는 확실히 잘 만들었다.

한 가지 정정: 폰트는 자체 호스팅이 아니다. `<head>`에서 Google Fonts(`fonts.googleapis.com`)로 Archivo·Inter·JetBrains Mono를 불러온다(재현: `grep -oE '<link[^>]*fonts\.googleapis[^>]*>' index.html`). 외부 요청이 0은 아니라는 뜻이다.

## 6. 트레이드오프 — 그래서 쓸까 말까

### 쓰지 말아야 할 때

- **진짜 스프링이 필요할 때.** 제스처를 중간에 가로채고, 속도를 이어받아 감속시키고, 인터럽트 가능한 모션이 필요하다면 고정 베지어로는 안 된다. 베지어는 시작과 끝이 정해진 곡선이고, 스프링은 상태 기계다.
- **stiffness/damping을 실제로 튜닝하고 싶을 때.** Kinetics는 그 기능을 제공하지 않는다. 히어로 데모는 데모일 뿐이다.
- **라이선스 리스크를 감당할 수 없을 때.** 아래 참고.

### 쓸 만한 때

- 마이크로 인터랙션 아이디어 카탈로그가 필요할 때. 117개를 훑는 데 10분, 마음에 드는 걸 고르는 데 1분이다.
- AI 코딩 에이전트에 넘길 모션 명세가 필요할 때. Prompt 탭을 그대로 쓰면 된다. 이게 이 사이트의 실질적 최고 사용법이다.
- 의존성 없이 CSS만으로 끝내고 싶을 때. 스니펫들은 실제로 가볍다.

### 진짜 스프링이 필요하다면

| 선택지 | 특징 | 언제 |
|---|---|---|
| CSS `linear()` | 스프링 곡선을 다수의 점으로 샘플링해 CSS 타이밍 함수로 표현. 런타임 JS 없음. Baseline 널리 사용 가능(2026-06, Chrome/Edge 113+·Firefox 112+·Safari 17.2+) | 인터럽트 없는 단발성 스프링 모션 |
| 스프링 런타임 (Motion/framer-motion, react-spring 등) | 속도 승계·인터럽트·제스처 연동 | 드래그·스와이프 등 사용자 입력이 모션 중간에 개입할 때 |
| Web Animations API + 직접 적분 | 완전 제어, 의존성 0 | 모션이 제품의 핵심이고 팀에 역량이 있을 때 |

## 7. CTO 체크: 라이선스가 없다

가장 실무적인 경고를 마지막에 둔다. **이 레포에는 라이선스가 없다.**

- GitHub API의 `license` 필드가 `null`이다: `curl -s https://api.github.com/repos/ckissi/kinetics | grep license`
- 레포 루트에 LICENSE 파일이 없다: `curl -s https://api.github.com/repos/ckissi/kinetics/contents/` → `[.claude, .gitattributes, .gitignore, README.md, astro.config.mjs, package-lock.json, package.json, public, src]`

퍼블릭 레포라는 사실은 사용 허가가 아니다. GitHub 문서는 라이선스 없는 레포에 대해 "누구도 복제·배포·2차적저작물 작성을 할 수 없다(no one may reproduce, distribute, or create derivative works)"고 명시한다. 저작권이 저작자에게 그대로 남기 때문이다. 예외는 GitHub 이용약관이 허용하는 열람과 포크뿐이다. 복붙을 전제로 설계된 라이브러리에서 이건 사소한 흠이 아니라 구조적 결함이다. 사용자에게 "복사해 가라"고 말하면서 복사해도 된다는 근거는 주지 않는다.

여기에 프로젝트 나이가 겹친다. 레포는 2026-06-24에 만들어졌고, 이 글을 쓰는 시점에 갓 3주를 넘긴 프로젝트다(2026-07-17 재확인 기준 stars 213 / forks 24 / open issues 1, 최종 푸시 2026-07-14 — 별점은 변동값이니 스냅샷으로 읽어라).

실무 결론:

1. **CSS/React 스니펫을 프로덕션에 복붙하려면** — 최소한 이슈로 라이선스를 문의하고 답을 받아라. 회사 코드베이스라면 법무 리스크를 감수할 이유가 없다.
2. **Prompt 탭은 상대적으로 안전하다 — 단, 조건이 붙는다.** 프롬프트를 읽고 그 의도대로 내 코드를 AI로 생성하는 것은 코드 복제와 층위가 다르다. 미국 저작권청 2025년 보고서(Part 2)도 프롬프트만으로는 AI 산출물의 저작권을 주장하기 어렵다고 본다. 다만 두 가지를 혼동하면 안 된다. AI가 생성한 산출물과 Kinetics가 쓴 프롬프트 문장은 다른 층위다. 같은 보고서는 프롬프트 문장 자체가 충분히 창작적이면 독립 저작물로 보호될 수 있다고 본다. 즉 **프롬프트 텍스트를 그대로 붙여넣는 것 역시 그 텍스트의 복제**다. 안전한 건 읽고 내 말로 다시 쓰는 쪽이다.
3. **레퍼런스로 쓰는 건 언제나 자유다.** 눈으로 보고 배우는 데 라이선스는 필요 없다.

## 마치며

Kinetics는 스프링 물리 라이브러리라는 간판을 달았지만, 스프링 물리는 히어로의 공 하나에만 산다. 나머지 116개는 잘 고른 베지어들이다. 그게 나쁜가? 아니다. 나쁜 건 카피이지 코드가 아니다.

이 사이트에서 정말 배울 것은 물리가 아니라 세 번째 탭이다. UI 라이브러리가 npm 패키지에서 복붙 코드로, 다시 프롬프트로 이동하는 궤적. 그 궤적의 초기 표본이 지금 눈앞에 있다. 마침 그 탭이 세 탭 중 가장 정직하기까지 하다.

관련: [[프롬프트-엔지니어링]] · [[에이전트-스킬은-워크플로다]] · [[디자인-스킬-비교-실험]]

## 출처

- Kinetics 사이트 (히어로 카피·117개 카드·코드 패널): https://kinetics.colorion.co — 2026-07-17 재확인. 발행 시점(2026-07-14)엔 99개였고 그 뒤 117개로 개편됐다. 위 수치는 전부 117개 기준으로 재집계했으며, 논지(슬라이더 미배선·고정 이징 지배·스프링은 베지어 하나)는 재현 시 전부 그대로였다
- Kinetics 소스: https://github.com/ckissi/kinetics — 2026-07-17 재확인 (created 2026-06-24, pushed 2026-07-14, license: null; stars는 변동값)
- GitHub API: `https://api.github.com/repos/ckissi/kinetics`, `.../contents/` — 2026-07-14 확인
- 사이트 자산 직접 수집: `/js/main.js`, `/js/physics-demo.js`, `/css/base.css`, `/css/effects-a.css`, `/css/effects-b.css`, `/css/effects-c.css` — 위 재현 명령 참조
- CSS `linear()` 이징 함수 — MDN: https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/linear
- CSS `linear()` 지원·Baseline (Widely available 2026-06-11; Chrome/Edge 113, Firefox 112, Safari 17.2) — web-features explorer: https://web-platform-dx.github.io/web-features-explorer/features/linear-easing/ / Chrome for Developers: https://developer.chrome.com/docs/css-ui/css-linear-easing-function
- 임계감쇠(ζ=1, 오버슈트 없음)·저감쇠(ζ<1) 정의 — Wikipedia, "Damping": https://en.wikipedia.org/wiki/Damping
- 라이선스 없는 퍼블릭 레포의 지위 — GitHub Docs, "Licensing a repository": https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
- 프롬프트와 저작권 — U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* (2025): https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf
