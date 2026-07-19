---
title: "Tinker & tinker-cookbook: 파인튜닝의 '중간 층'을 여는 매니지드 학습 SDK"
type: 도구
description: 저수준 학습 루프는 사용자가 쥐고 분산 인프라만 위임하는 파인튜닝 SDK Tinker와, 그 위의 레시피 라이브러리 tinker-cookbook 해부
tags: [파인튜닝, 강화학습, 도구, 인프라]
resource: https://github.com/thinking-machines-lab/tinker-cookbook
created: 2026-07-19
---

# Tinker & tinker-cookbook: 파인튜닝의 '중간 층'을 여는 매니지드 학습 SDK

파인튜닝 도구는 오랫동안 양극단만 있었다. 한쪽엔 `trainer.train()` 한 줄로 끝나는 고수준 래퍼가 있다. 알고리즘을 바꾸려는 순간 벽에 부딪힌다. 반대쪽엔 GPU 클러스터·스케줄러·체크포인트 복구까지 직접 짜는 풀스택 자가호스팅이 있다. 새 post-training 방법을 실험하려던 연구자는 대개 후자로 떠밀렸다 — 학습 루프 한 줄 바꾸자고 분산 인프라 전체를 떠안는 식으로.

**Tinker는 그 사이를 겨냥한다. 학습 루프는 당신이 파이썬으로 직접 쓰되, 분산 실행만 서비스에 위임하는 매니지드 학습 SDK다.** `forward_backward`·`optim_step` 같은 저수준 연산을 노출해 사용자가 손수 루프를 조립하고, 그 루프를 돌리는 GPU 스케줄링·리소스 할당·장애 복구는 Thinking Machines 인프라가 맡는다. **tinker-cookbook**은 Tinker API 위에 얹은 오픈소스 레시피·추상화 라이브러리 — SFT부터 RL, 선호학습, 증류, 멀티에이전트까지 "현실적인 예제"를 제공한다. 이 글은 두 층을 갈라 보고, 그것이 우리 위키의 자기개선·평가 논의에서 어디에 놓이는지까지 짚는다.

> 최신성 기준점: 이 글의 코드·폴더·모델 사실은 **2026년 7월 현재 GitHub README와 저장소 트리** 기준이다. 접근·과금처럼 시간에 민감한 항목은 관찰 시점을 문장마다 못 박았다.

## Tinker와 cookbook은 다른 것이다

먼저 흔한 혼동부터 끊자. 둘은 다른 계층이다.

| | Tinker | tinker-cookbook |
|---|---|---|
| 정체 | 저수준 학습 SDK / 매니지드 API | 그 위의 오픈소스 레시피·추상화 라이브러리 |
| 하는 일 | 학습 연산을 원격 분산 인프라에서 실행 | SFT·RL·DPO 등 "바로 돌려보는" 예제 제공 |
| 위치 | Thinking Machines가 운영하는 서비스 | GitHub 공개 저장소 (`thinking-machines-lab/tinker-cookbook`) |
| README 정의 | "a training SDK ... to fine-tune language models" | "builds on the Tinker API and provides common abstractions" |

README(공식)는 Tinker를 "연구자·개발자가 언어 모델을 파인튜닝하는 학습 SDK"로, 사용자가 "API 요청을 보내면 우리가 분산 학습의 복잡성을 처리한다"고 정의한다. cookbook은 "Tinker API 위에 얹혀, 파인튜닝에 흔히 쓰는 추상화를 제공"하는 레이어다. 저장소 태그라인 한 줄이 관계를 요약한다 — "Post-training with Tinker."

## 어떤 '층'을 여는가: 저수준 연산 + 위임된 인프라

Tinker의 설계 의도는 README 코드 예제에 그대로 드러난다.

```python
import tinker

service_client = tinker.ServiceClient()
training_client = service_client.create_lora_training_client(
    base_model="meta-llama/Llama-3.2-1B", rank=32,
)

# 학습 루프는 사용자가 조립한다 — 저수준 연산을 직접 호출
training_client.forward_backward(...)   # loss·gradient 계산
training_client.optim_step(...)         # 가중치 갱신
training_client.save_state(...)         # 체크포인트 저장
training_client.load_state(...)         # 체크포인트 복원

# 샘플링은 가중치를 저장한 뒤 얻는 별도 클라이언트에서
sampling_client = training_client.save_weights_and_get_sampling_client()
sampling_client.sample(...)
```

