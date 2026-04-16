# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 실행 명령

```bash
# cloud_draft/ 의존성 설치 (최초 1회, Windows 전용)
cd cloud_draft
uv sync
uv run python Scripts/pywin32_postinstall.py -install

# 웹 서버 실행
uv run python server.py   # → http://localhost:11000

# 단독 테스트 (HWP 없이 로직 확인)
uv run python test_cloud_draft.py
```

`OPENAI_API_KEY`는 `cloud_draft/server.py`와 `cloud_draft/test_cloud_draft.py` 상단에서 직접 설정한다.

---

## 두 시스템의 관계

이 디렉토리에는 두 개의 구현이 공존한다.

| 구분 | 위치 | 상태 | LLM | 출력 |
|---|---|---|---|---|
| **실동작 구현** | `cloud_draft/` | 운영 중 | OpenAI gpt-5.4-nano | HWP |
| **설계 구현** | `draft_generator.py` 외 | 실행 전 | Claude API | MD |

작업의 주 대상은 `cloud_draft/`이다. 루트의 `draft_generator.py`, `score_evaluator.py`는 별도 Claude API 기반 파이프라인으로 현재 미실행 상태.

---

## cloud_draft/ 아키텍처

```
survey_form.html  (브라우저 입력 폼)
      ↓  POST /api/generate (JSON)
server.py  (FastAPI)
      ↓  CloudDraft2026.make_draft(survey)
cloud_draft.py
      ├─ _select_templates()   pain_points + goal 키워드 점수화 → 후보 3개 중 랜덤 1개
      ├─ _ctx()                설문 dict → 프롬프트 주입용 텍스트 변환
      ├─ _build_prompt()       섹션별 프롬프트 조립
      ├─ _generate_section()   OpenAI API 병렬 호출 (8섹션)
      ├─ _assemble_hwp_data()  텍스트 + JSON 파싱(as_is_to_be, performance_metrics) + 체크박스 병합
      └─ _write_all_hwp()      template2026.hwp 누름틀 채우기 → outputs/{기업명}/*.hwp
```

### 10종 템플릿 4축

| 축 | 딕셔너리 | 역할 |
|---|---|---|
| A 강조점 | `EMPHASIS_GUIDE` | 섹션 전체 서술 방향 |
| B 서술방식 | `STYLE_GUIDE` | 서술형(단락) vs 구조형(항목 나열) |
| C 논거프레임 | `FRAME_GUIDE` | 문제→해결 / 목적→수단 / AS-IS/TO-BE |
| D-가 | `GA_GUIDE` (α~δ) | 이용목적 소항목 순서·통합 방식 |
| D-나 | `NA_GUIDE` (α~δ) | 이용계획 기능나열/워크플로우/카테고리/1:1매핑 |

선택된 템플릿의 축 값은 `_variation(tmpl)` → `_build_prompt()`로 각 섹션 프롬프트에 주입된다.

### 8개 생성 섹션 (TEXT_SECTIONS)

| 섹션 키 | HWP 필드 | 비고 |
|---|---|---|
| `business_status` | 동일 | 기업 현황 |
| `cloud_service_need` | 동일 | 가-α~δ 구성 적용 |
| `cloud_service_usage_plan_detail` | 동일 | 나-α~δ 구성 적용 |
| `as_is_to_be` | `as_is_status1~3` / `to_be_improvement1~3` | JSON 응답 → 6개 필드 분리 |
| `advanced_consulting_plan_detail` | 동일 | 컨설팅·자립 운영 계획 |
| `expected_effects_of_cloud_adoption` | 동일 | 기대효과 |
| `performance_metrics` | `performance_metric_item1~3` / `_target1~3` | JSON 응답 → 6개 필드 분리 |
| `future_service_usage_plan` | 동일 | 향후 활용 계획 |

---

## 수정 허용 범위

**컨텐츠 생성에 관여하는 부분만** 수정한다.

### 수정 가능 (`cloud_draft/cloud_draft.py`)
- `_ctx()` — 설문 dict → 프롬프트 텍스트 변환. 새 필드 추가 가능.
- `_build_prompt()` — 섹션별 프롬프트 문자열. 지시사항·필드 활용 방식 변경 가능.
- `SYSTEM_PROMPT` — 전역 역할·금지표현 정의. 내용 보완 가능.
- `EMPHASIS_GUIDE`, `STYLE_GUIDE`, `FRAME_GUIDE`, `GA_GUIDE`, `NA_GUIDE`, `SUBTITLE_POOL` — 프롬프트에 주입되는 가이드 텍스트.
- `survey_form.html` — 새 입력 필드 추가 가능 (폼 데이터가 프롬프트로 연결되므로).

### 수정 금지 (`cloud_draft/cloud_draft.py`)
- `server.py` 전체
- `_checkbox_fields()` (HWP 체크박스 매핑)
- `_write_all_hwp()`, `_fill_and_save()`, `_open_hwp()` (HWP 파일 처리)
- `make_draft()`, `_generate_section()` (비동기 실행·API 호출 구조)
- `CloudDraft2026` 클래스 구조, `TEXT_SECTIONS` 목록
- `TEMPLATES`, `_select_templates()`, `_PAIN_MAP`, `_GOAL_MAP` (템플릿 선택 알고리즘)

---

## 설문 스키마

- `survey_schema.json` — v1 기준 스키마 (변경 금지)
- `survey_schema_v2.json` — 기대효과·향후계획 필드 추가 버전

`cloud_draft/test_cloud_draft.py`의 `SURVEY` 딕셔너리가 실제 입력 예시.  
`survey_schema_v2.json` 대비 `cloud_draft/cloud_draft.py`에 아직 미반영된 필드:

| 필드 | 타입 | 반영 대상 섹션 |
|---|---|---|
| `strengths` | 텍스트 | `business_status`, `cloud_service_need` |
| `employees_patent` / `employees_non_patent` | 숫자 | `business_status` |
| `expected_effects` | array (최대 3개) | `expected_effects_of_cloud_adoption` |
| `future_plans` | array (최대 3개) | `future_service_usage_plan` |

이 필드를 반영할 때는 `_ctx()`에 추가하고, 해당 섹션의 `_build_prompt()` 지시사항에 활용 방식을 명시한다.
