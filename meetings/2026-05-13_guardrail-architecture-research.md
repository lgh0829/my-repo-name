# 멀티에이전트 LLM 시스템의 금지 의도(Forbidden Intent) 처리 아키텍처 의사결정 리서치

**작성 목적:** PatSol AI 어시스턴트 킥오프 미팅 의사결정 지원  
**작성일:** 2026-05-13  
**관련 이슈:** PS-827, PS-730  
**관련 문서:** [[2026-05-13_PS827-품질테스트-계획]]

---

## 1. 아키텍처 패턴 분류

### 패턴 A — 단일 레이어 (Orchestrator 통합형)

Orchestrator 프롬프트 안에 금지 의도 처리 로직을 모두 포함하는 방식.

```
User Input
    ↓
[Orchestrator (intent + barricade)]
    ↓ allowed only
Review Agent → Author Agent
```

| 항목 | 내용 |
|---|---|
| 장점 | 구현 단순, 유지보수 파일 1개, LLM의 컨텍스트 이해력 활용 |
| 장점 | 도메인 맥락을 고려한 nuanced 거부 가능 |
| 단점 | 프롬프트 인젝션 등 jailbreak에 취약 (비결정적 동작) |
| 단점 | Orchestrator 프롬프트 복잡도 증가 → 의도 분류 정확도 저하 가능 |
| 단점 | 거부 규칙 변경 시 Orchestrator 전체 재테스트 필요 |
| 단점 | LLM 응답 생성 후 거부 판단 시 compute 낭비 |

**해당하는 업계 사례:** OpenAI 초기 system prompt 기반 content policy, 초기 ChatGPT RLHF 내장 정책

---

### 패턴 B — 투 레이어 (Pre-filter + Orchestrator 분리형)

별도의 가드레일 레이어가 Orchestrator 앞단에서 금지 의도를 먼저 차단.

```
User Input
    ↓
[Pre-filter / Guardrail Layer]
    ├── BLOCKED → 즉시 거부 응답
    └── PASSED ↓
[Orchestrator (intent classification only)]
    ↓
Review Agent → Author Agent
```

| 항목 | 내용 |
|---|---|
| 장점 | 관심사 분리(SoC) — 거부 로직과 분류 로직 독립 유지보수 |
| 장점 | Pre-filter가 빠른 경우 compute 절약 (downstream LLM 미호출) |
| 장점 | 거부 규칙 변경이 Orchestrator에 영향 없음 |
| 장점 | Constitutional Classifiers처럼 hardened 모델 적용 가능 |
| 단점 | 레이턴시 추가 (직렬 처리 시) |
| 단점 | Pre-filter가 도메인 맥락 없이 판단 → 오탐(False Positive) 위험 |
| 단점 | 컴포넌트 추가로 인프라 복잡도 증가 |

**해당하는 업계 사례:**
- **Anthropic Constitutional Classifiers:** 별도 input/output classifier가 base model과 분리 운용. jailbreak 성공률 86% → 4.4%로 감소, 오탐 0.38% 증가, compute +23.7%
- **NVIDIA NeMo Guardrails:** `generate_user_intent` 단계에서 정의된 인텐트 목록 매칭 여부 판단. 단, 레이턴시 1.3초 이상 페널티 발생
- **OpenAI Moderation API:** 별도 API endpoint, 메인 completion과 비동기 실행 가능. "보수적 보조 신호로 간주해야 하며 단독 가드레일로 불충분"(OpenAI 공식 권고)

---

### 패턴 C — 하이브리드 (경량 Pre-filter + LLM Fallback)

규칙 기반 또는 경량 분류기로 명확한 케이스를 처리하고, 애매한 케이스만 LLM 판단으로 escalate. **2024-2025년 가장 활발히 연구되는 패턴.**

```
User Input
    ↓
[Fast Path: Regex / Light Classifier]  ← ~ms 단위
    ├── CLEARLY BLOCKED → 즉시 거부
    ├── CLEARLY SAFE → Orchestrator로 전달
    └── AMBIGUOUS ↓
[LLM Safety Judge]  ← ~300-500ms 추가
    ├── BLOCKED → 거부
    └── PASSED → Orchestrator로 전달
```

| 항목 | 내용 |
|---|---|
| 장점 | 대부분의 명확한 케이스는 fast path 처리 → 평균 레이턴시 최소화 |
| 장점 | 경계 케이스에서 LLM의 맥락 이해력 활용 |
| 장점 | 도메인 특화 규칙을 fast path에 하드코딩 가능 |
| 단점 | 가장 복잡한 구현 |
| 단점 | 두 판단 레이어 간 불일치 처리 로직 필요 |

