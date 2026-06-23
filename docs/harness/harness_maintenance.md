# 하네스 유지보수

작업 중 기준이 바뀌면 하네스 반영 후보를 사용자에게 제안한다. **직접 수정 후 통보가 아니라, 후보를 제시하고 승인받는다.**

---

## 변경 감지 트리거

| 변경 | 반영 위치 |
|---|---|
| 새 자동화 스크립트 패턴·라이브러리 추가 | `docs/harness/script_impl.md` |
| FRD 구조·파일명 규칙·분해 절차 변경 | `docs/harness/planning.md` |
| 새 서비스 연동·에이전트·커맨드 추가 | `docs/harness/infra.md` |
| ES URL·인증·인덱스 변경 | `docs/harness/infra.md` + `es-search/docs/harness/es_schema_*.md` |
| Claude 모델 ID 변경 | `docs/harness/infra.md` + `docs/harness/script_impl.md` |
| 절대 규칙·라우팅 테이블·산출물 위치 변경 | 루트 `CLAUDE.md` |

---

## 반영 절차

1. 변경된 기준과 근거를 한 줄로 정리.
2. 어느 문서의 어느 줄을 어떻게 바꿀지 후보 제시.
3. 사용자 승인 후 수정.
4. 루트 `CLAUDE.md`는 얇게 유지 — 세부는 `docs/harness/*.md`로 내린다.
