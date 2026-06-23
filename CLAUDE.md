# CLAUDE.md — cc-workspace 루트

이 파일은 **항상 읽히는 얇은 하네스**다. 세부 규칙은 작업 유형에 맞춰 `docs/harness/*.md`를 추가로 읽는다.

하위 디렉토리별 CLAUDE.md의 역할과 범위도 함께 안내한다. 작업 시작 전 해당 디렉토리의 CLAUDE.md를 함께 참조하세요.

---

## 절대 규칙

- **파일 삭제 금지**: `git clean` / `rm -rf` / `git reset --hard` 실행 전 사용자 확인.
- **Jira 쓰기는 승인 후**: 이슈 생성·수정은 초안을 채팅에 표시 → 승인 → `atlassian` MCP 실행.
- **시크릿 커밋 금지**: `.env.*` 파일은 `.example` 제외 절대 커밋하지 않는다.
- 추정·사실·가설을 섞지 않는다. 불확실한 내용은 `[추정]`으로 표시한다.
- 모델 ID는 메모리에서 추정하지 않는다 — `/claude-api` 스킬로 확인한다.

---

## 작업 시작 체크

작업 시작 전 아래를 확인한다.

- 작업 유형: 스크립트 구현 / 기획·FRD / 인프라 설정
- 관련 디렉토리의 CLAUDE.md를 읽었는가
- 세션 상태가 있는 디렉토리(`design/`, `automation/`)는 `session-state.md`를 먼저 읽었는가

---

## 참조 문서 라우팅

필요한 세부 문서만 읽는다.

| 작업 | 먼저 읽을 문서 |
|---|---|
| 자동화 스크립트 신규 작성·수정 | `docs/harness/script_impl.md` |
| FRD 작성, 기능 기획, 아이디어 → 이슈 분해 | `docs/harness/planning.md` |
| 서비스 연동, .claude 에이전트·커맨드, 환경 설정 | `docs/harness/infra.md` |
| 하네스 내용 변경·갱신 | `docs/harness/harness_maintenance.md` |
| ES 특허 데이터 분석 | `es-search/CLAUDE.md` |
| OKR 회고·분기 계획 | `roadmap/CLAUDE.md` |

---

## 작업 종료 체크

작업 중 스크립트 패턴, 기획 절차, 서비스 접속 정보, 에이전트·커맨드 구성이 바뀌었으면 `docs/harness/harness_maintenance.md`를 읽고 하네스 반영 후보를 사용자에게 제안한다.

---

---

## 하위 디렉토리 CLAUDE.md 구조

| 파일 | 성격 | 주요 내용 |
|---|---|---|
| `design/CLAUDE.md` | UX 설계·제품 스펙 | FRD 작성 표준, Jira 이슈 분해 절차, AI 기능 설계, 수직 슬라이스, Edit Scope Discipline, Jira Updates |
| `marketing/CLAUDE.md` | 마케팅·카피라이팅 | Korean Business Writing, B2B 카피 주의사항, 언어/어조 규칙, Jira 연동 안내 |
| `automation/CLAUDE.md` | 자동화·파이프라인 | 자동화 모드, 프롬프트 엔지니어링, 외부 API 연동, Verifying External Data |
| `article/CLAUDE.md` | 개인 블로그 글감 | 글 생애주기, 스타일 가이드 (비즈니스 외 용도) |
| `automation/cloudvoucher_prompt/CLAUDE.md` | 특정 파이프라인 코드 | HWP 생성 아키텍처, 수정 허용 범위 (기술 전용) |

---

## 섹션 → 파일 매핑

| 섹션 | 관리 파일 | 이유 |
|---|---|---|
| `## Korean Business Writing` | `marketing/CLAUDE.md` | 카피 작업 주 공간 |
| `## Jira Updates` | `design/CLAUDE.md` | PS-xxx 이슈, 기존 Jira 이슈 분해 절차 존재 |
| `## Verifying External Data` | `automation/CLAUDE.md` | 외부 API·데이터 연동 작업 |
| `## Edit Scope Discipline` | `design/CLAUDE.md` | FRD 편집 범위 초과 문제 발생 공간 |