**해당하는 업계 사례:**
- **SafeHarbor (2025, arxiv:2605.05704):** 2-layer MLP fast path(306ms) + 기반 LLM 판단 결합. LlamaGuard 대비 19% 빠른 속도, 93.2% 유해 요청 거부율 달성
- **Amazon Science (2024):** 경량 SetFit + LLM 불확실도 기반 라우팅으로 LLM 단독 대비 레이턴시 50% 절감, 정확도 2% 내 유지

---

## 2. 주요 트레이드오프 분석

### 2.1 레이턴시 vs. 정확도

| 방식 | 레이턴시 | 정확도 | 비고 |
|---|---|---|---|
| 규칙/정규식 pre-filter | < 10ms | 낮음 (명확한 패턴만) | false positive/negative 모두 높음 |
| 경량 분류 모델 (Llama Guard 등) | 300-400ms | 중간 | NeMo: 0% bypass, 16.22% false positive |
| LLM-as-judge (별도 호출) | 500ms-2s | 높음 | 레이턴시 허용 여부에 달림 |
| Orchestrator 내 in-context | 0ms 추가 | 중간 | jailbreak에 취약 |
| 하이브리드 | 10-400ms (케이스별) | 높음 | 복잡도 증가 |

> **실무 경험칙:** "5초를 추가하는 가드레일은 일주일 내에 비활성화된다" (NeMo 레이턴시 페널티 이슈)

### 2.2 유지보수성

| 방식 | 거부 규칙 수정 | 의도 분류 수정 | 독립성 |
|---|---|---|---|
| 단일 레이어 | Orchestrator 전체 재테스트 | 거부 규칙에 영향 가능성 | 낮음 |
| 투 레이어 | Pre-filter만 수정 | Orchestrator 독립 | 높음 |
| 하이브리드 | Fast path + Fallback 각각 | Orchestrator 독립 | 높음 |

### 2.3 도메인 특화 (특허/법률 AI) 고려사항

1. **False Positive 위험이 치명적**: "특허 등록 가능성이 있다"와 "특허 등록을 보장한다"의 구별은 일반 독성 분류기가 잡기 어렵다.
2. **도메인 내 거부 vs. 도메인 외 거부 혼재**: 완전 off-topic 요청(악성)과 도메인 내 법적 결론 단정(제한적 허용)은 다르게 처리해야 한다.
3. **법적 책임 방어선(UPL, Unauthorized Practice of Law):** Stanford CodeX 연구(2026)에 따르면 UPL 방지 거부는 "시스템 레벨의 구조적(structural) 거부"여야 하며 프롬프트 텍스트에 의존하는 것은 충분하지 않다.

---

## 3. PatSol 상황에 맞는 권장 방향

### 결론: 하이브리드 투 레이어 (패턴 C 변형) 권장

| 조건 | 분석 |
|---|---|
| 도메인: 특허 전문 | 금지 패턴이 "법적 결론 단정", "비특허 법적 조언" 등 전문적 분류 필요 |
| 규모: SaaS 초기 단계 | 과도한 인프라 복잡도 지양, 단계적 확장 가능한 구조 선호 |
| 에이전트 구조: 3단계 | Orchestrator 앞단 pre-filter가 downstream 전체 보호 |
| 출력 리스크: 명세서 작성 | "어디까지 처리하고 어디서 멈출지" 경계 설계가 핵심 |
| 법적 책임: UPL 준수 | 프롬프트 수준이 아닌 구조적 거부 레이어 필요 |

### 제안 아키텍처

```
User Input
    ↓
[Layer 1: Fast Barricade]
│ - 규칙 기반 / 소형 classifier
│ - 처리 대상:
│     (a) 완전 off-topic (특허 무관 일반 법률 상담, 유해 콘텐츠)
│     (b) 명백한 법적 결론 요청 패턴 ("등록 가능한가요?" 단독 형태)
│ - 레이턴시 목표: < 50ms
│ - BLOCKED → 즉시 표준 거부 메시지 반환
    ↓ PASSED
[Layer 2: Orchestrator]
│ - 의도 분류: {intent, confidence, candidates?}
│ - 도메인 내 경계 케이스 처리
│     (예: "등록 가능성 분석" → Review 에이전트에서 제한적 표현으로 처리)
│ - 완전 거부가 아닌 "제한된 응답" 라우팅 가능
    ↓
[Review Agent] → [Author Agent]
```

### Layer 1 금지 의도 분류 기준

특허 도메인의 금지 의도는 두 가지 유형으로 구분한다.

