# CLAUDE.md — cc-workspace 루트

이 파일은 `cc-workspace` 하위 디렉토리별 CLAUDE.md의 역할과 범위를 안내합니다.
작업 시작 전 해당 디렉토리의 CLAUDE.md를 함께 참조하세요.

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
