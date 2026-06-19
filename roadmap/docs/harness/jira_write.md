# Jira 이슈 작성 · MCP 쓰기 절차

작성 프로토콜 원본은 `JIRA.md`. 이 문서는 PO 작업에서의 운영 규칙 요약이다.

---

## 쓰기 전 원칙

- **회고·분석은 읽기 전용.** 이슈 생성·수정만 쓰기 작업이다.
- 쓰기 전 사용자에게 확인: (1) 범위(전체 프로젝트 vs 단일 이슈), (2) 포맷을 맞출 참조 이슈(예: PS-435), (3) 원하는 상세 수준.
- **초안을 먼저 채팅에 표시 → 승인 → MCP 실행.** 승인 없이 push 금지.

## 이슈 작성 기준 (`JIRA.md` 핵심)

- 유형은 Sub-task가 아닌 **Task**로 생성. description에 배경(Why)/기획의도/작업내용/완료조건을 풍부히 포함.
- **OKR 기여도가 평가 최상위 가중치** — 이슈마다 연결 KR·근거를 명시한다. OKR 무관 작업은 최종 점수 상한 3.0.
- 제목·설명·유형·우선순위·SP·라벨·연결 OKR이 AI 성과평가 입력이 되므로 누락 없이 채운다.
- `wand-jira-issue` 스킬이 있으면 초안 작성에 활용한다.

## MCP

- 생성·수정은 `atlassian` MCP (`jira_create_issue` / `jira_update_issue` / `jira_link_to_epic` 등).
- 의존성: 블로커 먼저 생성 후 실제 키를 `Blocked by`에 기재.
- 시간 추적이 필요하면 `wandsol` MCP (start/pause/complete) — Jira 상태 전이와는 별개.
