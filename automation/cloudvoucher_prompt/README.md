# 클라우드바우처 이용계획서 자동 초안 생성 시스템

PatSol(완드) 클라우드바우처 수요기업 이용계획서를 **10가지 변형 초안**으로 자동 생성하고, 선정 기준에 따라 자동 채점하는 파이프라인.

---

## 파일 구조

```
cloudvoucher_prompt/
│
├── README.md                   ← 이 문서
├── PLAN.md                     ← 시스템 설계 명세 (설문 설계·템플릿 전략·평가 기준)
│
├── draft_generator.py          ← [실행 1] 초안 생성기 (Claude API 기반)
├── score_evaluator.py          ← [실행 2] 자동 채점·갭분석기 (Claude API 기반)
│
├── survey_schema.json          ← 설문 입력 스키마 (필드 정의 + 예시)
├── survey_gonggan.json         ← 특허법인 공간 샘플 설문 (즉시 실행 가능)
│
├── base_content.md             ← 핵심 논거 풀 (섹션별 표현 변형 풀 포함)
│
├── templates/
│   ├── template_01.json        ← T01: 업무효율, 서술형, 문제→해결
│   ├── template_02.json        ← T02: 비용절감, 구조형, 문제→해결
│   ├── template_03.json        ← T03: 보안, 서술형, 목적→수단
│   ├── template_04.json        ← T04: 경쟁력, 구조형, AS-IS/TO-BE
│   ├── template_05.json        ← T05: 성장잠재력, 서술형, 목적→수단
│   ├── template_06.json        ← T06: 업무효율, 구조형, AS-IS/TO-BE
│   ├── template_07.json        ← T07: 보안+비용, 서술형, 문제→해결
│   ├── template_08.json        ← T08: 경쟁력+효율, 구조형, 목적→수단
│   ├── template_09.json        ← T09: 성장잠재력, 서술형, AS-IS/TO-BE
│   └── template_10.json        ← T10: 비용+보안, 구조형, 문제→해결
│
├── outputs/                    ← 생성 결과 (자동 생성)
│   └── {기업명}/
│       ├── draft_T01.md ~ draft_T10.md     ← 초안 10종
│       ├── evaluation_report.md            ← 10종 점수 비교 + 순위
│       └── eval_T01.md ~ eval_T10.md       ← 템플릿별 상세 평가
│
└── cloud_draft.py              ← (구버전, 참고용)
```

---

## 실행 준비

### 1. 패키지 설치

```bash
pip3 install anthropic
```

### 2. API 키 설정

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 실행 방법

### Step 1 — 초안 생성

```bash
cd ~/cc-workspace/automation/cloudvoucher_prompt

# 샘플 (특허법인 공간) 전체 10종 생성
python3 draft_generator.py --survey survey_gonggan.json

# 특정 템플릿만 생성
python3 draft_generator.py --survey survey_gonggan.json --templates T01,T03,T05

# 출력 디렉토리 지정
python3 draft_generator.py --survey survey_gonggan.json --output-dir /path/to/dir
```

**소요 시간**: 전체 10종 약 5~10분 (섹션별 병렬 호출, 템플릿 간 순차 처리)

**출력물**: `outputs/특허법인_공간/draft_T01.md ~ draft_T10.md`

---

### Step 2 — 자동 채점 및 갭 분석

```bash
# Step 1 완료 후 실행
python3 score_evaluator.py --company 특허법인_공간

# 특정 템플릿만 평가
python3 score_evaluator.py --company 특허법인_공간 --templates T01,T03

# 단일 파일 평가
python3 score_evaluator.py --draft outputs/특허법인_공간/draft_T01.md
```

**출력물**:
- `evaluation_report.md` — 10종 점수 비교표 + 순위 (총점 → ❸항목 동점 기준)
- `eval_T01~T10.md` — 근거 인용 + 개선 방향 상세 리포트

---

## 새 기업 신청서 생성

`survey_schema.json`의 `examples` 배열을 참고하여 새 설문 JSON 파일 작성.

```bash
cp survey_gonggan.json survey_새기업.json
# 파일 편집 후:
python3 draft_generator.py --survey survey_새기업.json
```

### 필수 입력 필드

| 필드 | 유형 | 설명 |
|---|---|---|
| `company_name` | 텍스트 | 기업명 |
| `main_work` | 텍스트 | 주요 업무 2~3문장 |
| `strengths` | 텍스트 | 기업 강점 |
| `employees_patent` | 숫자 | 변리사·보조 인원 |
| `employees_non_patent` | 숫자 | 비변리 인원 |
| `pain_points_rank` | `{first, second}` | 문제점 1·2순위 |
| `goal_rank` | `{first, second}` | 목표 1·2순위 |
| `cloud_current_state` | enum | 클라우드 현재 사용 현황 |
| `cloud_purpose` | enum | 사용 목적 |
| `cloud_readiness` | enum | 전환 준비도 |
| `cloud_method` | enum | 도입 방식 |
| `cloud_timeline` | enum | 도입 예정 시기 |
| `it_staff` | enum | IT 담당 인원 |
| `data_management` | enum | 데이터 관리 방식 |
| `it_asset_scale` | enum | IT 자산 규모 |

선택 필드(`key_customers`, `cloud_budget`, `revenue_scale`, `current_tools`, `specific_concerns`)는 결과물 다양성 향상에 활용됨.

---

## 평가 기준 (선정 배점)

| 항목 | 배점 | 동점시 우선순위 |
|---|:---:|:---:|
| ❶ 지원 필요성 | 20점 | 3 |
| ❷ 서비스 이용 계획의 적절성 | 30점 | 2 |
| ❸ 디지털 전환 및 선도사례 가능성 ★ | 30점 | **1 (최우선)** |
| ❹ 기대효과 | 20점 | 4 |

> ❸ 중 **AI 접목 서비스 및 산업도메인 특화 서비스 활용도** 항목이 우대 기준.
> 모든 초안에 "유사도 기반 벡터 검색", "IP 특화", "AI 보조 → 변리사 확정" 표현이 포함됨.

---

## 템플릿 10종 요약

| 템플릿 | 강조점 | 서술 방식 | 논거 프레임 |
|---|---|---|---|
| T01 | 업무효율 | 서술형 | 문제→해결 |
| T02 | 비용절감 | 구조형 | 문제→해결 |
| T03 | 보안 | 서술형 | 목적→수단 |
| T04 | 경쟁력 | 구조형 | AS-IS/TO-BE |
| T05 | 성장잠재력 | 서술형 | 목적→수단 |
| T06 | 업무효율 | 구조형 | AS-IS/TO-BE |
| T07 | 보안+비용 | 서술형 | 문제→해결 |
| T08 | 경쟁력+효율 | 구조형 | 목적→수단 |
| T09 | 성장잠재력 | 서술형 | AS-IS/TO-BE |
| T10 | 비용+보안 | 구조형 | 문제→해결 |