여기서 핵심은 **API가 `Trainer` 같은 고수준 덩어리가 아니라, 조합 가능한 저수준 연산 몇 가지를 준다**는 점이다. `forward_backward`로 gradient를 구하고 `optim_step`으로 갱신하는 흐름을 사용자가 직접 배열한다. 공지(2025-10)의 표현대로 "가장 흔한 post-training 방법 대부분"을 이 조각들의 조합으로 표현하게 하려는 것이다. 고수준 API로는 손대기 어려운 새 알고리즘을 실험하려는 층을 겨냥한 설계로 보인다(추정 — 소스는 "저수준 primitive 제공"과 "학계 얼리어답터"를 각각 말할 뿐, 둘을 인과로 잇지는 않았다).

인프라 쪽은 반대로 완전히 가려져 있다. 공지는 서비스가 "스케줄링·리소스 할당·장애 복구를 처리"한다고 밝혔고, X 공지는 이를 "노트북에서 파이썬으로 학습 루프를 쓰면, 우리가 분산 GPU에서 돌린다"로 요약했다. 비용 구조도 공지에 명시돼 있다. Tinker는 **LoRA**(Low-Rank Adaptation, 원본 가중치를 얼리고 작은 저계수 행렬만 학습하는 기법)를 쓰는데, 그 이유를 공지는 "여러 학습 잡이 같은 컴퓨트 풀을 공유해 비용을 낮추기 위해서"라고 직접 밝힌다. README는 LoRA를 쓴다고만 하고, 채택 이유는 공지 쪽에 있다.

정리하면 Tinker가 여는 층은 이렇다.

- **위임한 것:** GPU 프로비저닝, 분산 스케줄링, 장애 복구 — 사용자는 건드리지 않는다.
- **쥐고 있는 것:** 학습 루프의 논리, 손실 함수, 데이터 파이프라인, 알고리즘 선택 — 사용자가 코드로 표현한다.

## cookbook의 레시피: 폴더가 곧 지원 범위

cookbook 저장소의 `tinker_cookbook/recipes/` 아래 폴더들은 곧 "무엇을 학습시킬 수 있나"의 목록이다. 실제 트리에서 확인한 폴더를 기준으로 지원 패러다임을 묶으면 이렇다.

| 학습 방식 | 근거 폴더 |
|---|---|
| SFT (지도학습 파인튜닝) | `chat_sl/`, 루트 `sl_loop.py`·`sl_basic.py` |
| 검증 가능 보상 기반 RL | `math_rl/`, `code_rl/`, `verifiers_rl/`, 루트 `rl_loop.py`·`rl_basic.py` |
| 선호학습 (DPO 계열) | `preference/` |
| 증류 | `distillation/`, `prompt_distillation/`, `sdft/` |
| 멀티에이전트 RL (self-play·cross-play 포함) | `multiplayer_rl/` |
| 툴 사용 / 검색 | `search_tool/` (툴 사용 로직은 패키지 모듈 `tool_use/`에도 있다) |
| 오디오 | `audio/` |
| VLM 이미지 분류 | `vlm_classifier/` |
| 루브릭 기반 채점 | `rubric/` |

몇 가지 주의점. **`self-play`라는 독립 폴더는 없다** — self-play·cross-play는 `multiplayer_rl/` 안에 들어있다. `sdft`·`harbor_rl`·`true_thinking_score` 같은 폴더는 실재하지만 약어의 정확한 뜻은 저장소가 명시하지 않아 이 글에서 확언하지 않는다. 표의 "학습 방식↔폴더" 매핑은 폴더명과 README 서술에 근거하지만, 각 폴더 내부의 세부(예: `audio/`가 정확히 어떤 태스크인지)까지는 원문 재확인이 필요하다.

메인 패키지 `tinker_cookbook/` 바로 아래에는 `supervised/`(SFT 코어), `rl/`, `renderers/`(대화 포맷·토큰화 템플릿), `eval/`(평가), `preference/`, `distillation/`, `tool_use/` 등이 모듈로 나뉘어 있다. 최소 구현을 읽고 싶다면 `recipes/sl_loop.py`(SFT)와 `recipes/rl_loop.py`(RL)가 출발점이다.

## 평가: 학습만이 아니라 채점까지 한 상자에

cookbook에는 `eval/` 프레임워크가 포함돼, 학습한 모델을 여러 표준 벤치마크로 채점할 수 있다. 리서치 단계에서 수학·코딩·일반지식 계열의 구체 벤치마크 목록이 나왔지만, 요약을 한 번 경유한 값이라 개별 벤치마크명은 이 글에서 확정하지 않는다(정확한 목록은 `eval/` 소스를 직접 볼 것). 확실한 것은 **평가가 별도 도구가 아니라 같은 라이브러리 안에 있다**는 사실이다.

