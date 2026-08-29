---
title: Dogwood 비판적 검토 — 인가의 입력이 '요청 하나'에서 '지나온 궤적'으로 바뀔 때
type: 분석
description: "AWS가 공개한 에이전트 거버넌스 언어 Dogwood를 원문 기준으로 분석하고, 원문이 잘 짚은 것과 답하지 않은 것을 나눠 검토한다."
tags: [ai-에이전트, 거버넌스, 정책언어, 런타임검증]
resource: https://aws.amazon.com/ko/blogs/opensource/introducing-dogwood-runtime-verification-for-ai-agents/
date: 2026-08-29
---

에이전트에게 "5천 달러 넘게 송금하지 마"라는 규칙을 써본 적이 있다면, 그 규칙이 왜 잘 안 써지는지도 알 것이다. 요청 하나만 보면 이번 송금은 2천 달러다. 문제없다. 문제는 이번이 세 번째라는 사실인데, 그건 요청 안에 안 적혀 있다.

2026년 8월 6일 AWS가 오픈소스로 공개한 **Dogwood**는 정확히 그 빈칸을 겨냥한다. 원문의 표현으로 "에이전트와 그 도구를 위해 설계한 오픈소스 거버넌스 언어"다. 이 글의 결론부터 말하면, Dogwood의 중요한 대목은 새 연산자 네 개가 아니다.

## 핵심 주장

**Dogwood가 실제로 바꾼 것은 인가 판정의 입력이다.** 지금까지 정책 엔진에 들어가던 것은 요청 하나였다. Dogwood에 들어가는 것은 요청 하나 + 그 앞에 쌓인 이벤트 궤적(trace)이다. 입력이 바뀌면 딸려오는 것들이 있다. 판정하려면 과거를 어딘가에 들고 있어야 하고(상태), 그 과거는 시간에 따라 자라며(비용), 무엇보다 그 과거는 **판정하는 순간에도 계속 변한다**(동시성).

원문은 이 셋을 다 알고 있다. 앞의 둘은 뒤에서 대가로 직접 열거하고, 세 번째에는 절 하나를 통째로 할애한다. 그 세 번째 절은 이 블로그에서 가장 값진 부분이다. 단어 하나(`request` → `response`) 차이로 우회 가능한 정책이 되는 실패 사례를 트레이스까지 붙여 보여준다. 자기네 언어로 안전하지 않은 정책을 쓰는 법을 이만큼 자세히 보여주는 벤더 발표문은 드물다.

반대로 원문이 답하지 않은 것도 명확하다. **원문은 이벤트 로그가 어디에 얼마나 사는지를 말하지 않는다.** 그런데 Dogwood의 모든 판정은 그 로그를 읽어서 나온다. 도입을 검토한다면 언어 문법보다 이 질문에 먼저 답이 있어야 한다.

여기서 쓰는 용어 몇 개를 먼저 풀어둔다.

- **런타임 검증(runtime verification)** — 형식기법(formal methods)의 한 갈래로, 돌아가는 시스템이 "이렇게 동작해야 한다"는 형식 명세를 지키는지 실행 중에 확인하는 분야다. 원문의 정의를 그대로 옮기면 "실행 중인 시스템을 그 동작에 대한 형식 명세와 대조해 검사하는 것"이다.
- **point-in-time 인가** — 요청 하나를 고립시켜 그것만 보고 허용/거부를 정하는 방식. 과거 행동에 의존하지 않는다.
- **safety / liveness** — safety는 "무엇이 일어나면 안 되는가", liveness는 "무엇이 반드시 일어나야 하는가"를 다룬다. 형식기법에서 성질을 가르는 고전적인 두 축이다. liveness는 굳어진 한글 역어가 없어 이 글에서는 영문 그대로 쓴다.
- **MFOTL (Metric First-Order Temporal Logic)** — "지난 한 시간 안에" 같은 시간 창(metric)을 다루면서, 이벤트에 딸린 값을 변수에 묶어 조건을 걸 수도 있는(first-order) 시간 논리. Dogwood 시간 연산자의 수학적 바탕이다.

---

## 1. 무엇이 달라졌나 — Cedar가 못 하는 자리

AWS는 이미 **AgentCore Policy**를 갖고 있다. Amazon Bedrock AgentCore 안에서 도구 호출마다 그 행동을 허용할지 결정하는 계층이고, 출시 때 정책 언어로 **Cedar**를 썼다.

원문이 Cedar에 부여하는 성격은 이렇다. 빠르고, 읽기 쉽고, automated reasoning(자동 추론 — 정책을 실행하지 않고 수학적으로 분석해 성질을 증명하는 기법)으로 분석 가능하다. 그리고 감사와 집행이 기대는 보장이 하나 있다. "동일한 요청은 평가 순서나 시스템 상태와 무관하게 동일한 결정을 낸다."

바로 그 보장이 한계이기도 하다. Cedar는 각 요청을 고립 평가한다. 그래서 원문은 Cedar가 "단일 행동 주위에 안전 울타리(safety envelope)를 그릴 수는 있지만, 행동의 **연속**에 대한 규칙을 표현하도록 설계되지 않았다"고 쓴다.

에이전트를 통제하기 어려운 자리는 행동 하나가 아니라 연속이다. 원문이 든 세 가지가 정확하다.

