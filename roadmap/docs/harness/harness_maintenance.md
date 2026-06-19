# 하네스 유지보수

작업 중 기준이 바뀌면 하네스에 반영 후보를 사용자에게 제안한다. **직접 수정 후 통보가 아니라, 후보를 제시하고 승인받는다.**

---

## 변경 감지 트리거

아래가 바뀌면 하네스 갱신 후보다.

| 변경 | 반영 위치 |
|---|---|
| OKR 기준선(분기·Objective·KR·채점 기준) 갱신 | `2026-OKR.md` (원본) + 회고 절차 참조 |
| 새 Epic ↔ OKR 매핑 확정 / 미결 해소 | `docs/harness/okr_mapping.md` |
| CSV 컬럼·날짜·상태 체계 변화 (Jira export 포맷 변경) | `docs/harness/csv_parsing.md` |
| 채점 원칙·회고 산출물 포맷 변경 | `docs/harness/retrospective.md` |
| 우선순위 축·계획 절차 변경 | `docs/harness/planning.md` |
| Jira 작성 규칙·MCP 변경 | `docs/harness/jira_write.md` + `JIRA.md` |
| 절대 규칙·라우팅 테이블·산출물 위치 변경 | 루트 `CLAUDE.md` |

---

## 반영 절차

1. 변경된 기준과 근거를 한 줄로 정리.
2. 어느 문서의 어느 줄을 어떻게 바꿀지 후보 제시.
3. 사용자 승인 후 수정.
4. 루트 `CLAUDE.md`는 얇게 유지 — 세부는 `docs/harness/*.md`로 내린다.
