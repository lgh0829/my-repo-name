# ES v2 Schema Harness (`patent_*`)

원본 스키마 문서: `/Users/leegh/Documents/es_field_dictionary.md`

신규 ES(v2)는 중첩 스키마다. 평탄 필드명(`ApplicationNumber`, `Title`, `MainCPC` 등)으로 직접 쿼리하지 않는다.

## 접속 정보

```env
ES_URL=http://192.168.0.7:9207
ES_USERNAME=elastic
ES_PASSWORD=88888888
ES_INDEX=patent_*
```

## 전체 구조

```text
특허 문서 1건
├── application_id
├── metadata
├── status_history[]
└── documents
    ├── PUBLICATION
    └── GRANT
        └── versions[]
```

## 루트 / 메타데이터

| 용도 | v2 필드 | 비고 |
|---|---|---|
| 시스템 출원 ID | `application_id` | keyword |
| 국가 | `metadata.country` | keyword |
| 출원번호 | `metadata.application_number` | keyword |
| 출원일 | `metadata.application_date` | date, `yyyyMMdd` |
| 현재 상태 | `metadata.current_status` | 등록/공개/포기 등 |

## 상태 이력

| 용도 | v2 필드 |
|---|---|
| 상태 변경일 | `status_history[].date` |
| 이벤트 코드 | `status_history[].event_code` |
| 이벤트 설명 | `status_history[].description` |

## 공개 문서 (`documents.PUBLICATION`)

| 용도 | v2 필드 |
|---|---|
| 공개번호 | `documents.PUBLICATION.publication_id` |
| 공개일 | `documents.PUBLICATION.open_date` |
| 발명의 명칭 | `documents.PUBLICATION.inventiontitle` |
| 출원인 원문명 | `documents.PUBLICATION.parties.applicants[].name_raw` |
| 출원인 정규명 | `documents.PUBLICATION.parties.applicants[].name` |
| 발명자명 | `documents.PUBLICATION.parties.inventors[].name` — 리포트 표시 금지 |
| 대리인명 | `documents.PUBLICATION.parties.agents[].name` |
| CPC 클래스 | `documents.PUBLICATION.classifications.cpc.class` |
| CPC 메인그룹 | `documents.PUBLICATION.classifications.cpc.main_group` |
| CPC 서브그룹 | `documents.PUBLICATION.classifications.cpc.sub_group` |
| IPC 클래스 | `documents.PUBLICATION.classifications.ipc.class` |
| IPC 메인그룹 | `documents.PUBLICATION.classifications.ipc.main_group` |
| IPC 서브그룹 | `documents.PUBLICATION.classifications.ipc.sub_group` |

## 공개 문서 본문 섹션

`inventiontitle`과 `drawings`를 제외한 본문 섹션은 `{ p_number, text }` 구조다. 분석용 텍스트는 `*.text`를 문단 순서대로 이어 붙인다.

| v1 평탄 필드 대응 | v2 필드 |
|---|---|
| `Summary` | `documents.PUBLICATION.abstract.text` |
| `TechnicalField` | `documents.PUBLICATION.technical_field.text` |
| `Background` | `documents.PUBLICATION.background_art.text` |
| `Disclosure` | `documents.PUBLICATION.disclosure.text` |
| `Problem` | `documents.PUBLICATION.technicalproblem.text` |
| `SolutionProblem` | `documents.PUBLICATION.technicalsolution.text` |
| `Effects` | `documents.PUBLICATION.advantageouseffects.text` |
| `BriefDescriptionOfDrawings` | `documents.PUBLICATION.drawingdescription.text` |
| `Embodiment` | `documents.PUBLICATION.embodimentdescription.text` |
| 부호의 설명 | `documents.PUBLICATION.referencesignbag.text` |
| `Claims` | `documents.PUBLICATION.claims[].text` (`claim_number` 포함) |
| 도면 파일명 | `documents.PUBLICATION.drawings[].file_name` (검색 비대상) |

## 등록 문서 (`documents.GRANT`)

| 용도 | v2 필드 |
|---|---|
| 등록번호 | `documents.GRANT.grant_id` |
| 등록일 | `documents.GRANT.grant_date` |
| 공고일 | `documents.GRANT.publication_date` |
| 등록 버전 번호 | `documents.GRANT.versions[].version` |
| 등록 버전 기준일 | `documents.GRANT.versions[].version_date` |
| 등록 버전 비고 | `documents.GRANT.versions[].remarks` |

`documents.GRANT.versions[]` 내부의 `parties`, `classifications`, 본문 섹션 구조는 `documents.PUBLICATION`과 동일하다.

## 문서 선택 원칙

- 출원 공개 기준 분석: `documents.PUBLICATION` 우선.
- 등록 후 유효 명세서 분석: `documents.GRANT.versions[]` 중 최신 `version` 또는 최신 `version_date` 우선.
- 공개/등록 중 어느 문서를 썼는지 리포트에 명시한다.
- 직접 ES 쿼리보다 `scripts/db/build_local_db_v2.py`의 `map_source()` 매핑 로직을 우선 사용한다.
