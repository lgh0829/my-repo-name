# CLAUDE.md — QA 워크스페이스

이 파일은 **항상 읽히는 얇은 하네스**다. 세부 규칙은 작업 유형에 맞춰 `docs/harness/*.md`를 추가로 읽는다.

---

## 절대 규칙

- 테스트는 **상용서버**에서 수행한다. 실제 서비스 데이터를 임의로 생성·수정·삭제하지 않는다. 테스트용 더미 데이터만 사용한다.
- 테스트 결과는 사실 그대로 기록한다. 추측이나 주관적 판단이 포함될 경우 `[추정]`으로 표시한다.
- FAIL 항목은 반드시 Jira 버그 이슈로 신규 등록한다.
- 스크린샷은 증거 자료로 `output/screenshots/` 에 저장한다.
- Chrome 브라우저를 통해 실제 UI를 조작하며 테스트한다. 코드 분석만으로 PASS 판정하지 않는다.

---

## 작업 시작 체크

작업 시작 전 아래를 확인한다.

- 테스트 대상 이슈: Jira 이슈 키 (예: PS-869)
- 테스트 기능: 어느 기능 / TC 번호 범위
- 진입 경로: 어느 메뉴에서 시작하는지
- 재테스트 여부: 수정 완료 표시된 항목의 재검증인지
- 참조 FRD: 해당 이슈의 description에 명시된 FRD 링크

---

## 참조 문서 라우팅

필요한 세부 문서만 읽는다.

### 하네스 공통 규칙 (`docs/harness/`)

| 작업 | 먼저 읽을 문서 |
|---|---|
| 테스트 결과 기재 방법, Chrome 조작 방법, 버그 등록 절차 | `docs/harness/test_protocol.md` |
| 테스트 결과 누적 문서 작성 형식 | `docs/harness/result_format.md` |
| 하네스 기준 변경 이력 | `docs/harness/harness_maintenance.md` |

### 이슈별 TC 문서 (`docs/testcases/`)

| 이슈 | 기능 | TC 문서 |
|---|---|---|
| PS-869 | 청구항 구조화 (청구항 패널) | `docs/testcases/ps869_claims_panel.md` |
| PS-1077 | 사용성 테스트 (명세서 초안 생성·편집·목차·문단번호) | `docs/testcases/ps1077_spec_usability.md` |

---

## 산출물 위치

- 테스트 결과 문서: `output/<이슈키>_results.md`
- 스크린샷: `output/screenshots/<이슈키>_<TC번호>_<상태>.png`

---

## 작업 종료 체크

테스트 완료 후 아래를 확인한다.

1. 모든 TC 결과가 `output/<이슈키>_results.md`에 기록되었는지 확인
2. FAIL/부분 항목에 대한 Jira 버그 이슈가 등록되었는지 확인
3. 결과 요약을 해당 Jira 이슈 코멘트로 남긴다
4. 신규 테스트 기준·진입경로·환경 변경이 있으면 `docs/harness/harness_maintenance.md`에 기록한다
