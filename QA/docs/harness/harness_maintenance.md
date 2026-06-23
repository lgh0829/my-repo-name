# 하네스 유지보수 로그

테스트 진행 중 하네스 수정이 필요한 사항을 기록한다.

## 기록 형식

```
## YYYY-MM-DD — <변경 유형>

- 이슈: <무엇이 문제였나>
- 변경 파일: <수정한 harness 파일>
- 내용: <무엇을 바꿨나>
```

---

## 2026-06-23 — 초기 하네스 생성

- 이슈: QA 워크스페이스 신규 설정
- 변경 파일: 전체 신규 생성
- 내용: es-search 하네스 패턴을 따라 CLAUDE.md + docs/harness/ 구조 초기화
  - test_protocol.md: 결과 기재법, Chrome MCP 조작, 버그 등록 절차
  - ps869_claims_panel.md: PS-869 TC-01~TC-21 마스터 목록 (기능 1~6)
  - result_format.md: output 문서 작성 형식
  - harness_maintenance.md: 이 파일