이 지점이 우리 위키의 평가 논의와 맞닿는다. [[에이전트-평가-evals]]가 지적하듯 pass@1 한 줄 지표는 실제 능력을 과대평가하기 쉽고, [[aide2-재귀적-자기개선]]은 자기개선 주장에서 진짜 기여가 종종 '평가의 엄격함'에 있다고 본다. 학습 루프와 평가를 같은 상자에 둔 cookbook은, 최소한 "무엇으로 채점했나"를 코드로 드러낸다는 점에서 이 논의의 구체 사례가 된다.

## 지원 모델: Inkling, 그리고 오픈웨이트

모델은 base_model 문자열 하나로 지정한다. README 코드 예제의 기본값은 오픈웨이트 소형 모델 `meta-llama/Llama-3.2-1B`(LoRA rank=32)이고, 2025-10 공지는 대형 MoE `Qwen-235B-A22B`와 사용 사례의 `Qwen3-32B`를 이름으로 들며 "작은 모델에서 큰 모델로 바꾸는 게 문자열 하나 교체"라고 강조했다.

여기에 더해 **2026년 7월 현재 README 기준으로, Tinker는 `thinkingmachines/Inkling`이라는 자체 모델을 지원한다.** README는 Inkling을 "Tinker에 맞춘 Thinking Machines Lab의 모델 ... 코딩·추론·툴 호출·이미지/오디오 입력 처리가 가능한 범용 모델"로 소개하고, `tinker-cookbook[inkling]` extra로 설치한다. (Inkling이 언제부터 지원됐는지는 이 글의 범위 밖이다 — 출처마다 관찰 시점이 달라 시간 서사로 잇지 않는다.)

## skills/: 벤더가 배포한 Claude Code 스킬이라는 사례

한 가지 흥미로운 곁가지. 저장소 루트에는 `.claude-plugin/` 매니페스트와 `skills/` 폴더가 있고, 그 안에 스킬 둘이 들어있다.

- **`/tinker:research`** — post-training 실험(SFT·RL·DPO·증류·평가·하이퍼파라미터·모델 선택)을 계획하고 돌린다.
- **`/tinker:debug`** — 느린 학습·행(hang)·출력 불일치·렌더러 문제·에러를 진단한다.

즉 이 저장소는 **Anthropic이 아닌 제품 벤더(Thinking Machines Lab)가 자기 SDK를 쓰라고 Claude Code 스킬/플러그인을 직접 배포한 사례**다. 마켓플레이스에 `/plugin marketplace add thinking-machines-lab/tinker-cookbook`로 등록하는 방식이다. [[에이전트-스킬은-워크플로다]]가 말하는 "스킬 = 실행 워크플로"의 실물이자, [[marketing-skills-라이브러리]]의 스킬 라이브러리 설계 논의에서 '벤더가 딱 두 개짜리 얇은 스킬 세트로 시작한' 대조군으로 읽을 만하다. 다만 두 스킬의 실제 SKILL.md 내용까지 뜯어보진 않았으니, 구조 비교는 원문 확인 후에 하는 게 맞다.

## 자기개선 지도에서의 자리

우리 위키의 [[에이전트-자기개선-서베이]]는 개선 대상을 두 축으로 가른다 — 모델 가중치(θ)를 바꾸는가, 아니면 컨텍스트·스캐폴드(Σ)를 바꾸는가. **Tinker는 명백히 θ쪽 인프라다.** LoRA로 실제 가중치를 파인튜닝하는 API이기 때문이다. 그런데 그 서베이는 "대부분의 팀에게 θ쪽은 거의 닫혀 있다"고 적으면서 그 이유를 콕 집는다 — 벤더 API 뒤의 모델은 파인튜닝이 불가능하거나, 가능해도 "데이터·비용·평가 인프라가 별도 프로젝트급"이라서다. Tinker가 낮추려는 장벽이 정확히 그 지점이다(분산 인프라 위임 + LoRA 컴퓨트 공유로 비용 절감). 그래서 Tinker는 서베이가 "닫혀 있다"고 지목한 θ축을 실제로 여는 방향의 구체 사례가 된다.

