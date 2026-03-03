---
aliases:
  - PatSol 특허 검색 IA 흐름도 v0.1
작성일: 2026-03-03
수정일: 2026-03-03
상태: 초안
tags:
  - spec
  - search
  - wip
관련문서:
  - "[[ia_spec-v0.1]]"
  - "[[wireframe-ascii]]"
상위문서: "[[ia_spec-v0.1]]"
---

# PatSol 특허 검색 IA 흐름도 (v0.1)

> 원본: [[ia_spec-v0.1]] · [[wireframe-ascii]]
> 범위: 검색 방식 선택 → 검색 입력 → 검색 결과 전체

---

```mermaid
flowchart TD
    START([사용자 진입]) --> MODE{검색 방식 선택}

    %% ── 자연어 검색 분기 ──────────────────────────────────────
    MODE -->|자연어 검색| IMPORT_Q{문서 Import?}

    IMPORT_Q -->|Y| UPLOAD["2.1 문서 업로드
    직무발명서 · 도면 · 회의록 · 기타
    .pdf · .doc · .hwp 등"]
    UPLOAD --> EXTRACT[AI 텍스트 · 이미지 추출]
    EXTRACT -->|검색창 자동 채움| NL_INPUT

    IMPORT_Q -->|N| NL_INPUT["2.2.2 자연어 입력
    자유 서술 또는
    청구항 문장 붙여넣기"]

    NL_INPUT --> SUFFICIENCY{"AI 충분도 판단
    2.2.2.2
    기술 키워드 2개 이상
    + 목적/문제 맥락"}

    %% ── 경로 A ────────────────────────────────────────────────
    SUFFICIENCY -->|"충분 → 경로 A"| VDB_A["Vector DB 검색 Top 50"]

    %% ── 경로 B : Q&A 폼 (B-1 화면) ───────────────────────────
    SUFFICIENCY -->|불충분| CLUSTER["클러스터링
    상위 토픽 자동 생성
    2.2.2.4"]
    CLUSTER --> QA_FORM["B-1  토픽 Q&A 폼
    2.2.2.5"]

    QA_FORM --> QA_CHOICE{"입력 방식 선택"}
    QA_CHOICE -->|"토픽 칩 선택
    기술 단계 · 냉각 방식 등"| QA_SUBMIT[조건 제출]
    QA_CHOICE -->|"직접 텍스트 입력"| QA_SUBMIT
    QA_CHOICE -->|"선택 없이 그냥 검색"| VDB_B

    QA_SUBMIT --> EST{"예상 건수 확인"}
    EST -->|"50건 이하 → 경로 B-1"| VDB_B["Vector DB 검색 Top 50"]
    EST -->|"50건 초과 → 경로 B-2"| FILTER["2.2.2.7  필터 / 검색식 보강
    출원일 · 출원인 · IPC 코드
    또는 직접 검색식 입력"]
    FILTER --> VDB_B

    %% ── 자연어 A/B 결과 화면 통합 ────────────────────────────
    VDB_A --> RESULT_NL
    VDB_B --> RESULT_NL["결과 화면 (A / B-1 / B-2 통합)
    · 유사도 %
    · AI 추천 토픽 카드 (검색 결과 기반 생성)
    · 조건별 분포
    · 등록 상태 뱃지
    챗봇 패널(우): 자연어 요약"]

    %% ── 검색식 검색 분기 ──────────────────────────────────────
    MODE -->|검색식 검색| QUERY_INPUT["2.2.1 상세 검색식 입력
    키프리스 · 심사관 시점 · 자체 문법
    Boolean · CPC 코드
    대분류/소분류 드롭다운 포함"]

    QUERY_INPUT --> SYNTAX{"문법 오류 감지
    2.2.1.3"}
    SYNTAX -->|오류 없음| ES["Elastic Search 실행"]
    SYNTAX -->|오류 있음| SUGGEST["수정 제안
    원문 ↔ 수정안 병렬 표시
    Query Builder Assistant"]
    SUGGEST --> APPROVE{"사용자 승인?"}
    APPROVE -->|"수정안으로 검색"| ES
    APPROVE -->|"원문 그대로 검색"| ES

    ES --> RESULT_Q["결과 화면 (검색식)
    · 조건별 분포
    · 등록 상태 뱃지
    챗봇 패널(우): 실행된 검색식
    · 유사도 % 없음
    · AI 추천 토픽 카드 없음"]

    %% ── 2.3 검색 결과 공통 합류 ───────────────────────────────
    RESULT_NL --> RESULT_ENTRY
    RESULT_Q --> RESULT_ENTRY

    subgraph RESULT_SECTION["2.3 검색 결과 (공통 기능)"]
        RESULT_ENTRY["검색 결과 진입
        건수 · 경로 레이블 · 조건 칩"]

        %% 2.3.1 채팅
        RESULT_ENTRY --> CHAT["2.3.1 채팅
        컨텍스트: 현재 세션만"]
        CHAT --> NEW["새 주제 시작하기
        세션 종료 · 히스토리 보존"]
        CHAT --> FOLLOW["이어서 질문하기
        현재 세션 맥락 유지"]
        FOLLOW --> FOLLOWUP[후속 질문 입력]
        FOLLOWUP --> INTENT{"AI 의도 구분"}
        INTENT -->|"분석/요약형"| CHAT_RESP["채팅 응답
        결과 변경 없음"]
        INTENT -->|"검색 범위 조정형"| SEARCH_CTA["검색 범위 조정 CTA 제시
        '이 조건으로 다시 검색 →'"]
        SEARCH_CTA --> USER_OK{"사용자 확인?"}
        USER_OK -->|확인| RESULT_ENTRY
        USER_OK -->|취소| CHAT_RESP

        %% 2.3.2 검색 결과 조회
        RESULT_ENTRY --> VIEW["2.3.2 검색 결과 조회
        정렬: 유사도순(기본) · 출원일순 · 출원인순
        표시: 페이지네이션 (단위 설정 가능)"]
        VIEW --> TFILT["토픽 기반 필터링
        AI 추천 토픽 카드 선택"]
        VIEW --> QFILT["검색식 기반 필터링
        Boolean/CPC 조건 추가
        (Query Builder Assistant 적용)"]
        VIEW --> CNT["검색 건수 조회
        실시간 표시"]
        VIEW --> DET["특허 상세 조회
        청구항 · 도면 · 출원 이력
        챗봇 요약 · 유사/차이점 분석"]

        %% 2.3.3 분석 대상 문서 담기
        RESULT_ENTRY --> BASKET["2.3.3 분석 대상 문서 담기"]
        BASKET --> BADD["문서 추가
        결과에서 담기 또는
        출원번호 직접 입력"]
        BASKET --> BREM["문서 제외
        개별 또는 일괄"]
        BASKET --> RPT["분석 리포트 생성
        검색 의도 요약[1]
        공통점 · 차이점 · 비교표
        PDF 내보내기"]
        BASKET --> BDET["문서 상세 조회
        챗봇 요약 · 유사/차이점 분석"]
    end

    NEW -->|세션 종료 · 히스토리 보존| START

    %% 스타일
    style RESULT_SECTION fill:#f0f4ff,stroke:#6b7dbd
    style RESULT_NL fill:#e8f5e9,stroke:#388e3c
    style RESULT_Q fill:#e8f5e9,stroke:#388e3c
    style QA_FORM fill:#fff8e1,stroke:#fbc02d
    style SUFFICIENCY fill:#e3f2fd,stroke:#1976d2
    style EST fill:#e3f2fd,stroke:#1976d2
    style SYNTAX fill:#fce4ec,stroke:#e91e63
    style APPROVE fill:#fce4ec,stroke:#e91e63
    style QA_CHOICE fill:#e3f2fd,stroke:#1976d2
    style INTENT fill:#e3f2fd,stroke:#1976d2
    style USER_OK fill:#fce4ec,stroke:#e91e63
```

