# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 역할

이 저장소는 Elasticsearch에 저장된 특허 데이터를 쿼리하고 명세서 작성 스타일을 분석하여 인사이트 리포트와 스타일 프롬프트를 생성하는 에이전트 워크스페이스다.

분석 결과는 참고 자료이며, 최종 스타일 판단은 변리사가 한다.

---

## 인덱스 필드 목록 (kr_pub_patents) — 확인된 실제 필드명

> **쿼리 작성 전 반드시 이 목록을 참조한다. 아래에 없는 필드명은 사용하지 않는다.**

| 필드명 | 타입 | 설명 | 주의 |
|---|---|---|---|
| `ApplicationNumber` | keyword | 출원번호 (예: 1020230012647) | term 쿼리 사용 |
| `OpenNumber` | keyword | 공개번호 | — |
| `RegisterNumber` | keyword | 등록번호 | — |
| `ApplicationDate` | date | 출원일 | range 쿼리 사용 |
| `OpenDate` | date | 공개일 | — |
| `RegisterDate` | date | 등록일 | — |
| `Title` | text | 발명의 명칭 | match/match_phrase |
| `ApplicantName` | text | 출원인명 | match_phrase 권장 |
| `AgentNames` | text | 대리인(변리사/법인)명. `¶`로 복수 구분 | **사무소 전체명은 match_phrase 필수** (예: "리앤목특허법인"). 개인 변리사명은 match 가능 (예: "장수길") |
| `AttorneyName` | text | 담당 변리사명 | — |
| `InventorName` | text | 발명자명 | 개인정보 — 리포트 포함 금지 |
| `MainCPC` | text | 주 CPC 분류코드 (예: H01L21/67) | **`CPC_MAIN` `IPC_MAIN`은 존재하지 않음** |
| `SubCPC` | text | 부 CPC 분류코드 | **`CPC_SUB` `IPC_SUB`는 존재하지 않음** |
| `IPC_MAIN` | keyword | 주 IPC 분류코드 | 실제로는 비어 있는 경우 많음 — 기술 분야 필터는 `MainCPC` 우선 사용 |
| `IPC_SUB` | keyword | 부 IPC 분류코드 | 동상 |
| `Claims` | text | 청구항 전문. **`¶`로 청구항 구분** | — |
| `TechnicalField` | text | 기술분야 섹션 | — |
| `Background` | text | 배경기술 섹션 | — |
| `Embodiment` | text | 발명을 실시하기 위한 구체적인 내용 | — |
| `SolutionProblem` | text | 과제 해결 수단 | **사무소 편차 큼** (김앤장 50% / jang·leeandmok 0%). 횡단 비교 부적합 |
| `Problem` | text | 해결하려는 과제 | **실측 94~100% 채움** (평균 191~449자). 과제 제기 어법 분석에 사용 |
| `Effects` | text | 발명의 효과 | **실측 65~99% 채움** (평균 160~383자). 채움률 자체가 사무소 시그널 |
| `BriefDescriptionOfDrawings` | text | 도면의 간단한 설명 | — |
| `Summary` | text | 요약 | — |
| `Keyword` | text | 키워드 | — |
| `Disclosure` | text | 공개 전문 | — |
| `PatentLiterature` | text | 인용 특허문헌 | — |
| `PriorityApplicationNumber` | text | 우선권 출원번호 | — |
| `PriorityCountry` | text | 우선권 국가 | — |
| `PriorityFilingDate` | text | 우선권 출원일 | — |
| `SourceFile` | text | 원본 파일 경로 | — |
| `DocumentType` | text | 문서 유형 | — |
| `image` | text | 이미지 정보 | — |

### ❌ 절대 사용 금지 필드명 (존재하지 않거나 항상 비어 있음)

```
IPC_MAIN  →  MainCPC 로 대체
IPC_SUB   →  SubCPC  로 대체
CPC_MAIN  →  MainCPC 로 대체
CPC_SUB   →  SubCPC  로 대체
```

---

## 환경 설정

### .env 구조

프로젝트 루트에 `.env` 파일을 생성한다. `.env.example`이 없으므로 아래를 기준으로 작성한다.

```env
# Elasticsearch 접속 정보
ES_URL=http://192.168.0.163:9204
ES_USERNAME=elastic
ES_PASSWORD=Rx6U8blh53KmWzs1Brnj

# 분석 대상 인덱스
ES_INDEX=kr_pub_patents
```

`.env`는 절대 커밋하지 않는다.

---

## 작업 흐름

### 1단계: 목적 파악

작업 시작 전 반드시 아래를 확인한다. 불명확하면 가정하지 말고 질문한다.

- **분석 대상**: 출원인 / 사무소명 / 기술 분야(CPC 코드)
- **분석 목적**: 스타일 추출 / 트렌드 파악 / 비교 분석
- **출력 형태**: 인사이트 리포트 / 스타일 프롬프트 / 둘 다

### 2단계: Elasticsearch 쿼리

> **[절대 금지]** Elasticsearch에 대해 `DELETE`, `UPDATE`, `POST`(색인·업데이트 목적), `PUT`(매핑·설정 변경 목적) 등 데이터 변경·삭제와 관련된 쿼리는 어떠한 경우에도 실행하지 않는다. 오직 `GET` 기반 조회 쿼리만 허용된다.

쿼리 실행 전 항상 인덱스 매핑을 먼저 확인한다.

```
GET /kr_pub_patents/_mapping
```

#### 출원인별 특허 수집

```json
GET /kr_pub_patents/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "AgentNames": "{{사무소명}}" } },
        { "range": { "ApplicationDate": { "gte": "{{시작일}}", "lte": "{{종료일}}" } } }
      ]
    }
  },
  "_source": ["ApplicationNumber", "Title", "Claims", "Embodiment", "Background",
              "AgentNames", "ApplicantName", "ApplicationDate", "MainCPC", "SubCPC"],
  "size": 50,
  "sort": [{ "ApplicationDate": "desc" }]
}
```

