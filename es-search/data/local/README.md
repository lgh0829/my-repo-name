# patents_local.db — 스키마 문서

> 파일 경로: `es-search/data/local/patents_local.db`
> 생성일: 2026-06-10
> 레코드 수: 3,192건 전수 / 195.2 MB
> 출처 인덱스: `kr_pub_patents` + `kr_opn_patents` (두 인덱스 합산, pub 우선)

---

## 테이블 구성

```
patents_local.db
├── patents              ← 메타데이터 + 짧은 필드
├── patents_embodiment   ← Embodiment 전문 (대용량 분리)
└── patents_parsed       ← 사전 파싱 세그먼트 (향후 분석용)
```

---

## `patents` — 메타데이터 + 짧은 필드

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `application_number` | TEXT PK | 출원번호 |
| `index_name` | TEXT | `kr_pub_patents` 또는 `kr_opn_patents` |
| `title` | TEXT | 발명의 명칭 |
| `applicant_name` | TEXT | 출원인 |
| `agent_names` | TEXT | 대리인 (¶ 구분) |
| `main_cpc` | TEXT | 주 CPC 분류코드 |
| `sub_cpc` | TEXT | 부 CPC 분류코드 |
| `application_date` | TEXT | 출원일 |
| `open_number` | TEXT | 공개번호 |
| `open_date` | TEXT | 공개일 |
| `register_number` | TEXT | 등록번호 |
| `register_date` | TEXT | 등록일 |
| `technical_field` | TEXT | 기술분야 섹션 |
| `background` | TEXT | 배경기술 |
| `problem` | TEXT | 해결하려는 과제 |
| `solution_problem` | TEXT | 과제의 해결 수단 |
| `effects` | TEXT | 발명의 효과 |
| `brief_description` | TEXT | 도면의 간단한 설명 |
| `claims` | TEXT | 청구항 전문 (¶ 구분) |
| `summary` | TEXT | 요약 |

**인덱스**: `main_cpc`, `agent_names`, `application_date`

---

## `patents_embodiment` — 대용량 실시예 분리

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `application_number` | TEXT PK → FK | 출원번호 |
| `embodiment` | TEXT | 발명을 실시하기 위한 구체적인 내용 전문 |
| `embodiment_len` | INTEGER | 글자 수 |

---

## `patents_parsed` — 사전 파싱 세그먼트 (향후 분석용)

| 컬럼 | 타입 | 설명 | 향후 용도 |
|---|---|---|---|
| `application_number` | TEXT PK → FK | 출원번호 | |
| `emb_intro` | TEXT | Embodiment 첫 문단 (최대 800자) | 도입 정형구 유형 분류 |
| `emb_tail` | TEXT | Embodiment 마지막 문단 (최대 800자) | 말미 면책 유형 분류 |
| `emb_para_count` | INTEGER | Embodiment 단락 수 | 밀도 측정 |
| `bg_intro` | TEXT | Background 첫 문단 (최대 500자) | 배경기술 서술 패턴 |
| `bg_has_patent_cite` | INTEGER | 선행기술 특허문헌 인용 여부 (0/1) | A/B/C 클러스터 판별 |
| `prob_first_sent` | TEXT | Problem 첫 문장 (최대 300자) | 과제 어법 직접/간접 분류 |
| `claims_count` | INTEGER | 청구항 수 | 독립항 전략 분석 |
| `claims_first` | TEXT | 독립항1 전문 (최대 600자) | 발명 카테고리·구조 파악 |

---

## 기본 쿼리 예시

```sql
-- 3테이블 JOIN
SELECT p.application_number, p.title, p.main_cpc,
       e.embodiment_len,
       pp.emb_para_count, pp.bg_has_patent_cite, pp.claims_count
FROM patents p
JOIN patents_embodiment e USING(application_number)
JOIN patents_parsed pp USING(application_number)
LIMIT 10;

-- 도입 정형구 유형별 분포
SELECT
    CASE
        WHEN emb_intro LIKE '%권리범위가 제한되는 것은 아니다%' THEN '유형A 발명특정형'
        WHEN emb_intro LIKE '%이점 및 특징%'                   THEN '유형B 일반면책형'
        WHEN emb_intro LIKE '%실시예에 불과%'                  THEN '유형C 보일러플레이트형'
        WHEN emb_intro LIKE '%이하에서는%'                     THEN '유형D 국내표준형'
        ELSE '기타'
    END AS intro_type,
    COUNT(*) AS cnt
FROM patents_parsed
GROUP BY intro_type ORDER BY cnt DESC;

-- 선행기술 인용 여부별 분포 (A/B/C 클러스터)
SELECT bg_has_patent_cite, COUNT(*) FROM patents_parsed GROUP BY bg_has_patent_cite;

-- 특정 대리인 출원 조회
SELECT application_number, title, main_cpc, application_date
FROM patents
WHERE agent_names LIKE '%리앤목특허법인%'
ORDER BY application_date DESC
LIMIT 20;
```

---

## 관련 파일

| 파일 | 설명 |
|---|---|
| `../../scripts/db/build_local_db.py` | DB 생성 스크립트 (ES → SQLite) |
| `../../scripts/db/build_local_db_v2.py` | v2 ES DB 생성 스크립트 (ES → SQLite) |
| `build_db_log.txt` | 빌드 로그 |
| `../../output/disclaimer_anchor_dimensions.csv` | 32개 컬럼 측정값 (3,192건, DB와 동일 출원번호) |
