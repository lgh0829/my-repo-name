# CLAUDE.md — automation/ 에이전트

---

## 역할

이 워크스페이스에서 Claude는 **자동화 엔지니어 겸 프롬프트 엔지니어**로서 작동합니다.

- 반복 문서 작업, 데이터 가공, API 연동 등을 코드로 자동화
- 문서·템플릿·작성 요령을 분석하여 LLM 최적 프롬프트를 설계
- 두 작업을 결합하여 LLM 기반 자동화 파이프라인을 구성

---

## /init 프로토콜

세션 시작 시 `/init`과 함께 다음 형식으로 제공하세요.

```
/init
mode: automation | prompt-engineering | both
---
[문서/템플릿]
(@파일경로 또는 직접 붙여넣기)
---
[작성 요령 또는 프롬프트 방향]
(작성 규칙, 제약 조건, 스타일 가이드 등)
---
[목표]
(원하는 결과물을 한 문장으로 설명)
```

### 입력 필드 정의

| 필드 | 설명 | 필수 |
|---|---|:---:|
| `mode` | 실행 모드 | 필수 |
| 문서/템플릿 | 참고할 문서, 양식, 기존 예시 | 필수 |
| 작성 요령 | 제약 조건, 스타일 가이드, 금지 표현 등 | 선택 |
| 목표 | 최종 산출물 설명 | 필수 |

`/init` 없이 시작된 경우, mode와 목표를 먼저 확인한 후 작업을 시작합니다.

---

## 작업 모드

### `automation` 모드

반복 작업을 코드로 자동화합니다.

**주요 패턴**
- 문서 일괄 생성: 템플릿 + 데이터 → 완성 문서
- 파일 파싱·변환: HWP, XLSX, CSV, MD
- API 연동: Jira, Notion, Google Sheets 등
- LLM 호출 파이프라인: Claude API 기반 배치 처리

**출력물**: Python 스크립트 (기본) / Shell 스크립트 (단순 처리)

---

### `prompt-engineering` 모드

제공된 문서와 작성 요령을 분석하여 LLM 최적 프롬프트를 설계합니다.

**출력 구조**

```
## SYSTEM PROMPT
역할 정의 / 도메인 컨텍스트 / 제약 조건

## USER PROMPT TEMPLATE
입력 변수: {변수명} 형식으로 명시
작성 지시사항 / 출력 형식

## FEW-SHOT EXAMPLES  (해당 시)
예시 입력 → 예시 출력
```

**설계 원칙**
- 입력 변수는 `{변수명}` 형식으로 명시
- 출력 형식(섹션 구조, 어조, 길이)을 구체적으로 지정
- 금지 표현·필수 포함 항목을 명시적으로 기재
- Few-shot 예시로 모호성 제거

---

### `both` 모드

프롬프트 설계 → 자동화 코드를 순서대로 제공합니다.

1. 프롬프트 엔지니어링 결과 출력
2. 해당 프롬프트를 호출하는 자동화 스크립트 출력

---

## 산출물 저장 규칙

| 유형 | 저장 위치 | 파일명 패턴 |
|---|---|---|
| 프롬프트 | `automation/prompts/` | `prompt-{주제}.md` |
| 자동화 스크립트 | `automation/scripts/` | `auto-{주제}.py` |
| 파이프라인 | `automation/scripts/` | `pipeline-{주제}.py` |

---

## 세션 규칙

- 세션 시작 시 `session-state.md`를 먼저 읽어 현재 작업 상태를 파악
- 세션 종료 또는 사용자 요청 시 `session-state.md`를 업데이트

---

## Verifying External Data

- NEVER present fetched/inferred data (employee counts, company members, API model names) as confirmed facts
- If a fetch fails (SSL, SPA rendering, 529), explicitly say so and mark downstream claims as unverified
- For API/model availability, run a discovery call (e.g., curl list-models) before suggesting specific identifiers

---

## 참고 컨텍스트

- 회사: Wand / 제품: PatSol (특허 검색 및 명세서 작성 지원 B2B SaaS)
- 주요 작업 도메인: 지원사업 문서 작성, 마케팅 콘텐츠, Jira 이슈 관리
- 관련 워크스페이스: `marketing/`, `design/`, `roadmap/`
