# Quiet Move Simulator v2 — 출력 인덱스

> v2는 "일반 일상의 평균 문제"가 아니라, **특정 분야에 깊이 빠진 사람이 그 세계 안에서 살아가는 과정**을
> 행동·감정·기억·적응·회고(Reflection) 축으로 심층 추적하는 시스템입니다.
> 각 분야 파일은 **A~M 13개 섹션**을 포함합니다.

---

## v2 운영 원칙 (v1과의 차이)

| 구분 | v1 (output/) | v2 (output_v2/) |
|---|---|---|
| 대상 | 일상 시뮬레이션 (가정·취업·직장) | **특수 분야 심층** (취미·투자·경쟁·구매) |
| 질문 | 불만·니즈? | **집착·반복·회고·적응**은 무엇인가 |
| 핵심 | 전환점(Turning Point) | **Reflection(회고)과 부적응적 해석** |
| 산출 | Quiet Move (일상 루프) | Quiet Move (분야 루프 + 인지 과정) |
| 구분 태그 | 실측/추론/미검증 | **WORLD FACT / PERSONA ASSUMPTION / SIMULATED… / REFLECTION / CAUSAL INFERENCE** 등 |

> v2에서 특히 중요하게 보는 것(스펙 §19, §23): **사람이 생각을 정리하는 과정 자체의 마찰**과
> **수작업으로 만든 개인 시스템(엑셀·사진첩·셀프 카톡·즐겨찾기)**.

---

## 분야 선정 (서로 다른 성격, 스펙 §5)

| 파일 | 분야 | 성격 | 대표 페르소나 수 |
|---|---|---|---|
| [01_pokemon_card.md](01_pokemon_card.md) | 포켓몬 카드 | **강한 수집 욕구 + 투자(시세)** | 3 |
| [02_lol.md](02_lol.md) | LOL | **실시간 경쟁(복기 루프)** | 3 |
| [03_fishing.md](03_fishing.md) | 낚시 | **현장 활동(출조 준비)** | 3 |
| [04_fashion.md](04_fashion.md) | 패션 쇼핑 | **반복 구매(사이즈·위시)** | 3 |
| [05_running.md](05_running.md) | 러닝 | **자기계발(기록·크루)** | 3 |
| [06_cross_domain.md](06_cross_domain.md) | **교차 비교** | Quiet Move 비교 + Quietness Score | — |

---

## 각 파일의 공통 구조 (스펙 §37)

```
A. Domain World        분야의 세계 상태 (WORLD FACT 위주)
B. Domain Persona      대표 참가자 (정체성·집착·장비·지출·시간)
C. Behavioral Loop     반복되는 행동 구조 (분야의 중독적 루프)
D. Mental Timeline     감정 / 기분 / 생각의 시간적 흐름
E. Memory Timeline     과거 경험·기억의 누적과 재활성화
F. Adaptation Map      불편에 대응해 스스로 만든 해결책(개인 도구)
G. Reflection Timeline 회고가 발생한 순간과 내용 (R1~R8)
H. Abstraction/General 사람이 자신의 경험에서 뽑은 (부정확할 수 있는) 패턴
I. Turning Points      행동·사고가 바뀐 순간
J. Friction Map        시간·돈·행동·감정·인지·사회적 비용
K. Quiet Move Candidates  작은 개입 후보 (행동 + 인지 과정)
L. Minimal Product     가장 작은 제품 형태
M. Counterfactual      개입 전후 비교 + Quietness Score
```

---

## 결과물 읽는 법

- 태그 `(WORLD FACT)` = 웹 리서치로 확인된 실제 세계 조건
- 태그 `(PERSONA ASSUMPTION)` = 페르소나 설정(가정)
- 태그 `(SIMULATED …)` / `(REFLECTION)` = 시뮬레이션에서 발생한 경험·생각·감정·회고
- 태그 `(CAUSAL INFERENCE)` = 관측에서 유도한 인과 해석 (가설)
- 태그 `(QUIET MOVE)` / `(PRODUCT HYPOTHESIS)` = 개입 가설

> **중요**: v2 산출물은 "사람을 조사해 실제 수요를 찾은 결과"가 아니다.
> 스펙 §38 — 시뮬레이션 결과를 실제 사용자 조사처럼 표현하지 않는다.