| 규칙의 형태 | 예 | 요청 하나로 판정 가능한가 |
|---|---|---|
| 선행조건(prerequisite) | 승인받기 전엔 팔지 마라 | 불가 — 승인은 과거에 있다 |
| 비율 제한(rate limit) | 한 시간에 5건까지 | 불가 — 앞의 4건을 세야 한다 |
| 순서(ordering) | 기밀을 본 뒤엔 외부와 접촉하지 마라 | 불가 — "본 뒤"가 과거 참조다 |

세 줄 모두 오른쪽 칸이 "불가"다. Dogwood는 이 칸을 채우러 왔다.

## 2. 문법 — 절 하나가 늘었다

Cedar의 `when { ... }` 조건은 현재 인가 요청만 본다. Dogwood는 여기에 두 번째 종류의 절 `when temporal { ... }`을 더한다. 이 조건은 요청 이전에 무슨 일이 있었는지도 볼 수 있다.

**이벤트**는 도구 호출의 요청(request) 아니면 그 결과(response)다. 각 이벤트는 입력 인자, 요청한 주체(principal) 등 그 호출에 딸린 데이터를 함께 기록한다.

원문은 주식 거래 에이전트로 예제를 끌고 간다. 도구는 `ApproveSale`, `SellShares`, `Transfer` 셋이다.

### 첫 예제 — 승인 없이는 못 판다

```text
// Permit a sale only if approval for the same amount of the same
// stock came back granted within the last hour.
permit ( principal, action == AgentCore::Action::"SellShares", resource )
when temporal {
    formerly within 1h AgentCore::Action::"ApproveSale"::response{
        input.stock:     context.input.stock,
        input.shares:    context.input.shares,
        output.approved: true
    }
};
```

`formerly`는 과거를 보는 연산자다. 지정한 시간 창 안에서 그 조건이 **최소 한 번** 성립했으면 참이 된다. 여기서 창은 `within 1h`. 조건은 대응하는 `ApproveSale::response` 이벤트가 있었고, 그 호출의 `input.stock`·`input.shares`가 지금 요청의 `context.input.stock`·`context.input.shares`와 일치하며, `output.approved`가 `true`였다는 것이다.

트레이스로 보면 이렇게 움직인다. `@n`은 초 단위 타임스탬프이고, 요청이면 줄 끝에 판정이 붙는다. 시간은 항상 상대 기준이다. 요청과 과거 이벤트의 시간 차만 보므로 절대값 자체는 의미가 없다.

```text
@0     SellShares::request      { stock: "AMZN", shares: 100 }                  -> DENY
@1700  ApproveSale::response    { stock: "AMZN", shares: 100, approved: true }
@1800  SellShares::request      { stock: "AMZN", shares: 100 }                  -> ALLOW
@7200  SellShares::request      { stock: "AMZN", shares: 100 }                  -> DENY
```

첫 요청은 승인 기록이 없어 거부다. 두 번째 줄은 응답이라 판정이 없지만 이력에 남아 이후 요청에 영향을 준다. 세 번째는 창 안에 승인이 있어 허용, 네 번째는 승인이 창 밖으로 밀려나 다시 거부다.

원문은 이 트레이스를 두고 한 가지를 더 짚는다. 에이전트는 도구를 병렬로, 비동기로 호출할 수 있고 멀티 에이전트 환경에서는 그 얽힘이 더 심해지므로, 정책을 쓸 때 이런 동시성을 염두에 두라는 것이다. 다만 이 대목은 읽기가 매끄럽지 않다. 원문은 "마지막 `SellShares::request`가 직전에 허용된 요청의 응답보다 먼저 온다"고 설명하는데, 정작 트레이스에는 `SellShares::response` 줄이 하나도 없다. 지적하려는 현상 자체는 뒤의 request/response 절에서 제대로 다뤄지니, 여기서는 넘어가도 좋다.

### 시간 조건은 '식'이라서 Cedar 안에 들어간다

실제 규칙은 대개 과거에 대한 사실과 이번 요청에 대한 사실을 함께 요구한다. Dogwood는 `temporal { ... }`을 **식**(expression)으로 만들어 평범한 `when` 절 안에 Cedar 조건과 나란히 놓을 수 있게 했다.

```text
// Permit a sale only if it is small (a plain, point-in-time check on
// this request) AND approval for the same stock and amount came back
// granted within the last hour (the temporal check, inline via the
// `temporal` marker).
permit ( principal, action == AgentCore::Action::"SellShares", resource )
when {
    context.input.shares <= 100
    && temporal {
        formerly within 1h AgentCore::Action::"ApproveSale"::response{
            input.stock:     context.input.stock,
            input.shares:    context.input.shares,
            output.approved: true
        }
    }
};
```

`context.input.shares <= 100`은 Dogwood 없이도 쓰던 그대로의 Cedar다. 그 옆의 `temporal { ... }`이 과거를 본다. 둘 다 성립해야 허용된다.

```text
@0    SellShares::request      { stock: "AMZN", shares: 50 }                    -> DENY
@60   ApproveSale::response    { stock: "AMZN", shares: 50, approved: true }
@120  SellShares::request      { stock: "AMZN", shares: 50 }                    -> ALLOW
@180  ApproveSale::response    { stock: "AMZN", shares: 500, approved: true }
@240  SellShares::request      { stock: "AMZN", shares: 500 }                   -> DENY
```

첫 요청은 주식 수가 임계 아래인데도 이력에 승인이 없어 거부다. 시간 조건 쪽이 깨진 것이다. 세 번째 줄은 양쪽 다 성립해 허용. 마지막은 승인이 있는데도 500주가 Cedar 쪽 임계를 넘어 거부다.

