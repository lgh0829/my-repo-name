# Epic ↔ OKR Initiative 매핑

Jira `로드맵`·`목표` 커스텀 필드가 비어 있으므로, **Epic(`Parent summary`) → OKR Initiative 매핑은 PO가 의미 기반으로 수행**한다. 매핑이 모호하면 추정하지 말고 미결로 표시한다.

매핑 기준선은 `2026-OKR.md`이며, 매 분기 재확인한다.

---

## 2026 Q2 매핑 (확정분)

| Epic (`Parent summary`) | 대응 OKR |
|---|---|
| 재검색 구현 및 검색 히스토리 고도화 | Initiative 2 (검색 엔진) |
| 도면 일관성 검증 및 생성 프롬프트 고도화 | Initiative 1 (AI 명세서 품질 — 도면) |
| 청구항 구조화 | Initiative 1 / 3 |
| 명세서 AI 어시스턴트 구현 | Initiative 4 (AI 어시스턴스) |
| 청구항 보정 및 명세서 기재요건 검토 시스템 | Initiative 1 |
| 소프트런칭 준비 | KR 직접 (활성·전환) |
| 구독 환불 / 회원 탈퇴 | 소프트런칭 전제 |
| GA4 신규 세팅 / 사용자 지표 트래킹 | Initiative 5 (지표·이벤트 트래킹) |

## 매핑 미정 / 미식별 (Q2 미결)

- Initiative 6 (선행기술 리포트 생성) — 대응 Epic이 CSV에서 식별 안 됨.
- Objective 2 (스터디 운영 / 내부 Q&A 봇) — "특허/AI 스터디" Epic 1건 외 미식별.
- infra/tech-debt Epic(OTel 분산추적 등) — 특정 KR이 아닌 **기반 작업**. 별도 분류.

> 매핑 결과를 Jira `목표`·`로드맵` 필드에 역기입하면 다음 회고를 자동 집계할 수 있다 (개선 후보).
