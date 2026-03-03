# 세션 시작 시 필독

세션을 시작하면 `session-state.md`를 먼저 읽고 현재 작업 상태와 핵심 결정 사항을 파악하세요.
세션이 끝나거나 사용자가 요청하면 `session-state.md`를 최신 상태로 업데이트하세요.

---

# Markdown 작성 규칙

## Frontmatter 필수 항목
- aliases: 한글 제목
- 작성일: YYYY-MM-DD
- 수정일: YYYY-MM-DD
- 상태: 초안 | 검토중 | 확정 | deprecated
- tags: 소문자 영문
- 관련문서: 리스트형 wikilink
- 상위문서: 단일 wikilink (없으면 빈값)

## 파일명 규칙
- 영문 소문자 + 하이픈
- 유형-주제-세부내용 순
- 예: frd-patent-search.md / spec-llm-routing.md

## 태그 규칙
- 문서유형: frd / spec / wireframe / userstory / meeting
- 도메인: search / result / onboarding / mypage
- 상태: wip / review / done