설계 관점에서 이 결정은 문법 편의 이상이다. 시간 조건을 별도 절로만 두면 "Cedar 정책"과 "Dogwood 정책"이 갈라져 정책 집합이 두 갈래로 관리된다. 식으로 만들면 한 정책 안에서 섞인다.

## 3. 연산자 넷 — 그리고 그 밑의 정체

원문이 나열한 연산자는 넷이다.

| 묻고 싶은 것 | 연산자 |
|---|---|
| 이 일이 있었나? | `formerly` |
| 몇 번? | `count_within` |
| 서로 다른 것 몇 개? | `count_distinct_within` |
| 합쳐서 얼마? | `sum_within` |

### 세기 — `count_within`

```text
// Forbid a transfer once five have already
// gone out in the last hour.
forbid ( principal, action == AgentCore::Action::"Transfer", resource )
when temporal {
    count_within(1h, AgentCore::Action::"Transfer"::request{ input.amount: _ }) > 5
};
```

`_`는 와일드카드다. 금액은 상관없고 일어났다는 사실만 센다.

```text
@0    Transfer::request  { amount: 20 }  -> ALLOW   // 1st transfer
@60   Transfer::request  { amount: 20 }  -> ALLOW   // 2nd
@120  Transfer::request  { amount: 20 }  -> ALLOW   // 3rd
@180  Transfer::request  { amount: 20 }  -> ALLOW   // 4th
@240  Transfer::request  { amount: 20 }  -> ALLOW   // 5th
@300  Transfer::request  { amount: 20 }  -> DENY    // 6th in the window exceeds limit
```

여기서 산수를 한 번 맞춰볼 만하다. 조건은 `> 5`인데 여섯 번째에서 거부가 났다. 심사 중인 요청을 **빼고** 세면 @300 시점의 이전 요청은 다섯 건이고 `5 > 5`는 거짓이라 허용이 나와야 한다. 트레이스가 거부인 이상, 심사 중인 그 요청 자신이 카운트에 들어갔다는 뜻이다. 실제로 원문은 뒤쪽 절에서 이를 명시한다. `Transfer::request` 이벤트에는 "인가 심사 중인 요청을 포함한" 모든 요청이 들어간다. 임계값을 쓸 때 이 한 칸이 어긋나면 한도가 통째로 하나 밀린다.

### 서로 다른 것 세기 — `count_distinct_within`

```text
// Forbid a transfer that would make it the fourth distinct
// recipient paid in the last hour.
forbid ( principal, action == AgentCore::Action::"Transfer", resource )
when temporal {
  count_distinct_within(u, 1h, AgentCore::Action::"Transfer"::request{ input.user: u }) > 3
};
```

수취인을 `u`에 묶고, 창 안에서 `u`가 가진 서로 다른 값의 개수를 센다. 같은 사람에게 두 번 보내면 하나로 세고, 새 사람이 등장하면 눈금이 하나 오른다.

```text
@0    Transfer::request  { user: "bob" }    -> ALLOW   // 1 distinct recipient
@60   Transfer::request  { user: "carol" }  -> ALLOW   // 2
@120  Transfer::request  { user: "dave" }   -> ALLOW   // 3
@180  Transfer::request  { user: "erin" }   -> DENY    // would be 4th distinct recipient
@240  Transfer::request  { user: "bob" }    -> DENY    // still 4 (bob, carol, dave, erin)
```

**이 트레이스의 마지막 줄은 이 글에서 가장 오래 붙들고 있을 만한 한 줄이다.** `erin`에게 보내려던 송금은 거부됐다. 그런데 원문의 주석은 그다음 `bob` 재시도를 설명하며 창에 든 수취인을 `(bob, carol, dave, erin)` 넷으로 센다. **거부된 요청의 `erin`이 여전히 창 안에 있다.**

즉 이벤트 로그에는 거부된 시도도 남고, 그 시도가 이후 판정에 계속 영향을 준다. 언어 가이드가 그 동작 방식까지 확인해준다. 모든 이벤트는 판정에 앞서 먼저 시간 엔진에 넘겨져 이력에 들어가고, 허용됐는지 거부됐는지는 기록 여부를 가르지 않는다.

운영 관점에서 함의가 작지 않다. 이 트레이스에서 창을 넷으로 밀어올린 것은 성공한 송금이 아니라 **거부당한 `erin` 시도**다. 거부는 아무 일도 없었던 상태로 되돌려주지 않는다. 그다음은 정책의 종류에 따라 갈린다. 서로 다른 값을 세는 정책이라면 같은 상대에게 다시 시도해봐야 눈금은 그대로다. 마지막 줄이 `still 4`인 이유가 그것이다. 반대로 건수나 금액을 세는 정책이라면 거부된 요청도 창에 그대로 남아 계속 세어지므로, 거부와 재시도를 반복하는 에이전트는 남은 한도를 스스로 갉아먹는다. 원문은 이 결과를 트레이스로 보여주되, 그 운영상 함의를 따로 논하지는 않는다.

### 합계 — `sum_within`

```text
// Forbid a transfer once more than $5,000 has been
// transferred in the last hour, across any number of transfers.
forbid ( principal, action == AgentCore::Action::"Transfer", resource )
when temporal {
    sum_within(a, 1h, AgentCore::Action::"Transfer"::request{ input.amount: a }) > 5000
};
```

`count_within`과 구조가 같고, 이벤트 개수 대신 각 전송의 `amount`를 `a`에 묶어 더한다.

### 매크로였다