---

## 결과 화면 비교

| 구분 | 자연어 A / B-1 / B-2 (통합) | 검색식 |
|---|---|---|
| 레이아웃 | 검색결과(좌) · 사이드바(우: 분석대상+채팅) | 동일 |
| 검색 헤더 | 입력 쿼리 요약 | 실행된 검색식 |
| 챗봇 패널 검색 의도 | 자연어 요약 (Q&A 대화 맥락 포함) | 실행된 검색식 |
| 유사도 % | 있음 | 없음 |
| AI 추천 토픽 카드 | 있음 (검색 결과 기반 생성) | 없음 |
| 조건별 분포 | 있음 | 있음 |
| 등록 상태 뱃지 | 있음 | 있음 |
| 선행기술로 저장 | 있음 | 있음 |

## 경로 진입 조건 요약

| 경로 | 진입 조건 | 검색 엔진 | spec 항목 |
|---|---|---|---|
| 검색식 | 검색식 직접 입력 | Elastic Search | 2.2.1 |
| 경로 A | 자연어 충분 | Vector DB Top 50 | 2.2.2.2 → 2.2.2.3 |
| 경로 B-1 | 자연어 불충분 → 토픽 선택 → 예상 50건 이하 | Vector DB Top 50 | 2.2.2.4 → 2.2.2.6 |
| 경로 B-2 | 자연어 불충분 → 토픽 선택 → 예상 50건 초과 | Vector DB Top 50 | 2.2.2.7 → 2.2.2.6 |

## OQ 결정 현황

| OQ | 상태 | 결정 내용 |
|---|---|---|
| OQ-1 | ✅ 결정 | 검색창 자동 채움 (현행 서비스) |
| OQ-2 | ✅ 결정 | 대분류/소분류 드롭다운 포함 |
| OQ-3 | ✅ 결정 | 현재 세션만 |
| OQ-3a | ✅ 결정 | AI가 후속 질문 의도 구분 → 검색 범위 조정형이면 CTA 제시 → 사용자 확인 후 결과 재진입 |
| OQ-4 | ✅ 결정 | 정렬 옵션 포함, 유사도순 디폴트 |
| OQ-5 | ✅ 결정 | 페이지네이션 (단위 설정 가능) |
| OQ-6 | ✅ 결정 | PDF 내보내기 |
