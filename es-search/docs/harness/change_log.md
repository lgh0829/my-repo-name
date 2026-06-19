# Harness Change Log

하네스 기준에 영향을 준 변경만 기록한다. 과거 산출 리포트의 내용 변경 이력은 기록하지 않는다.

## 기록 형식

```markdown
## YYYY-MM-DD — [태그]

- 변경:
- 반영 파일:
- 비고:
```

## 2026-06-19 — output_path

- 변경: 로컬 DB와 DB 생성 스크립트를 `output/src_db/`에서 분리했다.
- 반영 파일: `AGENTS.md`, `CLAUDE.md`, `docs/harness/report_format.md`, `docs/harness/es_schema_v2.md`, `docs/harness/app_building.md`, `data/local/README.md`
- 비고: 로컬 DB/빌드 로그는 `data/local/`, DB 생성 스크립트는 `scripts/db/`를 기준 위치로 사용한다.