원문이 조용히 던지는 사실 하나. `count_within`·`count_distinct_within`·`sum_within`, 그리고 뒤에 나올 `bind`는 **Dogwood의 원시 연산자가 아니다.** 표준 라이브러리에 정의된 **매크로**이고, MFOTL에서 가져온 핵심 시간 연산자 부분집합으로 정의되어 있다. 더 복잡한 정책은 그 하부 MFOTL 연산을 직접 쓸 수 있다.

이 설계는 언어를 두 층으로 나눈다. 위층은 실무자가 읽을 수 있는 이름들, 아래층은 형식기법 논문의 어휘다. 위층이 이 넷으로 닫혀 있는 것은 아니다. 원문은 자주 쓰는 패턴에 직접 이름을 붙여 매크로를 정의하고 표준 라이브러리 너머로 공유 라이브러리를 만들 수 있다고 밝힌다. 다만 새 이름을 만들려면 결국 그 밑의 연산으로 뜻을 적어야 하고, 그 순간 요구되는 팀 역량이 달라진다. 도입 검토에서 빠지기 쉬운 비용이 여기 있다.

## 4. 원문에서 가장 값진 절 — `request`냐 `response`냐

앞의 비율 제한 정책들이 모두 `Transfer::request` 기준이었다는 것은 우연이 아니다. 원문은 절을 따로 떼어 그 이유를 설명한다.

`Transfer::request` 이벤트는 인가 심사 중인 요청까지 포함한 모든 요청을 담는다. `Transfer::response`는 **완료된** 전송만 담는다. 그래서 아래 정책은 앞의 것과 단어 하나만 다른데, 우회가 가능해진다.

```text
// Forbid a transfer once more than $5,000 has already
// settled in the last hour.
forbid ( principal, action == AgentCore::Action::"Transfer", resource )
when temporal {
    sum_within(a, 1h, AgentCore::Action::"Transfer"::response{ input.amount: a }) > 5000
};
```

원문의 트레이스는 두 정책의 판정을 나란히 놓는다. 왼쪽 열이 `response` 기준, 오른쪽 열이 `request` 기준이다.

```text
                                                response       request
@0  Transfer::request     { amount: 2000 }       ALLOW          ALLOW
@1  Transfer::request     { amount: 2000 }       ALLOW          ALLOW
@2  Transfer::request     { amount: 2000 }       ALLOW          DENY
@3  Transfer::response    { amount: 2000 }
@4  Transfer::response    { amount: 2000 }
@5  Transfer::request     { amount: 2000 }       ALLOW          DENY
```

갈라지는 지점은 세 번째 요청이다. 그 시점에 요청된 금액은 합쳐서 $6,000이고 아직 아무것도 완료되지 않았다. 요청 기준 정책은 거부한다. 완료분만 합산하는 정책은 아직 완료가 없으니 허용한다. 에이전트가 아직 아무것도 결제되지 않은 사이에 동시 요청을 쏟아부으면 한도가 통째로 뚫린다.

**이 절이 중요한 이유는 우회 사례 하나를 알려주기 때문이 아니다.** 정책 계층이 이제 무엇이 되었는지를 알려주기 때문이다. 시간 조건을 도입한 순간, 정책은 "지금 이 요청이 규칙에 맞나"를 묻는 순수 함수가 아니라 **동시에 변하는 상태를 읽고 판정하는 시스템**이 된다. 분산 시스템에서 익숙한 질문들이 통째로 정책 언어 안으로 들어온다. 무엇을 사실로 칠 것인가, 언제 관측된 것인가, 관측 사이에 무엇이 끼어들 수 있나. 원문 자신도 이 절을 "동시·비동기 도구 호출이 있는 상황에서 의도한 비율 제한을 **안전하게** 달성하기 위해" 필요한 이야기로 규정한다.

한편 원문의 마지막 예제는 반대 방향을 보여준다.

```text
// Forbid a transfer larger than everything already
// settled in the last hour, combined.
forbid ( principal, action == AgentCore::Action::"Transfer", resource )
when temporal {
    bind(prior,
        sum_within(a, 1h, AgentCore::Action::"Transfer"::response{ input.amount: a }),
        context.input.amount > prior)
};
```

`bind`는 집계 결과에 이름을 붙여 현재 요청과 비교할 수 있게 한다. 여기서는 창 안의 완료 총액이 `prior`가 되고, `context.input.amount > prior`가 "이미 정산된 것 전부를 합친 것보다 큰 단 하나의 송금"을 금지한다. 원문은 이를 "안티 스파이크(anti-spike) 규칙"이라 부른다. 에이전트가 스스로 만들어온 규모에서는 계속 움직이게 두되, 갑자기 나머지를 압도하는 결제 하나만 막는다.

```text
@0    Transfer::response    { amount: 1000 }               // $1,000 settled this hour
@60   Transfer::request     { amount: 500 }   -> ALLOW     // 500 <= 1,000 settled
@120  Transfer::request     { amount: 2000 }  -> DENY      // 2,000 > 1,000 settled
@180  Transfer::request     { amount: 800 }   -> ALLOW     // 800 <= 1,000 settled
```

여기서는 `response` 기준이 의도된 선택이다. 비교 대상이 "이미 **정산된**(settled) 것"이기 때문이다. 그러니까 원문은 한 절에서 요청 기준을 안전한 선택으로 설명하고, 다음 절에서 완료 기준 정책을 정상 예제로 제시한다. 둘 다 각자의 문맥에서는 타당하다. 다만 **원문은 "어느 쪽을 언제 고르는가"를 일반 규칙으로 정리해두지 않는다.** 각 예제의 이유만 문맥 안에 있을 뿐이다. 정책을 처음 쓰는 팀이 가장 먼저 요구하게 될 문서가 아마 이것일 것이다.

