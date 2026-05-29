---
aliases: 현행 명세서·청구항 생성 파이프라인 분석
작성일: 2026-04-23
수정일: 2026-04-23
상태: 초안
tags:
  - spec
  - pipeline
  - implementation
  - reference
관련문서:
  - "[[frd-spec-requirements]]"
  - "[[frd-spec-generation-pipeline]]"
  - "[[frd-spec-ai-assistant]]"
상위문서: ""
---

# 현행 명세서·청구항 생성 파이프라인 — 구현 분석

> 분석 대상 파일:
> - `routes/write.py`
> - `handlers/gpt_make_new_claim.py`
> - `handlers/gpt_config.py`

---

## 1. 전체 구조

```
[클라이언트]
    ↓ HTTP POST
[routes/write.py]
  - 요청 파싱 + JWT 토큰 검증
  - AskGPT / CloudDraft 인스턴스 호출
    ↓
[handlers/gpt_make_new_claim.py — AskGPT 클래스]
  - 실제 OpenAI API 호출 로직
  - 프롬프트 조립 + 응답 파싱
    ↓ 프롬프트 문자열 참조
[handlers/gpt_config.py — GPTPromptConfig / GPTModelConfig]
  - 언어별(KR/EN/JP/CN) 프롬프트 문자열 저장소
  - 모델 ID 상수 정의
```

### 1.1 주요 엔드포인트

| 엔드포인트 | 핸들러 메서드 | 기능 |
| --- | --- | --- |
| `POST /write_claims/` | `get_chatgpt_response()` | 청구항 생성 (3-step 체인) |
| `POST /write_specification/all_exclude` | 복수 메서드 병렬 | 명세서 전체 섹션 일괄 생성 |
| `POST /write_specification/{id}` | `get_specification_chatgpt()` | 단일 섹션 생성 |
| `POST /write_specification_Embodiment/` | `get_specification_embodiment()` | 실시예 단독 생성 |

---

## 2. 파이프라인 1 — 청구항 생성 (`/write_claims/`)

3단계 LLM 체인 구조. 각 단계 결과가 다음 단계의 입력으로 전달된다.

```
입력: 발명 텍스트(str 또는 dict) + 유사특허 텍스트 + claim_number

[Step 0] parse_claim_invention()
  모델: MODEL_DESC_DEFAULT
  목적: 비정형 발명 설명 → {구성들, 목적, 효과} JSON 구조화
  조건: 입력이 dict이고 CoreComponents/Solution/Effects 키를 모두 가지면 스킵
        ↓
[Step 1] 회피전략 생성 (response1)
  모델: GPT_4O (gpt-4o-2024-08-06) — 하드코딩
  프롬프트: GPTPromptConfig.KR.AVOIDANCE_STRATEGY
  입력: 유사특허 목록 + Step 0 발명 구조
  출력 JSON: {새_발명의_개요, 새_발명의_유사특허_회피전략, 분류, 말미}
        ↓
[Step 2] 청구항 초안 생성 (response2)
  모델: GPT_4O_DEFAULT (config에서 읽음)
  프롬프트: 하드코딩 few-shot 예시 2개(AI 연속공정장치, 기능성조성물)
           + Step 1 결과 문자열 + 발명 텍스트
  출력 JSON: {청구항1, 종속항1_1, 종속항1_2, ...}
  검증: 청구항1 길이 < 150자면 최대 3회 재시도
        ↓
[Step 3] 청구항 정제 (response3)
  모델: GPT_4O (하드코딩)
  프롬프트: GPTPromptConfig.KR.REFINE_CLAIMS
  목적: 명확성·선행사·카테고리 통일 (KIPO 심사 기준 기반)
  출력: 【청구항 1】【청구항 2】... 형식 최종 텍스트 (JSON → 평문 변환)
```

### 2.1 컨텍스트 전달 방식

step1 결과를 `response_prompt` 문자열로 포매팅하여 step2 프롬프트에 직접 이어 붙인다. 별도 메모리/상태 객체 없이 텍스트 연결 방식.

```python
# Step 1 결과 → Step 2 입력으로 연결
for key, value in response_dict.items():
    response_prompt += f"<{key}> {value.strip()}\n"

prompt2 = f"... {text}\n\n{response_prompt}"
```

---

## 3. 파이프라인 2 — 명세서 전체 생성 (`/write_specification/all_exclude`)

섹션별 병렬 생성 구조. `asyncio.gather`로 동시 실행.

```
입력: 청구항 텍스트(text) + 도면 목록(drawings) + 직무발명서(invention)

[공통 전처리]
  get_cpc_chatgpt(text)
    모델: GPT_4O_MINI
    목적: A~H 섹션 CPC 1글자 분류
    이후: 모든 섹션 생성 시 example_cpc[cpc] 예시 문단 주입
          ↓

[섹션 생성] asyncio.gather — 동시 실행
  get_specification_chatgpt(text, id, cpc, application_numbers)
  대상 id: Title, TechnicalField, Background, Problem,
           Solution, Effects, Summary, BriefDescriptionOfDrawings, prior_patent
  모델: MODEL_DESC_DEFAULT (Embodiment는 o4-mini-2025-05-08 하드코딩)
  프롬프트: "'{text}'을 특허출원하려고해, {prefix[id]} 다시 작성해줘"
           + CPC 기반 예시 문단 ({example[id]})
  prior_patent 처리:
    → ElasticSearch 조회 (QueryElastic.find_documents_by_country)
    → 각 특허 요약 생성 후 선행기술 인용 형식으로 포매팅
          ↓

[Description 생성] — 청구항별 병렬
  get_specification_description(text, id, cpc)
  청구항 '¶' 구분자로 분할 → 청구항별 asyncio.gather
  프롬프트: "청구항 N. '{claim_text}'을 명확성(Clarity) 결여,
            지지요건(Support) 결여, 실시가능성(Enablement) 결여
            사항들을 보완해서 <발명을 실시하기 위한 구체적인 내용>를 다시 작성해줘"
  결과: '¶'로 join
          ↓

[Embodiment 생성] — 청구항별 병렬
  get_specification_embodiment(text, id, cpc, drawings)
  모델: gpt-4.1-mini (하드코딩)
  청구항별 asyncio.gather
  프롬프트: 청구항 + 도면 설명 → 실시예 700자 이상
  추가 출력: 사용_도면 번호 배열 (drawing_indices)
```

