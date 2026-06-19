# Harness Maintenance

작업 중 분석 방향이나 운영 기준이 바뀌었을 때 하네스를 오염시키지 않으면서 다음 작업에 반영하기 위한 규칙이다.

## 언제 확인하는가

작업 종료 전에 아래 중 하나라도 발생했는지 확인한다.

- ES 기본 서버, 인덱스, 인증, 스키마 기본값 변경
- 필드명, 중첩 구조, 매핑 함수 등 데이터 해석 변경
- 참조 문서 라우팅 추가, 변경, 삭제
- 분석 기준, 클러스터 기준, 제외 기준 변경
- 리포트, CSV, 앱, DB 등 산출물 위치 변경
- 에이전트 실행 순서, fallback 정책, 검증 방식 변경

## 처리 원칙

- 기준 문서와 실행 코드에 영향을 주는 변경만 하네스 반영 후보로 본다.
- 과거 산출 리포트는 기록물이므로 원칙적으로 수정하지 않는다.
- 하네스 자동 수정 전에는 영향 파일과 변경 문구를 사용자에게 먼저 제안한다.
- 사용자가 명시적으로 승인하면 `AGENTS.md`, `CLAUDE.md`, `docs/harness/*.md` 중 필요한 파일만 수정한다.
- 반복적으로 승인된 동일 유형의 변경은 이후 자동 반영 대상으로 승격할 수 있다.

## 변경 후보 분류

| 태그 | 의미 | 대표 반영 위치 |
|---|---|---|
| `es_default` | 기본 ES 서버, 인덱스, 인증, 버전 변경 | `AGENTS.md`, `CLAUDE.md`, `es_schema_*.md` |
| `schema` | 필드명, 중첩 구조, 매핑 로직 변경 | `es_schema_*.md`, 관련 스크립트 |
| `routing` | 작업 유형별 참조 문서 변경 | `AGENTS.md`, `CLAUDE.md` |
| `analysis_rule` | 분석 기준, 분류 기준, 제외 기준 변경 | `style_analysis_rules.md`, 관련 세부 문서 |
| `output_path` | 산출물 저장 위치 변경 | `report_format.md`, `AGENTS.md`, `CLAUDE.md` |
| `agent_behavior` | 에이전트 절차, fallback, 검증 방식 변경 | 해당 agent 문서 또는 세부 하네스 |

## 사용자에게 제안할 형식

```markdown
하네스 반영 후보가 있습니다.

- 변경 유형: `output_path`
- 변경 내용: 로컬 DB 위치를 `output/src_db/`에서 `data/local/`로 변경
- 영향 파일: `AGENTS.md`, `CLAUDE.md`, `docs/harness/report_format.md`
- 제안: 새 산출물 위치 규칙을 기준 문서에 반영하고, 과거 리포트는 수정하지 않음
```

## 변경 이력

승인되어 반영된 변경은 `docs/harness/change_log.md`에 짧게 남긴다.