## 5. Cedar 위에 쌓았다는 것 — 그러면 결정성은 어디로 갔나

원문의 논리는 이렇다. 런타임 검증은 인가를 **대체하는 게 아니라 일반화**하므로, Cedar에서 이탈하지 않고 그 위에 쌓을 수 있었다. 결과로 얻은 호환성은 강하다.

- 문법적으로 유효한 Cedar 정책은 전부 문법적으로 유효한 Dogwood 정책이다. 기존 정책 집합을 재작성·마이그레이션 없이 그대로 쓴다.
- 인가 의미론도 유지된다 — 기본 거부(deny by default), `forbid`가 `permit`을 무효화.
- AgentCore Policy 안에서도 Dogwood 정책 지원이 함께 출시됐다. 고객은 기존 정책을 그대로 두고 시간 조건만 얹어 확장할 수 있다.

마이그레이션 부담이 0이라는 점은 정책 언어에서 드문 미덕이다. 이미 Cedar로 통제 계층을 세운 조직이라면 "새 언어를 배울까"가 아니라 "이 규칙 하나에 과거 참조가 필요한가"만 물으면 된다.

**다만 한 문장은 짚고 넘어갈 필요가 있다.** 원문은 의미론 유지를 설명한 뒤 "이는 감사와 집행이 이미 기대고 있는 보장이 변함없이 이어진다는 뜻"이라고 맺는다. "감사와 집행이 기대는 보장"에 원문이 이름을 붙인 자리는 앞의 한 곳뿐이고, 거기서 그것은 "동일한 요청은 평가 순서나 시스템 상태와 무관하게 동일한 결정을 낸다"였다.

여기서 한 번 걸린다. 시간 조건은 정의상 시스템 상태(이벤트 로그)를 입력으로 받는다. 동일한 요청이 로그 상태에 따라 다른 판정을 내는 것이 이 언어의 존재 이유다. 4절의 트레이스가 바로 그 그림이다. 그러면 그 결정성은 어디로 갔나.

답은 원문 밖, 함께 공개된 언어 가이드에 있다. Dogwood 정책은 Cedar로 **하강**(lowering)한다. 시간 조건은 `context.<id>` 슬롯이 되고, 시간 모니터가 이벤트 이력을 보고 그 슬롯을 채운 뒤, 최종 판정은 평범한 Cedar가 내린다. 가이드는 이걸 정확하게 적어뒀다. Dogwood는 값이 채워진 컨텍스트를 만들고, 최종 Cedar 판정은 정책 저장소가 내린다. 그러니 결정성은 사라진 게 아니라 자리를 옮겼다. **이제 그것은 요청 하나가 아니라 "요청 + 채워진 컨텍스트"에 대해 성립한다.**

바뀐 것은 결정성의 유무가 아니라 그것이 성립하는 단위이고, 그래서 감사와 재현에 남겨야 할 것도 함께 바뀐다. 예전에는 요청 하나를 다시 넣으면 같은 답이 나왔다. 이제는 요청만으로 부족하고 그 시점의 컨텍스트가 함께 있어야 한다. 가이드는 이 구분을 API 이름으로 못 박아뒀다.

`is_self_contained_cedar()`는 하강 과정에서 시간·프로바이더 슬롯이 하나도 올라오지 않았을 때만 참이다. 거짓이면 내보낸 Cedar 산출물만으로는 그 정책의 의미를 재현할 수 없고, 가이드 주석의 표현으로 "재현하려면 Dogwood의 모니터가 필요하지 내보낸 Cedar만으로는 안 된다".

재현 경로도 따로 마련돼 있다. CLI의 `dogwood replay`는 이벤트 트레이스 전체를 상태를 가진 인가 엔진에 흘려보내 판정 지점마다 결과를 찍는다. 가이드가 이걸 검증과 나란히 세운다 — 검증은 정책이 적법한지를 증명하고, `replay`는 그것이 실제로 무엇을 하는지를 보여준다.

딸려오는 문제가 하나 더 있다. 저장소 문서는 Dogwood가 판정을 반환할 뿐 스스로 기록하지는 않는다고 적는다. 감사 로그는 도입하는 쪽이 인가 호출 주위에 직접 붙일 몫이다. 판정 하나를 나중에 해명해야 하는 조직이라면, 남겨야 할 것이 판정만이 아니라 **그 판정이 본 이력**이라는 뜻이다.

## 6. 원문이 스스로 밝힌 대가

원문은 값을 치른다는 사실을 감추지 않는다. "시간 정책의 표현력은 공짜로 오지 않는다"며 셋을 든다.

| 대가 | 원문 서술 |
|---|---|
| 상태 | 평가에 이벤트의 상태 추적(stateful tracking)이 필요하다 |
| 비용 | 평가의 시간복잡도가 이벤트 로그의 길이에 의존할 수 있다 |
| 분석 도구 | 시간 조건은 현재 Cedar가 제공하는 automated reasoning 분석 도구를 **지원하지 않는다** |

셋 중 실무에서 가장 아플 것은 세 번째다. Cedar를 고른 이유의 상당 부분이 "정책 집합을 실행하지 않고 분석할 수 있다"는 것이었는데, 시간 조건을 쓰는 순간 그 정책은 그 도구의 사정권 밖으로 나간다. 정책이 의도대로 동작하는지 확인하는 방법이 정적 증명에서 트레이스 대조로 내려간다는 뜻이다. 원문이 파서·검증기와 함께 **참조 인터프리터**를 같이 낸 것도 이 맥락에서 읽힌다. 정책의 동작을 실행해서 탐색하라는 것이다.