대비도 유효하다. [[하네스-자기개선]]이 정리하는 근미래 자기개선 논의는 '가중치보다 하네스(Σ)를 고치는 쪽이 먼저'라고 본다. Tinker는 그 반대 축, 즉 **가중치를 바꾸는 일 자체를 저비용화**한다. 두 흐름은 경쟁이 아니라 [[ai-엔지니어링-4계층]] 스택에서 서로 다른 층을 건드리는 작업으로 나란히 놓인다.

## 트레이드오프: 언제 쓰지 말아야 하나

Tinker의 '중간 층' 포지션은 공짜가 아니다.

- **접근·과금이 불투명하다(가장 큰 실무 리스크).** 2025-10 공지 시점 기준으로 Tinker는 private beta로 시작했고, "처음엔 무료, 몇 주 안에 사용량 기반 과금을 도입할 예정"이라고 밝혔다. **그 이후 실제로 유료 전환됐는지, 여전히 beta인지, 지금 신규 가입이 열려 있는지는 이 글로 확인할 수 없다.** 도입을 검토한다면 콘솔과 가격 페이지를 직접 확인하는 것이 첫 단계다.
- **자가호스팅이 아니다 — 인프라 위임의 다른 이름은 종속이다.** 학습이 Thinking Machines 클러스터에서 돈다는 것은, 데이터가 외부로 나가고 가용성·가격을 벤더에 의존한다는 뜻이다. 온프렘 규제가 걸린 조직이나 자체 GPU가 이미 있는 팀에는 맞지 않는다.
- **저수준이라는 건 러닝커브다.** `.train()` 한 줄을 원하는 사람에게 `forward_backward`/`optim_step`을 직접 배열하라는 건 과하다. 학습 루프를 커스터마이즈할 이유가 없다면 고수준 래퍼가 낫다.
- **LoRA 중심이다.** 컴퓨트 공유·비용 절감이라는 장점의 이면은, 전체 파라미터 풀 파인튜닝(full fine-tuning)이 필요한 작업에는 결이 다를 수 있다는 점이다(README·공지가 full FT 지원 여부를 명시하지 않아 이 글에서 확정하지 않는다).
- **cookbook의 세부는 아직 요약 의존이다.** 벤치마크 목록·일부 폴더의 정확한 의미·전체 지원 모델 목록은 이 글에서 확정하지 않았다. 프로덕션 판단 전에는 해당 소스를 직접 읽어야 한다.

## 실무 적용: 그래서 언제 손대나

- **새 post-training 알고리즘을 실험하는 연구자/팀:** 딱 맞는 도구다. 인프라를 안 짜도 되면서 루프는 완전히 손에 쥔다. `recipes/sl_loop.py`·`rl_loop.py`부터 읽고, `research` 스킬로 실험 셋업을 잡는 흐름이 자연스럽다.
- **표준 SFT/DPO를 빠르게 돌리려는 팀:** cookbook의 기성 레시피로 충분할 수 있다. 다만 고수준 래퍼(예: 일반적인 Trainer류) 대비 이득이 있는지는 팀의 커스터마이즈 요구로 판단하라.
- **먼저 확인할 것:** 현재 접근 가능 여부와 과금(콘솔·가격 페이지), 필요한 base 모델이 실제 지원 목록에 있는지(`model_info.py`), 데이터 외부 반출이 규정상 허용되는지. 이 셋이 막히면 도구 자체의 매력과 무관하게 도입이 멈춘다.

## 관련

[[에이전트-자기개선-서베이]] · [[에이전트-평가-evals]] · [[aide2-재귀적-자기개선]] · [[하네스-자기개선]] · [[에이전트-스킬은-워크플로다]] · [[marketing-skills-라이브러리]] · [[ai-엔지니어링-4계층]]

## 출처

- Tinker Cookbook README (raw, 1차) — https://raw.githubusercontent.com/thinking-machines-lab/tinker-cookbook/main/README.md (관찰 2026-07-19)
- GitHub 저장소 및 트리 (1차) — https://github.com/thinking-machines-lab/tinker-cookbook (관찰 2026-07-19)
- 공식 공지 "Announcing Tinker" (1차, 2025-10 시점) — https://thinkingmachines.ai/news/announcing-tinker/
- 공식 X 공지 (1차) — https://x.com/thinkymachines/status/1973447428977336578
- VentureBeat 보도 (2차) — https://venturebeat.com/ai/thinking-machines-first-official-product-is-here-meet-tinker-an-api-for
- DeepLearning.AI The Batch (2차) — https://www.deeplearning.ai/the-batch/thinking-machines-new-tinker-api-makes-it-easier-to-fine-tune-models-on-many-gpus