#### 기술 분야 필터 (CPC 기준)

```json
GET /kr_pub_patents/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "AgentNames": "{{사무소명}}" } },
        { "match_phrase_prefix": { "MainCPC": "{{CPC 분류코드}}" } }
      ]
    }
  },
  "_source": ["ApplicationNumber", "Title", "Claims", "Embodiment", "MainCPC"],
  "size": 30
}
```

#### AgentNames 쿼리 방식

```
법인명 전체 (예: 리앤목특허법인)  →  match_phrase 필수
  { "match_phrase": { "AgentNames": "리앤목특허법인" } }

개인 변리사명 (예: 장수길)        →  match 가능
  { "match": { "AgentNames": "장수길" } }
```

#### 쿼리 후 검증 체크리스트

- `hits.total.value`가 예상 범위인가
- 빈 필드가 많은 문서는 분석 제외
- 샘플 3건을 먼저 출력해서 데이터 품질 확인
- 결과가 비어 있으면 조건 완화 전에 사용자에게 알린다

### 3단계: 스타일 분석 항목

**(A) 청구항 축**

| 항목 | 분석 내용 |
|---|---|
| 청구항 구조 | 독립항 수, 종속항 수, 평균 청구항 길이 |
| 독립항 전략 | 출원 단위 전략 패턴 분류 (장치단독/순수형/3-way 등). 종속항이 독립항 카테고리를 상속하므로 **말미 총량 통계로 전략을 해석하지 말 것** |
| 표현 방식 | 기능적 vs 구조적 표현 비율, 자주 쓰는 연결어 |
| 도면 참조 방식 | 괄호형 `(10)` / 인라인형 `도면 10` / 미참조 |
| 구성요소 기재 방식 | 한 청구항 묶음형 vs 종속항 분리형 |

**(B) 명세서 본문 축** (검증된 변별력 항목만)

| 항목 | 분석 내용 | 측정 필드 | 변별력 |
|---|---|---|---|
| 선행기술 인용 방식 | 특허문헌 인용 vs 문제만 서술 | `Background` | 극강 (10~84%) |
| 과제 제기 어법 | 직접("문제가 있었다") vs 간접("요구된다") | `Problem`+`Background` | 강 |
| 실시예 구조 | "제N실시예" 마커 → 복수/단일 분류 | `Embodiment` | 강 (복수 3~23%) |
| 효과 표현 방식 | 효과 섹션 채움률 + 정성표현률 | `Effects` | 중 |
| 발명의 설명 밀도 | 청구항 대비 설명 분량 비율, 실시예 개수 | `Embodiment` | 중 |
| 언어 패턴 | 자주 쓰는 표현, 특이한 문체 | 전체 | 사무소별 |

> ❌ **변별력 없어 제외**: 도면 연계 밀도(세 사무소 15±1회/1000자), 효과 수치표현(3% 동일)
> ⚠️ **횡단 비교 불가**: 과제해결수단(`SolutionProblem`) mirror율 — jang·leeandmok 0% 채움

- 표본 10건 미만이면 신뢰도 낮음을 명시한다
- CPC 분류별로 나눠서 분석한다 (필드: `MainCPC`)
- 수치는 평균과 범위를 함께 제시한다 (예: 독립항 평균 2.3개, 범위 1~5개)

### 4단계: 인사이트 리포트 구조

```
# [분석 대상] 명세서 스타일 분석 리포트

## 요약
- 분석 기간:
- 분석 건수:
- 핵심 스타일 특성 3줄 요약

## 데이터 개요
- 수집 쿼리 조건
- 유효 문서 수 / 제외 문서 수 및 사유

## 스타일 분석 결과
### 청구항 구조
### 표현 방식
### 도면 참조 방식
### 구성요소 기재 방식
### 발명의 설명 밀도
### 언어 패턴

## 인사이트
- 이 스타일의 강점
- 다른 스타일과의 차이점
- 특이 패턴 또는 주의사항

## 스타일 프롬프트

## 부록: 분석 특허 번호 목록
```

작성 원칙: 수치 근거 없는 주관적 평가 금지. 불확실한 내용은 `[추정]` 태그를 붙인다.

### 5단계: 스타일 프롬프트 구조

```
## 명세서 작성 스타일 지침 — [스타일명]

### 청구항 작성 규칙
- 독립항은 [N]개를 기본으로 한다
- 종속항은 독립항당 평균 [N]개로 구성한다
- [구체적 표현 패턴 예시]

### 표현 방식
- [기능적/구조적] 표현을 우선한다
- 자주 쓰는 연결어: [예시 목록]
- 피해야 할 표현: [예시 목록]

### 도면 참조
- [괄호형/인라인형] 방식 사용
- 예시: [실제 예시]

### 구성요소 기재
- [묶음형/분리형] 방식 사용
- 예시 청구항 구조: [실제 예시]

### 발명의 설명
- 실시예는 [N]개를 기본으로 한다
- 설명 밀도: [상세/표준/간결]

### 금지 사항
- [이 스타일에서 쓰지 않는 표현이나 구조]
```

프롬프트 길이는 500~1000자 이내로 유지한다.

---

## 출력 규칙

- 리포트는 마크다운으로 작성한다
- 수치 테이블은 마크다운 테이블 사용
- 쿼리·프롬프트는 코드 펜스로 감싼다
- 데이터 기반 사실과 해석은 시각적으로 구분한다
- 개인정보(발명자 이름, 주소 등)는 리포트에 포함하지 않는다