AWS는 이 트레이드오프를 이렇게 정리한다. 에이전트 행동을 통제하는 정책에는 적절하지만, Cedar가 쓰여온 다른 모든 용도에 맞지는 않을 수 있다. **그것이 Cedar를 개조하지 않고 새 언어를 만든 이유 가운데 하나다.** 기존 사용자에게 비용을 전가하지 않으려는 판단이고, 정책 언어처럼 신뢰가 자산인 계층에서는 옳은 선택으로 보인다.

## 7. 원문이 답하지 않은 것

여기서부터는 원문에 답이 없는 항목들이다. 없다는 사실 자체가 결함이라는 뜻은 아니다. 소개 블로그의 분량 문제일 수 있다. 몇 개는 저장소와 언어 가이드가 이미 답을 갖고 있고, 그 답이 그대로 도입 조건이 된다. 나머지는 아직 열려 있다. 어느 쪽이든 도입을 검토하는 쪽에서는 이 목록이 곧 다음 회의의 안건이다.

**① 이벤트 로그는 어디에 살고 얼마나 남는가.** 원문은 평가 비용이 로그 길이에 의존할 수 있다고만 말한다. 저장 위치, 보존 기간, 재시작·장애 조치 시의 거동에 대한 서술은 없다. 그런데 `within 1h`라는 창은 "지난 한 시간의 이벤트를 갖고 있다"는 전제 위에서만 뜻을 갖는다. 이 전제는 생각보다 쉽게 깨진다. 저장소 README가 직접 인정한다. 참조 인터프리터는 순수 인메모리라 크래시나 재시작 뒤에는 트레이스가 사라지고, 기본 시간 엔진에는 축출도 용량 상한도 없다.

이력이 사라진 직후의 판정은 어느 쪽으로 기울까. 두 경우를 갈라야 한다. 시간 엔진이 **오류를 내는** 경우는 안전하다. 언어 가이드는 외부 저장소에 닿지 못하는 것 같은 실패가 판정을 닫는다(fail closed)고 명시한다. 위험한 쪽은 엔진은 멀쩡한데 이력만 빈 경우다. 창이 비었으니 `forbid ... count_within > 5` 같은 가드는 조건이 성립하지 않아 **아무것도 막지 못한다.** 기본 거부 아래이므로 최종 허용 여부는 여전히 `permit`이 정하지만, 넓은 `permit` 위에 가드를 얹는 흔한 구성이라면 한도만 조용히 사라진 채 문이 열려 있는 셈이다.

반대로 넘어지는 정책도 있다. 승인 선행을 요구하는 `formerly` 계열은 이력이 비면 승인을 못 찾아 거부로 닫힌다. **같은 사고에서 어떤 규칙은 닫히고 어떤 규칙은 열린다.** 도입 전에 확인할 것은 로그의 내구성 하나가 아니라, 내 정책 집합이 그 사고에서 어느 쪽으로 넘어지는가다.

**② 멀티 에이전트에서 로그의 경계는 어디인가.** 원문은 예제를 단일 에이전트로 한정하면서도 이런 얽힘이 멀티 에이전트 환경에서도 생긴다고 언급하고, 로드맵에서는 여러 에이전트가 함께 이룬 묶음(앙상블) 차원의 성질을 목표로 든다. 그렇다면 창은 에이전트별인가, 세션별인가, 테넌트별인가. 원문 자체에는 답이 없지만 이후 자료에는 있다. 그리고 그 답이 하나가 아니라는 점이 핵심이다. **경계는 언어가 정하지 않는다. 실행 환경이 정하고, 두 쪽이 서로 반대로 정해져 있다.**

관리형 쪽은 세션이다. AWS는 2026년 8월 20일 글에서 집행이 한 세션 안의 궤적을 평가한다고 명시한다. 세션을 가로질러 합산되는 한도는 정책 문장을 어떻게 고쳐 써도 얻을 수 없다는 뜻이다. 자체 호스팅 쪽 기본값은 정반대다. 저장소 README는 인가 엔진 인스턴스 하나가 이벤트 이력 하나를 감시하며 주체 사이에 격리도 분할도 없다고 적는다. `pin` 기능이 지정한 키로 분할된 *것처럼* 정책을 해석해주긴 하지만, 그렇다고 이력이 실제로 분할 저장된다는 뜻은 아니라고 README가 덧붙인다.

같은 언어인데 한쪽은 세션 단위로 미리 좁혀져 있고 다른 쪽은 전부가 한 통에 담긴다. 그러니 경계는 문법에서 읽어낼 수 있는 값이 아니라 배포자가 먼저 정해야 하는 값이다. 세션보다 넓은 한도가 필요하다면 그 지점이 첫 번째 설계 결정이 된다.

**③ 오픈소스 릴리스로 무엇까지 할 수 있는가.** 원문이 오픈소스 릴리스에 부여한 용도는 명확하다 — "선호하는 IDE나 코딩 에이전트로 정책을 정의하고, 파서·검증기·참조 인터프리터로 동작을 탐색한다". 집행(enforcement)을 언급한 문장은 따로 있다. AgentCore Policy 안에서의 Dogwood 지원이다. 원문은 자체 호스팅 집행이 가능한지를 말하지 않지만, 저장소는 말한다. README는 참조 인터프리터가 프로덕션용이 아니며 **Dogwood 정책을 집행하는 인가 엔진으로 직접 쓰라고 만든 것이 아니라고** 못 박고, 그 목적은 언어의 의미론을 시험하고 평가하는 것이라고 적는다. 이유도 나열한다. ①에서 본 인메모리 트레이스와 축출·상한 부재에 더해, 이벤트 타임스탬프를 검증하지 않고 이벤트를 인증하지도 않는다.

