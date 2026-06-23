# 기획 아이디어 및 계획 관리

**트리거**: 신규 기능 아이디어 검토, FRD 작성, 스프린트 계획, 기획 산출물 업데이트 시.

---

## 작업 시작 시 항상 먼저 읽을 파일

| 파일 | 이유 |
|---|---|
| `design/session-state.md` | 현재 진행 중인 작업·결정 사항 |
| `design/UBIQUITOUS_LANGUAGE.md` | 용어 혼용 방지 — FRD 작성 전 필수 |
| `design/SERVICE_POLICY.md` | 정책 충돌 여부 확인 |
| `roadmap/2026-OKR.md` | 기획 아이템이 OKR에 연결되는지 확인 |

---

## 아이디어 → 기획 워크플로우

```
아이디어 포착
  ↓
OKR 정합성 확인 (roadmap/2026-OKR.md)
  ↓
FRD 작성 (Template/frd.md 기반)
  ↓
Grill Mode로 설계 검토
  ↓
수직 슬라이스 분해 → Jira 이슈 초안
  ↓
사용자 승인 → atlassian MCP로 이슈 생성
```

---

## FRD 작성 규칙

- 템플릿: `Template/frd.md`
- 파일명: `design/frd-{주제}.md` (영문 소문자 + 하이픈)
- 필수 frontmatter:

```yaml
---
aliases: 한글 제목
작성일: YYYY-MM-DD
수정일: YYYY-MM-DD
상태: 초안 | 검토중 | 확정 | deprecated
tags: [frd, {도메인}]
관련문서: []
상위문서:
---
```

- AI 기능 FRD는 **5절을 "AI 동작 정의"로 교체**하고 도구를 읽기전용/문서변경으로 먼저 분류 (상세: `design/CLAUDE.md` AI 기능 설계 원칙 절)

---

## 수직 슬라이스 분해 (Jira 이슈화)

1. FRD → 수직 슬라이스 목록 초안 (각 슬라이스 = 독립 데모 가능 단위)
2. 각 슬라이스: 제목 / HITL·AFK 여부 / 의존 이슈 / 연관 사용자 스토리 번호
3. 채팅에 초안 표시 → 사용자 승인
4. 블로커 이슈 먼저 생성 → `Blocked by` 실제 번호 기재

---

## 계획 문서 위치

| 산출물 | 위치 |
|---|---|
| FRD | `design/frd-{주제}.md` |
| 스펙 | `design/spec-{주제}.md` |
| IA 구조 | `design/ia-{주제}.csv` |
| 스프린트 계획 | `design/sprint-plan-{주제}.md` |
| 분기 계획 | `roadmap/YYYY-QN-plan.md` |
| 회고 | `roadmap/YYYY-QN-retrospective.md` |

---

## Edit Scope Discipline

- 사용자가 "A를 수정해줘" 라고 하면 **A만** 수정한다.
- 관련 있어 보이는 다른 항목을 함께 수정하지 않는다.
- 멀티스텝 계획은 각 단계마다 승인을 받는다.

---

## 세션 종료 시

`design/session-state.md`를 현재 작업 상태·결정 사항·미결 항목으로 업데이트한다.