---

## 4. 프롬프트 구성 (`gpt_config.py`)

언어별 네임스페이스로 분리된 정적 문자열 저장소.

| 네임스페이스 | 주요 프롬프트 | 용도 |
| --- | --- | --- |
| `Common` | `SYSTEM_EXPERT`, `CPC_CLASSIFICATION` | 언어 공통 |
| `KR` | `AVOIDANCE_STRATEGY`, `REFINE_CLAIMS`, `SPEC_GENERATION`, `COMPOSITION_PROMPT` | 한국어 청구항·명세서 생성 |
| `EN` | `REFINE_CLAIMS`, `AVOIDANCE_STRATEGY` | 영어 출력 버전 |
| `JP` | `SPEC_EMBODIMENT`, `SPEC_DESC_REWRITE` 포함 전체 | 일본어 — JP만 실시예 전용 프롬프트 존재 |
| `CN` | `REFINE_CLAIMS`, `AVOIDANCE_STRATEGY` | 중국어 출력 버전 |

### 4.1 모델 설정 실제 사용 현황

`GPTModelConfig`의 `MODEL_*_DEFAULT`가 실제 호출에서 override 되는 구조.

| 설정값 | config 정의 | 실제 사용 |
| --- | --- | --- |
| `MODEL_DESC_DEFAULT` | "gpt-5.2" (placeholder) | 대부분 섹션 생성, Description, Drawings |
| `MODEL_CLAIM_DEFAULT` | "gpt-5.2" (placeholder) | 키워드 추출, boolean query |
| `GPT_4O` | "gpt-4o-2024-08-06" | 회피전략(Step 1), 청구항 정제(Step 3) — 하드코딩 |
| `GPT_4O_MINI` | "gpt-4o-mini" | CPC 분류 — 하드코딩 |
| `"gpt-4.1-mini"` | 없음 | 실시예 생성 — 하드코딩 |
| `"o4-mini-2025-05-08"` | 없음 | Embodiment (단일 섹션 경로) — 하드코딩 |

> config의 DEFAULT 값들은 현재 placeholder 상태("gpt-5.2")이며, 고품질이 필요한 경로(회피전략·정제·실시예)는 코드 내 하드코딩 모델로 실행된다.

---

## 5. 현행 구현에 없는 기능 (FRD 대비)

`frd-spec-requirements.md`에서 설계하는 기재요건 검증 기능과의 차이.

| FRD 기능 | 현행 구현 여부 | 비고 |
| --- | --- | --- |
| 레이어 1 — 다항제 형식 위반 탐지 (인용번호, 이중인용 등) | **없음** | |
| 레이어 1 — 명확·간결 표현 사전 탐지 | **없음** | |
| 레이어 2 — 뒷받침 요건 검토 (T-03) | **없음** | Description 프롬프트에 "지지요건 결여 보완" 지시가 있으나, 검토 결과 반환 기능 아님 |
| 레이어 2 — 실시가능 요건 검토 (T-04) | **없음** | |
| 레이어 2 — 도면 정합성 검토 (T-05) | **없음** | |
| CPC 기반 예시 주입 | **있음** | `example_cpc[cpc]` — 명세서 생성 품질 향상용 |
| ElasticSearch 선행기술 조회 | **있음** | `prior_patent` 섹션 생성 시 사용 |

### 5.1 현행 Description 프롬프트의 기재요건 언급

`get_specification_description` 내 각 청구항별 프롬프트:

```
"명확성(Clarity) 결여, 지지요건(Support) 결여, 실시가능성(Enablement) 결여
사항들을 보완해서 <발명을 실시하기 위한 구체적인 내용>를 다시 작성해줘"
```

이는 명세서 섹션을 **생성하면서 보완하라는 지시**이며, 기재요건 항목별 검토 결과를 구조화하여 반환하는 기능이 아니다.

---

## 6. 토큰 관리

`truncate_text()` 함수가 `gpt_make_new_claim.py`에 정의되어 있으며, `generate_claims()` 호출 전 프롬프트에 적용된다.

```python
def truncate_text(text, model="gpt-4o-2024-08-06", max_tokens=124000):
    # tiktoken으로 인코딩 → max_tokens 초과 시 자름
    # o/4.1 계열 → o200k_base, 그 외 → cl100k_base 폴백
```

- 기본 한도: 124,000 토큰
- 현재 청구항 생성 step2 프롬프트에만 적용. 명세서 섹션 생성 경로에는 미적용