그러니 현재 그림은 이렇게 정리된다. **언어는 열려 있고, 집행 가능한 구현은 관리형 서비스 쪽에 있다.** 자체 집행을 원한다면 그 목록을 스스로 채워 인가 엔진을 만드는 일이 된다.

**④ 성능.** 지연·처리량 수치는 원문에 없다. 로그 길이 의존성을 스스로 밝힌 이상, 창 크기와 이벤트 밀도가 큰 워크로드에서 어떻게 되는지는 도입 전에 직접 재야 할 값이다.

**⑤ "오픈소스"의 현재 온도.** Apache 2.0이고 참조 코드와 언어 가이드가 공개돼 있다. 동시에 원문은 "아직 Dogwood에 대한 직접 기여를 받고 있지 않다"고 명시한다. 언어 설계와 향후 방향에 대한 피드백은 환영하고, Cedar 커뮤니티 구성원들과 이미 공유해 초기 의견을 반영했으며, 계획은 반응 수집 → 언어 안정화 후 기여 개방 → 커뮤니티와 거버넌스 구축 순이라고 한다.

저장소도 같은 말을 한다. CONTRIBUTING은 이곳이 사내 레포의 읽기 전용 미러이며, 지금은 외부 기여를 받지 않아 PR은 병합되지 않고 이슈 트래킹도 쓰지 않는다고 적는다. 읽고 포크할 수는 있지만 아직 함께 만드는 단계는 아니다. 로드맵에 있는 기능을 기다리는 입장이라면 그 일정에 대한 영향력이 현재로선 피드백뿐이라는 뜻이기도 하다.

## 8. 로드맵 — 지금은 safety만 본다

원문이 못을 박는다. **오늘의 Dogwood는 safety를 검증한다.** 최근 과거를 보고 규칙을 깨는 행동을 금지한다. 그게 전부이고, 다음이 예고되어 있다.

**절대 시간 연산자.** 지금의 모든 창은 상대적이다. "한 시간 안"은 시계를 따라 앞으로 미끄러지는 창이다. 현실의 규칙 상당수는 벽시계 경계에 고정돼 있다. 자정에 리셋되는 일일 쿼터, "영업 종료 전" 같은 것들이다. 그런 규칙에는 미끄러지지 않는 창이 필요하다.

**liveness.** safety가 "무엇이 일어나면 안 되는가"라면 liveness는 "무엇이 반드시 일어나야 하는가"다. 승인은 결국 이행되어야 하고, 시작된 작업은 종료 상태에 도달해야 하고, 열린 자원은 해제되어야 한다. 미래를 추론하는 연산자가 필요하고, 원문에 따르면 MFOTL은 이 개념을 이미 모델링하고 있어 확장이 자연스러운 다음 걸음이다.

에이전트를 운영해본 사람에겐 이 항목이 남 얘기가 아니다. 실전에서 자주 아픈 것은 에이전트가 하면 안 될 일을 하는 경우만이 아니라, **시작해놓고 끝내지 않는 경우**다. 승인 요청을 던지고 잊고, 락을 잡고 놓지 않고, 작업을 열어두고 다음 루프로 넘어간다. 이 부류는 오늘의 Dogwood가 다루는 범위 밖이다. 정지 조건과 종료 판정을 다루는 [[루프-엔지니어링]]의 문제 영역과 정확히 겹치는 자리이기도 하다.

**멀티 에이전트 오케스트레이션.** 일이 여러 에이전트로 퍼지면 검사할 성질도 하나의 에이전트가 아니라 앙상블에 대한 것이 된다 — 누가 누구에게 넘길 수 있는가, 어느 에이전트가 락을 쥐고 있는가, 그룹 전체가 진전하고 있는가. 원문은 이곳이 "궁극적으로 Dogwood를 데려가고 싶은 자리"라고 쓴다.

## 9. 그래서 언제 쓰고, 언제 쓰지 말아야 하나

Dogwood를 쓰지 말아야 할 경우가 먼저다.

**규칙에 과거가 필요 없다면 쓰지 마라.** 이건 절차로 만들 수 있다. 규칙을 한 문장으로 적고, 그 문장이 "…한 뒤에", "…번까지", "…를 하고 나서는" 중 하나를 포함하는지 본다. 없으면 point-in-time으로 충분하고, 그러면 Cedar로 쓴다. 그편이 automated reasoning 분석 도구의 사정권 안에 남는다. 시간 조건은 필요한 규칙에만 쓰는 도구지, 정책 집합 전체를 옮겨갈 이유가 아니다.

**정적 분석이 규제 요건인 조직이라면 신중하라.** 정책을 실행 없이 증명할 수 있어야 하는 요구가 있다면, 시간 조건을 쓰는 순간 그 요구를 만족하는 방법이 바뀐다. 원문이 이 한계를 명시했으니 협상은 도입 전에 끝내는 게 낫다.

