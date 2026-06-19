# AGENTS.md — es-search

이 저장소는 Elasticsearch 특허 데이터를 조회해 명세서 작성 스타일을 분석하고, 리포트·CSV·스타일 프롬프트·간단한 뷰어 앱을 만드는 작업 공간이다.

이 파일은 **항상 읽히는 얇은 하네스**다. 세부 규칙은 작업 유형에 맞춰 `docs/harness/*.md`를 추가로 읽는다.

---

## 절대 규칙

- ES에는 조회만 수행한다. `DELETE`, `UPDATE`, 색인 목적 `POST`, 매핑·설정 목적 `PUT` 금지.
- 수치 근거 없는 주관적 평가는 금지한다.
- 불확실한 내용은 `[추정]`으로 표시한다.
- 개인정보, 특히 발명자명(`InventorName` / v2 inventors)은 리포트와 화면에 포함하지 않는다.
- 기존 리포트를 갱신할 때는 새 결론과 충돌하는 구수치를 함께 정정한다.

---

## 작업 시작 체크

작업 시작 전 아래를 확인한다.

- 분석 대상: 출원인 / 사무소명 / 대리인 / CPC / 특정 출원번호
- 분석 목적: 스타일 추출 / 비교 분석 / 프롬프트 생성 / 앱·데이터 생성
- 출력물: markdown 리포트 / CSV / 앱 화면 / 프롬프트
- ES 버전: v2(`patent_*`) / v1(`kr_pub_patents`, `kr_opn_patents`)
- JP 번역 출원 포함 여부

---

## 참조 문서 라우팅

필요한 세부 문서만 읽는다.

| 작업 | 먼저 읽을 문서 |
|---|---|
| 신규 ES(v2) 조회, `patent_*`, 중첩 스키마 | `docs/harness/es_schema_v2.md` |
| 구형 ES(v1) 조회, 기존 리포트 재현 | `docs/harness/es_schema_v1.md` |
| 스타일 분석 기준, JP 제외, CPC 유형, 청구항/본문 축 | `docs/harness/style_analysis_rules.md` |
| Embodiment 전개방식 분석 | `docs/harness/embodiment_analysis.md` |
| C0~C4 본문 스타일 클러스터, 프롬프트 분기 | `docs/harness/body_style_clusters.md` |
| 리포트·스타일 프롬프트 작성 형식 | `docs/harness/report_format.md` |
| 클러스터 뷰어 앱, Streamlit 화면 | `docs/harness/app_building.md` |
| 작업 중 기준 변경 감지, 하네스 반영 후보 정리 | `docs/harness/harness_maintenance.md` |

원본 v2 스키마 문서가 필요하면 `/Users/leegh/Documents/es_field_dictionary.md`를 확인한다.

---

## ES 빠른 구분

### v2 기본값

```env
ES_URL=http://192.168.0.7:9207
ES_USERNAME=elastic
ES_PASSWORD=88888888
ES_INDEX=patent_*
```

v2는 중첩 스키마다. 평탄 필드명으로 직접 쿼리하지 않는다. 가능하면 `scripts/db/build_local_db_v2.py`의 `map_source()`를 경유한다.

### v1 구형

```env
ES_URL=http://192.168.0.163:9204
ES_USERNAME=elastic
ES_PASSWORD=Rx6U8blh53KmWzs1Brnj
ES_INDEX=kr_pub_patents
```

v1은 평탄 스키마다. CPC는 `MainCPC` / `SubCPC`를 사용한다. `IPC_MAIN`, `IPC_SUB`, `CPC_MAIN`, `CPC_SUB`는 분석 필터에 쓰지 않는다.

---

## 산출물 위치

- 리포트: `output/*.md`
- 데이터: `output/*.csv`
- 앱: 저장소 루트 또는 전용 앱 디렉터리
- DB 생성 스크립트: `scripts/db/`
- 로컬 DB/빌드 로그: `data/local/`

---

## 작업 종료 체크

작업 중 ES 기본값, 스키마 해석, 참조 문서 라우팅, 분석 기준, 산출물 위치가 바뀌었으면 `docs/harness/harness_maintenance.md`를 읽고 하네스 반영 후보를 사용자에게 제안한다.