**Type A — 하드 차단 (법적 책임 직결, Layer 1에서 차단):**
- 특허권 침해 회피 법률 조언 요청
- 경쟁사 특허 무효화 전략 단정 요청
- 명세서가 아닌 법원 제출용 문서 작성 요청

**Type B — 소프트 리다이렉트 (Orchestrator에서 제한적 처리):**
- "이 발명이 특허 등록될 수 있나요?" → Review 에이전트가 기재요건 분석 결과 제시, 등록 가능 단정 표현 금지 (P-4)
- "경쟁사 특허를 우회하는 클레임을 써줘" → 클레임 초안 제공 가능, 법적 안전성 보장 표현 제거

### 단계적 구현 전략

| 단계 | 내용 |
|---|---|
| Phase 1 (지금) | 규칙 기반 Layer 1 (정규식 + 명시적 패턴 목록). PS-827 테스트로 패턴 발굴 |
| Phase 2 | 발굴된 패턴으로 fine-tuned 경량 분류기 학습 |
| Phase 3 | 출력 레이어 가드레일 추가 (Author 출력에서 법적 단정 표현 감지·재생성) |

---

## 4. 출력 레이어 가드레일 (추가 고려사항)

입력 필터링만으로는 불충분하다. Author 에이전트 출력에 대한 post-LLM 검사도 필요하다.

- **표현 수준 가드레일:** "특허 등록 가능" 단정 표현이 출력에 포함되었는지 정규식/문장 임베딩으로 검사
- **자기수정 루프:** 위반 표현 감지 시 Author 에이전트에 재생성 요청 (최대 2회 retry)

> Anthropic 가이드는 이 패턴을 "가장 강력한 post-LLM 패턴"으로 명시.

---

## 5. 킥오프 미팅 제안 핵심 근거

> "Orchestrator 단일 레이어는 구현이 간단하지만, 세 가지 이유로 투 레이어 분리를 권장한다.
>
> **첫째,** 법적 결론 단정 방지는 UPL(무면허 법률 행위) 리스크와 직결되며, Anthropic·Stanford 연구 모두 이런 거부는 프롬프트 텍스트가 아닌 구조적 레이어로 처리해야 한다고 권고한다.
>
> **둘째,** Orchestrator에 거부 로직이 섞이면 의도 분류 정확도가 낮아진다. 두 책임을 분리해야 각각 독립적으로 개선할 수 있다.
>
> **셋째,** Layer 1을 경량(규칙 기반 + 소형 모델)으로 구성하면 추가 레이턴시를 50ms 이하로 제한하면서 Orchestrator의 compute를 보호할 수 있다. 특허 도메인의 금지 패턴은 상대적으로 명확하게 열거 가능하기 때문에 범용 독성 분류기보다 특화된 경량 분류기가 오히려 정확도가 높다.
>
> 초기에는 규칙 기반 Layer 1으로 시작하고, 데이터가 쌓이면 fine-tuned classifier로 교체하는 단계적 전략을 취한다."

---

## 출처

- [SafeHarbor: Hierarchical Memory-Augmented Guardrail for LLM Agent Safety (arxiv, 2025)](https://arxiv.org/html/2605.05704)
- [LLM Guardrails Best Practices — Datadog](https://www.datadoghq.com/blog/llm-guardrails-best-practices/)
- [AI Agent Guardrails: Pre-LLM & Post-LLM Best Practices — Arthur AI](https://www.arthur.ai/blog/best-practices-for-building-agents-guardrails)
- [AI Agent Guardrails: Rules That LLMs Cannot Bypass — AWS/DEV Community](https://dev.to/aws/ai-agent-guardrails-rules-that-llms-cannot-bypass-596d)
- [The landscape of LLM guardrails — ML6](https://www.ml6.eu/en/blog/the-landscape-of-llm-guardrails-intervention-levels-and-techniques)
- [Constitutional Classifiers — Anthropic](https://www.anthropic.com/research/constitutional-classifiers)
- [Building Effective AI Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications — EMNLP 2023](https://aclanthology.org/2023.emnlp-demo.40.pdf)
- [Measuring Effectiveness and Performance of AI Guardrails — NVIDIA Technical Blog](https://developer.nvidia.com/blog/measuring-the-effectiveness-and-performance-of-ai-guardrails-in-generative-ai-applications/)
- [OpenAI Safety Best Practices](https://developers.openai.com/api/docs/guides/safety-best-practices)
- [Intent Detection in the Age of LLMs — ACL Anthology (2024)](https://aclanthology.org/2024.emnlp-industry.114/)
- [Implementing AI Guardrails using a Multi-Agent System Orchestrator — Medium](https://medium.com/@devesh2178/implementing-ai-guardrails-using-a-multi-agent-system-orchestrator-9144ad062a0e)