**로그를 책임질 수 없다면 아직이다.** 이벤트 이력의 내구성은 언어가 아니라 배포자가 푸는 문제다. 7절 ①을 풀지 않은 채 시간 정책에 통제를 맡기는 것은, 판정의 정확성을 눈에 보이지 않는 로그 저장 계층의 상태에 맡기는 것이다.

반대로 쓸 이유는 분명하다. 선행조건·비율 제한·순서 — 이 셋 중 하나라도 지금 애플리케이션 코드 안에 흩어져 있다면, 그 규칙들은 원래 정책 계층에 있어야 할 것들이다. 코드에 흩어진 규칙은 감사하기 어렵고, 에이전트가 다른 경로로 같은 도구를 부르면 우회된다. 도구 호출 경계에 규칙을 모으는 것이 [[ai-에이전트-통제-시스템]]이 말하는 통제 구조의 핵심이고, Dogwood는 그 경계에서 표현할 수 있는 문장의 범위를 넓힌다.

한 가지 관점을 더 얹는다. 에이전트의 신뢰를 확보하는 방법은 오랫동안 **사후 평가**였다. 벤치마크를 돌리고, 궤적을 채점하고, 회귀를 잡는다([[에이전트-평가-evals]]). 사후 평가는 통계를 준다. 통계는 "이 에이전트가 대체로 잘한다"는 말이지 "이번 송금이 규칙을 지킨다"는 말이 아니다. 런타임 검증은 후자를 노린다. 둘은 대체 관계가 아니다. 평가는 에이전트를 고치고, 런타임 검증은 사고를 막는다. [[프로덕션-ai-에이전트-기본-개념]]에서 도구 거버넌스를 별도 층으로 세우는 이유가 여기 있고, [[에이전틱-엔지니어링]] 관점에서 보면 시간 정책은 에이전트에게 허용된 행동 공간을 궤적 단위로 좁히는 장치다.

## 마무리 — 읽고 남는 문장 하나

블로그 전체에서 가장 오래 남는 것은 연산자 표가 아니라 저 트레이스 한 줄이다.

```text
@240  Transfer::request  { user: "bob" }    -> DENY    // still 4 (bob, carol, dave, erin)
```

거부된 시도가 창에 남아 다음 판정을 좁힌다. 정책의 입력이 궤적이 되면 이런 일이 생긴다 — **실패도 이력이다.** 에이전트를 운영하는 쪽에서 새로 감당해야 할 사고방식이 이 한 줄에 다 들어 있다.

관련: [[ai-에이전트-통제-시스템]] · [[프로덕션-ai-에이전트-기본-개념]] · [[에이전트-평가-evals]] · [[루프-엔지니어링]] · [[에이전틱-엔지니어링]] · [[ai-엔지니어링-4계층]]

## 출처

- **1차 출처**: Marc Brooker, Joseph Tassarotti, Jean-Baptiste Tristan, *Introducing Dogwood: runtime verification for AI agents*, AWS Open Source Blog, 2026-08-06. [원문 링크](https://aws.amazon.com/ko/blogs/opensource/introducing-dogwood-runtime-verification-for-ai-agents/)
  - 이 글의 모든 코드 예제·이벤트 트레이스·인용은 위 원문에서 그대로 옮겼다. 트레이스의 타임스탬프·금액·판정은 원문 값이다.
  - 직접 센 수치 — "정책 코드 예제 7개": 집계 범위는 원문 본문 중 `permit`/`forbid`로 시작하는 정책 코드 블록(승인 후 판매, 혼합 절, `count_within`, `count_distinct_within`, `sum_within`, `sum_within` 오류 변형, `bind`). 연산자 넷은 원문이 직접 나열한 항목의 수다.
- **Dogwood 저장소 (README·CONTRIBUTING, Apache 2.0)**: [github.com/dogwood-policy/dogwood](https://github.com/dogwood-policy/dogwood) — 멀티테넌시 기본값과 `pin`(7절 ②), 참조 인터프리터의 용도 제한과 인메모리 트레이스 소실(7절 ①③), 판정을 기록하지 않는다는 서술(5절), 외부 기여 미수용(7절 ⑤)의 근거.
- **Dogwood 언어 가이드** (저장소 동봉, `dogwood-docs/guide/`) — 하강(lowering)과 `context.<id>` 슬롯, `is_self_contained_cedar()`, 시간 엔진 실패 시 판정을 닫는다는 서술은 [07-api-and-workflow.md](https://github.com/dogwood-policy/dogwood/blob/main/dogwood-docs/guide/07-api-and-workflow.md), `dogwood replay`와 "검증 대 재생" 대비는 [12-cli.md](https://github.com/dogwood-policy/dogwood/blob/main/dogwood-docs/guide/12-cli.md).
- **AgentCore에서의 집행 단위**: AWS, *Authoring Dogwood policies from natural language in Amazon Bedrock AgentCore*, AWS Machine Learning Blog, 2026-08-20. [원문 링크](https://aws.amazon.com/blogs/machine-learning/authoring-dogwood-policies-from-natural-language-in-amazon-bedrock-agentcore/) — 집행이 한 세션 안의 궤적을 평가한다는 서술(7절 ②)의 근거. 릴리스 2주 뒤 자연어 정책 저작 기능이 붙었음도 이 글이 알린다.
- 원문이 참조로 든 관련 글: *Why Policy in Amazon Bedrock AgentCore chose Cedar for securing agentic workflows* — Cedar 선택 이유와 automated reasoning의 중요성을 다룬다고 원문이 소개한다. (본 글에서는 원문의 소개 문장만 근거로 삼았고 해당 글 자체는 확인하지 않았다.)
